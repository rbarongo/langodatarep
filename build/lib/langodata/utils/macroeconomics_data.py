import os
import pandas as pd
from langodata.utils.database import DatabaseConnection
from langodata.utils.logger import Logger


def read_macroeconomics_data(data_group: str, data_source: str, data_type: str, data_frequency: str, start_period: str, end_period: str) -> dict:
    """
    Reads Time Series BOT data from the specified data source and returns a result dictionary.

    Args:
        data_group (str): The data group ("MACROECONOMICS"). 
        data_source (str): The data source ("DOMESTIC").
        data_type (str): The type of data to fetch ("BOP", "CPI", "NATIONAL-ACCOUNTS", "FISCAL", "MONETARY", "INTEREST-RATES", "COMMODITIES-PRICES","REAL-SECTOR").
        data_frequency (str): Frequency ("DAILY","MONTHLY","QUARTERLY","ANNUAL-CALENDAR","ANNUAL-FINANCIAL").
        start_period (str): Start date of the period (YYYY-MM-DD).
        end_period (str): End date of the period (YYYY-MM-DD).
        Example: read_macroeconomics_data('MACROECONOMICS','DWH','CPI','MONTHLY','31-JAN-2060','31-JAN-2026')

    Returns:
        dict: Contains Info, Debug, Contains SQL query, and column names.
    """
    logger = Logger()

    result    = {"info": "", "debug": "", "df": pd.DataFrame()}
    
    
    # Validate inputs
    valid_data_sources = ["DWH"]
    valid_data_group = ["MACROECONOMICS"]
    valid_data_types =  ["CPI", "BOP", "NATIONAL-ACCOUNTS", "FISCAL", "MONETARY", "INTEREST-RATES", "COMMODITIES-PRICES","REAL-SECTOR"]
    #valid_data_format = ["WIDE", "LONG"]
    valid_data_frequencies = ["DAILY","MONTHLY","QUARTERLY","ANNUAL-CALENDAR","ANNUAL-FINANCIAL"]

    if data_source not in valid_data_sources:
        result["debug"] += f"Invalid data source: {data_source}. "
        return result
    if data_group not in valid_data_group:
        result["debug"] += f"Invalid data group: {data_group}. "
        return result
    if data_type not in valid_data_types:
        result["debug"] += f"Invalid data type: {data_type}. "
        return result
    if data_frequency not in valid_data_frequencies:    
        result["debug"] += f"Invalid data frequency: {data_frequency}. "
        return result

        
    try:
    
        # Determine schema
        with DatabaseConnection(data_source) as conn:
    
            if data_source == "DWH":
                schema = "DWH."        
            
            table_mapping = {
                "CPI": "FACT_CPI",
                "BOP": "FACT_BOP"
                }
            data_table =    table_mapping.get(data_type)
            #Define SQL query
            table_name = f"{schema}{data_table}"            
            #condition = "1=1" #if bank_code == "*" else f"INSTITUTIONCODE = '{bank_code}'" 
            
            #print("tablename: " + table_name)
            result["debug"] += f"Table name: {table_name}. "

            # Determine the frequency code for the WHERE clause
            freq_code = {
                "DAILY": "D", "MONTHLY": "M", "QUARTERLY": "Q", 
                "ANNUAL-CALENDAR": "A", "ANNUAL-FINANCIAL": "F"
            }.get(data_frequency)

            sql_mapping = {
                "CPI": f"""
                    SELECT 
                        T.TIME_PERIOD,
                        T.YEAR,
                        T.MONTH,
                        L.LOCATION_NAME,
                        L.LOCATION_ISO,
                        I.INDICATOR_NAME,
                        I.DESCRIPTION AS INDICATOR_DESCRIPTION,
                        F.VALUE,
                        U.UNIT,
                        FR.FREQUENCY,
                        S.SOURCE
                FROM {table_name} F
                JOIN DWH.DIM_TIME T       ON F.TIME_ID = T.TIME_ID
                JOIN DWH.DIM_LOCATION L   ON F.LOCATION_ID = L.LOCATION_ID
                JOIN DWH.DIM_INDICATOR I  ON F.INDICATOR_ID = I.INDICATOR_ID
                JOIN DWH.DIM_UNITS U      ON F.UNIT_ID = U.UNIT_ID
                JOIN DWH.DIM_FREQ FR      ON F.FREQ_ID = FR.FREQ_ID
                JOIN DWH.DIM_SOURCES S    ON F.SOURCE_ID = S.SOURCE_ID
                WHERE 
                    T.TIME_PERIOD BETWEEN '{start_period}' AND '{end_period}'
                    AND FR.FREQUENCY = '{freq_code}' -- Takes 'M' from 'MONTHLY', 'Q' from 'QUARTERLY'
                """,

                "BOP": f"""
                    SELECT 
                        T.TIME_PERIOD,
                        T.YEAR,
                        T.MONTH,
                        T.QUARTER,
                        L.LOCATION_NAME,
                        I.INDICATOR_NAME,
                        I.DESCRIPTION AS INDICATOR_DESCRIPTION,
                        F.VALUE,
                        U.UNIT,
                        FR.FREQUENCY,
                        S.SOURCE
                FROM {table_name} F
                JOIN DWH.DIM_TIME T        ON F.TIME_ID = T.TIME_ID
                JOIN DWH.DIM_LOCATION L    ON F.LOCATION_ID = L.LOCATION_ID
                JOIN DWH.DIM_INDICATOR I   ON F.INDICATOR_ID = I.INDICATOR_ID
                JOIN DWH.DIM_UNITS U       ON F.UNIT_ID = U.UNIT_ID
                JOIN DWH.DIM_FREQ FR       ON F.FREQ_ID = FR.FREQ_ID
                JOIN DWH.DIM_SOURCES S     ON F.SOURCE_ID = S.SOURCE_ID
                    WHERE 
                        T.TIME_PERIOD BETWEEN '{start_period}' AND '{end_period}'
                        AND FR.FREQUENCY = '{freq_code}' -- Balance of Payments is often reported Quarterly ('Q')
                        ORDER BY T.TIME_PERIOD DESC"""
                }
          
            sql = sql_mapping.get(data_type)
           
            
            
            #result['sql_query']= sql
            
            
            #print(f"sql is : {sql}")
            result["debug"] += f"SQL query: {sql}"


        
            #Fetch data
            data = conn.execute_query(sql)
     

            #Define columns based on data_type
            columns_mapping = {
                "CPI": ["TIME_PERIOD", "YEAR", "MONTH", "LOCATION_NAME", "LOCATION_ISO", 
                       "INDICATOR_NAME", "INDICATOR_DESCRIPTION", "VALUE", "UNIT", 
                       "FREQUENCY", "SOURCE"], 
                "BOP": ["TIME_PERIOD", "YEAR", "MONTH", "QUARTER", "LOCATION_NAME", "INDICATOR_NAME",
                        "INDICATOR_DESCRIPTION", "VALUE", "UNIT", 
                        "FREQUENCY", "SOURCE"]                      
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
            logger.info(f"Macroeconomics data successfully retrieved.")
            #print(result["df"].head())
    except Exception as e:
        error_message = f"Error fetching Macroeconomics data: {str(e)}"
        result["debug"] += str(error_message) if error_message else ""
        logger.error(error_message)

    #result['info'] = logger.info("Fetching data completed successfully.")
    #result['debug'] += logger.debug(f"Executed SQL query: {sql}")
    return result



