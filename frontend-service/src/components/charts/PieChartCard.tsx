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

interface LabelProps {
  cx?: number;
  cy?: number;
  midAngle?: number;
  innerRadius?: number;
  outerRadius?: number;
  percent?: number;
  index?: number;
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

const renderLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }: LabelProps) => {
  if (
    cx == null ||
    cy == null ||
    midAngle == null ||
    innerRadius == null ||
    outerRadius == null ||
    percent == null
  ) {
    return null;
  }

  const RADIAN = Math.PI / 180;
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);

  if (percent < 0.05) return null;

  return (
    <text
      x={x}
      y={y}
      fill="white"
      textAnchor="middle"
      dominantBaseline="central"
      fontSize={11}
      fontWeight={600}
    >
      {`${(percent * 100).toFixed(0)}%`}
    </text>
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
        <div style={{ width: '60%' }} className="min-w-0 shrink-0">
          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius="45%"
                outerRadius="75%"
                paddingAngle={2}
                dataKey="value"
                labelLine={false}
                label={renderLabel}
              >
                {chartData.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={colors[index % colors.length]}
                  />
                ))}
              </Pie>
              <Tooltip
                content={<CustomTooltip />}
                isAnimationActive={false}
                wrapperStyle={{ pointerEvents: 'none' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div style={{ width: '40%' }} className="min-w-0 flex flex-col gap-1.5 overflow-y-auto max-h-[350px]">
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
