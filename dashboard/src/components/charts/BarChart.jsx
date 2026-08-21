import { BarChart as RechartBarChart, Bar, CartesianGrid, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { formatCurrency } from '../../utils/formatting';

function CustomTooltip({ active, payload }) {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 border border-gray-300 rounded-lg shadow-lg">
        <p className="text-sm font-medium text-gray-900">{payload[0].payload.name || payload[0].payload.platform}</p>
        <p className="text-sm" style={{ color: payload[0].color }}>
          {payload[0].name}: {formatCurrency(payload[0].value)}
        </p>
      </div>
    );
  }
  return null;
}

export default function BarChart({ data, dataKey, name, color = '#4a9fbd', horizontal = false }) {
  if (horizontal) {
    return (
      <ResponsiveContainer width="100%" height={400}>
        <RechartBarChart data={data} layout="vertical" margin={{ top: 10, right: 30, left: 200, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis type="number" stroke="#9ca3af" style={{ fontSize: '12px' }} />
          <YAxis dataKey="name" type="category" stroke="#9ca3af" style={{ fontSize: '12px' }} width={180} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey={dataKey} fill={color} name={name} radius={[0, 8, 8, 0]} />
        </RechartBarChart>
      </ResponsiveContainer>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RechartBarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey="name" stroke="#9ca3af" style={{ fontSize: '12px' }} />
        <YAxis stroke="#9ca3af" style={{ fontSize: '12px' }} />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        <Bar dataKey={dataKey} fill={color} name={name} radius={[8, 8, 0, 0]} />
      </RechartBarChart>
    </ResponsiveContainer>
  );
}
