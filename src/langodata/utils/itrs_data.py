import os
import pandas as pd
from langodata.utils.database import DatabaseConnection
from langodata.utils.logger import Logger
from typing import Dict
from datetime import datetime


def read_itrs_data(data_group: str, data_source: str, data_type: str, bank_code: str, start_period: str, end_period: str) -> dict:
    """
    Reads ITRS data from the specified data source and returns a result dictionary.

    Args:
        data_group (str): The data group (e.g., "ITRS").
        data_source (str): The data source (e.g., "BSIS" or "EDI").
        data_type (str): The type of data to fetch.
        bank_code (str): Bank code to filter data. Use '*' for all banks.
        start_period (str): Start date of the period (DD-MON-YYYY).
        end_period (str): End date of the period (DD-MON-YYYY).

    Returns:
        dict: Contains Info, Debug, and DataFrame with ITRS data.
    """
    logger = Logger()
    result = {"info": "", "debug": "", "df": pd.DataFrame()}

    # Validate inputs
    valid_data_sources = ["BSIS", "EDI"]
    valid_data_types = [
        "RATES", "MONITORING", "OVERALL_ANALYSIS", "TRANSFORMATION_ERRORS",
        "COUNTRIES_SECTORS_TZS", "COUNTRIES_SECTORS_USD",
        "CONSOLIDATED_TZS", "CONSOLIDATED_USD",
        "REGION_SECTOR_TZS", "REGION_SECTOR_USD",
        "URT_PAYMENTS", "URT_RECEIPTS",
        "ZNZ_PAYMENTS", "ZNZ_RECEIPTS",
        "URT_PAYMENTS_FINAL", "URT_RECEIPTS_FINAL",
        "ZNZ_PAYMENTS_FINAL", "ZNZ_RECEIPTS_FINAL"
    ]

    if data_source not in valid_data_sources:
        result["debug"] += f"Invalid data source: {data_source}. "
        return result
    if data_type not in valid_data_types:
        result["debug"] += f"Invalid data type: {data_type}. "
        return result

    try:
        with DatabaseConnection(data_source) as conn:
            # Determine schema
            schema = get_schema(data_source, data_type)
            
            # Get table name
            table_name = get_table_name(data_type, schema)
            
            # Get SQL query
            sql_query = get_sql_query(data_type, table_name, start_period, end_period, bank_code)
            
            if not sql_query:
                result["debug"] += f"No query found for data type: {data_type}. "
                return result

            # Execute query
            data = conn.execute_query(sql_query)
            
            # Get column names
            columns = get_columns(data_type)
            if not columns:
                raise ValueError(f"Invalid data_type '{data_type}'. No column mapping found.")

            # Construct DataFrame
            if data:
                result["df"] = pd.DataFrame(data, columns=columns)
                logger.info(f"Data successfully retrieved for {data_type}.")
                result["info"] = f"Query executed successfully for {data_type}."
            else:
                logger.warning(f"No data found for the given parameters: {data_type}")
                result["info"] = "No data found for the given parameters."

    except Exception as e:
        error_message = f"Error fetching ITRS data: {str(e)}"
        result["debug"] += error_message
        logger.error(error_message)

    return result


def get_schema(data_source: str, data_type: str) -> str:
    """Determine the schema based on the data source and type."""
    if data_source == "BSIS":
        return "BSIS_DEV."
    elif data_source == "EDI":
        return "EDI."
    return ""


