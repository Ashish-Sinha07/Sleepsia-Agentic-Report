export default function ChartCard({ title, children, subtitle }) {
  return (
    <div className="card">
      <div className="card-header">
        <h3 className="font-semibold text-gray-900">{title}</h3>
        {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
      </div>
      <div className="card-body">
        {children}
      </div>
    </div>
  );
}
