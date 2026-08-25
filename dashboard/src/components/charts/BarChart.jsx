import { BarChart as RechartBarChart, Bar, Cell, CartesianGrid, XAxis, YAxis, Tooltip, Legend, LabelList, ResponsiveContainer } from 'recharts';
import { formatCurrency } from '../../utils/formatting';

function CustomTooltip({ active, payload, colorFor, color }) {
  if (active && payload && payload.length) {
    const entry = payload[0].payload;
    const swatch = colorFor ? colorFor(entry) : color || payload[0].color;
    return (
      <div className="bg-white p-3 border border-gray-300 rounded-lg shadow-lg">
        <p className="text-sm font-medium text-gray-900">{entry.name || entry.platform}</p>
        <p className="text-sm" style={{ color: swatch }}>
          {payload[0].name}: {formatCurrency(payload[0].value)}
        </p>
      </div>
    );
  }
  return null;
}

export default function BarChart({ data, dataKey, name, color = '#4a9fbd', colorFor, horizontal = false, height = 400, showValueLabels = false }) {
  // Hover highlight: a subtle dark ring on the active bar, so charts feel
  // responsive to the pointer even without a click action attached yet.
  const activeBar = { stroke: '#1f2d3d', strokeWidth: 1.5, fillOpacity: 0.9 };

  const cells = colorFor
    ? data.map((entry, index) => <Cell key={`cell-${index}`} fill={colorFor(entry)} />)
    : null;

  if (horizontal) {
    return (
      <ResponsiveContainer width="100%" height={height}>
        <RechartBarChart
          data={data}
          layout="vertical"
          margin={{ top: 10, right: showValueLabels ? 60 : 20, left: 10, bottom: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" horizontal={false} />
          <XAxis type="number" stroke="#9ca3af" style={{ fontSize: '12px' }} />
          <YAxis dataKey="name" type="category" stroke="#9ca3af" style={{ fontSize: '12px' }} width={180} interval={0} />
          <Tooltip content={<CustomTooltip colorFor={colorFor} color={color} />} cursor={{ fill: '#f2f4f7' }} />
          <Bar dataKey={dataKey} fill={color} name={name} radius={[0, 4, 4, 0]} maxBarSize={28} activeBar={activeBar}>
            {cells}
            {showValueLabels && (
              <LabelList
                dataKey={dataKey}
                position="right"
                formatter={formatCurrency}
                fill="#6b7280"
                fontSize={12}
              />
            )}
          </Bar>
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
        <Tooltip content={<CustomTooltip />} cursor={{ fill: '#f2f4f7' }} />
        {!colorFor && <Legend />}
        <Bar dataKey={dataKey} fill={color} name={name} radius={[8, 8, 0, 0]} activeBar={activeBar}>
          {cells}
        </Bar>
      </RechartBarChart>
    </ResponsiveContainer>
  );
}
