import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.extras import RealDictCursor
import psycopg2

app = FastAPI()

# Database connection parameters
hostname = "localhost"
database = "pdf_datasets"
username = "postgres"
pwd = os.getenv("DB_PASSWORD", "Metal1394ever!")
port_id = 5432

# Configure CORS to allow frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your frontend's URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/api/top-industries")
async def get_top_industries():
    conn = None
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=hostname,
            dbname=database,
            user=username,
            password=pwd,
            port=port_id
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # SQL query to fetch all data from the top_industries table
        cur.execute("SELECT rank, total_no_of_factories, no_of_factories_in_operation, fixed_capital, total_persons_engaged, output, gross_value_added FROM top_industries ORDER BY id ASC")
        data = cur.fetchall()
        return data

    except (Exception, psycopg2.Error) as error:
        print(f"Error while fetching data: {error}")
        return {"error": "Could not retrieve data from the database."}
    finally:
        if conn:
            cur.close()
            conn.close()