import psycopg2
import csv
from datetime import datetime

# Database connection parameters for the new recharts database
hostname = "localhost"
database = "recharts"  # New database name
username = "postgres"
pwd = "Metal1394ever!"  # Use your actual password
port_id = 5432

def connect_to_db():
    """Connect to PostgreSQL recharts database"""
    return psycopg2.connect(
        host=hostname,
        dbname=database,
        user=username,
        password=pwd,
        port=port_id
    )

def create_populations_table():
    """Create the populations table with proper data types"""
    conn = connect_to_db()
    cur = conn.cursor()

    # Create populations table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS populations (
        id SERIAL PRIMARY KEY,
        district VARCHAR(100) NOT NULL,
        geographical_area DECIMAL(10,2) NOT NULL,
        population_density INTEGER NOT NULL,
        male INTEGER NOT NULL,
        female INTEGER NOT NULL,
        total_population INTEGER NOT NULL,
        percentage_share DECIMAL(5,2) NOT NULL,
        rank_position INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );"""

    cur.execute(create_table_query)
    conn.commit()
    cur.close()
    conn.close()
    print("Table 'populations' created successfully")

def ingest_population_data():
    """Ingest data from CSV file into PostgreSQL populations table"""
    # First create the table
    create_populations_table()

    # Connect to PostgreSQL
    conn = connect_to_db()
    cur = conn.cursor()

    try:
        # Open the CSV file
        with open('Area_Population_Density_and_Population_2011_Census.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            row_count = 0
            error_count = 0

            # Insert each row into the table
            for row in csv_reader:
                try:
                    # Skip the "State Total" row as it's summary data
                    if row['District'].strip().lower() == 'state total':
                        continue
                        
                    # Parse and validate data
                    district = row['District'].strip()
                    geographical_area = float(row['Geograpical Area (Sq.Kms)'].strip())
                    population_density = int(row['Population Density'].strip())
                    male = int(row['Male'].strip())
                    female = int(row['Female'].strip())
                    total_population = int(row[' Total'].strip())  # Note the space in header
                    percentage_share = float(row['Percentage Share to Total Population'].strip())
                    rank_position = int(row['Rank'].strip())
                    
                    # Insert into database
                    cur.execute("""
                        INSERT INTO populations 
                        (district, geographical_area, population_density, male, female, 
                         total_population, percentage_share, rank_position) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (district, geographical_area, population_density, male, female, 
                          total_population, percentage_share, rank_position))
                    
                    row_count += 1
                    
                    # Print progress every 50 rows
                    if row_count % 50 == 0:
                        print(f"Processed {row_count} rows...")
                        
                except (ValueError, KeyError) as e:
                    error_count += 1
                    print(f"Error processing row {row_count + error_count}: {e}")
                    print(f"Row data: {row}")
                    continue

            # Commit and close the connection
            conn.commit()
            print(f"Data ingested successfully!")
            print(f"Total rows processed: {row_count}")
            print(f"Errors encountered: {error_count}")
            
    except Exception as e:
        print(f"Error during data ingestion: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def verify_data():
    """Verify the data was inserted correctly"""
    conn = connect_to_db()
    cur = conn.cursor()
    
    try:
        # Get total count
        cur.execute("SELECT COUNT(*) FROM populations;")
        total_count = cur.fetchone()[0]
        print(f"Total records in populations table: {total_count}")
        
        # Get sample data
        cur.execute("SELECT district, geographical_area, population_density FROM populations LIMIT 5;")
        sample_data = cur.fetchall()
        print("\nSample data:")
        for row in sample_data:
            print(f"District: {row[0]}, Area: {row[1]}, Density: {row[2]}")
            
    except Exception as e:
        print(f"Error verifying data: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("Setting up PostgreSQL database for population data...")
    ingest_population_data()
    verify_data()
    print("Setup complete!")