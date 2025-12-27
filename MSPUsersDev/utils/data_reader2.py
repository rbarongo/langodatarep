import pandas as pd
from datetime import datetime, timedelta
from utils.logger import Logger
from utils.license_manager import validate_license, check_license_status
from utils.auth_token import authenticate_user
from utils.msp_data import read_msp_data 
from utils.profile_reader import read_fsp_profile
from utils.submission_manager import read_submissions

def validate_inputs(data_group, data_source, start_period, end_period):
    """
    Validates inputs for the read functions.
    """
    errors = []
    valid_data_groups = [
        "MSP", "ITRS", "NPS", "BANK", "FUNDS", "MORGAGE", "LEASING", 
        "TMS", "FXCFMIS", "CBR", "DERP-DATA"
    ]
    valid_data_sources = ["BSIS", "EDI"]

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


def read_data(data_group, data_source, data_type, bank_code, start_period, end_period):

    logger = Logger()
    feedback = {"info": "", "debug": "", "df": pd.DataFrame()}

    
    # License validation
    try:
        validate_license()
        if not check_license_status():
            feedback["debug"] += "Invalid license. Please validate your license."
            return feedback
    except Exception as e:
        feedback["debug"] += f"License validation failed: {str(e)}"
        return feedback
          

    
    # User authentication
    try:
        if not authenticate_user():
            feedback["debug"] += "User authentication failed."
            return feedback
    except Exception as e:
        feedback["debug"] += f"Authentication error: {str(e)}"
        return feedback
    
    # Input validation
    if data_group not in ["MSP", "ITRS", "NPS", "BANK", "FUNDS", "MORGAGE", "LEASING", "TMS", "FXCFMIS", "CBR", "DERP-DATA"]:
        feedback["debug"] += f"Invalid data group: {data_group}. "
        return feedback
    if data_source not in ["BSIS", "EDI"]:
        feedback["debug"] += f"Invalid data source: {data_source}. "
        return feedback
    #if data_type not in [f"{i:02}" for i in range(1, 11)] + ["*"]:
    #    feedback["debug"] += f"Invalid data type: {data_type}"        
    #    return feedback
   
    # Validate date format (assume 'DD-MMM-YYYY')
    try:
        datetime.strptime(start_period, "%d-%b-%Y")  # e.g., 30-SEP-2024
    except ValueError:
        feedback["debug"] += f"Invalid start_period: {start_period}. Expected format: DD-MMM-YYYY"
        return feedback
    try:
        datetime.strptime(end_period, "%d-%b-%Y")  # e.g., 30-DEC-2024
    except ValueError:
        feedback["debug"] += f"Invalid end_period: {end_period}. Expected format: DD-MMM-YYYY"
        return feedback

  
    # Select appropriate handler
    try:
        if data_group == "MSP":
            feedback = read_msp_data(data_group, data_source, data_type, bank_code, start_period, end_period)
        elif data_group == "SUBMISSIONS":
            feedback = read_submissions(data_group, data_source, data_type, bank_code, start_period, end_period)           
        else:
            feedback["debug"] += f"No handler found for data group: {data_group}."
    except Exception as e:
        feedback["debug"] += f"Error while retrieving data: {str(e)}"

    return feedback


def read_profile(data_group, data_source, bank_code):
    logger = Logger()
    feedback = {"info": "", "debug": "", "df": pd.DataFrame()}
    
    # License validation
    try:
        validate_license()
        if not check_license_status():
            feedback["debug"] += "Invalid license. Please validate your license."
            return feedback
    except Exception as e:
        feedback["debug"] += f"License validation failed: {str(e)}"
        return feedback
          

    
    # User authentication
    try:
        if not authenticate_user():
            feedback["debug"] += "User authentication failed."
            return feedback
    except Exception as e:
        feedback["debug"] += f"Authentication error: {str(e)}"
        return feedback
    
    # Input validation
    if data_group not in ["MSP", "ITRS", "NPS", "BANK", "FUNDS", "MORGAGE", "LEASING", "TMS", "FXCFMIS", "CBR", "DERP-DATA"]:
        feedback["debug"] += f"Invalid data group: {data_group}. "
        return feedback
    if data_source not in ["BSIS", "EDI"]:
        feedback["debug"] += f"Invalid data source: {data_source}. "
        return feedback
   
  
    # Select appropriate handler
    try:
        feedback = read_fsp_profile(data_group, data_source, bank_code)            
    except Exception as e:
        feedback["debug"] += f"Error while retrieving data: {str(e)}"

    return feedback
