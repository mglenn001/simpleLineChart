from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import csv
import os

# Initialize FastAPI application
# title and version are used in the OpenAPI (Swagger UI) documentation
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
    Matches the structure of a row in the CSV file after parsing.
    """
    District: str
    GeographicalArea: float
    PopulationDensity: int
    Male: int
    Female: int
    Total: int
    PercentageShare: float
    Rank: int

class ChartDataPoint(BaseModel):
    """
    Pydantic model representing a simplified data point for charting purposes.
    Designed to provide specific fields required by a charting library like Recharts.
    """
    District: str
    GeographicalAreaSqKms: float
    PopulationDensity: int

@app.get("/")
def read_root():
    """
    Root endpoint for the API.
    Provides a simple status message to confirm the API is running.
    """
    return {"message": "Population Data API", "status": "running"}

@app.get("/districts", response_model=List[DistrictData])
def get_all_districts():
    """Get all district data"""
    try:
        districts = load_csv_data()
        return districts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")

@app.get("/chart-data", response_model=List[ChartDataPoint])
def get_chart_data(limit: int = 20):
    """Get chart data for the first N districts (default 20)"""
    try:
        districts = load_csv_data()
        # Filter out "State Total" and limit results
        filtered_districts = [d for d in districts if d.District.lower() != "state total"]
        limited_districts = filtered_districts[:limit]
        
        # Transform to chart format
        chart_data = []
        for district in limited_districts:
            chart_data.append(ChartDataPoint(
                District=district.District,
                GeographicalAreaSqKms=district.GeographicalArea,
                PopulationDensity=district.PopulationDensity
            ))
        
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")

@app.get("/districts/{district_name}")
def get_district_by_name(district_name: str):
    """Get specific district data by name"""
    try:
        districts = load_csv_data()
        district = next((d for d in districts if d.District.lower() == district_name.lower()), None)
        if not district:
            raise HTTPException(status_code=404, detail="District not found")
        return district
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/top-districts")
def get_top_districts(by: str = "population", limit: int = 10):
    """Get top districts by population, density, or area"""
    try:
        districts = load_csv_data()
        # Filter out "State Total"
        filtered_districts = [d for d in districts if d.District.lower() != "state total"]
        
        if by == "population":
            sorted_districts = sorted(filtered_districts, key=lambda x: x.Total, reverse=True)
        elif by == "density":
            sorted_districts = sorted(filtered_districts, key=lambda x: x.PopulationDensity, reverse=True)
        elif by == "area":
            sorted_districts = sorted(filtered_districts, key=lambda x: x.GeographicalArea, reverse=True)
        else:
            raise HTTPException(status_code=400, detail="Invalid 'by' parameter. Use: population, density, or area")
        
        return sorted_districts[:limit]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

def load_csv_data() -> List[DistrictData]:
    """Load and parse CSV data"""
    csv_path = "Area_Population_Density_and_Population_2011_Census.csv"
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    districts = []
    with open(csv_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            try:
                # Clean and convert data
                district = DistrictData(
                    District=row['District'].strip(),
                    GeographicalArea=float(row['Geograpical Area (Sq.Kms)'].strip()),
                    PopulationDensity=int(row['Population Density'].strip()),
                    Male=int(row['Male'].strip()),
                    Female=int(row['Female'].strip()),
                    Total=int(row[' Total'].strip()),  # Note the space in the CSV header
                    PercentageShare=float(row['Percentage Share to Total Population'].strip()),
                    Rank=int(row['Rank'].strip())
                )
                districts.append(district)
            except (ValueError, KeyError) as e:
                print(f"Error parsing row {row}: {e}")
                continue
    
    return districts

if __name__ == "__main__":
    # This block ensures that uvicorn runs the FastAPI application when the script is executed directly.
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)