import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { HealthCheck } from '../types';

interface LatencyChartProps {
  data: HealthCheck[];
}

export function LatencyChart({ data }: LatencyChartProps) {
  // Map data for Recharts, taking only checks that completed (latency !== null)
  const chartData = data
    .filter(d => d.latency_ms !== null)
    .map(d => ({
      time: new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      latency: d.latency_ms
    }));

  if (chartData.length === 0) {
    return (
      <div className="chart-container flex-center text-muted">
        No latency data available for the selected period.
      </div>
    );
  }

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis 
            dataKey="time" 
            stroke="#94a3b8" 
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          <YAxis 
            stroke="#94a3b8" 
            fontSize={12}
            tickLine={false}
            axisLine={false}
            tickFormatter={(value) => `${value}ms`}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1a1d24', borderColor: '#334155', color: '#f8fafc' }}
            itemStyle={{ color: '#3b82f6' }}
            cursor={{ stroke: '#475569', strokeWidth: 1 }}
          />
          <Line 
            type="monotone" 
            dataKey="latency" 
            stroke="#3b82f6" 
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: '#3b82f6', stroke: '#1a1d24', strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
