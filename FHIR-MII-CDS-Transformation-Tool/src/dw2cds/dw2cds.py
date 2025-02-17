import argparse
import logging
import os
import pathlib
from typing import Union

import fhir_config_loader
import loader
import pandas as pd
import transformer
from tqdm import tqdm


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename='run.log', encoding='utf-8', level=logging.INFO)


class dw2cds:
    def __init__(
        self,
        data_folder_path: Union[os.PathLike, str],
        config_path: Union[os.PathLike, str],
        output_data_folder_path: Union[os.PathLike, str],
        processor_paths: list[Union[str, os.PathLike]],
        fhir_base_url: str
    ):
        self.fhir_config_loader = fhir_config_loader.FHIRConfigLoader(
            config_path=config_path,
        )
        self.data_folder_path = data_folder_path
        self.output_data_folder_path = output_data_folder_path
        self.processor_paths = processor_paths
        self.tables = {}
        self.fhir_base_url = fhir_base_url

        self.mappings = self.fhir_config_loader.load_mappings()

        for mapping in self.mappings:
            self.transformer = transformer.FHIRTransformer(
                field_mappings=mapping,
                processor_paths=processor_paths,
                output_data_folder_path=self.output_data_folder_path
            )
            logger.info(f"Transforming {mapping.get('resourceType')}")
            self.transform(
                resource_type=mapping.get("resourceType"),
                used_tables=mapping.get("usedTables"),
                join_on=mapping.get("join_on", []),
            )

    def _load_tables(self, tables_to_load: list[str]):
        loaded_tables = {}
        for table_name in tables_to_load:
            custom_table_config = self.fhir_config_loader.config.get(
                "table_loader",
            ).get(table_name)
            if custom_table_config:
                loaded_tables[table_name] = loader.Loader(
                    data_path=os.path.join(
                        self.data_folder_path,
                        custom_table_config.get("file_name"),
                    ),
                    configuration=custom_table_config,
                ).load()
            else:
                logger.warning(f"No configuration found for table {table_name}.")
        return loaded_tables

    def transform(
        self,
        resource_type: str,
        used_tables: list[str],
        join_on: list[dict[str, Union[str, dict[str, str]]]],
    ):
        if len(used_tables) == 0:
            logger.error("No tables defined in the config file.")
            return

        self.tables = self._load_tables(used_tables)

        joined_table = None
        if join_on:
            joined_table = self._perform_joins(join_on)
        else:
            joined_table = self.tables[used_tables[0]].copy()
            joined_table.columns = [
                used_tables[0] + "." + col
                for col in self.tables[used_tables[0]].columns
            ]

        logger.debug(f"Joined table columns: {joined_table.columns}")
        tqdm.pandas(desc=f"Transforming {resource_type}")
        joined_table.progress_apply(
            self.transformer.transform,
            axis=1,
            args=(resource_type, self.fhir_base_url),
        )

        # Unload tables to free up memory
        self.tables.clear()

    def _perform_joins(self, join_on: list[dict[str, Union[str, dict[str, str]]]]):
        joined_table = None
        keys = []

        # Collect all the keys that will be used for joining
        for join_spec in join_on:
            for table, key in join_spec.items():
                if table != "join_type":
                    keys.append(key)

        for join_spec in join_on:
            left_table, right_table, join_type = None, None, "inner"
            for table, key in join_spec.items():
                if table != "join_type":
                    if not left_table:
                        left_table, left_key = table, key
                    else:
                        right_table, right_key = table, key
                else:
                    join_type = key

            if left_table in self.tables and right_table in self.tables:
                left_tmp_table = self.tables[left_table].copy()
                right_tmp_table = self.tables[right_table].copy()

                left_tmp_table.columns = [
                    left_table + "." + col if col not in keys else col
                    for col in left_tmp_table.columns
                ]
                right_tmp_table.columns = [
                    right_table + "." + col if col not in keys else col
                    for col in right_tmp_table.columns
                ]
                if joined_table is None:
                    joined_table = pd.merge(
                        left_tmp_table,
                        right_tmp_table,
                        left_on=left_key,
                        right_on=right_key,
                        how=join_type,
                    )
                else:
                    joined_table = pd.merge(
                        joined_table,
                        right_tmp_table,
                        left_on=left_key,
                        right_on=right_key,
                        how=join_type,
                    )

                joined_table = joined_table.loc[
                    :,
                    ~joined_table.columns.duplicated(keep="first"),
                ]

            else:
                if left_table not in self.tables:
                    logger.error(f"Table {left_table} not loaded.")
                if right_table not in self.tables:
                    logger.error(f"Table {right_table} not loaded.")

            # Iterate over the columns of the DataFrame
            for column in joined_table.columns:
                # Check if the column name ends with '_x' or '_y'
                if column.endswith("_x") or column.endswith("_y"):
                    # Extract the original column name
                    original_column_name = column[:-2]

                    # Check if both columns exist in the DataFrame
                    if (
                        original_column_name + "_x" in joined_table.columns
                        and original_column_name + "_y" in joined_table.columns
                    ):
                        # Drop the column ending with '_y'
                        joined_table = joined_table.drop(
                            columns=[original_column_name + "_y"],
                        )

                        # Rename the column ending with '_x' to the original column name
                        joined_table = joined_table.rename(
                            columns={original_column_name + "_x": original_column_name},
                        )
        return joined_table


# Argument parsing for command line execution
parser = argparse.ArgumentParser(description="DW2CDS")
parser.add_argument(
    "-c",
    "--config_path",
    type=str,
    help="Path to the FHIR config file",
    default=str(
        pathlib.Path(
            os.path.join(os.getcwd(), "omfs-dataset", "config", "config.json"),
        ).resolve(),
    ),
)
parser.add_argument(
    "-d",
    "--data_folder_path",
    type=str,
    help="Path to the data folder",
    default=str(
        pathlib.Path(os.path.join(os.getcwd(), "omfs-dataset", "data")).resolve(),
    ),
)
parser.add_argument(
    "-o",
    "--output_data_folder",
    type=str,
    help="Path to the output data folder",
    default=str(pathlib.Path(os.path.join(os.getcwd(), "output")).resolve()),
)
parser.add_argument(
    "-p",
    "--processor_paths",
    type=str,
    help="Path to the processor files",
    nargs="+",
    default=[
        os.path.join(
            os.getcwd(),
            "omfs-dataset",
            "config",
            "omfs_data_processors.py",
        ),
    ],
)
parser.add_argument(
    "-f",
    "--fhir_server_url",
    type=str,
    help="URL of the FHIR server",
    default="http://host.docker.internal:8080/fhir",
)

if __name__ == "__main__":
    args = parser.parse_args()
    dw2cds = dw2cds(
        data_folder_path=args.data_folder_path,
        config_path=args.config_path,
        output_data_folder_path=args.output_data_folder,
        processor_paths=args.processor_paths,
        fhir_base_url=args.fhir_server_url
    )
