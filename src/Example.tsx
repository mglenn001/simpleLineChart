import React, { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  ResponsiveContainer,
} from 'recharts';

interface ChartData {
  characteristic: string;
  industry: string;
  value: number;
}

const Example: React.FC = () => {
  const [data, setData] = useState<ChartData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/all-india-stats');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const jsonData = await response.json();
        console.log('Raw API response:', jsonData);
        
        // Check if the response is an array or has a data property
        if (Array.isArray(jsonData)) {
          setData(jsonData);
        } else if (jsonData.data && Array.isArray(jsonData.data)) {
          setData(jsonData.data);
        } else if (jsonData.error) {
          throw new Error(jsonData.error);
        } else {
          throw new Error('Unexpected response format');
        }
        
      } catch (error) {
        console.error('Failed to fetch data:', error);
        setError(error instanceof Error ? error.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading data...</div>;
  }

  if (error) {
    return (
      <div style={{ padding: '20px' }}>
        <h2>Error loading data:</h2>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div style={{ padding: '20px' }}>
        <h2>No data available</h2>
        <p>The API returned no data. Check your database and API endpoints.</p>
      </div>
    );
  }

  // Process data to create chart data with both Working Capital and Invested Capital
  const processChartData = () => {
    // Filter data for Working Capital and Invested Capital
    const workingCapitalData = data.filter(d => 
      d.characteristic && d.characteristic.includes('Working Capital') && !d.characteristic.includes('Physical')
    );
    
    const investedCapitalData = data.filter(d => 
      d.characteristic && d.characteristic.includes('Invested Capital')
    );

    console.log('Working Capital Data:', workingCapitalData);
    console.log('Invested Capital Data:', investedCapitalData);

    // Get all unique industries
    const allIndustries = [...new Set([
      ...workingCapitalData.map(d => d.industry),
      ...investedCapitalData.map(d => d.industry)
    ])];

    // Create combined data structure
    const chartData = allIndustries.map(industry => {
      const workingCapital = workingCapitalData.find(d => d.industry === industry)?.value || 0;
      const investedCapital = investedCapitalData.find(d => d.industry === industry)?.value || 0;
      
      return {
        industry: industry.replace('industry_', ''), // Clean up industry name
        'Working Capital': workingCapital,
        'Invested Capital': investedCapital
      };
    });

    return chartData;
  };

  const chartData = processChartData();

  console.log('Chart Data:', chartData);

  return (
    <div style={{ padding: '20px' }}>
      <h1>All India - Working Capital & Invested Capital by Industry</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <p>Total data points: {data.length}</p>
        <p>Industries displayed: {chartData.length}</p>
      </div>

      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={500}>
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="industry" 
              angle={-45}
              textAnchor="end"
              height={80}
              interval={0}
            />
            <YAxis 
              tickFormatter={(value) => `₹${(value / 1000000).toFixed(0)}M`}
            />
            <Tooltip 
              formatter={(value: any, name: string) => [
                `₹${value?.toLocaleString()} Lakh`,
                name
              ]}
              labelFormatter={(label) => `Industry: ${label}`}
            />
            <Legend />
            <Bar dataKey="Working Capital" fill="#8884d8" />
            <Bar dataKey="Invested Capital" fill="#82ca9d" />
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <div>
          <p>No Working Capital or Invested Capital data found to display in chart.</p>
          <h3>Available data (first 10 rows):</h3>
          <table style={{ borderCollapse: 'collapse', width: '100%' }}>
            <thead>
              <tr>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Characteristic</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Industry</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Value</th>
              </tr>
            </thead>
            <tbody>
              {data.slice(0, 10).map((item, index) => (
                <tr key={index}>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{item.characteristic}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{item.industry}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{item.value?.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Debug section */}
      <details style={{ marginTop: '20px' }}>
        <summary>Debug Information</summary>
        <div>
          <h4>Raw Data Sample:</h4>
          <pre style={{ backgroundColor: '#f5f5f5', padding: '10px', fontSize: '12px', overflow: 'auto' }}>
            {JSON.stringify(data.slice(0, 5), null, 2)}
          </pre>
        </div>
      </details>
    </div>
  );
};

export default Example;