from __future__ import annotations

import logging
import re
from datetime import timedelta
from unidecode import unidecode


import pycountry
from dateutil import parser
from dateutil.parser import parse
from loguru import logger


def process_join_text(*args) -> str:
    """Concatenates the input arguments into a single string.

    Args:
        *args: A variable number of arguments.

    Returns:
        str: The concatenated string.
    """
    return " ".join([str(arg) for arg in args])


def process_sanitize_text(text):
    """
    Removes all characters from the text that are not in the character class [ \r\n\t\S].

    :param text: The text to be sanitized.
    :return: The sanitized text that matches the specified pattern.
    """
    # Define the pattern for allowed characters
    allowed_pattern = r'[ \r\n\t\S]'
    
    # Remove all characters not matching the allowed pattern
    sanitized_text = ''.join(re.findall(allowed_pattern, text))
    
    return sanitized_text

def process_sanitize_text_dual(text):
    """
    Sanitizes the input text so it conforms to two regex patterns:
    1. `[ \r\n\t\S]+`: Allows spaces, tabs, newlines, and any visible characters.
    2. `[\r\n\t\u0020-\uFFFF]+`: Allows tabs, newlines, and Unicode characters from \u0020 to \uFFFF.

    :param text: The input string to be sanitized.
    :return: The sanitized string that matches both patterns.
    """
    # Pattern 1: `[ \r\n\t\S]+`
    pattern1 = r'[ \r\n\t\S]'
    
    # Pattern 2: `[\r\n\t\u0020-\uFFFF]+`
    pattern2 = r'[\r\n\t\u0020-\uFFFF]'
    
    # Apply the first pattern
    sanitized_text = ''.join(re.findall(pattern1, text))
    
    # Apply the second pattern
    sanitized_text = ''.join(re.findall(pattern2, sanitized_text))
    
    return sanitized_text

def process_birth_date(*args) -> str:
    """Converts date format from 'dd-mm-yyyy' to 'yyyy-mm-dd'.

    Args:
        *args: A variable number of arguments. The first argument should be the date string.

    Returns:
        str: The converted date string in 'yyyy-mm-dd' format.

    Raises:
        TypeError: If the value argument is not a string.
    """
    value = args[0]
    if not isinstance(value, str):
        raise TypeError(f"Expected str for value, got {type(value)}")
    try:
        parsed_date = parse(value)
        return parsed_date.date().isoformat()
    except Exception as e:
        logger.error(f"Error processing date: {value} - {e}")
        return value


def process_name(*args) -> str:
    """Concatenates the name and prename arguments.

    Args:
        *args: A variable number of arguments. The first argument should be the name and the second argument should be the prename.

    Returns:
        str: The concatenated name and prename string.
    """
    name, prename = args
    if str(prename).lower() != "nan":
        return f"{prename} {name}"
    elif str(name).lower() != "nan":
        return name
    else:
        logging.error("Name and prename are both 'None'")
        raise ValueError("Name and prename are both 'None'")


def process_test(*args) -> str:
    """Capitalizes the street argument.

    Args:
        *args: A variable number of arguments. The first argument should be the street string.

    Returns:
        str: The capitalized street string.

    Raises:
        TypeError: If the street argument is not a string.
    """
    street = str(args[0])
    if not isinstance(street, str):
        raise TypeError(f"Expected str for street, got {type(street)}")
    return street.capitalize()


def process_address_text(*args) -> str:
    """Processes and concatenates address parts into a single address string.

    Args:
        *args: A variable number of arguments representing address parts.

    Returns:
        str: The concatenated address string.

    Note:
        If no valid address parts are found, the return value will be 'None'.
    """
    address_parts = []
    for arg in args:
        try:
            if str(arg).lower() not in (None, "nan"):
                address_parts.append(str(arg))
        except TypeError:
            logger.error(f"Address text not found as no valid address found in {args}")
    address = " ".join(address_parts)

    # Ensure the resulting address matches the required pattern
    if re.match(r"[ \r\n\t\S]+", address):
        return address
    else:
        return "none"


