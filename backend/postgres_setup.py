import pdfplumber
import psycopg2
import os

# Database connection parameters
hostname = "localhost"
database = "pdf_datasets" # The database name from your prompt
username = "postgres"
pwd = os.getenv("DB_PASSWORD", "Metal1394ever!") # It's safer to use an environment variable for the password
port_id = 5432

def create_and_ingest_data():
    """
    Connects to the PostgreSQL database, creates a new table,
    and ingests data extracted from India2.pdf.
    """
    conn = None
    try:
        # Establish a connection to the database
        conn = psycopg2.connect(
            host=hostname,
            dbname=database,
            user=username,
            password=pwd,
            port=port_id
        )
        cur = conn.cursor()

        # SQL to create the table based on the PDF's table structure
        create_table_query = """
        CREATE TABLE IF NOT EXISTS top_industries (
            id SERIAL PRIMARY KEY,
            rank VARCHAR(100),
            total_no_of_factories VARCHAR(100),
            no_of_factories_in_operation VARCHAR(100),
            fixed_capital VARCHAR(100),
            total_persons_engaged VARCHAR(100),
            output VARCHAR(100),
            gross_value_added VARCHAR(100)
        );
        """
        cur.execute(create_table_query)
        conn.commit()
        print("Table 'top_industries' created or already exists.")

        # Use pdfplumber to open the PDF and extract tables
        with pdfplumber.open("India2.pdf") as pdf:
            # We are interested in the table on the first page
            page = pdf.pages[0]
            # Extract tables from the page
            tables = page.extract_tables()

            # Assuming the first table is the one we want
            if tables and len(tables) > 0:
                table = tables[0]

                # Start from the third row to skip headers and blank rows
                for row in table[2:]:
                    # Check if the row has enough elements to avoid index errors
                    if len(row) >= 7:
                        # Extract data from the row
                        rank = row[0].replace("\n", " ") if row[0] else None
                        total_no_of_factories = row[1].replace("\n", " ") if row[1] else None
                        no_of_factories_in_operation = row[2].replace("\n", " ") if row[2] else None
                        fixed_capital = row[3].replace("\n", " ") if row[3] else None
                        total_persons_engaged = row[4].replace("\n", " ") if row[4] else None
                        output = row[5].replace("\n", " ") if row[5] else None
                        gross_value_added = row[6].replace("\n", " ") if row[6] else None
                        
                        # Insert data into the table
                        insert_query = """
                        INSERT INTO top_industries (
                            rank, total_no_of_factories, no_of_factories_in_operation,
                            fixed_capital, total_persons_engaged, output, gross_value_added
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s);
                        """
                        cur.execute(insert_query, (
                            rank, total_no_of_factories, no_of_factories_in_operation,
                            fixed_capital, total_persons_engaged, output, gross_value_added
                        ))

                conn.commit()
                print(f"Successfully ingested data into 'top_industries' table.")
            else:
                print("No tables found on the first page.")

    except (Exception, psycopg2.Error) as error:
        print(f"Error while connecting to PostgreSQL or processing PDF: {error}")
    finally:
        # Close the database connection
        if conn:
            cur.close()
            conn.close()
            print("PostgreSQL connection closed.")

if __name__ == '__main__':
    create_and_ingest_data()