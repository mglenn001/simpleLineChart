import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.extras import RealDictCursor
import psycopg2
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Add endpoint to check all available data
@app.get("/api/all-india-stats/debug")
async def debug_all_india_stats():
    """Debug endpoint to see all data in the table"""
    conn = None
    try:
        conn = psycopg2.connect(
            host=hostname,
            dbname=database,
            user=username,
            password=pwd,
            port=port_id
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Get table structure
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'all_india_stats'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()

        # Get sample data
        cur.execute("SELECT * FROM all_india_stats LIMIT 10;")
        sample_data = cur.fetchall()

        # Get row count
        cur.execute("SELECT COUNT(*) as total_rows FROM all_india_stats;")
        row_count = cur.fetchone()['total_rows']

        return {
            "table_structure": columns,
            "sample_data": sample_data,
            "total_rows": row_count
        }

    except (Exception, psycopg2.Error) as error:
        logger.error(f"Error in debug endpoint: {error}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(error)}")
    finally:
        if conn:
            cur.close()
            conn.close()

# Original endpoint with better error handling
@app.get("/api/all-india-stats")
async def get_all_india_stats():
    conn = None
    try:
        conn = psycopg2.connect(
            host=hostname,
            dbname=database,
            user=username,
            password=pwd,
            port=port_id
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # First, let's see what data we actually have
        cur.execute("SELECT DISTINCT characteristic_name FROM all_india_stats;")
        available_characteristics = [row['characteristic_name'] for row in cur.fetchall()]
        logger.info(f"Available characteristics: {available_characteristics}")

        # SQL query to fetch Working Capital and Invested Capital for all industries
        cur.execute("""
            SELECT characteristic_name, 
                   industry_0163, industry_0164, industry_0893,
                   industry_1010, industry_1020, industry_1030, 
                   industry_1040, industry_1050, industry_1061 
            FROM all_india_stats 
            WHERE characteristic_name ILIKE '%Working Capital%' 
               OR characteristic_name ILIKE '%Invested Capital%';
        """)
        data = cur.fetchall()

        if not data:
            # If no specific matches, get the first few rows for debugging
            cur.execute("""
                SELECT characteristic_name, 
                       industry_0163, industry_0164, industry_0893,
                       industry_1010, industry_1020, industry_1030, 
                       industry_1040, industry_1050, industry_1061 
                FROM all_india_stats 
                LIMIT 5;
            """)
            data = cur.fetchall()

        # Transform data into a long format for easier frontend visualization
        transformed_data = []
        for row in data:
            characteristic = row['characteristic_name']
            for key, value in row.items():
                if key != 'characteristic_name' and value is not None:
                    transformed_data.append({
                        "characteristic": characteristic,
                        "industry": key,
                        "value": value
                    })

        logger.info(f"Returning {len(transformed_data)} data points")
        return {
            "data": transformed_data,
            "available_characteristics": available_characteristics,
            "message": f"Found {len(data)} matching rows"
        }

    except (Exception, psycopg2.Error) as error:
        logger.error(f"Error while fetching data: {error}")
        raise HTTPException(status_code=500, detail=f"Could not retrieve data from the database: {str(error)}")
    finally:
        if conn:
            cur.close()
            conn.close()

# New endpoint to get all characteristics
@app.get("/api/characteristics")
async def get_characteristics():
    """Get all available characteristics in the database"""
    conn = None
    try:
        conn = psycopg2.connect(
            host=hostname,
            dbname=database,
            user=username,
            password=pwd,
            port=port_id
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT DISTINCT characteristic_name FROM all_india_stats ORDER BY characteristic_name;")
        characteristics = [row['characteristic_name'] for row in cur.fetchall()]
        
        return {"characteristics": characteristics}

    except (Exception, psycopg2.Error) as error:
        logger.error(f"Error fetching characteristics: {error}")
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        if conn:
            cur.close()
            conn.close()

# New endpoint to get data for specific characteristics
@app.get("/api/data/{characteristic}")
async def get_data_by_characteristic(characteristic: str):
    """Get data for a specific characteristic"""
    conn = None
    try:
        conn = psycopg2.connect(
            host=hostname,
            dbname=database,
            user=username,
            password=pwd,
            port=port_id
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT * FROM all_india_stats 
            WHERE characteristic_name ILIKE %s;
        """, (f"%{characteristic}%",))
        
        data = cur.fetchall()
        return {"data": data}

    except (Exception, psycopg2.Error) as error:
        logger.error(f"Error fetching data for characteristic {characteristic}: {error}")
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        if conn:
            cur.close()
            conn.close()