def process_country(*args) -> str:
    """Processes the country argument and returns the corresponding country code.

    Args:
        *args: A variable number of arguments. The first argument should be the country string.

    Returns:
        str: The country code.

    Note:
        If the country is not found, the return value will be 'None'.
    """
    country = str(args[0]).upper()
    try:
        if country == "D" or country == "DE":
            return "DE"
        if country == "CDN":
            return "CA"
        if country == "EAK":
            return "KE"
        if country == "UAE":
            return "AE"
        if country == "XK":
            return "LC"
        if country == "RCB":
            return "CG"
        if len(country) == 3:
            return pycountry.countries.get(alpha_3=country).alpha_2
        if len(country) == 2:
            return pycountry.countries.get(alpha_2=country).alpha_2
    except AttributeError:
        try:
            return pycountry.countries.search_fuzzy(country)[0].alpha_2
        except LookupError:
            try:
                return pycountry.countries.search_fuzzy(country)[0].alpha_3
            except LookupError:
                logger.error(f"Country not found: {country}")
                return "none"


def process_gender(*args) -> str:
    """Processes the gender argument and returns the corresponding gender code.

    Args:
        *args: A variable number of arguments. The first argument should be the gender string.

    Returns:
        str: The gender code.

    Note:
        If the gender is not recognized, the return value will be 'None'.
    """
    if args[0] == "M":
        return "male"
    if args[0] == "W":
        return "female"
    return "unknown"


def process_patient_reference(*args) -> str:
    """Processes the patient reference argument and returns the patient ID.

    Args:
        *args: A variable number of arguments. The first argument should be the patient reference string.

    Returns:
        str: The patient ID.

    Note:
        If the patient reference is not recognized, the return value will be 'None'.
    """
    if str(args[0]).lower() == "nan":
        return "none"
    return "Patient/" + str(args[0]).replace(".0", "")


def process_encounter_class(*args) -> dict:
    """Processes the encounter class argument and returns the corresponding FHIR class details.

    Args:
        *args: A variable number of arguments. The first argument should be the encounter class string.

    Returns:
        dict: The FHIR class details.
    """
    encounter_class = str(args[0])
    encounter_class_map = {
        "S": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "IMP",
            "display": "inpatient encounter",
        },
        "SN": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "IMP",
            "display": "inpatient encounter",
        },
        "SV": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "IMP",
            "display": "inpatient encounter",
        },
        "A": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "AMB",
            "display": "ambulatory encounter",
        },
    }

    return encounter_class_map.get(
        encounter_class,
        {
            "system": "None",
            "code": "None",
            "display": "None",
        },
    )


def process_location_reference(*args) -> str:
    if str(args[0]).lower() == "nan":
        return "none"
    return "Location/" + str(args[0]).replace(".0", "")



def process_time_format_duration(start: str, duration: str) -> dict:
    """
    Converts a start time and duration into an ISO 8601 period format.

    Args:
        start: The start time as a string in any recognizable datetime format.
        duration: Duration in minutes as a string.

    Returns:
        str: A dictionary-like string with 'start' and 'end' keys formatted in ISO 8601.

    Raises:
        ValueError: If start or duration cannot be parsed or converted.
    """
    try:
        # Parse the start time using isoparse for consistency
        start_time = parser.isoparse(str(start))

        # Clean and validate the duration input
        # Attempt to convert the duration to a float to handle decimal values
        duration_minutes = float(duration)

        # If the duration is too small (like 0.01), treat it as 1 minute
        if duration_minutes < 1:
            duration_minutes = 1

        # Convert duration to timedelta, assuming it's in minutes
        duration_timedelta = timedelta(minutes=duration_minutes)

        # Calculate end time
        end_time = start_time + duration_timedelta

        # Format both start and end times in ISO 8601 with a 'Z' suffix
        start_iso = start_time.isoformat() + "Z"
        end_iso = end_time.isoformat() + "Z"

        return {"start": start_iso, "end": end_iso}
    except Exception as e:
        # Handle potential parsing or calculation errors
        return None

