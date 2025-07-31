import pdfplumber
import psycopg2
import os
import re

# Database connection parameters
hostname = "localhost"
database = "pdf_datasets"
username = "postgres"
pwd = os.getenv("DB_PASSWORD", "Metal1394ever!")
port_id = 5432

def clean_numeric_value(value_str):
    """Clean and convert string values to integers, handling various formats"""
    if not value_str or value_str.strip() == '':
        return None
    
    # Remove newlines, commas, and extra spaces
    cleaned = str(value_str).replace('\n', '').replace(',', '').strip()
    
    # Handle negative values
    if cleaned.startswith('-'):
        try:
            return -int(cleaned[1:])
        except ValueError:
            return None
    
    # Try to convert to integer
    try:
        return int(cleaned)
    except ValueError:
        return None

def create_and_ingest_data():
    """
    Connects to the PostgreSQL database, creates a new table for the All_India data,
    and ingests data extracted from All_India.pdf.
    """
    conn = None
    try:
        conn = psycopg2.connect(
            host=hostname,
            dbname=database,
            user=username,
            password=pwd,
            port=port_id
        )
        cur = conn.cursor()

        # SQL to create the new table for the All-India dataset
        create_table_query = """
        CREATE TABLE IF NOT EXISTS all_india_stats (
            id SERIAL PRIMARY KEY,
            characteristic_name VARCHAR(255),
            all_industries BIGINT,
            industry_0163 BIGINT,
            industry_0164 BIGINT,
            industry_0893 BIGINT,
            industry_1010 BIGINT,
            industry_1020 BIGINT,
            industry_1030 BIGINT,
            industry_1040 BIGINT,
            industry_1050 BIGINT,
            industry_1061 BIGINT
        );
        """
        cur.execute(create_table_query)
        conn.commit()
        print("Table 'all_india_stats' created or already exists.")

        # Clean existing data to avoid duplicates on rerun
        cur.execute("DELETE FROM all_india_stats;")
        conn.commit()

        with pdfplumber.open("All_India.pdf") as pdf:
            page = pdf.pages[0]
            
            # Extract text and try to parse it line by line
            text = page.extract_text()
            lines = text.split('\n')
            
            # Find the start of the data (after headers)
            data_started = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Skip header lines and start processing when we find numbered characteristics
                if re.match(r'^\d+\.', line):
                    data_started = True
                
                if not data_started:
                    continue
                
                # Split the line and try to extract data
                parts = re.split(r'\s+', line)
                
                if len(parts) < 2:
                    continue
                
                # Extract characteristic name (everything before the first number)
                characteristic_match = re.match(r'^(\d+\.\s*[^0-9]+)', line)
                if not characteristic_match:
                    continue
                
                characteristic_name = characteristic_match.group(1).strip()
                
                # Extract numbers from the line
                numbers_text = line[len(characteristic_match.group(1)):].strip()
                number_parts = re.split(r'\s+', numbers_text)
                
                # Convert to numbers
                values = []
                for part in number_parts[:10]:  # We expect 10 columns of data
                    cleaned_value = clean_numeric_value(part)
                    values.append(cleaned_value)
                
                # Pad with None if we don't have enough values
                while len(values) < 10:
                    values.append(None)
                
                # Only insert if we have at least one non-null value
                if any(v is not None for v in values):
                    insert_query = """
                    INSERT INTO all_india_stats (characteristic_name, all_industries, industry_0163, industry_0164, industry_0893, industry_1010, industry_1020, industry_1030, industry_1040, industry_1050, industry_1061)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """
                    cur.execute(insert_query, (characteristic_name, *values))

        # If the above method doesn't work well, try table extraction as fallback
        try:
            with pdfplumber.open("All_India.pdf") as pdf:
                page = pdf.pages[0]
                
                # Try different table extraction settings
                tables = page.extract_tables(table_settings={
                    "vertical_strategy": "lines_strict",
                    "horizontal_strategy": "lines_strict",
                    "snap_tolerance": 3,
                })
                
                if tables:
                    table = tables[0]
                    print(f"Found table with {len(table)} rows")
                    
                    # Clear previous data
                    cur.execute("DELETE FROM all_india_stats;")
                    conn.commit()
                    
                    for i, row in enumerate(table):
                        if i < 2:  # Skip header rows
                            continue
                        
                        if not row or not row[0]:
                            continue
                        
                        characteristic_name = str(row[0]).replace('\n', ' ').strip()
                        
                        # Skip if it's just a number or header
                        if characteristic_name.isdigit() or 'Characteristics' in characteristic_name:
                            continue
                        
                        values = []
                        for j in range(1, min(11, len(row))):  # Get up to 10 data columns
                            cleaned_value = clean_numeric_value(row[j])
                            values.append(cleaned_value)
                        
                        # Pad with None if needed
                        while len(values) < 10:
                            values.append(None)
                        
                        if any(v is not None for v in values):
                            insert_query = """
                            INSERT INTO all_india_stats (characteristic_name, all_industries, industry_0163, industry_0164, industry_0893, industry_1010, industry_1020, industry_1030, industry_1040, industry_1050, industry_1061)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                            """
                            cur.execute(insert_query, (characteristic_name, *values))
        
        except Exception as table_error:
            print(f"Table extraction fallback failed: {table_error}")

        conn.commit()
        print("Successfully ingested data into 'all_india_stats' table.")

    except (Exception, psycopg2.Error) as error:
        print(f"Error while connecting to PostgreSQL or processing PDF: {error}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()
            print("PostgreSQL connection closed.")

if __name__ == '__main__':
    create_and_ingest_data()