def get_table_name(data_type: str, schema: str = "") -> str:
    """Return the table name mapped to the given data type."""
    itrs_prefix = "ITRS_"
    table_mapping = {
        "RATES": f"{schema}{itrs_prefix}FI_RATE",
        "MONITORING": "SYS.{itrs_prefix}MONITORING",
        "OVERALL_ANALYSIS": f"{schema}{itrs_prefix}master_details",
        "TRANSFORMATION_ERRORS": f"{schema}{itrs_prefix}ERRORS",
        "COUNTRIES_SECTORS_TZS": f"{schema}{itrs_prefix}ITRS_DETAIL",
        "COUNTRIES_SECTORS_USD": f"{schema}{itrs_prefix}ITRS_DETAIL",
        "CONSOLIDATED_TZS": f"{schema}{itrs_prefix}ITRS_DETAIL",
        "CONSOLIDATED_USD": f"{schema}{itrs_prefix}ITRS_DETAIL",
        "REGION_SECTOR_TZS": f"{schema}{itrs_prefix}ITRS_DETAIL",
        "REGION_SECTOR_USD": f"{schema}{itrs_prefix}ITRS_DETAIL",
        "URT_PAYMENTS": f"{schema}{itrs_prefix}URT_PAYMENTS",
        "URT_RECEIPTS": f"{schema}{itrs_prefix}URT_RECEIPTS",
        "ZNZ_PAYMENTS": f"{schema}{itrs_prefix}ZNZ_PAYMENTS",
        "ZNZ_RECEIPTS": f"{schema}{itrs_prefix}ZNZ_RECEIPTS",
        "URT_PAYMENTS_FINAL": f"{schema}{itrs_prefix}URT_PAYMENTS_FINAL",
        "URT_RECEIPTS_FINAL": f"{schema}{itrs_prefix}URT_RECEIPTS_FINAL",
        "ZNZ_PAYMENTS_FINAL": f"{schema}{itrs_prefix}ZNZ_PAYMENTS_FINAL",
        "ZNZ_RECEIPTS_FINAL": f"{schema}{itrs_prefix}ZNZ_RECEIPTS_FINAL"
    }
    return table_mapping.get(data_type)


