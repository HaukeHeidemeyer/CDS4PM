import pandas as pd
import os
import pickle

from pm4py import write_ocel_csv, write_ocel_json, write_ocel_xml, write_ocel_sqlite
from pm4py.objects.ocel.obj import OCEL
from cds4py.utils.plugins import load_plugins, load_modifiers, apply_condition, apply_modifier
from tqdm import tqdm
import numpy as np
import numpy.core
import logging

logger = logging.getLogger(__name__)

# Set the maximum number of columns to display
pd.set_option('display.max_columns', None)

# Dynamically load plugins and modifiers
plugins = load_plugins()
modifiers = load_modifiers()


def ensure_columns(df, required_columns):
    for column in required_columns:
        if column not in df.columns:
            df[column] = pd.NA
    return df


def create_ocel_event_log(query_data, defined_objects, defined_events, defined_o2o_relations, debug=False):
    if debug:
        # Path to the pickle file for debugging
        pickle_file_path = "ocel_event_log_debug.pkl"
        if os.path.exists(pickle_file_path):
            with open(pickle_file_path, "rb") as file:
                data = pickle.load(file)
                query_data = data['query_data']
                defined_objects = data['defined_objects']
                defined_events = data['defined_events']
                defined_o2o_relations = data['defined_o2o_relations']
                print("Loaded data from pickle file for debugging.")
        else:
            data = {
                'query_data': query_data,
                'defined_objects': defined_objects,
                'defined_events': defined_events,
                'defined_o2o_relations': defined_o2o_relations
            }
            with open(pickle_file_path, "wb") as file:
                pickle.dump(data, file)
                print(f"Saved arguments to pickle file for debugging at {pickle_file_path}.")

    # Ensure that defined_o2o_relations is a list
    if isinstance(defined_o2o_relations, dict):
        defined_o2o_relations = [defined_o2o_relations]
        logger.debug("Converted defined_o2o_relations from dict to list for processing.")

    if not isinstance(defined_o2o_relations, list):
        logger.error(f"Expected list for defined_o2o_relations but got {type(defined_o2o_relations)}")
        return None

    events = []
    objects = []
    object_id_list = []
    relations = []
    o2o_relations = []

    # Create objects based on the defined object attributes
    for resource_type, df in tqdm(query_data.items()):
        for row in tqdm(df.itertuples(index=False), total=len(df)):
            for object_name, object_def in defined_objects.get(resource_type, {}).items():
                accepted = True
                for attr in object_def['attributes']:
                    if attr['include']:
                        if apply_condition(getattr(row, attr['column_name']), attr['condition'], attr.get('condition_value', '')):
                            continue
                        else:
                            accepted = False
                            break
                if accepted:
                    oid = f"{object_name}-{row.id}"
                    object_data = {
                        'ocel:oid': oid,
                        'ocel:type': resource_type
                    }
                    for attr in object_def['attributes']:
                        if attr['include']:
                            object_data[attr['column_name']] = apply_modifier(getattr(row, attr['column_name']), attr['modifier'], attr.get('modifier_value', None))
                    objects.append(object_data)
                    object_id_list.append(oid)

    # Create events and relationships
    for resource_type, df in query_data.items():
        for row in tqdm(df.itertuples(index=False), total=len(df)):
            for event_name, event_def in defined_events.get(resource_type, {}).items():
                base_event_name = event_def['event_name']
                if pd.isna(getattr(row, event_def['timestamp'])):
                    continue
                event_id = f"{base_event_name}-{row.id}"
                event = {
                    'ocel:eid': event_id,
                    'ocel:activity': base_event_name,
                    'ocel:timestamp': getattr(row, event_def['timestamp']),
                }
                for attr in event_def['attributes']:
                    value = apply_modifier(getattr(row, attr['column_name']), attr['modifier'],
                                           attr.get('modifier_value', None))
                    if attr['include'] and apply_condition(getattr(row, attr['column_name']), attr['condition'], attr.get('condition_value', '')):
                        event[attr['column_name']] = value
                    if attr['add_to_event_name']:
                        if value is not None and pd.notna(value) and not value.isspace() and value != "":
                            event['ocel:activity'] += f"_{value}"
                        event['ocel:activity'] += f"_{value}"
                events.append(event)

                # Add the relations
                rel = event_def.get('relations', [])
                for r in rel:
                    related_object = r.get('related_object', None)
                    qualifier = r.get('qualifier')
                    if qualifier == "null":
                        qualifier = None
                    if not related_object or not qualifier:
                        continue
                    related_object_parts = related_object.split(": ")
                    if len(related_object_parts) == 2:
                        related_resource_type, related_object_name = related_object_parts
                    else:
                        raise ValueError(f"Invalid related object format: {related_object}")

                    if related_resource_type == resource_type:
                        relations.append({"ocel:eid": event_id, "ocel:activity": event['ocel:activity'],
                                          "ocel:timestamp": getattr(row, event_def['timestamp']),
                                          "ocel:oid": f"{resource_type}-{row.id}", "ocel:type": resource_type,
                                          "ocel:qualifier": None})
                        continue
                    related_object_id = getattr(row, r.get('reference', "")).split("/")[1]
                    if related_object_id == "":
                        raise ValueError(f"Related object id is empty for {related_object_name}")

                    related_object_full_name = f"{related_object_name}-{related_object_id}"
                    if related_object_full_name not in object_id_list:
                        if str(related_object_full_name).removesuffix(".0") not in object_id_list:
                            logger.debug(f"Related object {related_object_full_name} not found in the object list")
                            continue
                        else:
                            related_object_full_name = str(related_object_full_name).removesuffix(".0")

                    relations.append({
                        'ocel:eid': event_id,
                        'ocel:activity': event['ocel:activity'],
                        'ocel:timestamp': event['ocel:timestamp'],
                        'ocel:oid': related_object_full_name,
                        'ocel:type': related_object_name,
                        'ocel:qualifier': qualifier
                    })

    # Process object-to-object relations
    if defined_o2o_relations:
        for o2o_relation in defined_o2o_relations:
            for resource_type, l in o2o_relation.items():
                for entry in l:
                    # Extract fields from the entry
                    condition = entry.get('condition', 'None')
                    condition_param = entry.get('condition_param', '')
                    qualifier = entry.get('qualifier', None)
                    target_field = entry.get('target_field', '')
                    reference = entry.get('reference', '')
                    related_object = entry.get('related_object', '')

                    # Ensure related_object format is correct
                    related_object_parts = related_object.split(": ")
                    if len(related_object_parts) != 2:
                        logger.warning(f"Unexpected related object format: {related_object}")
                        continue

                    related_resource_type, related_object_name = related_object_parts

                    # Iterate over query data to find matching object pairs
                    df = query_data[resource_type]
                    for row in df.itertuples(index=False):
                        # Apply the condition
                        if apply_condition(getattr(row, target_field), condition, condition_param):
                            # Get the direct value without applying a modifier
                            reference_value = getattr(row, reference)
                            if reference_value and str(reference_value) != "nan" and str(reference_value) != "None" and str(reference_value) != "null":
                                so = entry.get("source_object").strip()
                                source_object = f"{so}-{row.id}"
                                if isinstance(reference_value, float):
                                    print(reference_value)
                                    reference_value = str(reference_value)

                                target_object_id = reference_value.split("/")[-1]
                                target_object = f"{related_object_name}-{target_object_id}"

                                # Check if both source and target objects exist
                                if source_object in object_id_list and target_object in object_id_list:
                                    o2o_relations.append({
                                        'ocel:oid': source_object,
                                        'ocel:oid_2': target_object,
                                        'ocel:qualifier': qualifier
                                    })

    # Convert lists to pandas DataFrames
    events_df = None
    if len(events) != 0:
        events_df = pd.DataFrame(events)
    objects_df = None
    if len(objects) != 0:
        objects_df = pd.DataFrame(objects)
    relations_df = None
    if len(relations) != 0:
        relations_df = pd.DataFrame(relations)
    o2o_df = None
    if len(o2o_relations) != 0:
        o2o_df = pd.DataFrame(o2o_relations)


    # Create OCEL object with all dataframes
    ocel = OCEL(events=events_df, objects=objects_df, relations=relations_df, o2o=o2o_df)

    return ocel


def export_ocel_event_log(ocel, file_path, format):
    if format == "csv":
        objects_path = file_path + "_objects.csv"
        write_ocel_csv(ocel, file_path, objects_path,)
    elif format == "json":
        write_ocel_json(ocel, file_path)
    elif format == "xml":
        write_ocel_xml(ocel, file_path)
    elif format == "sqlite":
        write_ocel_sqlite(ocel, file_path)
    else:
        raise ValueError("Unsupported export format: {}".format(format))


if __name__ == "__main__":
    ocel = create_ocel_event_log(None, None, None, None, True)

    print(ocel)
    export_ocel_event_log(ocel, "test_ocel", "json")