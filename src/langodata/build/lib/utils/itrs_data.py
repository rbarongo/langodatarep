import os
import pandas as pd
from utils.database import DatabaseConnection
from utils.logger import Logger
from typing import Dict

def get_schema(data_source: str, data_type: str) -> str:
    """Determine the schema based on the data source and type."""
    if data_source == "BSIS":
        return "" if "CONS" in data_type else "BSIS_DEV."
    elif data_source == "EDI":
        return "EDI."
    return ""
    

def get_table_name(data_type: str) -> str:
    """Return the table name mapped to the given data type."""
    table_mapping = {
        "RATES":"FI_RATE",
        "MONITORING": "MONITORING",
        "OVERALL_ANALYSIS":"master_details",
        "TRANSFORMATION_ERRORS": "ERRORS",
        "COUNTRIES_SECTORS_TZS":"master_details",
        "COUNTRIES_SECTORS_USD": "master_details",
        "CONSOLIDATED_TZS":"master_details",
        "REGION_SECTOR_TZS": "master_details",                             
        "REGION_SECTOR_USD":"master_details",
        "URT_PAYMENTS": "URT_PAYMENTS",  
        "URT_RECEIPTS": "URT_RECEIPTS", 
        "ZNZ_PAYMENTS": "ZNZ_PAYMENTS",  
        "ZNZ_RECEIPTS": "ZNZ_RECEIPTS",  
        "URT_PAYMENTS_FINAL": "URT_PAYMENTS_FINAL",  
        "URT_RECEIPTS_FINAL": "URT_RECEIPTS_FINAL", 
        "ZNZ_PAYMENTS_FINAL": "ZNZ_PAYMENTS_FINAL",  
        "ZNZ_RECEIPTS_FINAL": "ZNZ_RECEIPTS_FINAL" 
    }
    
    return table_mapping.get(data_type.upper())
    
    
    
