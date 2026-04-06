import React, { useState, useEffect, useCallback, useMemo } from 'react';
import type { FC } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faRotate,
  faArrowLeft,
  faMagnifyingGlass,
  faXmark,
} from '@fortawesome/free-solid-svg-icons';
import Layout from '../components/Layout';
import PageTitle from '../components/PageTitle';
import DataTable from '../components/DataTable';
import DateInput from '../components/DateInput';
import FilterChip from '../components/FilterChip';
import { cnabService } from '../services/cnabService';
import type { StoreResponse, TransactionResponse, TransactionTypeResponse } from '../types/cnab';
import type { Column } from '../components/DataTable';
import { formatCpf, formatCurrency, formatDate } from '../utils/formatters';

// ─── Nature badge ────────────────────────────────────────────────────────────

function NatureBadge({ nature }: { nature: string }): React.ReactElement {
  const isEntrada = nature.toLowerCase() === 'entrada';
  const badgeClass = isEntrada
    ? 'badge bg-success/10 text-success border border-success/20'
    : 'badge bg-error/10 text-error border border-error/20';
  const dotClass = isEntrada ? 'dot-completed' : 'dot-failed';
  return (
    <span className={badgeClass}>
      <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${dotClass}`} aria-hidden="true" />
      {isEntrada ? 'Entrada' : 'Saída'}
    </span>
  );
}

// ─── Store row type for DataTable ────────────────────────────────────────────

type StoreRow = StoreResponse & Record<string, unknown>;

// Flat transaction row: replaces nested transaction_type with flat fields
interface FlatTransactionRow extends Record<string, unknown> {
  id: string;
  type_description: string;
  type_nature: string;
  amount: string;
  card: string;
  occurred_at: string;
  occurred_time: string;
}

function flattenTransaction(t: TransactionResponse): FlatTransactionRow {
  return {
    id: t.id,
    type_description: t.transaction_type?.description ?? '',
    type_nature: t.transaction_type?.nature ?? '',
    amount: t.amount,
    card: t.card,
    occurred_at: t.occurred_at,
    occurred_time: t.occurred_time,
  };
}

// ─── Column definitions ──────────────────────────────────────────────────────

const storeColumns: Column<StoreRow>[] = [
  {
    key: 'name',
    label: 'Loja',
    sortable: true,
  },
  {
    key: 'owner_name',
    label: 'Dono',
    sortable: true,
  },
  {
    key: 'owner_cpf',
    label: 'CPF',
    sortable: false,
    render: (value) => formatCpf(String(value ?? '')),
  },
  {
    key: 'balance',
    label: 'Saldo',
    sortable: true,
    render: (value) => {
      const num = parseFloat(String(value ?? '0'));
      return (
        <span className={num >= 0 ? 'text-success' : 'text-error'}>
          {formatCurrency(String(value ?? '0'))}
        </span>
      );
    },
  },
  {
    key: 'total_income',
    label: 'Receitas',
    sortable: true,
    render: (value) => (
      <span className="text-success">{formatCurrency(String(value ?? '0'))}</span>
    ),
  },
  {
    key: 'total_expense',
    label: 'Despesas',
    sortable: true,
    render: (value) => (
      <span className="text-error">{formatCurrency(String(value ?? '0'))}</span>
    ),
  },
  {
    key: 'transaction_count',
    label: 'Transações',
    sortable: true,
  },
];

const transactionColumns: Column<FlatTransactionRow>[] = [
  {
    key: 'type_description',
    label: 'Tipo',
    sortable: true,
  },
  {
    key: 'type_nature',
    label: 'Natureza',
    sortable: false,
    render: (value) => <NatureBadge nature={String(value ?? '')} />,
  },
  {
    key: 'amount',
    label: 'Valor',
    sortable: true,
    render: (value) => formatCurrency(String(value ?? '0')),
  },
  {
    key: 'card',
    label: 'Cartão',
    sortable: false,
  },
  {
    key: 'occurred_at',
    label: 'Data',
    sortable: true,
    render: (value) => formatDate(String(value ?? '')),
  },
  {
    key: 'occurred_time',
    label: 'Hora',
    sortable: false,
  },
];

// ─── Nature filter options ───────────────────────────────────────────────────

const NATURE_OPTIONS = [
  {
    value: 'entrada',
    label: 'Entrada',
    colorClass: 'chip-completed',
    dotClass: 'dot-completed',
  },
  {
    value: 'saida',
    label: 'Saída',
    colorClass: 'chip-failed',
    dotClass: 'dot-failed',
  },
];

// ─── Main component ──────────────────────────────────────────────────────────

const Stores: FC = () => {
  // Store list state
  const [stores, setStores] = useState<StoreResponse[]>([]);
  const [storesLoading, setStoresLoading] = useState(true);
  const [nameInput, setNameInput] = useState('');
  const [ownerInput, setOwnerInput] = useState('');
  const [nameFilter, setNameFilter] = useState('');
  const [ownerFilter, setOwnerFilter] = useState('');

  // Selected store state
  const [selectedStore, setSelectedStore] = useState<StoreResponse | null>(null);

  // Transaction list state
  const [transactions, setTransactions] = useState<TransactionResponse[]>([]);
  const [transactionsLoading, setTransactionsLoading] = useState(false);

  // Transaction filters
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [selectedNatures, setSelectedNatures] = useState<string[]>([]);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [transactionTypes, setTransactionTypes] = useState<TransactionTypeResponse[]>([]);

  // Debounce name/owner filters
  useEffect(() => {
    const timer = setTimeout(() => setNameFilter(nameInput), 300);
    return () => clearTimeout(timer);
  }, [nameInput]);

  useEffect(() => {
    const timer = setTimeout(() => setOwnerFilter(ownerInput), 300);
    return () => clearTimeout(timer);
  }, [ownerInput]);

  // Load transaction types once
  useEffect(() => {
    cnabService
      .getTransactionTypes()
      .then(setTransactionTypes)
      .catch(() => setTransactionTypes([]));
  }, []);

  // Load stores
  const loadStores = useCallback(async (name: string, owner: string) => {
    try {
      setStoresLoading(true);
      const data = await cnabService.listStores({
        name: name || undefined,
        owner_name: owner || undefined,
      });
      setStores(data.results);
    } catch {
      setStores([]);
    } finally {
      setStoresLoading(false);
    }
  }, []);

  useEffect(() => {
    loadStores(nameFilter, ownerFilter);
  }, [nameFilter, ownerFilter, loadStores]);

  // Load transactions for selected store
  const loadTransactions = useCallback(
    async (
      storeId: string,
      types: string[],
      natures: string[],
      from: string,
      to: string,
    ) => {
      try {
        setTransactionsLoading(true);

        // Resolve type UUIDs to codes as CSV
        const typeCodes = types
          .map((id) => transactionTypes.find((tt) => tt.id === id)?.code)
          .filter((c): c is number => c !== undefined);

        // Nature: if only one selected, send it; if both or none, send nothing
        let natureParam: string | undefined;
        if (natures.length === 1) {
          natureParam = natures[0];
        }

        const data = await cnabService.getStoreTransactions(storeId, {
          type_codes: typeCodes.length > 0 ? typeCodes.join(',') : undefined,
          nature: natureParam,
          date_from: from || undefined,
          date_to: to || undefined,
        });
        setTransactions(data.results);
      } catch {
        setTransactions([]);
      } finally {
        setTransactionsLoading(false);
      }
    },
    [transactionTypes],
  );

  useEffect(() => {
    if (!selectedStore) return;
    loadTransactions(selectedStore.id, selectedTypes, selectedNatures, dateFrom, dateTo);
  }, [selectedStore, selectedTypes, selectedNatures, dateFrom, dateTo, loadTransactions]);

  // Row click handler
  const handleStoreRowClick = useCallback(
    (row: StoreRow) => {
      const store = stores.find((s) => s.id === row.id);
      if (!store) return;
      setSelectedStore(store);
      setSelectedTypes([]);
      setSelectedNatures([]);
      setDateFrom('');
      setDateTo('');
      setTransactions([]);
    },
    [stores],
  );

  const handleBack = () => {
    setSelectedStore(null);
    setTransactions([]);
  };

  const handleTypeToggle = (typeId: string) => {
    setSelectedTypes((prev) =>
      prev.includes(typeId) ? prev.filter((t) => t !== typeId) : [...prev, typeId],
    );
  };

  const handleNatureToggle = (value: string) => {
    setSelectedNatures((prev) =>
      prev.includes(value) ? prev.filter((n) => n !== value) : [...prev, value],
    );
  };

  const handleClearTypeFilters = () => {
    setSelectedTypes([]);
    setSelectedNatures([]);
  };

  // Prepare store rows with click support via rowKey
  const storeRows = useMemo(() => stores as StoreRow[], [stores]);
  const transactionRows = useMemo(
    () => transactions.map(flattenTransaction),
    [transactions],
  );

  // Build unique transaction type chips — key by id, use description as label
  const typeChips = useMemo(
    () =>
      transactionTypes.map((tt) => ({
        id: tt.id,
        label: tt.description,
        colorClass: 'chip-processing',
        dotClass: 'dot-processing',
      })),
    [transactionTypes],
  );

  const hasTypeFilters = selectedTypes.length > 0 || selectedNatures.length > 0;

  return (
    <Layout>
      <div className="space-y-6">
        <PageTitle
          title="Lojas Importadas"
          subtitle="Consulte lojas e transações importadas dos arquivos CNAB."
        />

        {/* Store list filters */}
        <div className="surface-card p-4 flex flex-wrap gap-4 items-end">
          <div>
            <label className="text-muted text-xs block mb-1" htmlFor="store-name-input">
              Nome da loja
            </label>
            <div className="relative">
              <FontAwesomeIcon
                icon={faMagnifyingGlass}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-muted text-xs pointer-events-none"
                aria-hidden="true"
              />
              <input
                id="store-name-input"
                type="text"
                value={nameInput}
                onChange={(e) => setNameInput(e.target.value)}
                placeholder="Nome da loja..."
                className="filter-input rounded-lg pl-8 pr-3 py-2 text-sm"
                aria-label="Filtrar por nome da loja"
              />
            </div>
          </div>

          <div>
            <label className="text-muted text-xs block mb-1" htmlFor="store-owner-input">
              Nome do dono
            </label>
            <div className="relative">
              <FontAwesomeIcon
                icon={faMagnifyingGlass}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-muted text-xs pointer-events-none"
                aria-hidden="true"
              />
              <input
                id="store-owner-input"
                type="text"
                value={ownerInput}
                onChange={(e) => setOwnerInput(e.target.value)}
                placeholder="Nome do dono..."
                className="filter-input rounded-lg pl-8 pr-3 py-2 text-sm"
                aria-label="Filtrar por nome do dono"
              />
            </div>
          </div>

          <button
            type="button"
            onClick={() => loadStores(nameFilter, ownerFilter)}
            className="btn-reload inline-flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-lg transition-all shrink-0"
            aria-label="Recarregar lista de lojas"
          >
            <FontAwesomeIcon icon={faRotate} aria-hidden="true" />
            Recarregar
          </button>
        </div>

        {/* Store DataTable */}
        <div>
          <DataTable<StoreRow>
            data={storeRows}
            columns={storeColumns}
            loading={storesLoading}
            defaultSortKey="name"
            defaultSortDir="asc"
            rowKey={(row) => row.id}
            emptyMessage="Nenhuma loja encontrada para os filtros informados."
            onRowClick={handleStoreRowClick}
            selectedRowKey={selectedStore?.id}
          />
        </div>

        {/* Store detail section */}
        {selectedStore && (
          <div className="space-y-4">
            {/* Detail header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <h3 className="section-title">
                Transações de{' '}
                <span className="text-accent">{selectedStore.name}</span>
              </h3>
              <button
                type="button"
                onClick={handleBack}
                className="btn-reload inline-flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-lg transition-all shrink-0 self-start sm:self-auto"
                aria-label="Voltar para lista de lojas"
              >
                <FontAwesomeIcon icon={faArrowLeft} aria-hidden="true" />
                Voltar
              </button>
            </div>

            {/* Transaction filters */}
            <div className="surface-card p-4 space-y-4">
              {typeChips.length > 0 && (
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-muted mb-2">Tipo de Transação</p>
                  <div className="flex flex-wrap gap-2 items-center">
                    {typeChips.map((chip) => (
                      <FilterChip
                        key={chip.id}
                        label={chip.label}
                        colorClass={chip.colorClass}
                        dotClass={chip.dotClass}
                        active={selectedTypes.includes(chip.id)}
                        onClick={() => handleTypeToggle(chip.id)}
                      />
                    ))}
                    {hasTypeFilters && (
                      <button
                        type="button"
                        onClick={handleClearTypeFilters}
                        className="inline-flex items-center gap-1 px-2 py-1 text-xs text-muted hover:text-primary rounded-lg transition-colors"
                        aria-label="Limpar filtros de tipo e natureza"
                      >
                        <FontAwesomeIcon icon={faXmark} aria-hidden="true" />
                        Limpar
                      </button>
                    )}
                  </div>
                </div>
              )}

              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-muted mb-2">Natureza</p>
                <div className="flex flex-wrap gap-2 items-center">
                  {NATURE_OPTIONS.map((opt) => (
                    <FilterChip
                      key={opt.value}
                      label={opt.label}
                      colorClass={opt.colorClass}
                      dotClass={opt.dotClass}
                      active={selectedNatures.includes(opt.value)}
                      onClick={() => handleNatureToggle(opt.value)}
                    />
                  ))}
                </div>
              </div>

              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-muted mb-2">Período</p>
                <div className="flex flex-col sm:flex-row gap-3">
                  <DateInput value={dateFrom} onChange={setDateFrom} label="De" />
                  <DateInput value={dateTo} onChange={setDateTo} label="Até" />
                </div>
              </div>
            </div>

            {/* Transactions DataTable */}
            <DataTable<FlatTransactionRow>
              data={transactionRows}
              columns={transactionColumns}
              loading={transactionsLoading}
              defaultSortKey="occurred_at"
              defaultSortDir="desc"
              rowKey={(row) => row.id}
              emptyMessage="Nenhuma transação encontrada para os filtros selecionados."
            />
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Stores;
