import pandas as pd
from datetime import datetime
from langodata.utils.logger import Logger
from langodata.utils.license_manager import validate_license, check_license_status
from langodata.utils.auth_token import authenticate_user
from langodata.utils.msp_data import read_msp_data
from langodata.utils.macroeconomics_data import read_macroeconomics_data
from langodata.utils.itrs_data import read_itrs_data
from langodata.utils.profile_reader import read_fsp_profile
from langodata.utils.submission_manager import read_submissions

def validate_inputs(data_group, data_source, start_period, end_period):
    """
    Validates inputs for the read functions.
    """
    errors = []
    valid_data_groups = [
        "MSP", "MACROECONOMICS", "ITRS", "NPS", "BANK", "FUNDS", "MORGAGE", "LEASING", 
        "TMS", "FXCFMIS", "CBR", "DERP-DATA", "TS-BOP",
        "IT-MONITORING", "IT-SECURITY", "CURRENCY", "FINANCIAL-MARKETS", 
        "PHYSICAL-SECURITY", "TOURISM"
    ]
    valid_data_sources = ["BSIS", "EDI", "DWH"]

    if data_group not in valid_data_groups:
        errors.append(f"Invalid data group: {data_group}")
    if data_source not in valid_data_sources:
        errors.append(f"Invalid data source: {data_source}")
    try:
        datetime.strptime(start_period, "%d-%b-%Y")
    except ValueError:
        errors.append(f"Invalid start_period: {start_period}. Expected format: DD-MMM-YYYY")
    try:
        datetime.strptime(end_period, "%d-%b-%Y")
    except ValueError:
        errors.append(f"Invalid end_period: {end_period}. Expected format: DD-MMM-YYYY")

    return errors

def validate_environment(data_group="BSIS"):
    """
    Validates license and authentication based on data group.
    """
    try:
        validate_license()
        if not check_license_status():
            return "Invalid license. Please validate your license."
    except Exception as e:
        return f"License validation failed: {str(e)}"

    try:
        if not authenticate_user(data_group):
            return f"User authentication failed for {data_group}."
    except Exception as e:
        return f"Authentication error: {str(e)}"

    return None

def execute_handler(handler_function, *args):
    """
    Executes the given handler function with the provided arguments.
    """
    try:
        return handler_function(*args)
    except Exception as e:
        return {"info": "", "debug": f"Handler error: {str(e)}", "df": pd.DataFrame()}

def read_data(data_group, data_source, data_type, bank_code, start_period, end_period):
    """
    Reads data based on specified parameters and handles workflow.
    """
    data_frequency = bank_code
    logger = Logger()
    feedback = {"info": "", "debug": "", "df": pd.DataFrame()}

    # Validate environment with specific data_group
    env_error = validate_environment(data_group)
    if env_error:
        feedback["debug"] = env_error
        return feedback

    # Validate inputs
    input_errors = validate_inputs(data_group, data_source, start_period, end_period)
    if input_errors:
        feedback["debug"] = " | ".join(input_errors)
        return feedback

    # Select appropriate handler
    if data_group == "MSP":
        feedback = execute_handler(read_msp_data, data_group, data_source, data_type, bank_code, start_period, end_period)
    if data_group == "MACROECONOMICS":
        data_frequency = bank_code
        feedback = execute_handler(read_macroeconomics_data, data_group, data_source, data_type, data_frequency, start_period, end_period)
    if data_group == "ITRS":
        feedback = execute_handler(read_itrs_data, data_group, data_source, data_type, bank_code, start_period, end_period)
    elif data_group == "SUBMISSIONS":
        feedback = execute_handler(read_submissions, data_group, data_source, data_type, bank_code, start_period, end_period)
    else:
        feedback["debug"] = f"No handler found for data group: {data_group}"

    # Check if result is empty
    if feedback["df"].empty:
        feedback["debug"] += " | Output DataFrame is empty. Check data source or query parameters."
    
    return feedback

def read_profile(data_group, data_source, fsp_code):
    """
    Reads FSP profile data based on specified parameters.
    """
    logger = Logger()
    df = pd.DataFrame()
    feedback = {"info": "", "debug": "", "df": pd.DataFrame()}

    # Validate environment
    env_error = validate_environment()
    if env_error:
        feedback["debug"] = env_error
        return feedback

    # Validate inputs
    if data_group not in [
        "MSP", "ITRS", "NPS", "BANK", "FUNDS", "MORGAGE", "LEASING", 
        "TMS", "FXCFMIS", "CBR", "DERP-DATA", "TS-BOP"
    ]:
        feedback["debug"] = f"Invalid data group: {data_group}"
        return feedback
    if data_source not in ["BSIS","EDI","DERPTS"]:
        feedback["debug"] = f"Invalid data source: {data_source}"
        return feedback

    # Execute handler
    feedback = execute_handler(read_fsp_profile, data_group, data_source, fsp_code)

    # Check if result is empty
    if feedback["df"].empty:
        feedback["debug"] += " | Output DataFrame is empty. Check data source or query parameters."
    
    return feedback
