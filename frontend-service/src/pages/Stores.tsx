import type { FC } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faStore } from '@fortawesome/free-solid-svg-icons';
import Layout from '../components/Layout';

const Stores: FC = () => {
  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h2 className="text-[#eceff4] text-xl font-semibold">Lojas</h2>
          <p className="text-[#d8dee9] text-sm mt-1">
            Visualize todas as lojas identificadas nos arquivos CNAB importados.
          </p>
        </div>

        <div className="bg-[#3b4252] border border-[#434c5e] rounded-xl p-8 flex flex-col items-center justify-center text-center min-h-48">
          <div className="w-14 h-14 rounded-xl bg-[#434c5e] flex items-center justify-center mb-4">
            <FontAwesomeIcon icon={faStore} size="xl" className="text-[#88c0d0]" />
          </div>
          <p className="text-[#d8dee9] font-medium">Nenhuma loja encontrada</p>
          <p className="text-[#d8dee9] text-sm mt-1">Importe um arquivo CNAB para visualizar as lojas.</p>
        </div>
      </div>
    </Layout>
  );
};

export default Stores;
