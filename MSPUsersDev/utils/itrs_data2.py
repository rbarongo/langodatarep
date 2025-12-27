import os
import pandas as pd
from utils.database import DatabaseConnection
from utils.logger import Logger


def read_itrs_data(data_group: str, data_source: str, data_type: str, bank_code: str, start_period: str, end_period: str) -> dict:

    logger = Logger()

    result    = {"info": "", "debug": "", "df": pd.DataFrame()}
    
    
    # Validate inputs
    valid_data_sources = ["BSIS", "EDI"]
    valid_data_types = ["RATES"]

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
            data_table =    table_mapping.get(data_type)
            #Define SQL query
            table_name = f"{schema}ITRS_{data_table}"            
            condition = "1=1" if bank_code == "*" else f"INSTITUTIONCODE = '{bank_code}'" 
            
            #Define SQL query
            sql_mapping = {
                "RATES": f"""
                SELECT ROWNUM AS Sno, A.RA_DATE AS REPORTING_DATE, A.CU_CODE AS CURRENCY, B.CU_DESC AS DESCRIPTION, A.RA_SRATE AS TZS_RATE, A.RA_DRATE AS USD_RATE
                FROM {table_name} A,  ITRS_FI_CURR B
                WHERE 
                A.RA_DATE BETWEEN '{start_period}' AND '{end_period}'
                AND A.CU_CODE = B.CU_CODE
                ORDER BY A.CU_CODE 
                """,
                "MONITORING": f"""select rownum as "S/NO", A."RETURN NAME", A."EDI RECORDS", A."LAST EDI UPDATE",  A."BSIS RECORDS", A."TRANSFORMED RECORDS",
                A."LAST MIGRATION", TO_CHAR(ROUND(A."MIGRATION PERCENTAGE",0)) || '%' AS "MIGRATION PERCENTAGE" , A."LAST TRANSFORMATION", 
                TO_CHAR(ROUND(A."TRANSFORMATION PERCENTAGE",0)) || '%' AS "TRANSFORMATION PERCENTAGE"  , TO_CHAR(ROUND(A."COMPLETION PERCENTAGE",0)) || '%' AS "COMPLETION PERCENTAGE"  from SYS.ITRS_MONITORING A """, 
                "OVERALL_ANALYSIS": f""" Select * from {table_name}
                where reportingdate between '{start_period}' AND '{end_period}' """ ,     
                "TRANSFORMATION_ERRORS": f"""SELECT ROWNUM as SNO, ERROR_DATE, ERROR_DETAILS, ERROR_TYPE, ERROR_ID FROM (
                SELECT  ERROR_DATE, ERROR_DETAILS, ERROR_TYPE, ID AS ERROR_ID FROM {table_name}  
                WHERE LAST_DAY(TO_DATE(ERROR_DATE,'DD-MM-YY') -31) between '{start_period}' AND '{end_period}'  
                order by ERROR_dATE DESC )""",
                "COUNTRIES_SECTORS_TZS": f"""select *  from 
                (
                 select distinct COUNTRY, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION AS LOCATION_PURPOSE , amount_in_tzs_eqv from {table_name} 
                 where reportingdate between  '{start_period}' AND '{end_period}'  
                 group by COUNTRY, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION ,amount_in_tzs_eqv
                 order by COUNTRY asc, SECTOR asc
                )
                 PIVOT
                (
                 SUM(amount_in_tzs_eqv)
                 FOR LOCATION_PURPOSE IN ('PAYMENT -URT','RECEIPTS -URT', 'PAYMENT -ZANZIBAR', 'RECEIPTS -ZANZIBAR')
                ) """,                  
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
                "CONSOLIDATED_TZS": f"""  select *  from 
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


               
                "REGIONS_SECTOR_USD": f""" select *  from 
                (
                select distinct COUNTRY, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION AS LOCATION_PURPOSE , AMOUNT_IN_USD_EQV from {table_name}    
                where reportingdate between  '{start_period}' AND '{end_period}'  
                group by COUNTRY, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION ,AMOUNT_IN_USD_EQV
                order by COUNTRY asc, SECTOR asc
                )
                PIVOT
                (
                SUM(AMOUNT_IN_USD_EQV)
                FOR LOCATION_PURPOSE IN ('PAYMENT -URT','RECEIPTS -URT', 'PAYMENT -ZANZIBAR', 'RECEIPTS -ZANZIBAR')
                )""" ,                           
                "REGIONS_SECTOR_USD": f""" select *  from 
                (
                select distinct COUNTRY, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION AS LOCATION_PURPOSE , AMOUNT_IN_USD_EQV from {table_name}    
                where reportingdate between  '{start_period}' AND '{end_period}'  
                group by COUNTRY, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION ,AMOUNT_IN_USD_EQV
                order by COUNTRY asc, SECTOR asc
                )
                PIVOT
                (
                SUM(AMOUNT_IN_USD_EQV)
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
                "URT_PAYMENTS": f"""
                select DESCRIPTIONNO AS SNO, REPORTINGDATE, PURPOSE, PU_CODE AS CODE, SECTOR,  COUNTRY, CURRENCY, AMOUNT  
                from {table_name}
                where reportingdate between '{start_period}' AND '{end_period}'
                and '{condition}'
                """ ,  
                "URT_RECEIPTS": f"""
                select DESCRIPTIONNO AS SNO, REPORTINGDATE, PURPOSE, PU_CODE AS CODE, SECTOR,  COUNTRY, CURRENCY, AMOUNT  
                from {table_name}
                where reportingdate between '{start_period}' AND '{end_period}'
                and '{condition}'
                """ ,  
                "ZNZ_PAYMENTS": f"""
                select DESCRIPTIONNO AS SNO, REPORTINGDATE, PURPOSE, PU_CODE AS CODE, SECTOR,  COUNTRY, CURRENCY, AMOUNT  
                from {table_name}
                where reportingdate between '{start_period}' AND '{end_period}'
                and '{condition}'
                """ ,  
                "ZNZ_RECEIPTS": f"""
                select DESCRIPTIONNO AS SNO, REPORTINGDATE, PURPOSE, PU_CODE AS CODE, SECTOR,  COUNTRY, CURRENCY, AMOUNT  
                from {table_name}
                where reportingdate between '{start_period}' AND '{end_period}'
                and '{condition}'
                """ ,                 
               "URT_PAYMENTS_FINAL": f"""
                select DESCRIPTIONNO AS SNO, REPORTINGDATE, PURPOSE, PU_CODE AS CODE, SECTOR,  COUNTRY, CURRENCY, AMOUNT  
                from {table_name}
                where reportingdate between '{start_period}' AND '{end_period}'
                and '{condition}'
                """ ,  
                "URT_RECEIPTS_FINAL": f"""
                select DESCRIPTIONNO AS SNO, REPORTINGDATE, PURPOSE, PU_CODE AS CODE, SECTOR,  COUNTRY, CURRENCY, AMOUNT  
                from {table_name}
                where reportingdate between '{start_period}' AND '{end_period}'
                and '{condition}'
                """ ,  
                "ZNZ_PAYMENTS_FINAL": f"""
                select DESCRIPTIONNO AS SNO, REPORTINGDATE, PURPOSE, PU_CODE AS CODE, SECTOR,  COUNTRY, CURRENCY, AMOUNT  
                from {table_name}
                where reportingdate between '{start_period}' AND '{end_period}'
                and '{condition}'
                """ ,  
                "ZNZ_RECEIPTS_FINAL": f"""
                select DESCRIPTIONNO AS SNO, REPORTINGDATE, PURPOSE, PU_CODE AS CODE, SECTOR,  COUNTRY, CURRENCY, AMOUNT  
                from {table_name}
                where reportingdate between '{start_period}' AND '{end_period}'
                and '{condition}'
                """                  
                 
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
                "RATES": ["Sno","REPORTING_DATE", "CURRENCY", "DESCRIPTION","TZS_RATE", "USD_RATE"],
                "MONITORING": ["S/NO", "RETURN NAME","EDI RECORDS","LAST EDI UPDATE",  "BSIS RECORDS", "TRANSFORMED RECORDS",
                         "LAST MIGRATION", "MIGRATION PERCENTAGE" , "LAST TRANSFORMATION", 
                         "TRANSFORMATION PERCENTAGE"  , "COMPLETION PERCENTAGE"],                
                "OVERALL_ANALYSIS": ["INSTITUTION","TRANSACTION_LOCATION","PERIOD","REPORTINGDATE","DATE","PURPOSE","PURPOSE_DESCRIPTION"],
                "TRANSFORMATION_ERRORS": ["SNO","ERROR_DATE","ERROR_DETAILS", "ERROR_TYPE","ERROR_ID"],  
                "COUNTRIES_SECTORS_TZS": ["COUNTRY", "SECTOR", "LOCATION_PURPOSE" , "AMOUNT_IN_TZS_EQV"],
                "COUNTRIES_SECTORS_USD": ["COUNTRY", "SECTOR", "LOCATION_PURPOSE" , "AMOUNT_IN_USD_EQV",
                       "CURRENT_AMOUNT", "ESM", "SUBSTANDARD", "DOUBTFUL", "LOSS", "WRITTENOFF"],    
                "CONSOLIDATED_TZS": ["COUNTRY","SECTOR","LOCATION_PURPOSE","AMOUNT_IN_USD_EQV"],
                "REGION_SECTOR_TZS": ["REGION_GROUPING","SECTOR","PAYMENT_URT","RECEIPTS_URT","PAYMENT_ZANZIBAR","RECEIPTS_ZANZIBAR"],       
                "REGION_SECTOR_USD": ["REGION_GROUPING","SECTOR","PAYMENT_URT","RECEIPTS_URT","PAYMENT_ZANZIBAR","RECEIPTS_ZANZIBAR"], 
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



