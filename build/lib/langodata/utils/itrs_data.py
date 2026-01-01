import os
import pandas as pd
from langodata.utils.database import DatabaseConnection
from langodata.utils.logger import Logger
from typing import Dict
from datetime import datetime

import oracledb
from langodata.utils.decryption import decrypt

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
    
def itrs_bop(reporting_date, user, password, dsn):
    """
    Main function to perform operations similar to the ITRS_BOP PL/SQL procedure.
    Processes service accounts and returns a Pandas DataFrame.
    """
    conn = None
    cursor = None
    try:
        # Connect to the database
        oracledb.init_oracle_client()  # Ensure Oracle client is initialized
        conn = oracledb.connect(user=user, password=password, dsn=dsn)
        cursor = conn.cursor()

        # Fetch static table records
        static_table_records = fetch_static_table(cursor)

        # Initialize results DataFrame
        results_df = initialize_results(static_table_records, reporting_date, cursor)

        # Define service accounts (load accounts from configuration)
        account_groups = load_account_groups()

        # Apply aggregates for all registered accounts
        for account_group in account_groups:
            for account_name, account_details in account_group.items():
                apply_aggregate(cursor, results_df, account_details, "PAYMENTS", reporting_date, user)
                apply_aggregate(cursor, results_df, account_details, "RECEIPTS", reporting_date, user)

        return results_df

    except oracledb.DatabaseError as e:
        print(f"Database error: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def load_account_groups():
    """Loads account groups from a predefined structure."""
    account_groups = []

    # Example account groups and their definitions
    account_groups.append({
        "Goods Account": {
            "payments_codes": [3101000, 3102000],
            "receipts_codes": [2101000, 2102000, 2103000, 2104000],
            "aggregate_code": 3100000,
            "aggregate_receipts_code": 2100000
        }
    })

    account_groups.append({
        "Sea Transport": {
            "payments_codes": [3203010, 3203020, 3203030],
            "receipts_codes": [2203010, 2203020, 2203030],
            "aggregate_code": 3203001,
            "aggregate_receipts_code": 2203001
        },
        "Air Transport": {
            "payments_codes": [3203110, 3203120, 3203130],
            "receipts_codes": [2203110, 2203120, 2203130],
            "aggregate_code": 3203100,
            "aggregate_receipts_code": 2203100
        },
        "Rail Transport": {
            "payments_codes": [3203210, 3203220, 3203230],
            "receipts_codes": [2203210, 2203220, 2203230],
            "aggregate_code": 3203200,
            "aggregate_receipts_code": 2203200
        },
        "Road Transport": {
            "payments_codes": [3203310, 3203320, 3203330],
            "receipts_codes": [2203310, 2203320, 2203330],
            "aggregate_code": 3203300,
            "aggregate_receipts_code": 2203300
        }
    })
    
    # Adding new account groups
    account_groups.append({
        "Other Transport": {
            "payments_codes": [3203410, 3203420, 3203430, 3203440, 3203450],
            "receipts_codes": [2203410, 2203420, 2203430, 2203440, 2203450],
            "aggregate_code": 3203400,
            "aggregate_receipts_code": 2203400
        },
        "Personal Travel": {
            "payments_codes": [3204210, 3204220, 3204230],
            "receipts_codes": [2204210, 2204220, 2204230],
            "aggregate_code": 3204200,
            "aggregate_receipts_code": 2204200
        },
        "Overall Travel": {
            "payments_codes": [3204100, 3204200],
            "receipts_codes": [2204100, 2204200],
            "aggregate_code": 3204000,
            "aggregate_receipts_code": 2204000
        },
        "Transport Aggregates": {
            "payments_codes": [3203001, 3203100, 3203200, 3203300, 3203400, 3203500],
            "receipts_codes": [2203001, 2203100, 2203200, 2203300, 2203400, 2203500],
            "aggregate_code": 3203000,
            "aggregate_receipts_code": 2203000
        }
    })
    
    account_groups.append({
        "Insurance and Pension Services": {
            "Direct Insurance": {
                "payments_codes": [3206110, 3206120],
                "receipts_codes": [2206110, 2206120],
                "aggregate_code": 3206100,
                "aggregate_receipts_code": 2206100
            },
            "Reinsurance": {
                "payments_codes": [3206210, 3206220],
                "receipts_codes": [2206210, 2206220],
                "aggregate_code": 3206200,
                "aggregate_receipts_code": 2206200
            },
            "Pension and Standardised Guarantee Services": {
                "payments_codes": [3206410, 3206420],
                "receipts_codes": [2206410, 2206420],
                "aggregate_code": 3206400,
                "aggregate_receipts_code": 2206400
            },
            "Overall Insurance and Pension Services": {
                "payments_codes": [3206100, 3206200, 3206300, 3206400],
                "receipts_codes": [2206100, 2206200, 2206300, 2206400],
                "aggregate_code": 3206000,
                "aggregate_receipts_code": 2206000
            }
        }
    })
    
    account_groups.append({
        "Telecommunications, Computer and Information Services": {
            "payments_codes": [3209100, 3209200, 3209300],
            "receipts_codes": [2209100, 2209200, 2209300],
            "aggregate_code": 3209000,
            "aggregate_receipts_code": 2209000
        }
    })

    account_groups.append({
        "Government Goods and Services n.i.e.": {
            "payments_codes": [3212100, 3212200, 3212300],
            "receipts_codes": [2212100, 2212200, 2212300],
            "aggregate_code": 3212000,
            "aggregate_receipts_code": 2212000
        }
    })

    account_groups.append({
        "Personal, Cultural and Recreational Services": {
            "payments_codes": [3211100, 3211200],
            "receipts_codes": [2211100, 2211200],
            "aggregate_code": 3211000,
            "aggregate_receipts_code": 2211000
        }
    })

    account_groups.append({
        "Other Business Services": {
            "payments_codes": [3210100, 3210200, 3210300],
            "receipts_codes": [2210100, 2210200, 2210300],
            "aggregate_code": 3210000,
            "aggregate_receipts_code": 2210000
        }
    })
    
    account_groups.append({
        "Overall Services": {
            "payments_codes": [3201000, 3202000, 3203000, 3204000, 3205000, 3206000, 3207000, 3208000, 3209000, 3210000, 3211000, 3212000],
            "receipts_codes": [2201000, 2202000, 2203000, 2204000, 2205000, 2206000, 2207000, 2208000, 2209000, 2210000, 2211000, 2212000],
            "aggregate_code": 3200000,
            "aggregate_receipts_code": 2200000
         }
    })

    # Primary Income Account Group (2301000 and 3301000)
    account_groups.append({
        "Primary Income": {
            "payments_codes": [3301100],
            "receipts_codes": [2301100],
            "aggregate_code": 3301000,
            "aggregate_receipts_code": 2301000
        }
    })

    # Salaries and Wages Account Group (2301100 and 3301100)
    account_groups.append({
        "Salaries and Wages": {
            "payments_codes": [3302111],
            "receipts_codes": [2302111],
            "aggregate_code": 3302100,
            "aggregate_receipts_code": 2302100
        }
    })

    # Portfolio Investment Account Group (2302200 and 3302200)
    account_groups.append({
        "Portfolio Investment": {
            "payments_codes": [3302210, 3302211, 3302220, 3302221, 3302230],
            "receipts_codes": [2302210, 2302211, 2302220, 2302221, 2302230],
            "aggregate_code": 3302200,
            "aggregate_receipts_code": 2302200
        }
    })

    # Other Investment Account Group (2302300 and 3302300)
    account_groups.append({
        "Other Investment": {
            "payments_codes": [3302310, 3302320, 3302321, 3302330],
            "receipts_codes": [2302310, 2302320, 2302321, 2302330],
            "aggregate_code": 3302300,
            "aggregate_receipts_code": 2302300
        }
    })

    # Compensation of Employees Account Group (2301000 and 3301000)
    account_groups.append({
        "Compensation of Employees": {
            "payments_codes": [3302100, 3302200, 3302300],
            "receipts_codes": [2302100, 2302200, 2302300],
            "aggregate_code": 3302000,
            "aggregate_receipts_code": 2302000
        }
    })

    # Reserve Assets Account Group (2303000)
    account_groups.append({
        "Reserve Assets": {
            "payments_codes": [],
            "receipts_codes": [2303100, 2303200],
            "aggregate_code": 2303000,
            "aggregate_receipts_code": 2303000
        }
    })

    # Other Primary Income Account Group (2304000 and 3303000)
    account_groups.append({
        "Other Primary Income": {
            "payments_codes": [3303100, 3303200],
            "receipts_codes": [2304100, 2304200],
            "aggregate_code": 3303000,
            "aggregate_receipts_code": 2304000
        }
    })
    
    # Other Primary Income Account Group (2304000 and 3303000)
    account_groups.append({
        "Other Primary Income": {
            "payments_codes": [3303100, 3303200],
            "receipts_codes": [2304100, 2304200],
            "aggregate_code": 3303000,
            "aggregate_receipts_code": 2304000
        }
    })

    # Primary Income Account Group (2305000 and 3304000)
    account_groups.append({
        "Primary Income": {
            "payments_codes": [3304100, 3304200],
            "receipts_codes": [2305100, 2305200],
            "aggregate_code": 3304000,
            "aggregate_receipts_code": 2305000
        }
    })

    # Secondary Income Account Group (2306000 and 3305000)
    account_groups.append({
        "Secondary Income": {
            "payments_codes": [3305100, 3305200],
            "receipts_codes": [2306100, 2306200],
            "aggregate_code": 3305000,
            "aggregate_receipts_code": 2306000
        }
    })

    # Tertiary Income Account Group (2307000 and 3306000)
    account_groups.append({
        "Tertiary Income": {
            "payments_codes": [3306100, 3306200],
            "receipts_codes": [2307100, 2307200],
            "aggregate_code": 3306000,
            "aggregate_receipts_code": 2307000
        }
    })

    # Quaternary Income Account Group (2308000 and 3307000)
    account_groups.append({
        "Quaternary Income": {
            "payments_codes": [3307100, 3307200],
            "receipts_codes": [2308100, 2308200],
            "aggregate_code": 3307000,
            "aggregate_receipts_code": 2308000
        }
    })

    # Other Expenses Account Group (2309000 and 3308000)
    account_groups.append({
        "Other Expenses": {
            "payments_codes": [3308100, 3308200],
            "receipts_codes": [2309100, 2309200],
            "aggregate_code": 3308000,
            "aggregate_receipts_code": 2309000
        }
    })

    # Primary Expenses Account Group (2310000 and 3309000)
    account_groups.append({
        "Primary Expenses": {
            "payments_codes": [3309100, 3309200],
            "receipts_codes": [2310100, 2310200],
            "aggregate_code": 3309000,
            "aggregate_receipts_code": 2310000
        }
    })

    # Secondary Expenses Account Group (2311000 and 3310000)
    account_groups.append({
        "Secondary Expenses": {
            "payments_codes": [3310100, 3310200],
            "receipts_codes": [2311100, 2311200],
            "aggregate_code": 3310000,
            "aggregate_receipts_code": 2311000
        }
    })

    # Tertiary Expenses Account Group (2312000 and 3311000)
    account_groups.append({
        "Tertiary Expenses": {
            "payments_codes": [3311100, 3311200],
            "receipts_codes": [2312100, 2312200],
            "aggregate_code": 3311000,
            "aggregate_receipts_code": 2312000
        }
    })

    # Quaternary Expenses Account Group (2313000 and 3312000)
    account_groups.append({
        "Quaternary Expenses": {
            "payments_codes": [3312100, 3312200],
            "receipts_codes": [2313100, 2313200],
            "aggregate_code": 3312000,
            "aggregate_receipts_code": 2313000
        }
    })

    account_groups.append({
        "Direct investment in Tanzania": {
            "payments_codes": [3601210, 3601220, 3601230],
            "receipts_codes": [2601210, 2601220, 2601230],
            "aggregate_code": 3601200,
            "aggregate_receipts_code": 2601200
        }
    })

    account_groups.append({
        "Direct Investment": {
            "payments_codes": [3601100, 3601200],
            "receipts_codes": [2601100, 2601200],
            "aggregate_code": 3601000,
            "aggregate_receipts_code": 2601000
        }
    })

    account_groups.append({
        "Assets": {
            "payments_codes": [3602110, 3602120],
            "receipts_codes": [2602110, 2602120],
            "aggregate_code": 3602100,
            "aggregate_receipts_code": 2602100
        }
    })

    account_groups.append({
        "Liabilities": {
            "payments_codes": [3602210, 3602220],
            "receipts_codes": [2602210, 2602220],
            "aggregate_code": 3602200,
            "aggregate_receipts_code": 2602200
        }
    })

    account_groups.append({
        "Portfolio Investment": {
            "payments_codes": [3601100, 3601200],
            "receipts_codes": [2601100, 2601200],
            "aggregate_code": 3602000,
            "aggregate_receipts_code": 2602000
        }
    })

    account_groups.append({
        "Assets": {
            "payments_codes": [3603110, 3603120, 3603130, 3603140],
            "receipts_codes": [2603110, 2603120, 2603130, 2603140],
            "aggregate_code": 3603100,
            "aggregate_receipts_code": 2603100
        }
    })

    account_groups.append({
        "Liabilities": {
            "payments_codes": [3603210, 3603220, 3603230, 3603240],
            "receipts_codes": [2603210, 2603220, 2603230, 2603240],
            "aggregate_code": 3603200,
            "aggregate_receipts_code": 2603200
        }
    })

    account_groups.append({
        "Other Investment": {
            "payments_codes": [3603100, 3603200],
            "receipts_codes": [2603100, 2603200],
            "aggregate_code": 3603000,
            "aggregate_receipts_code": 2603000
        }
    })

    account_groups.append({
        "Financial Account": {
            "payments_codes": [3601000, 3602000, 3603000],
            "receipts_codes": [2601000, 2602000, 2603000],
            "aggregate_code": 3600000,
            "aggregate_receipts_code": 2600000
        }
    })


    # You can load more account groups here by appending dictionaries for each group

    return account_groups

def fetch_static_table(cursor):
    """Fetches records from the static ITRS_BOP template table."""
    cursor.execute("""
        SELECT DESCRIPTIONNO, PURPOSE, RECEIPTS_CODE, PAYMENTS_CODE
        FROM BSIS_DEV.ITRS_URT_BOP_TEMPLATE
        ORDER BY DESCRIPTIONNO ASC
    """)
    return cursor.fetchall()

def initialize_results(static_table_records, reporting_date, cursor):
    """Initializes the results DataFrame."""
    columns = [
        "DESCRIPTIONNO", "PURPOSE", "RECEIPTS_CODE", "PAYMENTS_CODE",
        "RECEIPTS_AMOUNT", "PAYMENTS_AMOUNT", "NET_AMOUNT", "REG_DATE"
    ]
    results_df = pd.DataFrame(columns=columns)

    for record in static_table_records:
        description_no, purpose, receipts_code, payments_code = record
        payments_amount = calculate_amount(cursor, reporting_date, payments_code, "PAYMENTS")
        receipts_amount = calculate_amount(cursor, reporting_date, receipts_code, "RECEIPTS")
        net_amount = (receipts_amount or 0) - (payments_amount or 0)

        results_df = pd.concat([results_df, pd.DataFrame([[ 
            description_no, purpose, receipts_code, payments_code,
            receipts_amount, payments_amount, net_amount, reporting_date
        ]], columns=columns)], ignore_index=True)

    return results_df

def calculate_amount(cursor, reporting_date, code, transaction_type):
    """Calculates amounts for receipts or payments."""
    if code is not None:
        query = f"""
            SELECT SUM(NVL(AMOUNT_IN_USD_EQV, 0))
            FROM ITRS_URT_{transaction_type}_FINAL
            WHERE REPORTINGDATE = :reporting_date AND PU_CODE = :code
        """
        cursor.execute(query, [reporting_date, code])
        return cursor.fetchone()[0] or None
    return None

def apply_aggregate(cursor, df, codes, transaction_type, reporting_date, user):
    """Applies aggregate values for a specific account."""
    key = f"{transaction_type.lower()}_codes"
    aggregate_key = f"aggregate_{transaction_type.lower()}_code"
    selected_codes = codes.get(key, [])
    aggregate_code = codes.get(aggregate_key)

    if selected_codes and aggregate_code:
        total = df.loc[
            df[f"{transaction_type.upper()}_CODE"].isin(selected_codes),
            f"{transaction_type.upper()}_AMOUNT"
        ].sum()

        if total > 0:
            df.loc[df[f"{transaction_type.upper()}_CODE"] == aggregate_code, f"{transaction_type.upper()}_AMOUNT"] = total
           
            
def read_itrs_data(data_group: str, data_source: str, data_type: str, bank_code: str, start_period: str, end_period: str) -> dict:
    logger = Logger()
    result = {"info": "", "debug": "", "df": pd.DataFrame()}

    # Validate inputs
    valid_data_sources = ["BSIS", "EDI"]
    valid_data_types = ["RATES", "MONITORING", "OVERALL_ANALYSIS", "TRANSFORMATION_ERRORS", "COUNTRIES_SECTORS_TZS","COUNTRIES_SECTORS_USD",
    "CONSOLIDATED_TZS","CONSOLIDATED_USD","REGION_SECTOR_TZS","REGION_SECTOR_USD","URT_PAYMENTS", "URT_RECEIPTS", 
            "ZNZ_PAYMENTS", "ZNZ_RECEIPTS",
            "URT_PAYMENTS_FINAL", "URT_RECEIPTS_FINAL",
            "ZNZ_PAYMENTS_FINAL", "ZNZ_RECEIPTS_FINAL", "BOP" ]
    
          
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
        "ZNZ_RECEIPTS_FINAL": ["SNO", "REPORTINGDATE", "PURPOSE", "CODE", "SECTOR",  "COUNTRY", "CURRENCY", "AMOUNT_IN_ORIG_CURRENCY","AMOUNT_IN_USD_EQV","AMOUNT_IN_TZS_EQV"], 
        "BOP": ["DESCRIPTIONNO", "PURPOSE", "RECEIPTS_CODE", "PAYMENTS_CODE", "RECEIPTS_AMOUNT",  "PAYMENTS_AMOUNT", "NET_AMOUNT", "REG_DATE"]         
        }
    columns = columns_mapping.get(data_type)    

    try:
        with DatabaseConnection(data_source) as conn:
        
            if data_type in ["BOP"]:
                user = conn.get_user()
                password = conn.get_pass()
                dsn = conn.get_dsn()
                formatted_reporting_date = datetime.strptime(start_period, "%Y-%m-%d")
            
                result['df'] = itrs_bop(formatted_reporting_date, user, password, dsn)
                result["info"] += f"Retrieved ITRS BOP data."
            else:
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
            
            