def get_sql_query(data_type: str, table_name: str, start_period: str, end_period: str, bank_code: str) -> str:
    """Get SQL query for the specified data type."""
    condition = "1=1" if bank_code == "*" else f"INSTITUTIONCODE = '{bank_code}'"
    sql_queries = {
        "RATES": f"""
            SELECT ROWNUM AS Sno, A.RA_DATE AS REPORTING_DATE, A.CU_CODE AS CURRENCY, 
                   B.CU_DESC AS DESCRIPTION, A.RA_SRATE AS TZS_RATE, A.RA_DRATE AS USD_RATE
            FROM {table_name} A, ITRS_FI_CURR B
            WHERE A.RA_DATE BETWEEN '{start_period}' AND '{end_period}'
              AND A.CU_CODE = B.CU_CODE
            ORDER BY A.CU_CODE
        """,
        "MONITORING": """
            SELECT ROWNUM AS "S/NO", A."RETURN NAME", A."EDI RECORDS", A."LAST EDI UPDATE",  
                   A."BSIS RECORDS", A."TRANSFORMED RECORDS", A."LAST MIGRATION", 
                   TO_CHAR(ROUND(A."MIGRATION PERCENTAGE", 0)) || '%' AS "MIGRATION PERCENTAGE",
                   A."LAST TRANSFORMATION", 
                   TO_CHAR(ROUND(A."TRANSFORMATION PERCENTAGE", 0)) || '%' AS "TRANSFORMATION PERCENTAGE",
                   TO_CHAR(ROUND(A."COMPLETION PERCENTAGE", 0)) || '%' AS "COMPLETION PERCENTAGE"
            FROM SYS.ITRS_MONITORING A
        """,
        "OVERALL_ANALYSIS": f"""
            SELECT * 
            FROM {table_name}
            WHERE reportingdate BETWEEN '{start_period}' AND '{end_period}'
        """,
        "TRANSFORMATION_ERRORS": f"""
            SELECT ROWNUM AS SNO, ERROR_DATE, ERROR_DETAILS, ERROR_TYPE, ERROR_ID 
            FROM (
                SELECT ERROR_DATE, ERROR_DETAILS, ERROR_TYPE, ID AS ERROR_ID 
                FROM {table_name}  
                WHERE LAST_DAY(TO_DATE(ERROR_DATE, 'DD-MM-YY') - 31) 
                      BETWEEN '{start_period}' AND '{end_period}'  
                ORDER BY ERROR_DATE DESC
            )
        """,
        "COUNTRIES_SECTORS_TZS": f"""
            SELECT * 
            FROM (
                SELECT DISTINCT COUNTRY, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION AS LOCATION_PURPOSE, 
                                amount_in_tzs_eqv 
                FROM {table_name} 
                WHERE reportingdate BETWEEN '{start_period}' AND '{end_period}'
                GROUP BY COUNTRY, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION, amount_in_tzs_eqv
            )
            PIVOT (
                SUM(amount_in_tzs_eqv)
                FOR LOCATION_PURPOSE IN ('PAYMENT -URT', 'RECEIPTS -URT', 
                                         'PAYMENT -ZANZIBAR', 'RECEIPTS -ZANZIBAR')
            )
        """,
        "COUNTRIES_SECTORS_USD": f""" select *  from 
        (
        select distinct COUNTRY, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION AS LOCATION_PURPOSE , AMOUNT_IN_USD_EQV from {table_name}   
        where reportingdate between   '{start_period}' AND '{end_period}'  
        group by COUNTRY, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION ,AMOUNT_IN_USD_EQV
        order by COUNTRY asc, SECTOR asc
        )
        PIVOT
        (
        SUM(AMOUNT_IN_USD_EQV)
        FOR LOCATION_PURPOSE IN ('PAYMENT -URT','RECEIPTS -URT', 'PAYMENT -ZANZIBAR', 'RECEIPTS -ZANZIBAR')
        )""", 
        "CONSOLIDATED_USD": f"""  select *  from 
        (
        select distinct COUNTRY, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION AS LOCATION_PURPOSE , AMOUNT_IN_USD_EQV from {table_name}   
        where reportingdate between '{start_period}' AND '{end_period}' 
        group by COUNTRY, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION ,AMOUNT_IN_USD_EQV
        order by COUNTRY asc, SECTOR asc
        )
        PIVOT
        (
        SUM(AMOUNT_IN_USD_EQV)
        FOR LOCATION_PURPOSE IN ('PAYMENT -URT','RECEIPTS -URT', 'PAYMENT -ZANZIBAR', 'RECEIPTS -ZANZIBAR')
        ) """, 


               
        "CONSOLIDATED_TZS": f""" select *  from 
        (
        select distinct COUNTRY, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION AS LOCATION_PURPOSE , AMOUNT_IN_TZS_EQV from {table_name}    
        where reportingdate between  '{start_period}' AND '{end_period}'  
        group by COUNTRY, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION ,AMOUNT_IN_TZS_EQV
        order by COUNTRY asc, SECTOR asc
        )
        PIVOT
        (
        SUM(AMOUNT_IN_TZS_EQV)
        FOR LOCATION_PURPOSE IN ('PAYMENT -URT','RECEIPTS -URT', 'PAYMENT -ZANZIBAR', 'RECEIPTS -ZANZIBAR')
        )""" ,                           
                      
        "REGION_SECTOR_TZS": f"""
        select  REGION_GROUPING, SECTOR, sum(nvl(PAYMENT_URT,0)) AS PAYMENT_URT, sum(nvl(RECEIPTS_URT,0)) AS RECEIPTS_URT, sum(nvl(PAYMENT_ZANZIBAR,0)) AS PAYMENT_ZANZIBAR, sum(nvl(RECEIPTS_ZANZIBAR,0)) AS RECEIPTS_ZANZIBAR  from
        (
        select * from  itrs_pivot_002
        union 
        select *  from 
        (
        select 'EAC' as REGION_GROUPING , SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION AS LOCATION_PURPOSE , AMOUNT_IN_TZS_EQV from {table_name} 
        where reportingdate between '{start_period}' AND '{end_period}'
        and COUNTRY in ('TANZANIA','KENYA','UGANDA','RWANDA','BURUNDI','SOUTH SUDAN')
        union all
        select 'SADC' as REGION_GROUPING , SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION AS LOCATION_PURPOSE , AMOUNT_IN_TZS_EQV from {table_name} 
        where reportingdate between '{start_period}' AND '{end_period}'
        and COUNTRY in ('ANGOLA','BOTSWANA','CONGO','LESOTHO','MADAGASCAR','MALAWI','MAURITIUS','MOZAMBIQUE','NAMIBIA','SEYCHELLES','SOUTH AFRICA','SWAZILAND','TANZANIA','ZAMBIA','ZIMBABWE')
        union all
        select 'OTHER' as REGION_GROUPING , SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION AS LOCATION_PURPOSE , AMOUNT_IN_TZS_EQV from {table_name} 
        where reportingdate between '{start_period}' AND '{end_period}'
        and COUNTRY not in ('TANZANIA','KENYA','UGANDA','RWANDA','BURUNDI','SOUTH SUDAN','ANGOLA','BOTSWANA','CONGO','LESOTHO','MADAGASCAR','MALAWI','MAURITIUS','MOZAMBIQUE','NAMIBIA','SEYCHELLES','SOUTH AFRICA','SWAZILAND','ZAMBIA','ZIMBABWE')
        group by SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION ,AMOUNT_IN_TZS_EQV
        order by REGION_GROUPING asc, SECTOR asc
        )
        PIVOT
        (
        SUM(AMOUNT_IN_TZS_EQV)
        FOR LOCATION_PURPOSE IN ('PAYMENT -URT','RECEIPTS -URT', 'PAYMENT -ZANZIBAR', 'RECEIPTS -ZANZIBAR')
        ) 
        )
        group by REGION_GROUPING, SECTOR  
        order by  REGION_GROUPING asc, SECTOR asc

        """ ,  
        "REGION_SECTOR_USD": f"""
        select  REGION_GROUPING, SECTOR, sum(nvl(PAYMENT_URT,0)) AS PAYMENT_URT, sum(nvl(RECEIPTS_URT,0)) AS RECEIPTS_URT, sum(nvl(PAYMENT_ZANZIBAR,0)) AS PAYMENT_ZANZIBAR, sum(nvl(RECEIPTS_ZANZIBAR,0)) AS RECEIPTS_ZANZIBAR  from
        (
        select * from  itrs_pivot_002
        union 
        select *  from 
        (
        select 'EAC' as REGION_GROUPING , SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION AS LOCATION_PURPOSE , AMOUNT_IN_USD_EQV from {table_name}  
        where reportingdate between '{start_period}' AND '{end_period}'
        and COUNTRY in ('TANZANIA','KENYA','UGANDA','RWANDA','BURUNDI','SOUTH SUDAN')
        union all
        select 'SADC' as REGION_GROUPING , SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION AS LOCATION_PURPOSE , AMOUNT_IN_USD_EQV from {table_name}  
        where reportingdate between '{start_period}' AND '{end_period}'
        and COUNTRY in ('ANGOLA','BOTSWANA','CONGO','LESOTHO','MADAGASCAR','MALAWI','MAURITIUS','MOZAMBIQUE','NAMIBIA','SEYCHELLES','SOUTH AFRICA','SWAZILAND','TANZANIA','ZAMBIA','ZIMBABWE')
        union all
        select 'OTHER' as REGION_GROUPING , SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION AS LOCATION_PURPOSE , AMOUNT_IN_USD_EQV from {table_name}  
        where reportingdate between '{start_period}' AND '{end_period}'
        and COUNTRY not in ('TANZANIA','KENYA','UGANDA','RWANDA','BURUNDI','SOUTH SUDAN','ANGOLA','BOTSWANA','CONGO','LESOTHO','MADAGASCAR','MALAWI','MAURITIUS','MOZAMBIQUE','NAMIBIA','SEYCHELLES','SOUTH AFRICA','SWAZILAND','ZAMBIA','ZIMBABWE')
        group by SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION ,AMOUNT_IN_USD_EQV
        order by REGION_GROUPING asc, SECTOR asc
        )
        PIVOT
        (
        SUM(AMOUNT_IN_USD_EQV)
        FOR LOCATION_PURPOSE IN ('PAYMENT -URT','RECEIPTS -URT', 'PAYMENT -ZANZIBAR', 'RECEIPTS -ZANZIBAR')
        ) 
         )
        group by REGION_GROUPING, SECTOR  
        order by  REGION_GROUPING asc, SECTOR asc
        """,
        "ÜRT_PAYMENTS": f"""
        SELECT DESCRIPTIONNO AS SNO, REPORTINGDATE, PURPOSE, PU_CODE AS CODE, SECTOR,  COUNTRY, CURRENCY, AMOUNT  FROM {table_name}
        WHERE {condition} AND TRUNC(REPORTINGDATE) BETWEEN '{start_period}' AND '{end_period}'
        """,
        "ÜRT_RECEIPTS": f"""
        SELECT DESCRIPTIONNO AS SNO, REPORTINGDATE, PURPOSE, PU_CODE AS CODE, SECTOR,  COUNTRY, CURRENCY, AMOUNT  FROM {table_name}
        WHERE {condition} AND TRUNC(REPORTINGDATE) BETWEEN '{start_period}' AND '{end_period}'
        """,
        "ZNZ_PAYMENTS": f"""
        SELECT DESCRIPTIONNO AS SNO, REPORTINGDATE, PURPOSE, PU_CODE AS CODE, SECTOR,  COUNTRY, CURRENCY, AMOUNT  FROM {table_name}
        WHERE {condition} AND TRUNC(REPORTINGDATE) BETWEEN '{start_period}' AND '{end_period}'
        """,
        "ZNZ_RECEIPTS": f"""
        SELECT DESCRIPTIONNO AS SNO, REPORTINGDATE, PURPOSE, PU_CODE AS CODE, SECTOR,  COUNTRY, CURRENCY, AMOUNT  FROM {table_name}
        WHERE {condition} AND TRUNC(REPORTINGDATE) BETWEEN '{start_period}' AND '{end_period}'
        """, 
        "URT_PAYMENTS_FINAL": f"""
        SELECT DESCRIPTIONNO AS SNO, REPORTINGDATE, PURPOSE, PU_CODE AS CODE, SECTOR,  COUNTRY, CURRENCY, AMOUNT_IN_ORIG_CURRENCY,AMOUNT_IN_USD_EQV,AMOUNT_IN_TZS_EQV  FROM {table_name}
        WHERE {condition} AND TRUNC(REPORTINGDATE) BETWEEN '{start_period}' AND '{end_period}'
        """,
        "URT_RECEIPTS_FINAL": f"""
        SELECT DESCRIPTIONNO AS SNO, REPORTINGDATE, PURPOSE, PU_CODE AS CODE, SECTOR,  COUNTRY, CURRENCY, AMOUNT_IN_ORIG_CURRENCY,AMOUNT_IN_USD_EQV,AMOUNT_IN_TZS_EQV  FROM {table_name}
        WHERE {condition} AND TRUNC(REPORTINGDATE) BETWEEN '{start_period}' AND '{end_period}'
        """,
        "ZNZ_PAYMENTS_FINAL": f"""
        SELECT DESCRIPTIONNO AS SNO, REPORTINGDATE, PURPOSE, PU_CODE AS CODE, SECTOR,  COUNTRY, CURRENCY, AMOUNT_IN_ORIG_CURRENCY,AMOUNT_IN_USD_EQV,AMOUNT_IN_TZS_EQV  FROM {table_name}
        WHERE {condition} AND TRUNC(REPORTINGDATE) BETWEEN '{start_period}' AND '{end_period}'
        """,
        "ZNZ_RECEIPTS_FINAL": f"""
        SELECT DESCRIPTIONNO AS SNO, REPORTINGDATE, PURPOSE, PU_CODE AS CODE, SECTOR,  COUNTRY, CURRENCY, AMOUNT_IN_ORIG_CURRENCY,AMOUNT_IN_USD_EQV,AMOUNT_IN_TZS_EQV  FROM {table_name}
        WHERE {condition} AND TRUNC(REPORTINGDATE) BETWEEN '{start_period}' AND '{end_period}'
        """         
        
  
        # Add other queries similarly
        }
    return sql_queries.get(data_type)
    #,f"""
    #    SELECT DESCRIPTIONNO AS SNO, REPORTINGDATE, PURPOSE, PU_CODE AS CODE, SECTOR,  COUNTRY, CURRENCY, AMOUNT FROM {table_name}
    #    WHERE {condition} AND TRUNC(REPORTINGDATE) BETWEEN '{start_period}' AND '{end_period}'
    #    """)
    
           
            
