import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import * as React from 'react';

// Define the structure for each data point from the API
interface ChartData {
  District: string;
  GeographicalAreaSqKms: number;
  PopulationDensity: number;
}

// Define the state structure for the Example component
interface ExampleState {
  data: ChartData[];
  loading: boolean;
  error: string | null;
}

// Configuration for the API
const API_BASE_URL = 'http://localhost:8000';

export default function Example() {
  // Initialize the component's state
  const [state, setState] = React.useState<ExampleState>({
    data: [],
    loading: true,
    error: null
  });

  // useEffect hook to load data from FastAPI when the component mounts
  React.useEffect(() => {
    const loadDataFromAPI = async () => {
      try {
        setState(prevState => ({ ...prevState, loading: true, error: null }));

        // Fetch data from FastAPI endpoint
        const response = await fetch(`${API_BASE_URL}/chart-data?limit=20`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const chartData: ChartData[] = await response.json();

        // Update the component's state with the fetched data
        setState({
          data: chartData,
          loading: false,
          error: null
        });
      } catch (err) {
        // Handle any errors during fetching
        const errorMessage = err instanceof Error ? err.message : 'Failed to load data from API';
        setState({
          data: [],
          loading: false,
          error: errorMessage
        });
        console.error('Error loading data from API:', err);
      }
    };

    loadDataFromAPI();
  }, []); // Empty dependency array means this effect runs once after the initial render

  // Function to refresh data
  const refreshData = () => {
    setState(prevState => ({ ...prevState, loading: true, error: null }));
    // Trigger re-fetch by updating a dependency or calling the fetch function again
    window.location.reload(); // Simple approach, or you could extract the fetch logic
  };

  // Render loading state
  if (state.loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100%',
        flexDirection: 'column'
      }}>
        <div>Loading data from FastAPI...</div>
        <div style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
          Make sure FastAPI server is running on {API_BASE_URL}
        </div>
      </div>
    );
  }
  
  // Render error state
  if (state.error) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100%',
        flexDirection: 'column',
        color: 'red'
      }}>
        <div>Error: {state.error}</div>
        <button 
          onClick={refreshData}
          style={{
            marginTop: '10px',
            padding: '10px 20px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Retry
        </button>
        <div style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
          Make sure FastAPI server is running on {API_BASE_URL}
        </div>
      </div>
    );
  }
  
  // Render no data available state
  if (state.data.length === 0) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100%' 
      }}>
        No data available
      </div>
    );
  }

  // Calculate the maximum Y-axis value for dynamic scaling
  const allValues: number[] = [];
  state.data.forEach(row => {
    allValues.push(row.GeographicalAreaSqKms, row.PopulationDensity);
  });

  const maxYValue = allValues.length > 0 ? Math.max(...allValues) : 0;
  const paddedMaxY = maxYValue > 0 ? maxYValue * 1.1 : 100;

  return (
    <div style={{ width: '100%', height: '100%' }}>
      {/* Header with data info */}
      <div style={{ 
        padding: '10px', 
        backgroundColor: '#f8f9fa', 
        borderBottom: '1px solid #dee2e6',
        textAlign: 'center'
      }}>
        <h3 style={{ margin: '0 0 5px 0' }}>
          Karnataka Districts: Geographical Area vs Population Density
        </h3>
        <p style={{ margin: '0', color: '#666', fontSize: '14px' }}>
          Data from FastAPI • {state.data.length} districts • 
          <button 
            onClick={refreshData}
            style={{
              marginLeft: '10px',
              padding: '5px 10px',
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '3px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            Refresh
          </button>
        </p>
      </div>

      {/* Chart container */}
      <div style={{ width: '100%', height: 'calc(100% - 80px)' }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={state.data}
            margin={{
              top: 20,
              right: 30,
              left: 20,
              bottom: 100,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="District" 
              interval={0} 
              angle={-45} 
              textAnchor="end" 
              height={100}
              fontSize={12}
            />
            <YAxis domain={[0, paddedMaxY]} />
            <Tooltip 
              formatter={(value: number, name: string) => [
                typeof value === 'number' ? value.toLocaleString() : value,
                name === 'GeographicalAreaSqKms' ? 'Geographical Area (Sq.Kms)' : 'Population Density'
              ]}
              labelFormatter={(label: string) => `District: ${label}`}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="GeographicalAreaSqKms" 
              stroke="#8884d8" 
              activeDot={{ r: 6 }}
              name="Geographical Area (Sq.Kms)"
              strokeWidth={2}
            />
            <Line 
              type="monotone" 
              dataKey="PopulationDensity" 
              stroke="#82ca9d" 
              activeDot={{ r: 6 }}
              name="Population Density"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}