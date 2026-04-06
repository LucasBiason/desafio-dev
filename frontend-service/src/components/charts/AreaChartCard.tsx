import { type FC, memo } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

interface AreaChartCardProps {
  title: string;
  labels: string[];
  data: number[];
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
      <p className="text-accent text-sm font-semibold">
        {value} {value === 1 ? 'transação' : 'transações'}
      </p>
    </div>
  );
};

const AreaChartCard: FC<AreaChartCardProps> = memo(({ title, labels, data }) => {
  const chartData = labels.map((label, index) => ({
    label,
    value: data[index] ?? 0,
  }));

  return (
    <div className="surface-card p-5 flex flex-col gap-4">
      <h3 className="section-title">{title}</h3>
      <ResponsiveContainer width="100%" height={260}>
        <AreaChart data={chartData} margin={{ top: 4, right: 8, left: 8, bottom: 4 }}>
          <defs>
            <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="var(--chart-line)" stopOpacity={0.25} />
              <stop offset="95%" stopColor="var(--chart-line)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fill: 'var(--chart-axis)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            interval={2}
          />
          <YAxis
            tick={{ fill: 'var(--chart-axis)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            allowDecimals={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'var(--chart-cursor-line)' }} />
          <Area
            type="monotone"
            dataKey="value"
            stroke="var(--chart-line)"
            strokeWidth={2}
            fill="url(#areaGradient)"
            dot={false}
            activeDot={{ r: 5, fill: 'var(--chart-line)', stroke: 'var(--chart-line)' }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
});

AreaChartCard.displayName = 'AreaChartCard';

export default AreaChartCard;
