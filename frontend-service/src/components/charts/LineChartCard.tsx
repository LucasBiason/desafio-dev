import { type FC, memo } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Dot,
} from 'recharts';
import type { DotProps } from 'recharts';

interface LineChartCardProps {
  title: string;
  labels: string[];
  data: number[];
  color?: string;
}

interface TooltipPayload {
  value: number;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: TooltipPayload[];
  label?: string;
}

const CustomTooltip: FC<CustomTooltipProps> = ({ active, payload, label }) => {
  if (!active || !payload || payload.length === 0) return null;
  const value = payload[0].value;
  return (
    <div className="chart-tooltip">
      <p className="text-muted text-xs mb-1">{label}</p>
      <p className="text-accent text-sm font-semibold">{value} transações</p>
    </div>
  );
};

const CustomDot: FC<DotProps> = (props) => {
  const { cx, cy } = props;
  if (cx === undefined || cy === undefined) return null;
  return <Dot {...props} r={3} fill="var(--chart-line)" stroke="var(--chart-line)" />;
};

const LineChartCard: FC<LineChartCardProps> = memo(({ title, labels, data }) => {
  const chartData = labels.map((label, index) => ({
    label,
    value: data[index] ?? 0,
  }));

  return (
    <div className="surface-card p-5 flex flex-col gap-4">
      <h3 className="section-title">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData} margin={{ top: 4, right: 8, left: 8, bottom: 4 }}>
          <defs>
            <linearGradient id="lineGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="var(--chart-line)" stopOpacity={0.15} />
              <stop offset="95%" stopColor="var(--chart-line)" stopOpacity={0} />
            </linearGradient>
          </defs>
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
            allowDecimals={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'var(--chart-cursor-line)' }} isAnimationActive={false} />
          <Line
            type="monotone"
            dataKey="value"
            stroke="var(--chart-line)"
            strokeWidth={2}
            dot={<CustomDot />}
            activeDot={{ r: 5, fill: 'var(--chart-line)', stroke: 'var(--chart-line)' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
});

LineChartCard.displayName = 'LineChartCard';

export default LineChartCard;
