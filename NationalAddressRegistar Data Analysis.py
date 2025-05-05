import glob
import os
import pandas as pd
import pyodbc
import time
import logging

pd.set_option('future.no_silent_downcasting', True)
logging.basicConfig(level=logging.INFO)


def get_connection():
    """
    Returns a new pyodbc connection.
    """
    return pyodbc.connect(
        Driver='SQL Server',
        Server='10.100.17.147,34503', 
        Database='25W_CST2112_GROUP_2',
        UID='group2',
        PWD='27K9P2M4Q8',
    )


def create_raw_table(csv_file_path, table_name):
    """
    Reads column headers from a CSV file and returns a SQL
    CREATE TABLE statement using VARCHAR(255) for each column.
    """
    # Read only the first row to get headers (nrows=0 or usecols can do this)
    df_headers = pd.read_csv(csv_file_path, nrows=0)

    # Grab the column names
    columns = df_headers.columns

    # Build a line like "column_name VARCHAR(255)" for each column
    column_definitions = []
    for col in columns:
        # Remove spaces or special chars from column names if needed
        safe_col_name = col.replace(" ", "_")  
        column_definitions.append(f"{safe_col_name} VARCHAR(255)")

    # Join the column definitions with commas
    columns_sql = ",\n    ".join(column_definitions)

    # Final CREATE TABLE statement
    create_table_sql = f"CREATE TABLE {table_name} (\n    {columns_sql}\n);"
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            logging.info(f"Dropping {table_name} if it exists.")
            cur.execute(f'DROP TABLE IF EXISTS {table_name};')
            conn.commit()
            logging.info(f"Creating {table_name}...")
            cur.execute(create_table_sql)
            conn.commit()
            logging.info(f"{table_name} created.")


def load_raw_table(csv_files):
    logging.info("Inserting data into table NAR_raw...")
    with get_connection() as conn:
        with conn.cursor() as cur:
            for i, file in enumerate(csv_files):
                sql_query = f"""
                    BULK INSERT NAR_raw
                    FROM '{file}'
                    WITH (
                        FIELDTERMINATOR = ',',
                        ROWTERMINATOR = '0x0A',
                        FIRSTROW = 2,
                        CODEPAGE = 'ACP',
                        FORMAT = 'CSV'
                    );
                    """
                cur.execute(sql_query)
                conn.commit()
                logging.info("NAR_raw table updated successfully.")


def create_lookup_table():
    """Create six lookup tables"""

    table_definitions = {
        "Street_Type": """CREATE TABLE Street_Type (
            STREET_TYPE_ID INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
            STREET_TYPE VARCHAR(255)
        );""",

        "Street_Dir": """CREATE TABLE Street_Dir (
            STREET_DIR_ID INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
            STREET_DIR VARCHAR(255)
        );""",

        "CSD_Name": """CREATE TABLE CSD_Name (
            CSD_NAME_ID INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
            CSD_NAME_ENG VARCHAR(255),
            CSD_NAME_FRE VARCHAR(255)    
        );""",

        "CSD_Type": """CREATE TABLE CSD_Type (
            CSD_Type_ID INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
            CSD_Type_ENG VARCHAR(255),
            CSD_Type_FRE VARCHAR(255)    
        );""",
        
        "Mail_Mun_Name": """CREATE TABLE Mail_Mun_Name (
            Mail_Mun_Name_ID INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
            Mail_Mun_Name VARCHAR(255) 
        );""",

        "BG_DLS_QTR": """CREATE TABLE BG_DLS_QTR (
            BG_DLS_QTR_ID INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
            BG_DLS_QTR VARCHAR(255) 
        );""",

        "BG_DLS_MRD": """CREATE TABLE BG_DLS_MRD (
            BG_DLS_MRD_ID INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
            BG_DLS_MRD VARCHAR(255) 
        );""",

        "Prov_Code": """CREATE TABLE Prov_Code (
            Prov_Code INT PRIMARY KEY,
            Prov_Abrv VARCHAR(255),
            Prov_Desc_ENG VARCHAR(255),
            Prov_Desc_FRE VARCHAR(255)
        );"""
    }

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Dropping tables if they exist
            logging.info("Dropping tables if they exist.")
            drop_statements = [f"DROP TABLE IF EXISTS {table_name}" for table_name in table_definitions.keys()]

            for statement in drop_statements:
                cur.execute(statement)

            # Commiting the drop operation once
            conn.commit()

            # Creating tables
            for table_name, sql_create in table_definitions.items():
                logging.info(f"Creating table {table_name}.")
                cur.execute(sql_create)

            # Committing all creations at once
            conn.commit()
            logging.info("Lookup tables created successfully.")


