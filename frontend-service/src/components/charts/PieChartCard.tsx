import { type FC, memo } from 'react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
} from 'recharts';

interface PieChartCardProps {
  title: string;
  labels: string[];
  data: number[];
  colors: string[];
}

interface TooltipPayload {
  name: string;
  value: number;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: TooltipPayload[];
}

const CustomTooltip: FC<CustomTooltipProps> = ({ active, payload }) => {
  if (!active || !payload || payload.length === 0) return null;
  const item = payload[0];
  return (
    <div className="chart-tooltip">
      <p className="text-muted text-xs mb-1">{item.name}</p>
      <p className="text-primary text-sm font-semibold">{item.value} transações</p>
    </div>
  );
};

const PieChartCard: FC<PieChartCardProps> = memo(({ title, labels, data, colors }) => {
  const chartData = labels.map((label, index) => ({
    name: label,
    value: data[index] ?? 0,
  }));

  const total = chartData.reduce((sum, entry) => sum + entry.value, 0);

  return (
    <div className="surface-card p-5 flex flex-col gap-4">
      <h3 className="section-title">{title}</h3>
      <div className="flex items-center gap-4">
        <div className="w-1/2 min-w-0">
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius="55%"
                outerRadius="80%"
                paddingAngle={2}
                dataKey="value"
              >
                {chartData.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={colors[index % colors.length]}
                  />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="w-1/2 min-w-0 flex flex-col gap-1.5">
          {chartData.map((entry, index) => {
            const percentage = total > 0 ? ((entry.value / total) * 100).toFixed(1) : '0.0';
            const countStr = String(entry.value).padStart(2, ' ');
            return (
              <div key={index} className="flex items-center gap-2 text-xs">
                <span
                  className="w-2.5 h-2.5 rounded-full shrink-0"
                  style={{ backgroundColor: colors[index % colors.length] }}
                />
                <span className="text-secondary truncate flex-1">{entry.name}</span>
                <span className="text-muted whitespace-nowrap">
                  {countStr} ({percentage}%)
                </span>
              </div>
            );
          })}
          <div className="flex items-center gap-2 text-xs text-primary font-medium border-t border-surface pt-2 mt-2">
            <span>Total: {total}</span>
          </div>
        </div>
      </div>
    </div>
  );
});

PieChartCard.displayName = 'PieChartCard';

export default PieChartCard;