def get_sql_query(data_type: str, table_name: str, start_period: str, end_period: str, bank_code: str) -> str:
    """Get SQL query for the specified data type."""
    condition = "1=1" if bank_code == "*" else f"INSTITUTIONCODE = '{bank_code}'"

    sql_queries = {
        "RATES": f"""
            SELECT ROWNUM AS SNO, A.RA_DATE AS REPORTING_DATE, A.CU_CODE AS CURRENCY,
                   B.CU_DESC AS DESCRIPTION, A.RA_SRATE AS TZS_RATE, A.RA_DRATE AS USD_RATE
            FROM {table_name} A, ITRS_FI_CURR B
            WHERE A.RA_DATE BETWEEN TO_DATE('{start_period}', 'DD-MON-YYYY') AND TO_DATE('{end_period}', 'DD-MON-YYYY')
              AND A.CU_CODE = B.CU_CODE
            ORDER BY A.CU_CODE
        """,
        "MONITORING": f"""
            SELECT ROWNUM AS SNO, A."RETURN NAME", A."EDI RECORDS", A."LAST EDI UPDATE",
                   A."BSIS RECORDS", A."TRANSFORMED RECORDS", A."LAST MIGRATION",
                   TO_CHAR(ROUND(A."MIGRATION PERCENTAGE", 0)) || '%' AS MIGRATION_PERCENTAGE,
                   A."LAST TRANSFORMATION",
                   TO_CHAR(ROUND(A."TRANSFORMATION PERCENTAGE", 0)) || '%' AS TRANSFORMATION_PERCENTAGE,
                   TO_CHAR(ROUND(A."COMPLETION PERCENTAGE", 0)) || '%' AS COMPLETION_PERCENTAGE
            FROM {table_name} A
        """,
        "OVERALL_ANALYSIS": f"""
            SELECT *
            FROM {table_name}
            WHERE reportingdate BETWEEN TO_DATE('{start_period}', 'DD-MON-YYYY') AND TO_DATE('{end_period}', 'DD-MON-YYYY')
        """,
        "TRANSFORMATION_ERRORS": f"""
            SELECT ROWNUM AS SNO, ERROR_DATE, ERROR_DETAILS, ERROR_TYPE, ERROR_ID
            FROM (
                SELECT ERROR_DATE, ERROR_DETAILS, ERROR_TYPE, ID AS ERROR_ID
                FROM {table_name}
                WHERE LAST_DAY(TO_DATE(ERROR_DATE, 'DD-MM-YY') - 31)
                      BETWEEN TO_DATE('{start_period}', 'DD-MON-YYYY') AND TO_DATE('{end_period}', 'DD-MON-YYYY')
                ORDER BY ERROR_DATE DESC
            )
        """,
        "COUNTRIES_SECTORS_TZS": f"""
            SELECT *
            FROM (
                SELECT DISTINCT COUNTRY, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION AS LOCATION_PURPOSE,
                                amount_in_tzs_eqv
                FROM {table_name}
                WHERE reportingdate BETWEEN TO_DATE('{start_period}', 'DD-MON-YYYY') AND TO_DATE('{end_period}', 'DD-MON-YYYY')
                GROUP BY COUNTRY, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION, amount_in_tzs_eqv
            )
            PIVOT (
                SUM(amount_in_tzs_eqv)
                FOR LOCATION_PURPOSE IN ('PAYMENT -URT', 'RECEIPTS -URT', 'PAYMENT -ZANZIBAR', 'RECEIPTS -ZANZIBAR')
            )
        """,
        "COUNTRIES_SECTORS_USD": f"""
            SELECT *
            FROM (
                SELECT DISTINCT COUNTRY, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION AS LOCATION_PURPOSE,
                                AMOUNT_IN_USD_EQV
                FROM {table_name}
                WHERE reportingdate BETWEEN TO_DATE('{start_period}', 'DD-MON-YYYY') AND TO_DATE('{end_period}', 'DD-MON-YYYY')
                GROUP BY COUNTRY, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION, AMOUNT_IN_USD_EQV
                ORDER BY COUNTRY ASC, SECTOR ASC
            )
            PIVOT (
                SUM(AMOUNT_IN_USD_EQV)
                FOR LOCATION_PURPOSE IN ('PAYMENT -URT', 'RECEIPTS -URT', 'PAYMENT -ZANZIBAR', 'RECEIPTS -ZANZIBAR')
            )
        """,
        "CONSOLIDATED_TZS": f"""
            SELECT *
            FROM (
                SELECT DISTINCT COUNTRY, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION AS LOCATION_PURPOSE,
                                AMOUNT_IN_TZS_EQV
                FROM {table_name}
                WHERE reportingdate BETWEEN TO_DATE('{start_period}', 'DD-MON-YYYY') AND TO_DATE('{end_period}', 'DD-MON-YYYY')
                GROUP BY COUNTRY, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION, AMOUNT_IN_TZS_EQV
                ORDER BY COUNTRY ASC, SECTOR ASC
            )
            PIVOT (
                SUM(AMOUNT_IN_TZS_EQV)
                FOR LOCATION_PURPOSE IN ('PAYMENT -URT', 'RECEIPTS -URT', 'PAYMENT -ZANZIBAR', 'RECEIPTS -ZANZIBAR')
            )
        """,
        "CONSOLIDATED_USD": f"""
            SELECT *
            FROM (
                SELECT DISTINCT COUNTRY, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION AS LOCATION_PURPOSE,
                                AMOUNT_IN_USD_EQV
                FROM {table_name}
                WHERE reportingdate BETWEEN TO_DATE('{start_period}', 'DD-MON-YYYY') AND TO_DATE('{end_period}', 'DD-MON-YYYY')
                GROUP BY COUNTRY, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION, AMOUNT_IN_USD_EQV
                ORDER BY COUNTRY ASC, SECTOR ASC
            )
            PIVOT (
                SUM(AMOUNT_IN_USD_EQV)
                FOR LOCATION_PURPOSE IN ('PAYMENT -URT', 'RECEIPTS -URT', 'PAYMENT -ZANZIBAR', 'RECEIPTS -ZANZIBAR')
            )
        """,
        "REGION_SECTOR_TZS": f"""
            SELECT REGION_GROUPING, SECTOR, SUM(NVL(PAYMENT_URT, 0)) AS PAYMENT_URT,
                   SUM(NVL(RECEIPTS_URT, 0)) AS RECEIPTS_URT,
                   SUM(NVL(PAYMENT_ZANZIBAR, 0)) AS PAYMENT_ZANZIBAR,
                   SUM(NVL(RECEIPTS_ZANZIBAR, 0)) AS RECEIPTS_ZANZIBAR
            FROM (
                SELECT 'EAC' AS REGION_GROUPING, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION AS LOCATION_PURPOSE,
                       AMOUNT_IN_TZS_EQV
                FROM {table_name}
                WHERE reportingdate BETWEEN TO_DATE('{start_period}', 'DD-MON-YYYY') AND TO_DATE('{end_period}', 'DD-MON-YYYY')
                  AND COUNTRY IN ('TANZANIA', 'KENYA', 'UGANDA', 'RWANDA', 'BURUNDI', 'SOUTH SUDAN')
                UNION ALL
                SELECT 'SADC' AS REGION_GROUPING, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION AS LOCATION_PURPOSE,
                       AMOUNT_IN_TZS_EQV
                FROM {table_name}
                WHERE reportingdate BETWEEN TO_DATE('{start_period}', 'DD-MON-YYYY') AND TO_DATE('{end_period}', 'DD-MON-YYYY')
                  AND COUNTRY IN ('SOUTH AFRICA', 'ZAMBIA', 'ZIMBABWE')
            )
            PIVOT (
                SUM(AMOUNT_IN_TZS_EQV)
                FOR LOCATION_PURPOSE IN ('PAYMENT -URT', 'RECEIPTS -URT', 'PAYMENT -ZANZIBAR', 'RECEIPTS -ZANZIBAR')
            )
            GROUP BY REGION_GROUPING, SECTOR
            ORDER BY REGION_GROUPING ASC, SECTOR ASC
        """,
        "REGION_SECTOR_USD": f"""
            SELECT REGION_GROUPING, SECTOR, SUM(NVL(PAYMENT_URT, 0)) AS PAYMENT_URT,
                   SUM(NVL(RECEIPTS_URT, 0)) AS RECEIPTS_URT,
                   SUM(NVL(PAYMENT_ZANZIBAR, 0)) AS PAYMENT_ZANZIBAR,
                   SUM(NVL(RECEIPTS_ZANZIBAR, 0)) AS RECEIPTS_ZANZIBAR
            FROM (
                SELECT 'EAC' AS REGION_GROUPING, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION AS LOCATION_PURPOSE,
                       AMOUNT_IN_USD_EQV
                FROM {table_name}
                WHERE reportingdate BETWEEN TO_DATE('{start_period}', 'DD-MON-YYYY') AND TO_DATE('{end_period}', 'DD-MON-YYYY')
                  AND COUNTRY IN ('TANZANIA', 'KENYA', 'UGANDA', 'RWANDA', 'BURUNDI', 'SOUTH SUDAN')
                UNION ALL
                SELECT 'SADC' AS REGION_GROUPING, SECTOR, PURPOSE || ' -' || TRANSACTION_LOCATION AS LOCATION_PURPOSE,
                       AMOUNT_IN_USD_EQV
                FROM {table_name}
                WHERE reportingdate BETWEEN TO_DATE('{start_period}', 'DD-MON-YYYY') AND TO_DATE('{end_period}', 'DD-MON-YYYY')
                  AND COUNTRY IN ('SOUTH AFRICA', 'ZAMBIA', 'ZIMBABWE')
            )
            PIVOT (
                SUM(AMOUNT_IN_USD_EQV)
                FOR LOCATION_PURPOSE IN ('PAYMENT -URT', 'RECEIPTS -URT', 'PAYMENT -ZANZIBAR', 'RECEIPTS -ZANZIBAR')
            )
            GROUP BY REGION_GROUPING, SECTOR
            ORDER BY REGION_GROUPING ASC, SECTOR ASC
        """,
        "URT_PAYMENTS": f"""
            SELECT B.INSTITUTIONNAME, A.INSTITUTIONCODE, A.DESCRIPTIONNO AS SNO, A.REPORTINGDATE,A.PURPOSE, A.PU_CODE AS CODE, A.SECTOR, A.COUNTRY, A.CURRENCY, A.AMOUNT
            FROM {table_name} A, INSTITUTION B
            JOIN {table_name}_INSTITUTION B ON A.INSTITUTIONCODE = B.INSTITUTIONCODE
            WHERE {condition} AND A.INSTITUTIONCODE=B.INSTITUTIONCODE AND TRUNC(A.REPORTINGDATE) BETWEEN TO_DATE('{start_period}', 'DD-MON-YYYY') AND TO_DATE('{end_period}', 'DD-MON-YYYY')
            ORDER BY B.INSTITUTIONNAME, A.INSTITUTIONCODE,A.DESCRIPTIONNO, A.REPORTINGDATE DESC
        """,
        "URT_RECEIPTS": f"""
            SELECT B.INSTITUTIONNAME, A.INSTITUTIONCODE, A.DESCRIPTIONNO AS SNO, A.REPORTINGDATE,A.PURPOSE, A.PU_CODE AS CODE, A.SECTOR, A.COUNTRY, A.CURRENCY, A.AMOUNT
            FROM {table_name} A, INSTITUTION B
            JOIN {table_name}_INSTITUTION B ON A.INSTITUTIONCODE = B.INSTITUTIONCODE
            WHERE {condition} AND A.INSTITUTIONCODE=B.INSTITUTIONCODE AND TRUNC(A.REPORTINGDATE) BETWEEN TO_DATE('{start_period}', 'DD-MON-YYYY') AND TO_DATE('{end_period}', 'DD-MON-YYYY')
            ORDER BY B.INSTITUTIONNAME, A.INSTITUTIONCODE,A.DESCRIPTIONNO, A.REPORTINGDATE DESC
        """,
        "ZNZ_PAYMENTS": f"""
            SELECT B.INSTITUTIONNAME, A.INSTITUTIONCODE, A.DESCRIPTIONNO AS SNO, A.REPORTINGDATE,A.PURPOSE, A.PU_CODE AS CODE, A.SECTOR, A.COUNTRY, A.CURRENCY, A.AMOUNT
            FROM {table_name} A, INSTITUTION B
            JOIN {table_name}_INSTITUTION B ON A.INSTITUTIONCODE = B.INSTITUTIONCODE
            WHERE {condition} AND A.INSTITUTIONCODE=B.INSTITUTIONCODE AND TRUNC(A.REPORTINGDATE) BETWEEN TO_DATE('{start_period}', 'DD-MON-YYYY') AND TO_DATE('{end_period}', 'DD-MON-YYYY')
            ORDER BY B.INSTITUTIONNAME, A.INSTITUTIONCODE,A.DESCRIPTIONNO, A.REPORTINGDATE DESC
        """,
        "ZNZ_RECEIPTS": f"""
            SELECT B.INSTITUTIONNAME, A.INSTITUTIONCODE, A.DESCRIPTIONNO AS SNO, A.REPORTINGDATE,A.PURPOSE, A.PU_CODE AS CODE, A.SECTOR, A.COUNTRY, A.CURRENCY, A.AMOUNT
            FROM {table_name} A, INSTITUTION B
            JOIN {table_name}_INSTITUTION B ON A.INSTITUTIONCODE = B.INSTITUTIONCODE
            WHERE {condition} AND A.INSTITUTIONCODE=B.INSTITUTIONCODE AND TRUNC(A.REPORTINGDATE) BETWEEN TO_DATE('{start_period}', 'DD-MON-YYYY') AND TO_DATE('{end_period}', 'DD-MON-YYYY')
            ORDER BY B.INSTITUTIONNAME, A.INSTITUTIONCODE,A.DESCRIPTIONNO, A.REPORTINGDATE DESC
        """,
        "URT_PAYMENTS_FINAL": f"""
            SELECT DESCRIPTIONNO AS SNO, REPORTINGDATE, PURPOSE, PU_CODE AS CODE, SECTOR, COUNTRY, CURRENCY,
                   AMOUNT_IN_ORIG_CURRENCY, AMOUNT_IN_USD_EQV, AMOUNT_IN_TZS_EQV
            FROM {table_name}
            WHERE {condition} AND TRUNC(REPORTINGDATE) BETWEEN TO_DATE('{start_period}', 'DD-MON-YYYY') AND TO_DATE('{end_period}', 'DD-MON-YYYY')
            ORDER BY REPORTINGDATE DESC, SNO
        """,
        "URT_RECEIPTS_FINAL": f"""
            SELECT DESCRIPTIONNO AS SNO, REPORTINGDATE, PURPOSE, PU_CODE AS CODE, SECTOR, COUNTRY, CURRENCY,
                   AMOUNT_IN_ORIG_CURRENCY, AMOUNT_IN_USD_EQV, AMOUNT_IN_TZS_EQV
            FROM {table_name}
            WHERE {condition} AND TRUNC(REPORTINGDATE) BETWEEN TO_DATE('{start_period}', 'DD-MON-YYYY') AND TO_DATE('{end_period}', 'DD-MON-YYYY')
            ORDER BY REPORTINGDATE DESC, SNO
        """,
        "ZNZ_PAYMENTS_FINAL": f"""
            SELECT DESCRIPTIONNO AS SNO, REPORTINGDATE, PURPOSE, PU_CODE AS CODE, SECTOR, COUNTRY, CURRENCY,
                   AMOUNT_IN_ORIG_CURRENCY, AMOUNT_IN_USD_EQV, AMOUNT_IN_TZS_EQV
            FROM {table_name}
            WHERE {condition} AND TRUNC(REPORTINGDATE) BETWEEN TO_DATE('{start_period}', 'DD-MON-YYYY') AND TO_DATE('{end_period}', 'DD-MON-YYYY')
            ORDER BY REPORTINGDATE DESC, SNO
        """,
        "ZNZ_RECEIPTS_FINAL": f"""
            SELECT DESCRIPTIONNO AS SNO, REPORTINGDATE, PURPOSE, PU_CODE AS CODE, SECTOR, COUNTRY, CURRENCY,
                   AMOUNT_IN_ORIG_CURRENCY, AMOUNT_IN_USD_EQV, AMOUNT_IN_TZS_EQV
            FROM {table_name}
            WHERE {condition} AND TRUNC(REPORTINGDATE) BETWEEN TO_DATE('{start_period}', 'DD-MON-YYYY') AND TO_DATE('{end_period}', 'DD-MON-YYYY')
            ORDER BY REPORTINGDATE DESC, SNO
        """
    }
    return sql_queries.get(data_type)


