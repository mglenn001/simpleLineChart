import React, { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';

interface IndustryData {
  rank: string;
  total_no_of_factories: string;
  no_of_factories_in_operation: string;
  fixed_capital: string;
  total_persons_engaged: string;
  output: string;
  gross_value_added: string;
}

const Example: React.FC = () => {
  const [data, setData] = useState<IndustryData[]>([]);

  useEffect(() => {
    // Function to fetch data from the backend
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/top-industries'); // Assuming your FastAPI server runs on port 8000
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const jsonData = await response.json();
        setData(jsonData);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <div style={{ padding: '20px' }}>
      <h1>Top Industries in India - Data Visualization</h1>
      {data.length > 0 ? (
        <BarChart width={1000} height={500} data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="rank" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="fixed_capital" fill="#8884d8" name="Fixed Capital" />
          <Bar dataKey="total_persons_engaged" fill="#82ca9d" name="Total Persons Engaged" />
        </BarChart>
      ) : (
        <p>Loading data...</p>
      )}
    </div>
  );
};

export default Example;