def populate_lookup_table():
    lookup_table_insert = {
        "Street_Type": """
            INSERT INTO Street_Type (STREET_TYPE)
            SELECT DISTINCT UniqueStreetType
            FROM (
                SELECT OFFICIAL_STREET_TYPE AS UniqueStreetType FROM NAR_raw
                UNION ALL
                SELECT MAIL_STREET_TYPE AS UniqueStreetType FROM NAR_raw
            ) AS CombinedResults;
            """,

        "Street_Dir": """
            INSERT INTO Street_Dir (STREET_DIR)
            SELECT DISTINCT UniqueStreetDir
            FROM (
                SELECT OFFICIAL_STREET_DIR AS UniqueStreetDir FROM NAR_raw
                UNION ALL
                SELECT MAIL_STEET_DIR AS UniqueStreetDIR FROM NAR_raw
            ) AS CombinedResults;
            """,

        "CSD_Name": """
            INSERT INTO CSD_Name (CSD_NAME_ENG, CSD_NAME_FRE)
            SELECT DISTINCT CSD_ENG_NAME, CSD_FRE_NAME
            FROM NAR_raw;
            """,

        "CSD_Type": """
            INSERT INTO CSD_Type (CSD_Type_ENG, CSD_Type_FRE)
            SELECT DISTINCT CSD_TYPE_ENG_CODE, CSD_TYPE_FRE_CODE
            FROM NAR_raw;
            """,
        "Mail_Mun_Name": """
            INSERT INTO MAIL_MUN_NAME (MAIL_MUN_NAME)
            SELECT DISTINCT MAIL_MUN_NAME
            FROM NAR_raw;
            """,
        "BG_DLS_QTR": """
            INSERT INTO BG_DLS_QTR (BG_DLS_QTR)
            SELECT DISTINCT BG_DLS_QTR
            FROM NAR_raw;
            """,

        "BG_DLS_MRD": """
            INSERT INTO BG_DLS_MRD (BG_DLS_MRD)
            SELECT DISTINCT BG_DLS_MRD
            FROM NAR_raw;
            """,

        "Prov_Code": """INSERT INTO Prov_Code (
                Prov_Code,
                Prov_Abrv,
                Prov_Desc_ENG,
                Prov_Desc_FRE
            )
            VALUES
                (10, 'NL', 'Newfoundland and Labrador', 'Terre-Neuve-et-Labrador'),
                (11, 'PE', 'Prince Edward Island', 'Île-du-Prince-Édouard'),
                (12, 'NS', 'Nova Scotia', 'Nouvelle-Écosse'),
                (13, 'NB', 'New Brunswick', 'Nouveau-Brunswick'),
                (24, 'QC', 'Quebec', 'Québec'),
                (35, 'ON', 'Ontario', 'Ontario'),
                (46, 'MB', 'Manitoba', 'Manitoba'),
                (47, 'SK', 'Saskatchewan', 'Saskatchewan'),
                (48, 'AB', 'Alberta', 'Alberta'),
                (59, 'BC', 'British Columbia', 'Colombie-Britannique'),
                (60, 'YT', 'Yukon', 'Yukon'),
                (61, 'NT', 'Northwest Territories', 'Territoires du Nord-Ouest'),
                (62, 'NU', 'Nunavut', 'Nunavut');
            """
    }

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Inserting data into tables
            for table_name, sql_create in lookup_table_insert.items():
                logging.info(f"Inserting data into table {table_name}.")
                cur.execute(sql_create)

            # Committing all creations at once
            conn.commit()
            logging.info("Lookup tables created successfully.")