def read_itrs_data(data_group: str, data_source: str, data_type: str, bank_code: str, start_period: str, end_period: str) -> dict:
    logger = Logger()
    result = {"info": "", "debug": "", "df": pd.DataFrame()}

    # Validate inputs
    valid_data_sources = ["BSIS", "EDI"]
    valid_data_types = ["RATES", "MONITORING", "OVERALL_ANALYSIS", "TRANSFORMATION_ERRORS", "COUNTRIES_SECTORS_TZS","COUNTRIES_SECTORS_USD",
    "CONSOLIDATED_TZS","CONSOLIDATED_USD","REGION_SECTOR_TZS","REGION_SECTOR_USD","URT_PAYMENTS", "URT_RECEIPTS", 
            "ZNZ_PAYMENTS", "ZNZ_RECEIPTS",
            "URT_PAYMENTS_FINAL", "URT_RECEIPTS_FINAL",
            "ZNZ_PAYMENTS_FINAL", "ZNZ_RECEIPTS_FINAL" ]
    
          
    if data_source not in valid_data_sources:
        result["debug"] += f"Invalid data source: {data_source}. "
        return result
    if data_type not in valid_data_types:
        result["debug"] += f"Invalid data type: {data_type}. "
        return result
        
    #Define columns based on data_type
    columns_mapping = {
        "RATES": ["Sno","REPORTING_DATE", "CURRENCY", "DESCRIPTION","TZS_RATE", "USD_RATE"],
        "MONITORING": ["S/NO", "RETURN NAME","EDI RECORDS","LAST EDI UPDATE",  "BSIS RECORDS", "TRANSFORMED RECORDS",
                 "LAST MIGRATION", "MIGRATION PERCENTAGE" , "LAST TRANSFORMATION", 
                 "TRANSFORMATION PERCENTAGE"  , "COMPLETION PERCENTAGE"],                
        "OVERALL_ANALYSIS": ["INSTITUTION","TRANSACTION_LOCATION","PERIOD","REPORTINGDATE","DATE","PURPOSE","PURPOSE_DESCRIPTION"],
        "TRANSFORMATION_ERRORS": ["SNO","ERROR_DATE","ERROR_DETAILS", "ERROR_TYPE","ERROR_ID"],  
        "COUNTRIES_SECTORS_TZS": ["COUNTRY", "SECTOR", "PAYMENT -URT", "RECEIPTS -URT", "PAYMENT -ZANZIBAR", "RECEIPTS -ZANZIBAR"],
        "COUNTRIES_SECTORS_USD": ["COUNTRY", "SECTOR", "PAYMENT -URT", "RECEIPTS -URT", "PAYMENT -ZANZIBAR", "RECEIPTS -ZANZIBAR"],    
        "CONSOLIDATED_TZS": ["COUNTRY","SECTOR","PAYMENT -URT", "RECEIPTS -URT", "PAYMENT -ZANZIBAR", "RECEIPTS -ZANZIBAR"],
        "REGION_SECTOR_TZS": ["REGION_GROUPING","SECTOR","PAYMENT_URT","RECEIPTS_URT","PAYMENT_ZANZIBAR","RECEIPTS_ZANZIBAR"],       
        "REGION_SECTOR_USD": ["REGION_GROUPING","SECTOR","PAYMENT_URT","RECEIPTS_URT","PAYMENT_ZANZIBAR","RECEIPTS_ZANZIBAR"], 
        "REGION_SECTOR_USD": ["REGION_GROUPING","SECTOR","PAYMENT_URT","RECEIPTS_URT","PAYMENT_ZANZIBAR","RECEIPTS_ZANZIBAR"],
        "URT_PAYMENTS": ["SNO", "REPORTINGDATE", "PURPOSE", "CODE", "SECTOR",  "COUNTRY", "CURRENCY", "AMOUNT"],
        "URT_RECEIPTS": ["SNO", "REPORTINGDATE", "PURPOSE", "CODE", "SECTOR",  "COUNTRY", "CURRENCY", "AMOUNT"],
        "ZNZ_PAYMENTS": ["SNO", "REPORTINGDATE", "PURPOSE", "CODE", "SECTOR",  "COUNTRY", "CURRENCY", "AMOUNT"],
        "ZNZ_RECEIPTS": ["SNO", "REPORTINGDATE", "PURPOSE", "CODE", "SECTOR",  "COUNTRY", "CURRENCY", "AMOUNT"],  
        "URT_PAYMENTS_FINAL": ["SNO", "REPORTINGDATE", "PURPOSE", "CODE", "SECTOR",  "COUNTRY", "CURRENCY", "AMOUNT_IN_ORIG_CURRENCY","AMOUNT_IN_USD_EQV","AMOUNT_IN_TZS_EQV"],
        "URT_RECEIPTS_FINAL": ["SNO", "REPORTINGDATE", "PURPOSE", "CODE", "SECTOR",  "COUNTRY", "CURRENCY", "AMOUNT_IN_ORIG_CURRENCY","AMOUNT_IN_USD_EQV","AMOUNT_IN_TZS_EQV"],
        "ZNZ_PAYMENTS_FINAL": ["SNO", "REPORTINGDATE", "PURPOSE", "CODE", "SECTOR",  "COUNTRY", "CURRENCY", "AMOUNT_IN_ORIG_CURRENCY","AMOUNT_IN_USD_EQV","AMOUNT_IN_TZS_EQV"],
        "ZNZ_RECEIPTS_FINAL": ["SNO", "REPORTINGDATE", "PURPOSE", "CODE", "SECTOR",  "COUNTRY", "CURRENCY", "AMOUNT_IN_ORIG_CURRENCY","AMOUNT_IN_USD_EQV","AMOUNT_IN_TZS_EQV"]       
        }
    columns = columns_mapping.get(data_type)    

    try:
        with DatabaseConnection(data_source) as conn:

            schema = get_schema(data_source, data_type)
            #print('schema:', schema)
            table_name = f"{schema}ITRS_{get_table_name(data_type)}"
            #print('table_name:', table_name)
            sql_query = get_sql_query(data_type, table_name, start_period, end_period, bank_code)
            #print('sql_query:', sql_query)

            if not sql_query:
                result["debug"] += f"No query found for data type: {data_type}. "
                return result

            # Execute query and load data into DataFrame
            #result["df"] = pd.read_sql(sql_query, conn)
            data = conn.execute_query(sql_query)            

            #Construct DataFrame
            #result["columns_names"] = columns
            if data:            
                result["df"] = pd.DataFrame(data, columns=columns)
            else:
                logger.warning("No data found for the given parameters")
            logger.info(f"Data successfully retrieved.")
            result["info"] = f"Query executed successfully for {data_type}."

    except Exception as e:
        logger.error(f"Error fetching ITRS data: {e}")
        result["debug"] += f"Error fetching data: {str(e)}. "

    return result
            
            



