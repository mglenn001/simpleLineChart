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

  // Create simple chart data - just show Fixed Capital data
  const fixedCapitalData = data
    .filter(d => d.characteristic && d.characteristic.includes('Fixed Capital'))
    .map(d => ({
      industry: d.industry,
      value: d.value
    }));

  console.log('Fixed Capital Data:', fixedCapitalData);

  return (
    <div style={{ padding: '20px' }}>
      <h1>All India - Fixed Capital by Industry</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <p>Total data points: {data.length}</p>
        <p>Fixed Capital data points: {fixedCapitalData.length}</p>
      </div>

      {fixedCapitalData.length > 0 ? (
        <ResponsiveContainer width="100%" height={400}>
          <BarChart
            data={fixedCapitalData}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="industry" />
            <YAxis />
            <Tooltip formatter={(value: any) => [value?.toLocaleString(), 'Fixed Capital']} />
            <Bar dataKey="value" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <div>
          <p>No Fixed Capital data found to display in chart.</p>
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
    </div>
  );
};

export default Example;