import type { FC } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCloudArrowUp, faStore, faMoneyBillTransfer } from '@fortawesome/free-solid-svg-icons';
import Layout from '../components/Layout';
import PageTitle from '../components/PageTitle';
import SummaryCard from '../components/SummaryCard';

const Dashboard: FC = () => {
  return (
    <Layout>
      <div className="space-y-6">
        <PageTitle
          title="Bem-vindo ao CNAB Parser"
          subtitle="Gerencie seus arquivos CNAB e acompanhe as transações das suas lojas."
        />

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
            linkTo="/upload"
            linkLabel="Ver uploads"
          />
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
