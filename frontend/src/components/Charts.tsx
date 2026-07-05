import React from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444'];

interface ChartData {
  name: string;
  value: number;
}

export const StatCard = ({
  title,
  value,
  trend,
  icon: Icon,
  color,
}: {
  title: string;
  value: number | string;
  trend?: number;
  icon: React.ComponentType<{ className: string }>;
  color: string;
}) => (
  <div className="glass p-6 rounded-xl">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-gray-300 text-sm font-medium">{title}</p>
        <p className="text-3xl font-bold mt-2">{value}</p>
        {trend !== undefined && (
          <p className={`text-sm mt-2 ${trend >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}%
          </p>
        )}
      </div>
      <div className={`p-3 rounded-lg ${color}`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
    </div>
  </div>
);

export const SimpleBarChart = ({ data, title }: { data: any; title: string }) => (
  <div className="glass p-6 rounded-xl">
    <h3 className="text-lg font-semibold mb-4">{title}</h3>
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis stroke="#9CA3AF" />
        <YAxis stroke="#9CA3AF" />
        <Tooltip />
        <Legend />
        <Bar dataKey="value" fill="#3B82F6" />
      </BarChart>
    </ResponsiveContainer>
  </div>
);

export const SimpleLineChart = ({ data, title }: { data: any; title: string }) => (
  <div className="glass p-6 rounded-xl">
    <h3 className="text-lg font-semibold mb-4">{title}</h3>
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis stroke="#9CA3AF" />
        <YAxis stroke="#9CA3AF" />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="value" stroke="#10B981" />
      </LineChart>
    </ResponsiveContainer>
  </div>
);

export const SimplePieChart = ({ data, title }: { data: any; title: string }) => (
  <div className="glass p-6 rounded-xl">
    <h3 className="text-lg font-semibold mb-4">{title}</h3>
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie data={data} cx="50%" cy="50%" labelLine={false} label outerRadius={80} fill="#8884d8" dataKey="value">
          {data.map((entry: any, index: number) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  </div>
);