def get_columns(data_type: str) -> list:
    """Return column names for the specified data type."""
    columns_mapping = {
        "RATES": ["SNO", "REPORTING_DATE", "CURRENCY", "DESCRIPTION", "TZS_RATE", "USD_RATE"],
        "MONITORING": ["SNO", "RETURN NAME", "EDI RECORDS", "LAST EDI UPDATE", "BSIS RECORDS",
                      "TRANSFORMED RECORDS", "LAST MIGRATION", "MIGRATION_PERCENTAGE", "LAST TRANSFORMATION",
                      "TRANSFORMATION_PERCENTAGE", "COMPLETION_PERCENTAGE"],
        "OVERALL_ANALYSIS": ["INSTITUTION", "TRANSACTION_LOCATION", "PERIOD", "REPORTINGDATE", "DATE",
                            "PURPOSE", "PURPOSE_DESCRIPTION"],
        "TRANSFORMATION_ERRORS": ["SNO", "ERROR_DATE", "ERROR_DETAILS", "ERROR_TYPE", "ERROR_ID"],
        "COUNTRIES_SECTORS_TZS": ["COUNTRY", "SECTOR", "PAYMENT -URT", "RECEIPTS -URT",
                                  "PAYMENT -ZANZIBAR", "RECEIPTS -ZANZIBAR"],
        "COUNTRIES_SECTORS_USD": ["COUNTRY", "SECTOR", "PAYMENT -URT", "RECEIPTS -URT",
                                  "PAYMENT -ZANZIBAR", "RECEIPTS -ZANZIBAR"],
        "CONSOLIDATED_TZS": ["COUNTRY", "SECTOR", "PAYMENT -URT", "RECEIPTS -URT",
                            "PAYMENT -ZANZIBAR", "RECEIPTS -ZANZIBAR"],
        "CONSOLIDATED_USD": ["COUNTRY", "SECTOR", "PAYMENT -URT", "RECEIPTS -URT",
                            "PAYMENT -ZANZIBAR", "RECEIPTS -ZANZIBAR"],
        "REGION_SECTOR_TZS": ["REGION_GROUPING", "SECTOR", "PAYMENT_URT", "RECEIPTS_URT",
                             "PAYMENT_ZANZIBAR", "RECEIPTS_ZANZIBAR"],
        "REGION_SECTOR_USD": ["REGION_GROUPING", "SECTOR", "PAYMENT_URT", "RECEIPTS_URT",
                             "PAYMENT_ZANZIBAR", "RECEIPTS_ZANZIBAR"],
        "URT_PAYMENTS": ["SNO", "REPORTINGDATE", "PURPOSE", "CODE", "SECTOR", "COUNTRY", "CURRENCY", "AMOUNT"],
        "URT_RECEIPTS": ["SNO", "REPORTINGDATE", "PURPOSE", "CODE", "SECTOR", "COUNTRY", "CURRENCY", "AMOUNT"],
        "ZNZ_PAYMENTS": ["SNO", "REPORTINGDATE", "PURPOSE", "CODE", "SECTOR", "COUNTRY", "CURRENCY", "AMOUNT"],
        "ZNZ_RECEIPTS": ["SNO", "REPORTINGDATE", "PURPOSE", "CODE", "SECTOR", "COUNTRY", "CURRENCY", "AMOUNT"],
        "URT_PAYMENTS_FINAL": ["SNO", "REPORTINGDATE", "PURPOSE", "CODE", "SECTOR", "COUNTRY", "CURRENCY",
                              "AMOUNT_IN_ORIG_CURRENCY", "AMOUNT_IN_USD_EQV", "AMOUNT_IN_TZS_EQV"],
        "URT_RECEIPTS_FINAL": ["SNO", "REPORTINGDATE", "PURPOSE", "CODE", "SECTOR", "COUNTRY", "CURRENCY",
                              "AMOUNT_IN_ORIG_CURRENCY", "AMOUNT_IN_USD_EQV", "AMOUNT_IN_TZS_EQV"],
        "ZNZ_PAYMENTS_FINAL": ["SNO", "REPORTINGDATE", "PURPOSE", "CODE", "SECTOR", "COUNTRY", "CURRENCY",
                              "AMOUNT_IN_ORIG_CURRENCY", "AMOUNT_IN_USD_EQV", "AMOUNT_IN_TZS_EQV"],
        "ZNZ_RECEIPTS_FINAL": ["SNO", "REPORTINGDATE", "PURPOSE", "CODE", "SECTOR", "COUNTRY", "CURRENCY",
                              "AMOUNT_IN_ORIG_CURRENCY", "AMOUNT_IN_USD_EQV", "AMOUNT_IN_TZS_EQV"]
    }
    return columns_mapping.get(data_type)
