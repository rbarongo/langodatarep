import os
import pandas as pd
from utils.database import DatabaseConnection
from utils.logger import Logger
#from utils.license_manager import validate_license, check_license_status
#from utils.auth_token import authenticate_user

def read_fsp_profile(data_group: str, data_source: str, fsp_code: str) -> dict:
    """
    Reads MSP data from the specified data source and returns a result dictionary.

    Args:
        data_group (str): The data group (e.g., "MSP2").
        data_source (str): The data source (e.g., "BSIS" or "EDI").
        data_type (str): The type of data to fetch.
        fsp_code (str): Bank code to filter data. Use '*' for all banks.

    Returns:
        dict: Contains Info, Debug, Contains SQL query, and column names.
    """
    logger = Logger()
    feedback = {"info": "", "debug": "", "df": pd.DataFrame()}
    result = {"info": "", "debug": "", "sql_query": "", "columns_names": []}

    
    try:
        with DatabaseConnection(data_source) as conn:
            schema = "BSIS_DEV." if data_source in ["BSIS"] else ""
                 
            #Define SQL query 
            
            fsp_type_mapping = {
                "MSP": "MSP_INSTITUTION",
                "BANK": "INSTITUTION"                 
            }
            profile_table = fsp_type_mapping.get(data_group)
            #Define columns based on data_type
            columns_mapping = {
                "MSP": ["ROWNUM", "INSTITUTIONCODE",  "INSTITUTIONNAME" ,  "INSTITUTIONSTATUS" ,  "INCORPORATIONCERTIFICATENO",  "INCORPORATIONDATE" ,  "TIN" ,            "HQADDRESS",  "LICENSENO",  "LICENSINGDATE", "COMMENCEMENTDATE",  "CONTACT_PERSON" ,  "TEL_NO",  "E_MAIL",  "FAXNO" ,  
                            "POSTAL_ADDRESS" ,  "PHYSICAL_ADDRESS",  "COMPANY_EMAIL",  "CAPITAL_LEVEL" ,  "STATUS_COMMENTS",
                            "OWNERSHIP" ,  "CATEGORY" ,  "NO_AUTHORISED_SHARE",  "NO_PREFERENCE_SHARE",  "VALUE_AUTHORISED_SHARE",  
                            "AUDITOR_NAME"  ,  "REG_DATE  ,  REG_USER"],
                "BANK": ["INSTITUTIONCODE",  "INSTITUTIONNAME" ,  "INSTITUTIONSTATUS" ,  "INCORPORATIONCERTIFICATENO",  "INCORPORATIONDATE" ,              "HQADDRESS",  "LICENSENO",  "LICENSINGDATE", "COMMENCEMENTDATE",  "CONTACT_PERSON" , "FINANCIALYEAR_END", "TEL_NO", "FAXNO", "CABLE_ADDRESS", "E_MAIL",  "CAPITAL_LEVEL",  "APPROVAL_DATE",    "INSTITUTIONTYPE",  "AUDITORCODE",  "AUTHORISED_SHARES" , "USERNAME",
                "ACCOUNTING_SYSTEM","PHYSICAL_ADDRESS","SHORT_NAME", "STATUS_COMMENTS","CATEGORYNO", "NO_AUTHORISED_SHARE",        
                "NO_PREFERENCE_SHARE", "VALUE_AUTHORISED_SHARE", "VALUE_PREFERENCE_SHARE", "OWNERSHIP", "CBSBANK_CODE",
                "SMR_ACCOUNT", "CLEARING_ACCOUNT", "BIC_CODE", "TISS_MEMBER", "ITRS_URT", "ITRS_ZNZ" ]              
                          
            }
            columns = columns_mapping.get(data_group)
            condition = "1=1" if fsp_code == "*" else f"INSTITUTIONCODE = '{fsp_code}'" 
            source =  f"""
                {schema}{profile_table}
            """            
            sql = f"""
                SELECT * FROM {source}
                WHERE {condition}
            """

            result['sql_query']= sql
            
            #Fetch data
            data = conn.execute_query(sql)
            logger.info("Connected to data source and executed query.")
            

            if not columns:
                raise ValueError(f"Invalid data_type '{data_group}'. No column mapping found.")
                
            #Construct DataFrame
            result["columns_names"] = columns
            result["df"] = pd.DataFrame(data, columns=columns)
            logger.info("Data successfully retrieved and packed into a DataFrame.")

            
    except Exception as e:
        error_message = f"Error: {str(e)}"
        logger.error(error_message)
        result["debug"] = error_message

    return result