def create_data_table():
    """Create data tables Location and Address"""

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Create Address table
            logging.info("Dropping Location table if exists.")
            cur.execute('DROP TABLE IF EXISTS Location;')
            logging.info("Creating Location table...")
            sql_location = """CREATE TABLE Location (
                LOC_GUID VARCHAR(255) PRIMARY KEY,
                CIVIC_NO VARCHAR(255),
                CIVIC_NO_SUFFIX VARCHAR(255),
                OFFICIAL_STREET_NAME VARCHAR(255),
                OFFICIAL_STREET_TYPE_ID INT,
                OFFICIAL_STREET_DIR_ID INT,
                PROV_CODE INT,
                CSD_NAME_ID INT,
                CSD_TYPE_ID INT,
                MAIL_STREET_NAME VARCHAR(255),
                MAIL_STREET_TYPE_ID INT,
                MAIL_STEET_DIR_ID INT,
                MAIL_MUN_NAME_ID INT,
                MAIL_PROV INT,
                MAIL_POSTAL_CODE VARCHAR(255),
                BG_DLS_LSD VARCHAR(255),
                BG_DLS_QTR VARCHAR(255),
                BG_DLS_SCTN VARCHAR(255),
                BG_DLS_TWNSHP VARCHAR(255),
                BG_DLS_RNG VARCHAR(255),
                BG_DLS_MRD VARCHAR(255),
                BG_X VARCHAR(255),
                BG_Y VARCHAR(255)
            );"""
            cur.execute(sql_location)
            conn.commit()
            logging.info("Location table created.")

            # Create Address table
            logging.info("Dropping Address table if exists.")
            cur.execute('DROP TABLE IF EXISTS Address;')
            logging.info("Creating Address table...")       
            sql_address = """CREATE TABLE Address (
                ADDR_GUID VARCHAR(255) PRIMARY KEY,
                LOC_GUID VARCHAR(255),
                APT_NO_LABEL VARCHAR(255),
                BU_N_CIVIC_ADD VARCHAR(255),
                BU_USE VARCHAR(255)
            );"""          
            cur.execute(sql_address)
            conn.commit()
            logging.info("Address table created.")