def process_time_format(value: str) -> str:
    """
    Converts time format to 'hh:mm:ss' and datetime to ISO 8601 format using dateutil.parser.

    Args:
        value: A time or datetime string.

    Returns:
        str: The converted time string in 'hh:mm:ss' format or datetime string in ISO 8601 format.

    Raises:
        TypeError: If the argument is not a string.
        ValueError: If the value cannot be parsed into a valid time or datetime format.
    """
    value = str(value)

    value = value.strip()

    if not value:
        raise ValueError("Empty string provided")

    try:
        # Attempt to parse the value using dateutil.parser
        parsed_datetime = parser.isoparse(value)
        return parsed_datetime.isoformat() + "Z"
    except ValueError:

        # If not a datetime, attempt to parse as time
        try:
            parsed_time = parser.parse(value, fuzzy=True)
            # Return the time in 'HH:MM:SS' format
            return str(parsed_time.isoformat()) + "Z"
        except ValueError:
            logger.error(f"Error parsing time: {value}")
            return "none"


def process_encounter_reference(*args) -> str:
    """Processes the encounter reference argument and returns the encounter ID.

    Args:
        *args: A variable number of arguments. The first argument should be the encounter reference string.

    Returns:
        str: The encounter ID.

    Note:
        If the encounter reference is not recognized, the return value will be 'None'.
    """
    if str(args[0]).lower() == "nan":
        return "none"
    return "Encounter/" + str(args[0]).replace(".0", "")

def process_surgery_reference(*args) -> str:
    """Processes the surgery reference argument and returns the surgery ID.

    Args:
        *args: A variable number of arguments. The first argument should be the surgery reference string.

    Returns:
        str: The surgery ID.

    Note:
        If the surgery reference is not recognized, the return value will be 'None'.
    """
    if str(args[0]).lower() == "nan":
        return "none"
    return "Procedure/" + str(args[0]).replace(".0", "")

def process_recorder_reference(*args) -> dict:
    """Processes the recorder reference argument and returns the recorder ID.

    Args:
        *args: A variable number of arguments. The first argument should be the recorder reference string.

    Returns:
        str: The recorder ID.

    Note:
        If the recorder reference is not recognized, the return value will be 'None'.
    """
    if str(args[0]).lower() == "nan":
        return "none"
    reference = "PractitionerRole/" + practitioner_ref_fixer(str(args[0])).replace(".0", "")
    return reference

    


def process_body_site_code_snomed(*args):
    if args[0] == "L":
        return "7771000"
    elif args[0] == "R":
        return "24028007"
    elif args[0] == "B":
        return "51440002"
    else:
        return None


def process_procedure_code_finding_snomed(*args) -> dict:
    code = ""
    dis = ""
    category = str(args[0])
    if category == "OPBERICHT":
        code = "371526002"
        dis = "OP Bericht"
    elif category == "ARZTBRIEF":
        code = "371534008"
        dis = "Arztbrief"
    elif category == "LABORBERICHT":
        code = "4241000179101"
        dis = "Laborbericht"
    elif category == "VERLEGEBRIEF":
        code = "371535009"
        dis = "Verlegbericht"
    else:
        # General documentation procedure
        code = "23745001"
        dis = "General documentation procedure: " + str(category)

    return {"code": code, "system": "http://snomed.info/sct", "display": dis}

