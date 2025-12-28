import os
import pandas as pd
from utils.database import DatabaseConnection
from utils.logger import Logger
#from utils.license_manager import validate_license, check_license_status
#from utils.auth_token import authenticate_user

#read_deleted_returns, read_submitted_returns, late_submitted_returns, read_unsubmitted_returns, read_submission_errors

def read_submissions(data_group: str, data_source: str, data_type: str, bank_code: str, start_period: str, end_period: str) -> dict:
    """
    Reads MSP data from the specified data source and returns a result dictionary.

    Args:
        data_group (str): The data group (e.g., "MSP2").
        data_source (str): The data source (e.g., "BSIS" or "EDI").
        data_type (str): The type of data to fetch.  "SUBMITTED", "DELETED"
        bank_code (str): Bank code to filter data. Use '*' for all banks.
        start_period (str): Start date of the period (YYYY-MM-DD).
        end_period (str): End date of the period (YYYY-MM-DD).
        
    Returns:
        dict: Contains Info, Debug, Contains SQL query, and column names.
    """
    logger = Logger()
    feedback = {"info": "", "debug": "", "df": pd.DataFrame()}
    result = {"info": "", "debug": "", "sql_query": "", "columns_names": []}

    
    try:
        with DatabaseConnection(data_source) as conn:
            schema = "BSIS_DEV." if data_source in ["BSIS", "EDI"] else ""
                 
          
            
            #Define SQL query 
            
            action_columns_mapping = {
                "SUBMITTED": """A.BANKCODE AS INSTITUTIONCODE,UPPER(SUBMISSIONNAME) SUBMISSIONNAME,REPORTINGDATE,AUTHORIZEDDATE,UPPER(USERNAME)          SUBMITTEDBY,UPPER(USERNAME) AUTHORIZEDBY""",
                "DELETED": """A.BANKCODE AS INSTITUTIONCODE,UPPER(SUBMISSIONNAME) SUBMISSIONNAME,REPORTINGDATE,AUTHORIZEDDATE,UPPER(USERNAME)          SUBMITTEDBY,UPPER(USERNAME) AUTHORIZEDBY"""   
            }
            query_columns = action_columns_mapping.get(data_type)
            
            data_source= f"""{schema}BSIS_SUBMISSION_STATUS@BSIS_TO_EDI A,{schema}.BSIS_SUBMISSION_PERIOD@BSIS_TO_EDI B,
             {schema}.BSIS_SUBMISSION@BSIS_TO_EDI C, {schema}.BSIS_EDIUSERS@BSIS_TO_EDI  D"""            
            
            action_condition_mapping = {
                "SUBMITTED": """A.BANKCODE AS INSTITUTIONCODE,UPPER(SUBMISSIONNAME) SUBMISSIONNAME,REPORTINGDATE,AUTHORIZEDDATE,UPPER(USERNAME)          SUBMITTEDBY,UPPER(USERNAME) AUTHORIZEDBY""",
                "DELETED": """A.BANKCODE AS INSTITUTIONCODE,UPPER(SUBMISSIONNAME) SUBMISSIONNAME,REPORTINGDATE,AUTHORIZEDDATE,UPPER(USERNAME)          SUBMITTEDBY,UPPER(USERNAME) AUTHORIZEDBY FROM BSIS_SUBMISSION_STATUS@BSIS_TO_EDI A,
                BSIS_SUBMISSION_PERIOD@BSIS_TO_EDI B,BSIS_SUBMISSION@BSIS_TO_EDI C, BSIS_EDIUSERS@BSIS_TO_EDI D"""   
            }
            query_conditions = action_condition_mapping.get(data_type)
            institution_condition = "1=1" if bank_code == "*" else f"INSTITUTIONCODE = '{bank_code}'" 
            date_condition = f"TRUNC(REPORTINGDATE) BETWEEN '{start_period}' AND '{end_period}'"
            condition = institution_condition + date_condition
            
            #columns
            if not columns:
                raise ValueError(f"Invalid data_type '{data_type}'. No column mapping found.")
                
                
            columns_mapping = {
                "SUBMITTED": ["INSTITUTIONCODE", "SUBMISSIONNAME", "REPORTINGDATE", "AUTHORIZEDDATE", "SUBMITTEDBY", "AUTHORIZEDBY"],
                "DELETED": ["INSTITUTIONCODE", "SUBMISSIONNAME", "REPORTINGDATE", "AUTHORIZEDDATE", "SUBMITTEDBY", "AUTHORIZEDBY"]
    
            }
            columns = columns_mapping.get(data_type)  
           
            sql = f"""
                SELECT '{query_columns}' FROM {data_source}
                WHERE {condition}"""
                            
            
            result['sql_query']= sql
            
            #Fetch data
            data = conn.execute_query(sql)
            logger.info("Connected to data source and executed query.")
            
  
                
            #Construct DataFrame
            result["columns_names"] = columns
            result["df"] = pd.DataFrame(data, columns=columns)
            logger.info("Data successfully retrieved and packed into a DataFrame.")

            
    except Exception as e:
        error_message = f"Error: {str(e)}"
        logger.error(error_message)
        result["debug"] = error_message

    return result



