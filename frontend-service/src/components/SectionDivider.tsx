import type { FC } from 'react';

interface SectionDividerProps {
  label: string;
}

const SectionDivider: FC<SectionDividerProps> = ({ label }) => (
  <div className="flex items-center gap-3 mt-8 mb-4">
    <div className="h-px flex-1 border-surface border-t" />
    <span className="text-muted text-xs font-semibold uppercase tracking-wider">{label}</span>
    <div className="h-px flex-1 border-surface border-t" />
  </div>
);

export default SectionDivider;