# def (*args):
#     code = ""
#     dis = ""
#     desc = str(args[0])
#
#     if args[0] == "OPBERICHT":
#         code = "371526002"
#         desc = "OP Bericht"
#     elif args[0] == "ARZTBRIEF":
#         code = "371534008"
#         desc = "Arztbrief"
#     elif args[0] == "LABORBERICHT":
#         code = "4241000179101"
#         desc = "Laborbericht"
#     elif args[0] == "VERLEGEBRIEF":
#         code = "371535009"
#         desc = "Verlegbericht"
#     elif args[0] == "EXTERNAL_CONSULT":
#         code = "11429006"
#         desc = "external consult"
#     elif args[0] == "CONSENT":
#         code = "61861000000100"
#         desc = "Aufklärungsgespräch"
#     elif args[0] == "CT_THORAX":
#         code = "169069000"
#         desc = "CT Thorax"
#     elif args[0] == "CT_OTHER":
#         code = "77477000"
#         desc = "CT Other"
#     elif args[0] == "CT_MKG":
#         code = "77477000"
#         desc = "CT MKG"
#     elif args[0] == "CT_FLAP_AREA":
#         code = "77477000"
#         desc = "CT Flap Area"
#     elif args[0] == "CT_ABDOMEN":
#         code = "169070004"
#         desc = "CT Abdomen"
#     elif args[0] == "PETCT":
#         code = "450436003"
#         desc = "PETCT"
#     elif args[0] == "LOGOPAEDIE":
#         code = "5154007"
#         desc = "speech therapy"
#     elif args[0] == "EKG":
#         code = "301120008"
#         desc = "ekg"
#     elif args[0] == "CONSULT":
#         code = "11429006"
#         desc = "consult"
#     elif args[0] == "ENDO":
#         code = "698309000"
#         desc = "external consult - endo"
#     elif args[0] == "LYMPH_DRAIN":
#         code = "234303003"
#         desc = "lymphatic drainage"
#     elif args[0] == "TUMORBOARD":
#         code = "395557000"
#         desc = "tumorboard"
#     elif args[0] == "OPERATION_EXAM":
#         code = "302199004"
#         desc = "operation exam"
#     elif args[0] == "OTHER_IMAGING":
#         code = "363679005"
#         desc = "other imaging"
#     elif args[0] == "DENTAL_IMAGING":
#         code = "441875004"
#         desc = "dental imaging"
#     elif args[0] == "PHYSIO":
#         code = "91251008"
#         desc = "physical therapy"
#     elif args[0] == "CARE_MEASURE":
#         code = "225319004"
#         desc = "care measure"
#     elif args[0] == "EMERGENCY_ROOM":
#         code = "50849002"
#         desc = "emergency room"
#     elif args[0] == "EMERGENCY_SERVICE":
#         code = "409971007"
#         desc = "emergency service"
#     elif args[0] == "MRT":
#         code = "113091000"
#         desc = "mrt"
#     elif args[0] == "DIET_CONSULT":
#         code = "11429006"
#         desc = "external consult - diet consult"
#     elif args[0] == "SOCIAL_WORK":
#         code = "308440001"
#         desc = "social worker"
#     elif args[0] == "BIOPSY":
#         code = "86273004"
#         desc = "biopsy"
#     elif args[0] == "OP_PLANNING":
#         code = "866171008"
#         desc = "op-planning"
#     elif args[0] == "CONTROL":
#         code = "225353007"
#         desc = "control visit"
#     elif args[0] == "CONTROL_TU":
#         code = "39228008"
#         desc = "tumor follow up"
#     elif args[0] == "AOP":
#         code = "387713003"
#         desc = "ambulant operation"
#     elif args[0] == "NEUROLOGY":
#         code = "11429006"
#         desc = "external consult - neurology"
#     elif args[0] == "OPTHALMOLOGY":
#         code = ""
#         desc = "external consult - ophthalmology"
#     elif args[0] == "HEART_ECHO":
#         code = "11429006"
#         desc = "echocardiogramm"
#     elif args[0] == "LASER":
#         code = "122456005"
#         desc = "laser"
#     elif args[0] == "WOUND_THERAPY":
#         code = "225358003"
#         desc = "wound therapy"
#     elif args[0] == "PREMED":
#         code = "424252005"
#         desc = "premedication"
#     elif args[0] == "PSYCH_CONSULT":
#         code = "108311000"
#         desc = "external consult - psych consult"
#     elif args[0] == "IMPLANT":
#         code = "40388003"
#         desc = "implant"
#     elif args[0] == "PREANESTHESIA":
#         code = "398172005"
#         desc = "anesthesia consent"
#     elif args[0] == "DOCUMENT_OP":
#         code = "371525003"
#         desc = "document operation"
#     elif args[0] == "DOCUMENT_EXAM":
#         code = "371525003"
#         desc = "document examination"
#     elif args[0] == "DOCUMENT_OTHER":
#         code = "371525003"
#         desc = "document other measures"
#     elif args[0] == "OMFS_CONSENT_REPORT":
#         code = "408835000"
#         desc = "OMFS consent"
#     elif args[0] == "MICROBIOLOGY_REPORT":
#         code = ""
#         desc = "microbiology report"
#     elif args[0] == "ICU_TRANSFER_REPORT":
#         code = ""
#         desc = "ICU transfer report"
#     elif args[0] == "INFECTIOUS_DISEASES_REPORT":
#         code = ""
#         desc = "infectious diseases report"
#     elif args[0] == "TRANSFER_REPORT":
#         code = ""
#         desc = "transfer report"
#     elif args[0] == "DISTRESS_THERMOMETER":
#         code = ""
#         desc = "distress thermometer"
#     elif args[0] == "SCAN_MEDICATION":
#         code = ""
#         desc = "SCAN medication"
#     elif args[0] == "D_REPORT":
#         code = ""
#         desc = "D-report"
#     elif args[0] == "TUMORBOARD_REPORT":
#         code = ""
#         desc = "tumorboard report/protocoll"
#     elif args[0] == "OPERATION_REPORT":
#         code = ""
#         desc = "operation report"
#     elif args[0] == "PATHOLOGY_REPORT":
#         code = ""
#         desc = "pathology report"
#     elif args[0] == "DOCTORS_LETTER":
#         code = ""
#         desc = "doctors letter"
#     elif args[0] == "OTHER_REPORT":
#         code = ""
#         desc = "other report"
#     elif args[0] == "START_PREOP":
#         code = ""
#         desc = "start preop"
#     else:
#         # General documentation procedure
#         code = "23745001"
#         desc = "General documentation procedure"

