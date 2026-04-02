import type { FC } from 'react';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChevronRight } from '@fortawesome/free-solid-svg-icons';
import React from 'react';

interface SummaryCardProps {
  title: string;
  description: string;
  icon: React.ReactElement;
  linkTo: string;
  linkLabel: string;
}

const SummaryCard: FC<SummaryCardProps> = ({ title, description, icon, linkTo, linkLabel }) => (
  <div className="bg-surface border border-input rounded-xl p-5 flex flex-col gap-4">
    <div className="flex items-start justify-between">
      <div>
        <h3 className="section-title">{title}</h3>
        <p className="text-secondary text-sm mt-1">{description}</p>
      </div>
      <div className="w-10 h-10 rounded-lg bg-input flex items-center justify-center text-accent shrink-0">
        {icon}
      </div>
    </div>
    <Link
      to={linkTo}
      className="inline-flex items-center gap-1.5 text-accent hover:text-success text-sm font-medium transition-colors"
    >
      {linkLabel}
      <FontAwesomeIcon icon={faChevronRight} size="xs" />
    </Link>
  </div>
);

SummaryCard.displayName = 'SummaryCard';

export default SummaryCard;
