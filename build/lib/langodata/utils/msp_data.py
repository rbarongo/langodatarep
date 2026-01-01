import os
import pandas as pd
from langodata.utils.database import DatabaseConnection
from langodata.utils.logger import Logger


def read_msp_data(data_group: str, data_source: str, data_type: str, bank_code: str, start_period: str, end_period: str) -> dict:
    """
    Reads MSP data from the specified data source and returns a result dictionary.

    Args:
        data_group (str): The data group (e.g., "MSP2").
        data_source (str): The data source (e.g., "BSIS" or "EDI").
        data_type (str): The type of data to fetch.
        bank_code (str): Bank code to filter data. Use '*' for all banks.
        start_period (str): Start date of the period (YYYY-MM-DD).
        end_period (str): End date of the period (YYYY-MM-DD).

    Returns:
        dict: Contains Info, Debug, Contains SQL query, and column names.
    """
    logger = Logger()

    result    = {"info": "", "debug": "", "df": pd.DataFrame()}
    
    
    # Validate inputs
    valid_data_sources = ["BSIS", "EDI"]
    valid_data_types = [f"{i:02}" for i in range(1, 11)] + ["*", "CONS01", "CONS02", "CONS03", "CONS04","CONS05", "CONS06","CONS07I","CONS07II","CONS07III", "CONS07IV", "CONS08", "CONS09", "CONS10"]

    if data_source not in valid_data_sources:
        result["debug"] += f"Invalid data source: {data_source}. "
        return result
    if data_type not in valid_data_types:
        result["debug"] += f"Invalid data type: {data_type}. "
        return result

    
    try:
    
        # Determine schema
        with DatabaseConnection(data_source) as conn:
    
            if data_source == "BSIS":
                schema = "" if "CONS" in data_type else "BSIS_DEV."
            elif data_source == "EDI":
                schema = "EDI."
            else:
                schema = ""
            
            
            table_mapping = {
                "01":"01",
                "CONS01": "01",
                "02":"02",
                "CONS02": "02",
                "03":"03",
                "CONS03": "03",
                "04":"04",
                "CONS04": "04",                             
                "05":"05",
                "CONS05": "05",                 
                "06":"06", 
                "CONS06": "06", 
                "07":"07",
                "CONS07": "07", 
                "CONS07I": "07", 
                "CONS07II": "07",
                "CONS07III": "07",
                "CONS07IV": "07",
                "08":"08",
                "CONS08": "08", 
                "09":"09",
                "CONS09": "09", 
                "10":"10",
                "CONS10": "10"                 
                }
            data_table =    table_mapping.get(data_type)
            #Define SQL query
            table_name = f"{schema}MSP2_{data_table}"            
            condition = "1=1" if bank_code == "*" else f"INSTITUTIONCODE = '{bank_code}'" 
            
            #Define SQL query
            sql_mapping = {
                "CONS01": f"""SELECT ALL A.REPORTINGDATE, A.DESCRIPTIONNO, A.PARTICULARS, sum(A.AMOUNT)  AMOUNT  FROM {table_name} A where
                A.REPORTINGDATE BETWEEN '{start_period}' AND '{end_period}'
                group by A.REPORTINGDATE,  A.DESCRIPTIONNO, A.PARTICULARS
                order by A.DESCRIPTIONNO asc""",
                "CONS02": f"""SELECT ALL A.REPORTINGDATE, A.DESCRIPTIONNO, A.PARTICULARS, sum(A.AMOUNT)  AMOUNT, sum(A.YR_TO_DATE_AMOUNT) YR_TO_DATE_AMOUNT
                FROM {table_name} A where
                A.REPORTINGDATE BETWEEN '{start_period}' AND '{end_period}'
                group by A.REPORTINGDATE,  A.DESCRIPTIONNO, A.PARTICULARS
                order by A.DESCRIPTIONNO asc""", 
                "CONS03": f"""SELECT ALL  A.REPORTINGDATE, A.DESCRIPTIONNO, A.SECTOR, sum( A.BORROWERS) BORROWERS, sum(A.OUTSTANDING_AMOUNT) OUTSTANDING_AMOUNT, sum( A.CURRENT_AMOUNT) CURRENT_AMOUNT, sum(A.ESM) ESM, sum(A.SUBSTANDARD) SUBSTANDARD, sum(A.DOUBTFUL) DOUBTFUL, sum(A.LOSS) LOSS, sum(A.WRITTENOFF) WRITTENOFF FROM {table_name} A where A.REPORTINGDATE BETWEEN '{start_period}' AND '{end_period}' group by A.REPORTINGDATE,  A.DESCRIPTIONNO, A.SECTOR
                order by A.DESCRIPTIONNO""" ,     
                "CONS04": f"""SELECT ALL A.REPORTINGDATE, A.DESCRIPTIONNO, A.PARTICULARS, sum(A.BORROWERS) BORROWERS, sum(A.OUTSTANDING_AMOUNT) OUTSTANDING_AMOUNT, avg(A.WA_IRSLA) WA_IRSLA, avg(A.NIRSLA_LOWEST) NIRSLA_LOWEST, avg(A.NIRSLA_HIGHEST) NIRSLA_HIGHEST,
                avg(A.WA_IRRBA) WA_IRRBA, avg(A.NIRRBA_LOWEST) NIRRBA_LOWEST, avg(A.NIRRBA_HIGHEST) NIRRBA_HIGHEST FROM {table_name} A  
                where
                A.REPORTINGDATE BETWEEN '{start_period}' AND '{end_period}' group by A.REPORTINGDATE,  A.DESCRIPTIONNO, A.PARTICULARS order by A.DESCRIPTIONNO""","CONS05": f"""SELECT 
                ALL A.REPORTINGDATE, A.DESCRIPTIONNO, A.PARTICULARS, sum(A.AMOUNT)  AMOUNT 
                FROM {table_name}  A
                where
                A.REPORTINGDATE BETWEEN '{start_period}' AND '{end_period}' 
                group by 
                A.REPORTINGDATE,  A.DESCRIPTIONNO, A.PARTICULARS
                order by 
                A.DESCRIPTIONNO""",                  
                "CONS06": f"""SELECT 
                ALL A.REPORTINGDATE, A.DESCRIPTIONNO, A.PARTICULARS, 
                sum(A.NUMBER_COMPLAINTS) NUMBER_COMPLAINTS, sum(A.VALUE_COMPLAINTS) VALUE_COMPLAINTS, sum(A.COMPLAINTS_IR) COMPLAINTS_IR,
                sum(A.COMPLAINTS_AGREEMENT) COMPLAINTS_AGREEMENT, sum(A.COMPLAINTS_REPAYMENTS) COMPLAINTS_REPAYMENTS, sum(A.COMPLAINTS_LOAN_ST) COMPLAINTS_LOAN_ST, 
                sum(A.COMPLAINTS_LOAN_PROC) COMPLAINTS_LOAN_PROC, sum(A.COMPLAINTS_OTHERS) COMPLAINTS_OTHERS  
                FROM {table_name} A 
                where
                A.REPORTINGDATE BETWEEN '{start_period}' AND '{end_period}' 
                group by 
                A.REPORTINGDATE,  A.DESCRIPTIONNO, A.PARTICULARS
                order by 
                A.DESCRIPTIONNO""",                           
                "CONS07I": f"""SELECT ALL  A.REPORTINGDATE, A.DESCRIPTIONNO, A.PARTICULARS, sum(A.DEPOSIT_TZS) DEPOSIT_TZS, sum(A.DEPOSIT_FOREIGN_EQV_TZS) DEPOSIT_FOREIGN_EQV_TZS, 
                sum(A.DEPOSIT_TOTAL) DEPOSIT_TOTAL , sum(A.LOAN_TZS) LOAN_TZS, sum(A.LOAN_FOREIGN_EQV_TZS) LOAN_FOREIGN_EQV_TZS,
                sum( A.LOAN_TOTAL) LOAN_TOTAL FROM {table_name} A  where
                A.DESCRIPTIONNO  between 1 and 29 and
                A.REPORTINGDATE BETWEEN '{start_period}' AND '{end_period}' 
                group by A.REPORTINGDATE,  A.DESCRIPTIONNO, A.PARTICULARS
                order by A.DESCRIPTIONNO""" ,                           
                "CONS07II": f"""SELECT ALL A.REPORTINGDATE, A.DESCRIPTIONNO, A.PARTICULARS, sum(A.DEPOSIT_TZS) DEPOSIT_TZS , sum(A.DEPOSIT_FOREIGN_EQV_TZS) DEPOSIT_FOREIGN_EQV_TZS,
                sum(A.DEPOSIT_TOTAL) DEPOSIT_TOTAL, sum(A.LOAN_TZS) LOAN_TZS, sum(A.LOAN_FOREIGN_EQV_TZS) LOAN_FOREIGN_EQV_TZS,
                sum(A.LOAN_TOTAL) LOAN_TOTAL FROM {table_name} A
                where
                A.DESCRIPTIONNO  between 1 and 29 and
                A.REPORTINGDATE BETWEEN '{start_period}' AND '{end_period}'  
                group by A.REPORTINGDATE,  A.DESCRIPTIONNO, A.PARTICULARS
                order by A.DESCRIPTIONNO""" ,  
                "CONS07III": f"""SELECT ALL  A.REPORTINGDATE, A.DESCRIPTIONNO, A.PARTICULARS, sum(A.DEPOSIT_TZS) DEPOSIT_TZS, sum(A.DEPOSIT_FOREIGN_EQV_TZS) DEPOSIT_FOREIGN_EQV_TZS, 
                sum(A.DEPOSIT_TOTAL) DEPOSIT_TOTAL , sum(A.LOAN_TZS) LOAN_TZS, sum(A.LOAN_FOREIGN_EQV_TZS) LOAN_FOREIGN_EQV_TZS,
                sum( A.LOAN_TOTAL) LOAN_TOTAL FROM {table_name}  A  where
                A.DESCRIPTIONNO  between 1 and 29 and 
                A.REPORTINGDATE  BETWEEN '{start_period}' AND '{end_period}' 
                group by A.REPORTINGDATE,  A.DESCRIPTIONNO, A.PARTICULARS
                order by A.DESCRIPTIONNO """ ,  
                "CONS07IV": f"""SELECT ALL  A.REPORTINGDATE, A.DESCRIPTIONNO, A.PARTICULARS, sum(A.DEPOSIT_TZS) DEPOSIT_TZS, sum(A.DEPOSIT_FOREIGN_EQV_TZS) DEPOSIT_FOREIGN_EQV_TZS, 
                sum(A.DEPOSIT_TOTAL) DEPOSIT_TOTAL , sum(A.LOAN_TZS) LOAN_TZS, sum(A.LOAN_FOREIGN_EQV_TZS) LOAN_FOREIGN_EQV_TZS, sum( A.LOAN_TOTAL) LOAN_TOTAL
                FROM {table_name} A 
                where
                A.DESCRIPTIONNO  between 59 and 64 and
                A.REPORTINGDATE BETWEEN '{start_period}' AND '{end_period}' 
                group by A.REPORTINGDATE,  A.DESCRIPTIONNO, A.PARTICULARS
                order by A.DESCRIPTIONNO""",
                "CONS08": f"""SELECT ALL A.REPORTINGDATE, A.DESCRIPTIONNO -1 DESCRIPTIONNO , A.PARTICULARS, sum(A.AMOUNT) AMOUNT FROM {table_name} A where
                A.REPORTINGDATE BETWEEN '{start_period}' AND '{end_period}'  
                group by A.REPORTINGDATE,  A.DESCRIPTIONNO, A.PARTICULARS
                order by A.DESCRIPTIONNO""",
                "CONS09": f"""SELECT ALL A.REPORTINGDATE, A.DESCRIPTIONNO, A.PARTICULARS, sum(A.LOAN_FEMALE_NUMBER) LOAN_FEMALE_NUMBER, sum(A.LOAN_FEMALE_AMOUNT) LOAN_FEMALE_AMOUNT, 
                sum(A.LOAN_MALE_NUMBER) LOAN_MALE_NUMBER, sum(A.LOAN_MALE_AMOUNT) LOAN_MALE_AMOUNT, sum( A.LOAN_NUMBER) LOAN_NUMBER, sum(A.LOAN_AMOUNT) LOAN_AMOUNT 
                FROM {table_name} A where
                A.REPORTINGDATE BETWEEN '{start_period}' AND '{end_period}'   
                group by A.REPORTINGDATE,  A.DESCRIPTIONNO, A.PARTICULARS
                order by A.DESCRIPTIONNO""",
                "CONS10": f"""SELECT ALL A.REPORTINGDATE, A.DESCRIPTIONNO, A.PARTICULARS, 
                sum(A.BRANCHES) BRANCHES, sum(A.EMPLOYEES) EMPLOYEES, 
                sum(A.COMPULSORY_SAVINGS) COMPULSORY_SAVINGS, sum(A.BORROWERS_TO35YRS_M) BORROWERS_TO35YRS_M, 
                sum(A.BORROWERS_TO35YRS_F) BORROWERS_TO35YRS_F, sum(A.BORROWERS_ABOVE35YRS_M) BORROWERS_ABOVE35YRS_M,sum(BORROWERS_ABOVE35YRS_F) BORROWERS_ABOVE35YRS_F,
                sum(A.LOANS_TO35YRS_M) LOANS_TO35YRS_M, sum(A.LOANS_TO35YRS_F) LOANS_TO35YRS_F, sum( A.LOANS_ABOVE35YRS_M) LOANS_ABOVE35YRS_M, 
                sum(A.LOANS_ABOVE35YRS_F) LOANS_ABOVE35YRS_F, sum(A.AMOUNT_TO35YRS_M) AMOUNT_TO35YRS_M, sum(A.AMOUNT_TO35YRS_F) AMOUNT_TO35YRS_F, 
                SUM(A.AMOUNT_ABOVE35YRS_M) AMOUNT_ABOVE35YRS_M, sum(A.AMOUNT_ABOVE35YRS_F) AMOUNT_ABOVE35YRS_F
                FROM {table_name}  A where
                A.REPORTINGDATE BETWEEN '{start_period}' AND '{end_period}'    
                group by A.REPORTINGDATE,  A.DESCRIPTIONNO, A.PARTICULARS
                order by A.DESCRIPTIONNO"""
                }
          
            sql = sql_mapping.get(data_type, f"""
                SELECT * FROM {table_name}
                WHERE {condition} AND TRUNC(REPORTINGDATE) BETWEEN '{start_period}' AND '{end_period}'
                """)
           
            
            
            #result['sql_query']= sql
            
            
            #print(f"sql is : {sql}")


        
            #Fetch data
            data = conn.execute_query(sql)
     

            #Define columns based on data_type
            columns_mapping = {
                "01": ["INSTITUTIONCODE", "REPORTINGDATE", "DESCRIPTIONNO", "PARTICULARS", "AMOUNT"],
                "CONS01": ["REPORTINGDATE", "DESCRIPTIONNO", "PARTICULARS", "AMOUNT"],                
                "02": ["INSTITUTIONCODE", "REPORTINGDATE", "DESCRIPTIONNO", "PARTICULARS", "AMOUNT", "YR_TO_DATE_AMOUNT"],
                "CONS02": ["REPORTINGDATE", "DESCRIPTIONNO", "PARTICULARS", "AMOUNT","YR_TO_DATE_AMOUNT"],  
                "03": ["INSTITUTIONCODE", "REPORTINGDATE", "DESCRIPTIONNO", "SECTOR", "BORROWERS", "OUTSTANDING_AMOUNT",
                       "CURRENT_AMOUNT", "ESM", "SUBSTANDARD", "DOUBTFUL", "LOSS", "WRITTENOFF"],
                "CONS03": ["REPORTINGDATE", "DESCRIPTIONNO", "SECTOR", "BORROWERS", "OUTSTANDING_AMOUNT",
                       "CURRENT_AMOUNT", "ESM", "SUBSTANDARD", "DOUBTFUL", "LOSS", "WRITTENOFF"],    
                "04": ["INSTITUTIONCODE", "REPORTINGDATE", "DESCRIPTIONNO", "PARTICULARS", "BORROWERS",
                       "OUTSTANDING_AMOUNT", "WA_IRSLA", "NIRSLA_LOWEST", "NIRSLA_HIGHEST", "WA_IRRBA",
                       "NIRRBA_LOWEST", "NIRRBA_HIGHEST"],
                "CONS04": ["REPORTINGDATE", "DESCRIPTIONNO", "PARTICULARS", "BORROWERS",
                       "OUTSTANDING_AMOUNT", "WA_IRSLA", "NIRSLA_LOWEST", "NIRSLA_HIGHEST", "WA_IRRBA",
                       "NIRRBA_LOWEST", "NIRRBA_HIGHEST"],       
                "05": ["INSTITUTIONCODE", "REPORTINGDATE", "DESCRIPTIONNO", "PARTICULARS", "AMOUNT"],
                "CONS05": ["REPORTINGDATE", "DESCRIPTIONNO", "PARTICULARS", "AMOUNT"],
                "06": ["INSTITUTIONCODE", "REPORTINGDATE", "DESCRIPTIONNO", "PARTICULARS", "NUMBER_COMPLAINTS",
                       "VALUE_COMPLAINTS", "COMPLAINTS_IR", "COMPLAINTS_AGREEMENT", "COMPLAINTS_REPAYMENTS",
                       "COMPLAINTS_LOAN_ST", "COMPLAINTS_LOAN_PROC", "COMPLAINTS_OTHERS"],
                "CONS06": ["REPORTINGDATE", "DESCRIPTIONNO", "PARTICULARS", "NUMBER_COMPLAINTS",
                       "VALUE_COMPLAINTS", "COMPLAINTS_IR", "COMPLAINTS_AGREEMENT", "COMPLAINTS_REPAYMENTS",
                       "COMPLAINTS_LOAN_ST", "COMPLAINTS_LOAN_PROC", "COMPLAINTS_OTHERS"],
                "07": ["INSTITUTIONCODE", "REPORTINGDATE", "DESCRIPTIONNO", "PARTICULARS", "DEPOSIT_TZS",
                       "DEPOSIT_FOREIGN_EQV_TZS", "DEPOSIT_TOTAL", "LOAN_TZS", "LOAN_FOREIGN_EQV_TZS", "LOAN_TOTAL"],
                "CONS07I": ["REPORTINGDATE", "DESCRIPTIONNO", "PARTICULARS", "DEPOSIT_TZS", "DEPOSIT_FOREIGN_EQV_TZS", 
                            "DEPOSIT_TOTAL" , "LOAN_TZS", "LOAN_FOREIGN_EQV_TZS","LOAN_TOTAL"],
                "CONS07II": ["REPORTINGDATE", "DESCRIPTIONNO", "PARTICULARS", "DEPOSIT_TZS" , "DEPOSIT_FOREIGN_EQV_TZS",
                             "DEPOSIT_TOTAL","LOAN_TZS", "LOAN_FOREIGN_EQV_TZS","LOAN_TOTAL"],
                "CONS07III": ["REPORTINGDATE", "DESCRIPTIONNO", "PARTICULARS", "DEPOSIT_TZS", "DEPOSIT_FOREIGN_EQV_TZS", 
                              "DEPOSIT_TOTAL" , "LOAN_TZS", "LOAN_FOREIGN_EQV_TZS", "LOAN_TOTAL"],
                "CONS07IV": ["REPORTINGDATE", "DESCRIPTIONNO", "PARTICULARS", "DEPOSIT_TZS", "DEPOSIT_FOREIGN_EQV_TZS", 
                             "DEPOSIT_TOTAL" , "LOAN_TZS", "LOAN_FOREIGN_EQV_TZS", "LOAN_TOTAL"],
                "08": ["INSTITUTIONCODE", "REPORTINGDATE", "DESCRIPTIONNO", "PARTICULARS", "AMOUNT"],
                "CONS08": ["REPORTINGDATE", "DESCRIPTIONNO", "PARTICULARS", "AMOUNT"],
                "09": ["INSTITUTIONCODE", "REPORTINGDATE", "DESCRIPTIONNO", "PARTICULARS", "LOAN_FEMALE_NUMBER",
                       "LOAN_FEMALE_AMOUNT", "LOAN_MALE_NUMBER", "LOAN_MALE_AMOUNT", "LOAN_NUMBER", "LOAN_AMOUNT"],
                "CONS09": ["REPORTINGDATE", "DESCRIPTIONNO", "PARTICULARS", "LOAN_FEMALE_NUMBER","LOAN_FEMALE_AMOUNT","LOAN_MALE_NUMBER","LOAN_MALE_AMOUNT","LOAN_NUMBER", "LOAN_AMOUNT"],
                "10": ["INSTITUTIONCODE", "REPORTINGDATE", "DESCRIPTIONNO", "PARTICULARS", "BRANCHES", "EMPLOYEES",
                       "COMPULSORY_SAVINGS", "BORROWERS_TO35YRS_F", "BORROWERS_TO35YRS_M", "BORROWERS_ABOVE35YRS_F",
                       "BORROWERS_ABOVE35YRS_M", "LOANS_TO35YRS_F", "LOANS_TO35YRS_M", "LOANS_ABOVE35YRS_F",
                       "LOANS_ABOVE35YRS_M", "AMOUNT_TO35YRS_F", "AMOUNT_TO35YRS_M", "AMOUNT_ABOVE35YRS_F",
                       "AMOUNT_ABOVE35YRS_M"],
                "CONS10": ["REPORTINGDATE", "DESCRIPTIONNO", "PARTICULARS", "RANCHES","EMPLOYEES","COMPULSORY_SAVINGS","BORROWERS_TO35YRS_M","BORROWERS_TO35YRS_F",        "BORROWERS_ABOVE35YRS_M", "BORROWERS_ABOVE35YRS_F","LOANS_TO35YRS_M","LOANS_TO35YRS_F","LOANS_ABOVE35YRS_M","LOANS_ABOVE35YRS_F",           "AMOUNT_TO35YRS_M","AMOUNT_TO35YRS_F","AMOUNT_ABOVE35YRS_M","AMOUNT_ABOVE35YRS_F"]                       

            }
            columns = columns_mapping.get(data_type)
            if not columns:
                raise ValueError(f"Invalid data_type '{data_type}'. No column mapping found.")
                
   
                
            #Construct DataFrame
            #result["columns_names"] = columns
            if data:            
                result["df"] = pd.DataFrame(data, columns=columns)
            else:
                logger.warning("No data found for the given parameters")
            logger.info(f"Data successfully retrieved.")
            #print(result["df"].head())
    except Exception as e:
        error_message = f"Error fetching MSP data: {str(e)}"
        result["debug"] += str(error_message) if error_message else ""
        logger.error(error_message)

    #result['info'] = logger.info("Fetching data completed successfully.")
    #result['debug'] += logger.debug(f"Executed SQL query: {sql}")
    return result