def process_lea_code_des(*args):
    return str(args[0]) + " " + str(args[1])

def process_lea_codes(*args) -> dict:
    code = ""
    dis = ""
    category = str(args[0])
    desc = str(args[1])
    if "-" in category:
        code = category  # it is an OPS code
        dis = desc
    elif category == "AOP":
        if desc == "Intraoperative Maßnahmen":
            code = "133898004"  #  Präoperative Versorgung
            dis = "Praeoperative Versorgung"
        elif desc == "Anästhesie zur OP" or desc:
            code = "399097000"  # Administration of anaesthesia
            dis = "Administration of anaesthesia"
        elif desc == "ZVK Neuanlage":
            code = "404684003"  # Insertion of central venous catheter
            dis = "Insertion of central venous catheter"
            # raise ValueError(f"Unknown {category, desc}")
    elif category == "OPE":
        code = "387713003"  # Surgical Procedure
        dis = "Surgical Procedure"
    elif category == "PFL":
        code = "7922000"  # General treatment
        dis = "General treatment"
    elif category == "AWR":
        code = "182777000"  # General motioring of patient (post-surgery)
        dis = "General monitoring of patient post surgery"
        # Unhandled "LCD"
    if code == "":
        code = "261665006"
        dis = "General treatment"

        # raise ValueError(f"Unknown {category, desc}")
    # c = Coding(code=code, system="http://snomed.info/sct", display=dis)
    return {"code": code, "system": "http://snomed.info/sct", "display": dis}


def process_specialty(*args) -> dict:
    return {
        "code": str(args[1]),
        "system": "https://www.ukaachen.de/",
        "display": str(args[1]),
    }


def process_specialty_id(*args) -> str:
    return practitioner_ref_fixer(str(args[0]))


def practitioner_ref_fixer(input_str):
    transformations = {
        "ö": "oe",
        "ä": "ae",
        "ü": "ue",
        "Ö": "Oe",
        "Ä": "Ae",
        "Ü": "Ue",
        "ß": "ss",
        "_": "1",
        "-": "2",
    }
    for german_char, replacement in transformations.items():
        input_str = input_str.replace(german_char, replacement)
    return input_str.replace("#", "0").replace(" ", "")


