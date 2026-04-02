import type { FC } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faClockRotateLeft } from '@fortawesome/free-solid-svg-icons';
import Layout from '../components/Layout';

const History: FC = () => {
  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h2 className="text-[#eceff4] text-xl font-semibold">Histórico</h2>
          <p className="text-[#d8dee9] text-sm mt-1">
            Consulte o histórico completo de transações processadas.
          </p>
        </div>

        <div className="bg-[#3b4252] border border-[#434c5e] rounded-xl p-8 flex flex-col items-center justify-center text-center min-h-48">
          <div className="w-14 h-14 rounded-xl bg-[#434c5e] flex items-center justify-center mb-4">
            <FontAwesomeIcon icon={faClockRotateLeft} size="xl" className="text-[#88c0d0]" />
          </div>
          <p className="text-[#d8dee9] font-medium">Nenhuma transação encontrada</p>
          <p className="text-[#d8dee9] text-sm mt-1">Importe um arquivo CNAB para visualizar o histórico.</p>
        </div>
      </div>
    </Layout>
  );
};

export default History;
