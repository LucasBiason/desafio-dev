import type { FC } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faStore } from '@fortawesome/free-solid-svg-icons';
import Layout from '../components/Layout';

const Stores: FC = () => {
  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h2 className="text-[#FFFFFF] text-xl font-semibold">Lojas</h2>
          <p className="text-[#D8D8D8] text-sm mt-1">
            Visualize todas as lojas identificadas nos arquivos CNAB importados.
          </p>
        </div>

        <div className="bg-[#1e1e1e] border border-[#2a2a2a] rounded-xl p-8 flex flex-col items-center justify-center text-center min-h-48">
          <div className="w-14 h-14 rounded-xl bg-[#2a2a2a] flex items-center justify-center mb-4">
            <FontAwesomeIcon icon={faStore} size="xl" className="text-[#4FFA7B]" />
          </div>
          <p className="text-[#D8D8D8] font-medium">Nenhuma loja encontrada</p>
          <p className="text-[#D8D8D8] text-sm mt-1">Importe um arquivo CNAB para visualizar as lojas.</p>
        </div>
      </div>
    </Layout>
  );
};

export default Stores;