def process_invest_codes(cat, exa) -> dict:
    cat = str(cat)
    exa = str(exa)
    code = ""
    dis = " "

    if cat == "I3-ERN/DIAET" and exa == "ENTERNAEHR":
        code = ""
        dis = "Enteral feeding assessment"
    elif cat == "PHYS-UNTERS" and exa == "PT-EINZEL":
        code = "408439000"
        dis = "Physical therapy assessment"
    elif cat == "MKG-UNTERS" and exa == "NEU":
        code = ""
        dis = "Maxillofacial surgery consultation"
    elif cat == "NOTA-UNTERS" and exa == "KOSTABSPR":
        code = ""
        dis = "Cost assessment for emergency examination"
    elif cat == "ZM-RAD" and exa == "NOTFALL":
        code = ""
        dis = "Emergency dental radiography"
    elif cat == "OP_T" and exa == "CDBRENNEN":
        code = ""
        dis = "Intraoperative CDB (Central data burning)"
    elif cat == "AN-UNTERS" and exa == "OP_T":
        code = ""
        dis = "Pre-operative anesthetic examination"
    elif cat == "RADANF" and exa == "WIEDER":
        code = ""
        dis = "Follow-up radiological examination"
    elif cat == "MED1" and exa == "KONTROLLE":
        code = ""
        dis = "Control medical examination"
    elif cat == "PFLEGE" and exa == "SONSTIGES":
        code = ""
        dis = "Nursing-related assessment"
    elif cat == "KI-UNTERS" and exa == "AUFKLÄRUNG":
        code = ""
        dis = "Pediatric examination and briefing"
    elif cat == "HN-POLI" and exa == "SODVH":
        code = ""
        dis = "Head and neck outpatient examination"
    elif cat == "SOZ-UNTERS" and exa == "SODVGA":
        code = ""
        dis = "Social work assessment"
    elif cat == "CH-UNTERS" and exa == "EKG":
        code = ""
        dis = "Surgical consultation with ECG"
    elif cat == "DE-UNTERS" and exa == "KONSIL":
        code = ""
        dis = "Dermatological consultation"
    elif cat == "UC-UNTERS" and exa == "ABMELD":
        code = ""
        dis = "Final discharge examination"
    elif cat == "AU-AMBULANZ" and exa == "NEU-IMPLANT":
        code = ""
        dis = "New implant examination in ophthalmology"
    elif cat == "TUMOR" and exa == "OP-PLANUNG":
        code = ""
        dis = "Tumor surgery planning"
    elif cat == "AOP-UNTERS" and exa == "NEU-KIEFERGE":
        code = ""
        dis = "Outpatient pre-surgical examination for jaw surgery"
    elif cat == "PO-UNTERS" and exa == "SOAB":
        code = ""
        dis = "Postoperative follow-up examination"
    elif cat == "PH-UNTERS" and exa == "THOR":
        code = ""
        dis = "Thoracic examination"
    elif cat == "I1-UNTERS" and exa == "FÄDEN-EX":
        code = ""
        dis = "Suture removal examination"
    elif cat == "AU-ORTHOPTIK" and exa == "AUFNAHME":
        code = ""
        dis = "Orthoptics intake examination"
    elif cat == "OR-UNTERS" and exa == "OPT":
        code = ""
        dis = "Otorhinolaryngological examination"
    elif cat == "LASERZENTRUM" and exa == "AOP":
        code = ""
        dis = "Laser therapy outpatient pre-surgical examination"
    elif cat == "NU-ANF" and exa == "AUDIO":
        code = ""
        dis = "Nutritional audiological assessment"
    elif cat == "KF-UNTERS" and exa == "ANF-SOZIALD":
        code = ""
        dis = "Initial social services examination"
    elif cat == "AC_OE_ENDO" and exa == "FRIMP":
        code = ""
        dis = "Endoscopic examination with biopsy"
    elif cat == "HG-UNTERS" and exa == "GUSTOMETRIE":
        code = ""
        dis = "Gustometric examination"
    elif cat == "ST-UNTERS" and exa == "RIECHPRUEF":
        code = ""
        dis = "Olfactory testing"
    elif cat == "SPZ-UNTERS" and exa == "THIN":
        code = ""
        dis = "Social pediatric assessment"
    elif cat == "NE-UNTERS" and exa == "ZF2SE":
        code = ""
        dis = "Neurological examination"
    elif cat == "KO-UNTERS" and exa == "DE-WHD-MELAN":
        code = ""
        dis = "Follow-up melanoma examination"
    elif cat == "KK-UNTERS" and exa == ".CTCRA":
        code = ""
        dis = "CT angiography examination"
    elif cat == "PFLONKO" and exa == ".CTHWS":
        code = ""
        dis = "CT scan of the cervical spine"
    elif cat == "NU-UNTERS1" and exa == "CTOB":
        code = ""
        dis = "CT of the orbits"
    elif cat == "AU-UNTERS1" and exa == "CTBWL":
        code = ""
        dis = "CT of the bile ducts"
    elif cat == "ITA-UNTERS" and exa == "HNO":
        code = ""
        dis = "ENT examination"
    elif cat == "KINP-UNTERS" and exa == "AOP MIT ITN":
        code = ""
        dis = "Outpatient surgery with general anesthesia"
    elif cat == "I1-ECHOKARD" and exa == "MRGS":
        code = ""
        dis = "Echocardiogram with mitral regurgitation"
    elif cat == "I2-POLI" and exa == "BETTKONSIL":
        code = ""
        dis = "Bedside consultation in internal medicine"
    elif cat == "PS-UNTERS" and exa == "BEFUND":
        code = ""
        dis = "Psychiatric examination with report"
    elif cat == "AU-PHOTO" and exa == "DVT":
        code = ""
        dis = "Digital volume tomography"
    elif cat == "NC-UNTERS" and exa == "NEU-OP-PLAN":
        code = ""
        dis = "Neurosurgical operation planning"
    elif cat == "I4-UNTERS" and exa == "IMPLANTAT":
        code = ""
        dis = "Implant examination"
    elif cat == "AU-VA" and exa == "TU-PLANUNG":
        code = ""
        dis = "Tumor planning in ophthalmology"
    elif cat == "GG-UNTERS" and exa == "VERBANDWECHS":
        code = ""
        dis = "Dressing change"
    elif cat == "PM-UNTERS" and exa == "SOAX":
        code = ""
        dis = "Post-surgery assessment"
    elif cat == "NP-UNTERS" and exa == "SOHLK":
        code = ""
        dis = "Neurological follow-up examination"
    elif cat == "KIIN-UNTERS" and exa == "SOLEI":
        code = ""
        dis = "Pediatric examination with electronic intake"
    elif cat == "PA-UNTERS" and exa == ".MRANGAIC":
        code = ""
        dis = "MR angiography examination"
    elif cat == "PEDT-UNTERS" and exa == "CDEINLESEN":
        code = ""
        dis = "Cardiac device interrogation"
    elif cat == "KJIA-UNTERS" and exa == "NEU-PAT":
        code = ""
        dis = "New patient pediatric rheumatology examination"
    elif cat == "SE-UNTERS" and exa == "AM-TC":
        code = ""
        dis = "Ambulant TC scan"
    elif cat == "UR-UNTERS" and exa == "O KONSIL":
        code = ""
        dis = "Urology consultation"
    elif cat == "AN-SCHMERZ" and exa == ".CTOR":
        code = ""
        dis = "CT scan for pain management"
    elif cat == "MED3-DIA" and exa == ".CTSC":
        code = ""
        dis = "CT scan of the spine"
    elif cat == "PC-UNTERS" and exa == "ZF2SP":
        code = ""
        dis = "Primary care examination with follow-up"
    elif cat == "ANGIO" and exa == "LKG-KO":
        code = ""
        dis = "Angiography consultation"
    elif cat == "KILU-UNTERS" and exa == "SODVA":
        code = ""
        dis = "Pediatric follow-up examination"
    elif cat == "I3-POLI" and exa == "BILDDRUCK":
        code = ""
        dis = "Image printing examination"
    elif cat == "I1-SM/ICD" and exa == "WV-KINDER":
        code = ""
        dis = "ICD or pacemaker assessment in children"
    elif cat == "KJ-UNTERS" and exa == "MKG-LASER":
        code = ""
        dis = "Laser treatment in pediatric maxillofacial surgery"
    elif cat == "AU-PRIVAT" and exa == "ZF5SE":
        code = ""
        dis = "Private ophthalmological consultation"
    elif cat == "M5-UNTERS" and exa == "CTHTA":
        code = ""
        dis = "CT of the heart"
    elif cat == "HK-UNTERS" and exa == "FDGPETCTKM":
        code = ""
        dis = "FDG-PET scan with contrast"
    elif cat == "ZOP-ALLE" and exa == "BUTTON-WECH":
        code = ""
        dis = "Button change procedure"
    elif cat == "I1GC-UNTERS" and exa == "DE-WDH":
        code = ""
        dis = "German health examination"
    elif cat == "CH-STOMA" and exa == "NOTDIENST":
        code = ""
        dis = "Stoma emergency service"
    elif cat == "LO-UNTERS" and exa == "NNH":
        code = ""
        dis = "Examination of the sinuses"
    elif cat == "ZM-UNTERS" and exa == "CTNNH":
        code = ""
        dis = "CT of the paranasal sinuses"
    elif cat == "KIKU-UNTERS" and exa == "LOGO-AMB":
        code = ""
        dis = "Pediatric speech therapy outpatient examination"
    elif cat == "I1-CMRUNTERS" and exa == "SOWE":
        code = ""
        dis = "Cardiac MRI examination"
    elif cat == "PSIW-UNTERS" and exa == "SOKNI":
        code = ""
        dis = "Psychosomatic follow-up examination"
    elif cat == "PI-ÄRZTE" and exa == "ZF5SP":
        code = ""
        dis = "Physician's follow-up examination"
    elif cat == "GC-UNTERS" and exa == "BILDSCAN":
        code = ""
        dis = "Image scanning procedure"
    elif cat == "PI-KR.PFLEGE" and exa == "TTE":
        code = ""
        dis = "Transthoracic echocardiogram"
    elif cat == "PS-LEISTUNG" and exa == "CTHA":
        code = ""
        dis = "CT of the head and neck"
    elif cat == "FE-UNTERS" and exa == "ALLGEMEIN":
        code = ""
        dis = "General examination"
    elif cat == "IDHT-UNTERS" and exa == ".MRCRA":
        code = ""
        dis = "MR coronary angiography"
    elif cat == "I1HK-UNTERS" and exa == "BISPHOSPHONA":
        code = ""
        dis = "Bisphosphonate treatment follow-up"
    elif cat == "PI-ERGOTH." and exa == "DE-NEU":
        code = ""
        dis = "Occupational therapy assessment"
    elif cat == "OIM-UNTERS" and exa == "THLI":
        code = ""
        dis = "OIM examination with thoracic X-ray"
    elif cat == "NE-MZEB" and exa == "HNKONSIL":
        code = ""
        dis = "Head and neck consultation"
    elif cat == "AR-UNTERS" and exa == "FACESCAN":
        code = ""
        dis = "Facial scan"
    elif cat == "FZA-UNTERS" and exa == "OAE":
        code = ""
        dis = "Otoacoustic emissions test"
    elif cat == "AU-UNTERS" and exa == "NEU-DYSGNATH":
        code = ""
        dis = "New patient with jaw deformity"
    elif cat == "UM-UNTERS" and exa == "GESPRÄCH":
        code = ""
        dis = "Consultation conversation"
    elif cat == "WZAC-UNTERS" and exa == "SOHA":
        code = ""
        dis = "Wound care assessment"
    elif cat == "HU-UNTERS" and exa == "CTHT":
        code = ""
        dis = "CT of the head and thorax"
    elif cat == "FM6-UNTERS" and exa == "AMBKASSE":
        code = ""
        dis = "Ambulant cashier consultation"
    elif cat == "ERGOF-UNTERS" and exa == "GAST":
        code = ""
        dis = "Guest occupational therapy assessment"
    elif cat == "F-PHYSIO" and exa == "O ARZT":
        code = ""
        dis = "Physiotherapy follow-up with physician"
    elif cat == "AU-NH" and exa == "NORM.UNTERS":
        code = ""
        dis = "Normal eye examination"
    elif cat == "FH-MEDGER" and exa == "ONKOKONSIL":
        code = ""
        dis = "Oncology consultation"
    elif cat == "TC-UNTERS" and exa == "AOP OHNE ITN":
        code = ""
        dis = "Outpatient surgery without general anesthesia"
    elif cat == "PCF2-UNTERS" and exa == "ANSPRECHUKA":
        code = ""
        dis = "Patient communication examination"

    if code=="":
        code = "71388002" # Procedure
        dis = str(cat) + " " + str(exa) + unidecode(dis)


    return {"code": code, "system": "http://snomed.info/sct", "display": dis}

