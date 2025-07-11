import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import * as React from 'react';

// Define the structure for each data point in the chart
interface ChartData {
  [key: string]: string | number;
}

// Define the state structure for the Example component
interface ExampleState {
  data: ChartData[];
  loading: boolean;
  error: string | null;
}

export default function Example() {
  // Initialize the component's state
  const [state, setState] = React.useState<ExampleState>({
    data: [],
    loading: true,
    error: null
  });

  // useEffect hook to load CSV data when the component mounts
  React.useEffect(() => {
    const loadCSVData = () => {
      // Fetch the CSV file from the public folder
      fetch('/Area_Population_Density_and_Population_2011_Census.csv')
        .then((response) => {
          // Check if the network response was successful
          if (!response.ok) {
            throw new Error('Failed to fetch CSV file');
          }
          // Return the response body as text
          return response.text();
        })
        .then((csvText) => {
          // Parse the CSV text into an array of objects
          const lines = csvText.split('\n');
          // Get headers from the first line, trimming whitespace
          const headers = lines[0].split(',').map((h: string) => h.trim());
          
          const parsedData: ChartData[] = [];
          // Iterate over lines starting from the second line (skipping headers)
          for (let i = 1; i < lines.length; i++) {
            if (lines[i].trim()) { // Ensure the line is not empty
              const values = lines[i].split(',');
              const row: ChartData = {};
              // Map values to headers to create an object for each row
              for (let j = 0; j < headers.length; j++) {
                const header = headers[j];
                const value = values[j] ? values[j].trim() : '';
                // Attempt to convert value to a number; otherwise, keep as string
                const numValue = parseFloat(value);
                row[header] = !isNaN(numValue) ? numValue : value;
              }
              parsedData.push(row);
            }
          }

          // Filter out the "State Total" row to avoid skewing the chart
          // Assuming 'District' is the column containing 'State Total'
          const nameKeyForFiltering = 'District'; // Explicitly set the key for filtering
          const filteredData = parsedData.filter(row => {
            const rowNameValue = nameKeyForFiltering ? String(row[nameKeyForFiltering]).toLowerCase() : '';
            return rowNameValue !== 'state total';
          });
          
          // Take only the first 20 districts as requested
          const finalData = filteredData.slice(0, 20);

          // Update the component's state with the parsed and filtered data
          setState({
            data: finalData,
            loading: false,
            error: null
          });
        })
        .catch((err) => {
          // Handle any errors during fetching or parsing
          setState({
            data: [],
            loading: false,
            error: 'Failed to load CSV data'
          });
          console.error('Error loading CSV:', err);
        });
    };

    loadCSVData(); // Call the function to load data
  }, []); // Empty dependency array means this effect runs once after the initial render

  // Render loading state
  if (state.loading) {
    return React.createElement('div', null, 'Loading CSV data...');
  }
  
  // Render error state
  if (state.error) {
    return React.createElement('div', null, 'Error: ' + state.error);
  }
  
  // Render no data available state
  if (state.data.length === 0) {
    return React.createElement('div', null, 'No data available');
  }

  // Define the data keys for the chart
  const nameKey = 'District'; // X-axis will display District names
  const dataKeys = ['Geograpical Area (Sq.Kms)', 'Population Density']; // Y-axis lines for these two metrics

  // Calculate the maximum Y-axis value for dynamic scaling
  const allNumericValues: number[] = [];
  state.data.forEach(row => {
    dataKeys.forEach(key => { // Iterate through the specific dataKeys for the chart
      if (typeof row[key] === 'number') {
        allNumericValues.push(row[key] as number);
      }
    });
  });

  const maxYValue = allNumericValues.length > 0 ? Math.max(...allNumericValues) : 0;
  // Add 10% padding to the max Y value for better visualization, or default to 100 if no data
  const paddedMaxY = maxYValue > 0 ? maxYValue * 1.1 : 100; 

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart
        width={500}
        height={300}
        data={state.data}
        margin={{
          top: 5,
          right: 30,
          left: 20,
          bottom: 5,
        }}
      >
        <CartesianGrid strokeDasharray="3 3" /> {/* Grid lines for the chart */}
        <XAxis dataKey={nameKey} interval={0} angle={-45} textAnchor="end" height={100} /> {/* X-axis for Districts, rotated labels */}
        <YAxis domain={[0, paddedMaxY]} /> {/* Y-axis with dynamic domain */}
        <Tooltip /> {/* Tooltip for displaying data on hover */}
        <Legend /> {/* Legend to identify lines */}
        {/* Render a Line for each dataKey */}
        {dataKeys.map((key: string, index: number) => (
          <Line 
            key={key}
            type="monotone" 
            dataKey={key} 
            stroke={index === 0 ? "#8884d8" : "#82ca9d"} // Different colors for each line
            activeDot={{ r: 8 }} // Larger dot on hover
            name={key} // Display the full key name in the legend and tooltip
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}