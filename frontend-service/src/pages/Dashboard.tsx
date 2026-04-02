import React from 'react';
import type { FC } from 'react';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCloudArrowUp, faStore, faMoneyBillTransfer, faChevronRight } from '@fortawesome/free-solid-svg-icons';
import Layout from '../components/Layout';

interface SummaryCardProps {
  title: string;
  description: string;
  icon: React.ReactElement;
  linkTo: string;
  linkLabel: string;
}

const SummaryCard: FC<SummaryCardProps> = ({ title, description, icon, linkTo, linkLabel }) => (
  <div className="bg-[#3b4252] border border-[#434c5e] rounded-xl p-5 flex flex-col gap-4">
    <div className="flex items-start justify-between">
      <div>
        <h3 className="text-[#eceff4] text-base font-semibold">{title}</h3>
        <p className="text-[#d8dee9] text-sm mt-1">{description}</p>
      </div>
      <div className="w-10 h-10 rounded-lg bg-[#434c5e] flex items-center justify-center text-[#88c0d0] shrink-0">
        {icon}
      </div>
    </div>
    <Link
      to={linkTo}
      className="inline-flex items-center gap-1.5 text-[#88c0d0] hover:text-[#81a1c1] text-sm font-medium transition-colors"
    >
      {linkLabel}
      <FontAwesomeIcon icon={faChevronRight} size="xs" />
    </Link>
  </div>
);

const Dashboard: FC = () => {
  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h2 className="text-[#eceff4] text-xl font-semibold">Bem-vindo ao CNAB Parser</h2>
          <p className="text-[#d8dee9] text-sm mt-1">
            Gerencie seus arquivos CNAB e acompanhe as transações das suas lojas.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          <SummaryCard
            title="Upload de Arquivo"
            description="Importe arquivos CNAB 240 ou 400 para processar transações."
            icon={<FontAwesomeIcon icon={faCloudArrowUp} size="lg" />}
            linkTo="/upload"
            linkLabel="Ir para upload"
          />
          <SummaryCard
            title="Lojas Importadas"
            description="Visualize todas as lojas identificadas nos arquivos importados."
            icon={<FontAwesomeIcon icon={faStore} size="lg" />}
            linkTo="/stores"
            linkLabel="Ver lojas"
          />
          <SummaryCard
            title="Total de Transações"
            description="Consulte o histórico completo de transações processadas."
            icon={<FontAwesomeIcon icon={faMoneyBillTransfer} size="lg" />}
            linkTo="/history"
            linkLabel="Ver histórico"
          />
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
