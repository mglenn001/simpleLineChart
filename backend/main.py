from fastapi import FastAPI, HTTPException, Query # Ensure Query is imported
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional # Ensure Optional is imported
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime # Ensure datetime is imported

# Database connection parameters
hostname = "localhost"
database = "recharts"
username = "postgres"
pwd = "Metal1394ever!"  # Update with your actual password
port_id = 5432

# Initialize FastAPI application
app = FastAPI(title="Population Data API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DistrictData(BaseModel):
    """
    Pydantic model representing a single district's population data.
    Matches the structure of the PostgreSQL table.
    """
    id: int
    district: str
    geographical_area: float
    population_density: int
    male: int
    female: int
    total_population: int
    percentage_share: float
    rank_position: int

class ChartDataPoint(BaseModel):
    """
    Pydantic model representing a simplified data point for charting purposes.
    """
    District: str
    GeographicalAreaSqKms: float
    PopulationDensity: int

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(
            host=hostname,
            dbname=database,
            user=username,
            password=pwd,
            port=port_id,
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.get("/")
def read_root():
    """
    Root endpoint for the API.
    """
    return {"message": "Population Data API with PostgreSQL", "status": "running"}

@app.get("/districts", response_model=List[DistrictData])
def get_all_districts():
    """Get all district data from PostgreSQL"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, district, geographical_area, population_density, 
                   male, female, total_population, percentage_share, rank_position
            FROM populations 
            ORDER BY district
        """)
        
        rows = cur.fetchall()
        
        districts = []
        for row in rows:
            districts.append(DistrictData(
                id=row['id'],
                district=row['district'],
                geographical_area=float(row['geographical_area']),
                population_density=row['population_density'],
                male=row['male'],
                female=row['female'],
                total_population=row['total_population'],
                percentage_share=float(row['percentage_share']),
                rank_position=row['rank_position']
            ))
        
        return districts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")
    finally:
        if conn:
            conn.close()

# MODIFIED /chart-data ENDPOINT
@app.get("/chart-data", response_model=List[ChartDataPoint])
def get_chart_data(
    limit: int = Query(20, ge=1, description="Number of districts to return"),
    order_by: str = Query("district", description="Column to order by: 'district', 'population_density', 'geographical_area', 'total_population', 'rank_position'")
):
    """
    Get chart data for the first N districts, ordered by a specified column.
    """
    conn = None
    try:
        # Validate order_by parameter
        valid_orders = {
            "district": "district",
            "population_density": "population_density",
            "geographical_area": "geographical_area",
            "total_population": "total_population",
            "rank_position": "rank_position"
        }
        
        if order_by not in valid_orders:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid 'order_by' parameter. Must be one of: {', '.join(valid_orders.keys())}"
            )
        
        sort_column = valid_orders[order_by]
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Determine sort order (ASC for rank_position, DESC for others if common for 'top' lists, or always ASC for visual flow)
        # For a line graph, usually you want a continuous flow for the X-axis, so ASC makes sense for all.
        # However, if you're sorting by a metric like population/density for "top N", DESC might be desired.
        # Let's default to ASC for most and DESC for rank/population if that implies "top".
        # For simplicity in a line chart that shows trend over sorted data, ASC is generally better.
        # If showing "top 20 districts by population", then sort_column DESC is appropriate.
        # For this chart, let's assume `rank_position` is ascending from 1 to N, and others are ascending as well for visual flow.
        
        sql_query = f"""
            SELECT district, geographical_area, population_density
            FROM populations 
            ORDER BY {sort_column} ASC
            LIMIT %s;
        """
        
        cur.execute(sql_query, (limit,))
        
        rows = cur.fetchall()
        
        chart_data = []
        for row in rows:
            chart_data.append(ChartDataPoint(
                District=row['district'],
                GeographicalAreaSqKms=float(row['geographical_area']),
                PopulationDensity=row['population_density']
            ))
        
        return chart_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data for chart: {str(e)}")
    finally:
        if conn:
            conn.close()

@app.get("/districts/{district_name}")
def get_district_by_name(district_name: str):
    """Get specific district data by name"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, district, geographical_area, population_density, 
                   male, female, total_population, percentage_share, rank_position
            FROM populations 
            WHERE LOWER(district) = LOWER(%s)
        """, (district_name,))
        
        row = cur.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="District not found")
        
        district = DistrictData(
            id=row['id'],
            district=row['district'],
            geographical_area=float(row['geographical_area']),
            population_density=row['population_density'],
            male=row['male'],
            female=row['female'],
            total_population=row['total_population'],
            percentage_share=float(row['percentage_share']),
            rank_position=row['rank_position']
        )
        
        return district
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if conn:
            conn.close()

@app.get("/top-districts")
def get_top_districts(by: str = "population", limit: int = 10):
    """Get top districts by population, density, or area"""
    conn = None
    try:
        # Validate sort parameter
        valid_sorts = {
            "population": "total_population",
            "density": "population_density", 
            "area": "geographical_area"
        }
        
        if by not in valid_sorts:
            raise HTTPException(status_code=400, detail="Invalid 'by' parameter. Use: population, density, or area")
        
        sort_column = valid_sorts[by]
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(f"""
            SELECT id, district, geographical_area, population_density, 
                   male, female, total_population, percentage_share, rank_position
            FROM populations 
            ORDER BY {sort_column} DESC
            LIMIT %s
        """, (limit,))
        
        rows = cur.fetchall()
        
        districts = []
        for row in rows:
            districts.append(DistrictData(
                id=row['id'],
                district=row['district'],
                geographical_area=float(row['geographical_area']),
                population_density=row['population_density'],
                male=row['male'],
                female=row['female'],
                total_population=row['total_population'],
                percentage_share=float(row['percentage_share']),
                rank_position=row['rank_position']
            ))
        
        return districts
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if conn:
            conn.close()

@app.get("/stats")
def get_database_stats():
    """Get basic statistics about the database"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get total count
        cur.execute("SELECT COUNT(*) as total_districts FROM populations")
        total_count = cur.fetchone()['total_districts']
        
        # Get population statistics
        cur.execute("""
            SELECT 
                SUM(total_population) as total_population,
                AVG(population_density) as avg_density,
                MAX(population_density) as max_density,
                MIN(population_density) as min_density,
                AVG(geographical_area) as avg_area
            FROM populations
        """)
        stats = cur.fetchone()
        
        return {
            "total_districts": total_count,
            "total_population": int(stats['total_population']) if stats['total_population'] else 0,
            "average_density": round(float(stats['avg_density']), 2) if stats['avg_density'] else 0,
            "max_density": stats['max_density'],
            "min_density": stats['min_density'],
            "average_area": round(float(stats['avg_area']), 2) if stats['avg_area'] else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)