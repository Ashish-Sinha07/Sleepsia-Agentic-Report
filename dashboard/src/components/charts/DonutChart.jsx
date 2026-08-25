import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from 'recharts';
import { formatCurrency } from '../../utils/formatting';

// Two genuinely distinct categories (not degrees of the same thing), so two
// different hues rather than two tints of one - easier to tell apart at a glance.
const COLORS = ['#2a78d6', '#eda100'];

function CustomTooltip({ active, payload, total }) {
  if (active && payload && payload.length) {
    const percentage = ((payload[0].value / total) * 100).toFixed(1);
    return (
      <div className="bg-white p-3 border border-gray-300 rounded-lg shadow-lg">
        <p className="text-sm font-medium text-gray-900">{payload[0].name}</p>
        <p className="text-sm text-gray-700">{formatCurrency(payload[0].value)}</p>
        <p className="text-sm text-gray-600">{percentage}%</p>
      </div>
    );
  }
  return null;
}

export default function DonutChart({ data }) {
  const total = data.reduce((sum, item) => sum + item.value, 0);

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={80}
          outerRadius={120}
          paddingAngle={2}
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip total={total} />} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}
