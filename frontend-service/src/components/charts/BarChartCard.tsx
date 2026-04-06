import { type FC, memo } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from 'recharts';

interface BarChartCardProps {
  title: string;
  labels: string[];
  data: number[];
  color?: string;
}

interface TooltipPayload {
  value: number;
  name: string;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: TooltipPayload[];
  label?: string;
}

const MAX_LABEL_LENGTH = 15;

const truncateLabel = (label: string): string =>
  label.length > MAX_LABEL_LENGTH ? `${label.slice(0, MAX_LABEL_LENGTH)}…` : label;

const CustomTooltip: FC<CustomTooltipProps> = ({ active, payload, label }) => {
  if (!active || !payload || payload.length === 0) return null;
  const value = payload[0].value;
  const formatted = new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value);
  return (
    <div className="chart-tooltip">
      <p className="text-muted text-xs mb-1">{label}</p>
      <p className={`text-sm font-semibold ${value >= 0 ? 'text-success' : 'text-error'}`}>
        {formatted}
      </p>
    </div>
  );
};

const BarChartCard: FC<BarChartCardProps> = memo(({ title, labels, data }) => {
  const chartData = labels.map((label, index) => ({
    label: truncateLabel(label),
    fullLabel: label,
    value: data[index] ?? 0,
  }));

  const dynamicHeight = Math.max(300, chartData.length * 50);

  return (
    <div className="surface-card p-5 flex flex-col gap-4">
      <h3 className="section-title">{title}</h3>
      <div className="overflow-y-auto">
        <ResponsiveContainer width="100%" height={dynamicHeight}>
          <BarChart data={chartData} margin={{ top: 4, right: 8, left: 8, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" vertical={false} />
            <XAxis
              dataKey="label"
              tick={{ fill: 'var(--chart-axis)', fontSize: 11 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: 'var(--chart-axis)', fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v: number) =>
                new Intl.NumberFormat('pt-BR', { notation: 'compact', currency: 'BRL' }).format(v)
              }
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'var(--chart-cursor)' }} />
            <Bar dataKey="value" radius={[4, 4, 0, 0]} minPointSize={40}>
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.value >= 0 ? 'var(--chart-bar-positive)' : 'var(--chart-bar-negative)'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
});

BarChartCard.displayName = 'BarChartCard';

export default BarChartCard;
