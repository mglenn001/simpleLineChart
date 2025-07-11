import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import * as React from 'react';

interface ChartData {
  [key: string]: string | number;
}

interface ExampleState {
  data: ChartData[];
  loading: boolean;
  error: string | null;
}

export default function Example() {
  const [state, setState] = React.useState<ExampleState>({
    data: [],
    loading: true,
    error: null
  });

  React.useEffect(() => {
    const loadCSVData = () => {
      fetch('/Area_Population_Density_and_Population_2011_Census.csv')
        .then((response) => {
          if (!response.ok) {
            throw new Error('Failed to fetch CSV file');
          }
          return response.text();
        })
        .then((csvText) => {
          // Simple CSV parser
          const lines = csvText.split('\n');
          const headers = lines[0].split(',').map((h: string) => h.trim());
          
          const parsedData: ChartData[] = [];
          for (let i = 1; i < lines.length; i++) {
            if (lines[i].trim()) {
              const values = lines[i].split(',');
              const row: ChartData = {};
              for (let j = 0; j < headers.length; j++) {
                const header = headers[j];
                const value = values[j] ? values[j].trim() : '';
                // Try to convert to number, otherwise keep as string
                const numValue = parseFloat(value);
                row[header] = !isNaN(numValue) ? numValue : value;
              }
              parsedData.push(row);
            }
          }
          
          setState({
            data: parsedData,
            loading: false,
            error: null
          });
        })
        .catch((err) => {
          setState({
            data: [],
            loading: false,
            error: 'Failed to load CSV data'
          });
          console.error('Error loading CSV:', err);
        });
    };

    loadCSVData();
  }, []);

  if (state.loading) {
    return React.createElement('div', null, 'Loading CSV data...');
  }
  
  if (state.error) {
    return React.createElement('div', null, 'Error: ' + state.error);
  }
  
  if (state.data.length === 0) {
    return React.createElement('div', null, 'No data available');
  }

  // Get the first few keys for line chart (excluding name/label column)
  const allKeys = Object.keys(state.data[0]);
  const numericKeys: string[] = [];
  let nameKey = '';

  // Find numeric and string columns
  for (let i = 0; i < allKeys.length; i++) {
    const key = allKeys[i];
    const value = state.data[0][key];
    if (typeof value === 'number') {
      numericKeys.push(key);
    } else if (typeof value === 'string' && !nameKey) {
      nameKey = key;
    }
  }

  // Use first 2 numeric columns
  const dataKeys = numericKeys.slice(0, 2);
  
  // Use first string column or first column as name key
  if (!nameKey) {
    nameKey = allKeys[0];
  }

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
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={nameKey} />
        <YAxis />
        <Tooltip />
        <Legend />
        {dataKeys.map((key: string, index: number) => (
          <Line 
            key={key}
            type="monotone" 
            dataKey={key} 
            stroke={index === 0 ? "#8884d8" : "#82ca9d"} 
            activeDot={{ r: 8 }} 
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}