def populate_data_table():
    """populate Location and Address table with records from NAR_raw"""

    sql_location_insert = """
            WITH NAR_raw_CTE AS (
                SELECT 
                    N.*,
                    ROW_NUMBER() OVER (PARTITION BY N.LOC_GUID ORDER BY N.ADDR_GUID) AS row_num
                FROM NAR_raw N
                WHERE N.LOC_GUID IS NOT NULL
            )
            INSERT INTO Location (
                LOC_GUID,
                CIVIC_NO,
                CIVIC_NO_SUFFIX,
                OFFICIAL_STREET_NAME,
                OFFICIAL_STREET_TYPE_ID,
                OFFICIAL_STREET_DIR_ID,
                PROV_CODE,
                CSD_NAME_ID,
                CSD_TYPE_ID,
                MAIL_STREET_NAME,
                MAIL_STREET_TYPE_ID,
                MAIL_STEET_DIR_ID,
                MAIL_MUN_NAME_ID,
                MAIL_PROV,
                MAIL_POSTAL_CODE,
                BG_DLS_LSD,
                BG_DLS_QTR,
                BG_DLS_SCTN,
                BG_DLS_TWNSHP,
                BG_DLS_RNG,
                BG_DLS_MRD,
                BG_X,
                BG_Y
            )
            SELECT 
                N.LOC_GUID,
                N.CIVIC_NO,
                N.CIVIC_NO_SUFFIX,
                N.OFFICIAL_STREET_NAME,
                (SELECT STREET_TYPE_ID FROM Street_Type WHERE Street_Type = N.OFFICIAL_STREET_TYPE) AS OFFICIAL_STREET_TYPE_ID,
                (SELECT STREET_DIR_ID FROM Street_DIR WHERE Street_Dir = N.OFFICIAL_STREET_DIR) AS OFFICIAL_STREET_DIR_ID,
                (SELECT Prov_Code FROM Prov_Code WHERE Prov_Code = N.PROV_CODE) AS PROV_CODE,
                (SELECT CSD_NAME_ID FROM CSD_Name WHERE CSD_NAME_ENG = N.CSD_ENG_NAME AND CSD_NAME_FRE = N.CSD_FRE_NAME) AS CSD_NAME_ID,
                (SELECT CSD_TYPE_ID FROM CSD_Type WHERE CSD_TYPE_ENG = N.CSD_TYPE_ENG_CODE AND CSD_TYPE_FRE = N.CSD_TYPE_FRE_CODE) AS CSD_TYPE_ID,
                N.MAIL_STREET_NAME,
                (SELECT STREET_TYPE_ID FROM Street_Type WHERE Street_Type = N.MAIL_STREET_TYPE) AS MAIL_STREET_TYPE_ID,
                (SELECT STREET_DIR_ID FROM Street_DIR WHERE Street_Dir = N.MAIL_STEET_DIR) AS MAIL_STEET_DIR_ID,
                (SELECT MAIL_MUN_NAME_ID FROM Mail_Mun_Name WHERE MAIL_MUN_NAME = N.MAIL_MUN_NAME) AS MAIL_MUN_NAME_ID,
                (SELECT Prov_Code FROM Prov_Code WHERE Prov_Abrv = N.MAIL_PROV_ABVN) AS MAIL_PROV,
                N.MAIL_POSTAL_CODE,
                N.BG_DLS_LSD,
                (SELECT BG_DLS_QTR_ID FROM BG_DLS_QTR WHERE BG_DLS_QTR = N.BG_DLS_QTR) AS BG_DLS_QTR,
                N.BG_DLS_SCTN,
                N.BG_DLS_TWNSHP,
                N.BG_DLS_RNG,
                (SELECT BG_DLS_MRD_ID FROM BG_DLS_MRD WHERE BG_DLS_MRD = N.BG_DLS_MRD) AS BG_DLS_MRD,
                N.BG_X,
                N.BG_Y
            FROM NAR_raw_CTE N
            WHERE N.row_num = 1;

            """
    sql_address_insert = """
        INSERT INTO Address (
            ADDR_GUID,
            LOC_GUID,
            APT_NO_LABEL,
            BU_N_CIVIC_ADD,
            BU_USE
        )
        SELECT 
            N.ADDR_GUID,
            N.LOC_GUID,
            N.APT_NO_LABEL,
            N.BU_N_CIVIC_ADD,
            N.BU_USE
        FROM NAR_raw N;

        """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Inserting data into tables
            logging.info("Updating Location table...")
            cur.execute(sql_location_insert)
            conn.commit()
            logging.info("Location table updated successfully.")
            
            logging.info("Updating Address table...")
            cur.execute(sql_address_insert)
            conn.commit()
            logging.info("Address table updated successfully.")


def validate_result():
    """Validate number of records in NAR_raw and data tables"""
    with get_connection() as conn:
        with conn.cursor() as cur:
            sql_raw_count = f"SELECT COUNT(*) FROM NAR_raw;"
            sql_location_count = f"SELECT COUNT(*) FROM Location;"
            sql_address_count = f"SELECT COUNT(*) FROM Address;"

            cur.execute(sql_raw_count)
            raw_count = cur.fetchone()[0]

            cur.execute(sql_location_count)
            location_count = cur.fetchone()[0]

            cur.execute(sql_address_count)
            address_count = cur.fetchone()[0]

            print(f'Total number of records from raw table: {raw_count}')
            print(f'Total number of records from Location table: {location_count}')
            print(f'Total number of records from Address table: {address_count}')

            if raw_count == address_count:
                print('Number of records match between raw table and data tables.')
            else:
                print(f'Number of records between raw table and data tables are off by.{raw_count-address_count}')


def main():
    start = time.time()
    # Get all NAR files from directory
    csv_files = glob.glob(os.path.join(r"C:\cst2112_data\ga5_NAR", '*.csv'))

    # Create raw table for NAR files
    create_raw_table(csv_files[0], "NAR_raw")
    load_raw_table(csv_files)

    # Create and populate lookup tables
    create_lookup_table()
    populate_lookup_table()

    # Populate data table
    create_data_table()
    populate_data_table()
    
    # Check if number of records match between raw table and final data tables
    validate_result()

    # CALC & PRINT RUNTIME
    end = time.time()
    runtime = round((end - start), 2)
    if runtime < 60:
        print(f'Runtime: {runtime} seconds')
    else:
        print('Runtime: ' + str(round((runtime/60), 2)) + ' minutes')

if __name__ == "__main__":
    main()
