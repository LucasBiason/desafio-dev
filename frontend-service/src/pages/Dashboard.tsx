import { type FC, useCallback, useEffect, useMemo, useState } from 'react';
import {
  faScaleBalanced,
  faChartLine,
  faLayerGroup,
  faTriangleExclamation,
} from '@fortawesome/free-solid-svg-icons';
import Layout from '../components/Layout';
import DateInput from '../components/DateInput';
import PageTitle from '../components/PageTitle';
import { formatCurrency, formatDateTime } from '../utils/formatters';
import StatCard from '../components/charts/StatCard';
import BarChartCard from '../components/charts/BarChartCard';
import PieChartCard from '../components/charts/PieChartCard';
import AreaChartCard from '../components/charts/AreaChartCard';
import DataTable, { type Column } from '../components/DataTable';
import {
  dashboardService,
  type AdvancedKPIs,
  type ChartData,
  type DashboardFilters,
  type AvailableFilters,
  type TransactionDetail,
} from '../services/dashboardService';

type NatureFilter = 'todas' | 'entrada' | 'saida';

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

interface NatureToggleProps {
  value: NatureFilter;
  onChange: (value: NatureFilter) => void;
}

const NATURE_OPTIONS: { value: NatureFilter; label: string }[] = [
  { value: 'todas', label: 'Todas' },
  { value: 'entrada', label: 'Entradas' },
  { value: 'saida', label: 'Saídas' },
];

const NatureToggle: FC<NatureToggleProps> = ({ value, onChange }) => (
  <div className="flex items-center gap-1 surface-card p-1">
    {NATURE_OPTIONS.map((option) => (
      <button
        key={option.value}
        type="button"
        onClick={() => onChange(option.value)}
        className={[
          'px-3 py-1 rounded text-xs font-medium transition-colors',
          value === option.value
            ? 'bg-accent/20 text-accent'
            : 'text-muted hover:text-secondary',
        ].join(' ')}
        aria-pressed={value === option.value}
      >
        {option.label}
      </button>
    ))}
  </div>
);

interface DashboardData {
  kpis: AdvancedKPIs;
  balanceByStore: ChartData;
  transactionsByType: ChartData;
  hourly: ChartData;
}

const DETAIL_PAGE_SIZE = 20;

const TRANSACTION_COLUMNS: Column<TransactionDetail>[] = [
  {
    key: 'occurred_at',
    label: 'Data/Hora',
    sortable: true,
    render: (value) => (
      <span className="whitespace-nowrap font-mono text-xs">
        {formatDateTime(String(value ?? ''))}
      </span>
    ),
  },
  {
    key: 'store_name',
    label: 'Loja',
    sortable: true,
  },
  {
    key: 'type_description',
    label: 'Tipo',
    sortable: true,
  },
  {
    key: 'nature',
    label: 'Natureza',
    sortable: false,
    render: (value) => {
      const nature = String(value ?? '').toLowerCase();
      const isEntrada = nature === 'entrada';
      return (
        <span
          className={[
            'badge',
            isEntrada ? 'badge-completed' : 'badge-failed',
          ].join(' ')}
        >
          {isEntrada ? 'Entrada' : 'Saída'}
        </span>
      );
    },
  },
  {
    key: 'amount',
    label: 'Valor',
    sortable: true,
    render: (value, row) => {
      const isEntrada = String(row.nature ?? '').toLowerCase() === 'entrada';
      return (
        <span className={isEntrada ? 'text-success font-medium' : 'text-error font-medium'}>
          {formatCurrency(String(value ?? '0'))}
        </span>
      );
    },
  },
  {
    key: 'card',
    label: 'Cartão',
    sortable: false,
    render: (value) => (
      <span className="font-mono text-xs text-muted">{String(value ?? '')}</span>
    ),
  },
  {
    key: 'owner_name',
    label: 'Dono',
    sortable: true,
  },
];

const Dashboard: FC = () => {
  const [availableFilters, setAvailableFilters] = useState<AvailableFilters | null>(null);
  const [filtersLoading, setFiltersLoading] = useState(true);

  const [selectedStore, setSelectedStore] = useState<string>('');
  const [selectedOwner, setSelectedOwner] = useState<string>('');
  const [dateFrom, setDateFrom] = useState<string>('');
  const [dateTo, setDateTo] = useState<string>('');
  const [natureFilter, setNatureFilter] = useState<NatureFilter>('todas');

  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [detailRows, setDetailRows] = useState<TransactionDetail[]>([]);
  const [detailCount, setDetailCount] = useState(0);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailOrdering, setDetailOrdering] = useState<string>('-occurred_at');

  const currentParams = useMemo<DashboardFilters>(() => ({
    store_id: selectedStore || undefined,
    owner_name: selectedOwner || undefined,
    date_from: dateFrom || undefined,
    date_to: dateTo || undefined,
  }), [selectedStore, selectedOwner, dateFrom, dateTo]);

  useEffect(() => {
    let cancelled = false;

    const loadFilters = async () => {
      try {
        const filters = await dashboardService.getAvailableFilters();
        if (!cancelled) {
          setAvailableFilters(filters);
          setDateFrom(filters.date_range.min_date);
          setDateTo(filters.date_range.max_date);
        }
      } catch {
        if (!cancelled) {
          setAvailableFilters({
            stores: [],
            owners: [],
            date_range: { min_date: '', max_date: '' },
          });
        }
      } finally {
        if (!cancelled) {
          setFiltersLoading(false);
        }
      }
    };

    loadFilters();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (filtersLoading) return;

    let cancelled = false;

    const loadCharts = async () => {
      setLoading(true);
      setError(null);
      try {
        const [kpis, balanceByStore, transactionsByType, hourly] = await Promise.all([
          dashboardService.getAdvancedKpis(currentParams),
          dashboardService.getBalanceByStore(currentParams),
          dashboardService.getTransactionsByType(currentParams),
          dashboardService.getTransactionsByHour(currentParams),
        ]);

        if (!cancelled) {
          setData({ kpis, balanceByStore, transactionsByType, hourly });
        }
      } catch {
        if (!cancelled) {
          setError('Não foi possível carregar os dados do dashboard.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadCharts();

    return () => {
      cancelled = true;
    };
  }, [filtersLoading, currentParams]);

  useEffect(() => {
    if (filtersLoading) return;

    let cancelled = false;
    const natureParam = natureFilter === 'todas' ? undefined : natureFilter;

    const loadDetail = async () => {
      setDetailLoading(true);
      try {
        const detail = await dashboardService.getTransactionsDetail(1, DETAIL_PAGE_SIZE, currentParams, natureParam, detailOrdering);
        if (!cancelled) {
          setDetailRows(detail.results);
          setDetailCount(detail.count);
        }
      } catch {
        if (!cancelled) {
          setDetailRows([]);
          setDetailCount(0);
        }
      } finally {
        if (!cancelled) {
          setDetailLoading(false);
        }
      }
    };

    loadDetail();

    return () => {
      cancelled = true;
    };
  }, [filtersLoading, currentParams, natureFilter, detailOrdering]);

  const handleDetailPageChange = useCallback(async (page: number, pageSize: number) => {
    const natureParam = natureFilter === 'todas' ? undefined : natureFilter;
    setDetailLoading(true);
    try {
      const result = await dashboardService.getTransactionsDetail(page, pageSize, currentParams, natureParam, detailOrdering);
      setDetailRows(result.results);
      setDetailCount(result.count);
    } catch {
      // Keep existing rows on error
    } finally {
      setDetailLoading(false);
    }
  }, [currentParams, natureFilter, detailOrdering]);

  const handleDetailSortChange = useCallback((key: string, dir: 'asc' | 'desc') => {
    const ordering = dir === 'desc' ? `-${key}` : key;
    setDetailOrdering(ordering);
  }, []);

  const cashFlowVariant = (value: string): 'success' | 'error' => {
    return parseFloat(value) >= 0 ? 'success' : 'error';
  };

  const isEmpty =
    !loading &&
    data !== null &&
    data.kpis.total_transactions === 0;

  return (
    <Layout>
      <div className="space-y-2">
        <PageTitle
          title="Dashboard de Conciliação Bancária"
          subtitle="Visão geral das transações importadas e saúde financeira por unidade."
        />

        {/* Filters */}
        <div className="surface-card p-4 flex flex-wrap gap-4 items-end">
          <div>
            <label className="text-muted text-xs block mb-1">Loja</label>
            <select
              className="filter-input rounded-lg px-3 py-1.5 text-sm [color-scheme:dark]"
              value={selectedStore}
              onChange={(e) => setSelectedStore(e.target.value)}
              disabled={filtersLoading}
            >
              <option value="">Todas</option>
              {availableFilters?.stores.map((store) => (
                <option key={store.id} value={store.id}>
                  {store.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-muted text-xs block mb-1">Representante</label>
            <select
              className="filter-input rounded-lg px-3 py-1.5 text-sm [color-scheme:dark]"
              value={selectedOwner}
              onChange={(e) => setSelectedOwner(e.target.value)}
              disabled={filtersLoading}
            >
              <option value="">Todos</option>
              {availableFilters?.owners.map((owner) => (
                <option key={owner} value={owner}>
                  {owner}
                </option>
              ))}
            </select>
          </div>

          <DateInput value={dateFrom} onChange={setDateFrom} label="Período de" disabled={filtersLoading} />
          <DateInput value={dateTo} onChange={setDateTo} label="até" disabled={filtersLoading} />

        </div>

        {error && (
          <div className="alert-error rounded-xl p-4 text-sm">{error}</div>
        )}

        {loading ? (
          <>
            <SectionDivider label="O Panorama" />
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="skeleton-stat" />
              ))}
            </div>

            <SectionDivider label="O Desempenho" />
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
              <div className="skeleton-chart" style={{ height: 380 }} />
              <div className="skeleton-chart" style={{ height: 380 }} />
            </div>

            <SectionDivider label="A Operação" />
            <div className="skeleton-chart" style={{ height: 300 }} />
            <div className="skeleton-chart" style={{ height: 380 }} />
          </>
        ) : isEmpty ? (
          <div className="surface-card p-10 flex flex-col items-center justify-center gap-3 text-center">
            <p className="text-muted text-sm">
              Nenhum dado importado. Faça upload de um arquivo CNAB para visualizar o dashboard.
            </p>
          </div>
        ) : data ? (
          <>
            {/* 1. O PANORAMA */}
            <SectionDivider label="O Panorama" />
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard
                title="Fluxo de Caixa Líquido"
                value={formatCurrency(data.kpis.cash_flow)}
                subtitle="Saldo consolidado"
                tooltip="Soma de todas as entradas menos todas as saídas no período selecionado."
                icon={faScaleBalanced}
                variant={cashFlowVariant(data.kpis.cash_flow)}
              />
              <StatCard
                title="Eficiência de Vendas"
                value={formatCurrency(data.kpis.avg_ticket)}
                subtitle="Ticket médio geral"
                tooltip="Valor médio das transações de entrada (créditos, recebimentos, vendas)."
                icon={faChartLine}
                variant="default"
              />
              <StatCard
                title="Volume Operacional"
                value={data.kpis.total_transactions}
                subtitle="Total de ocorrências"
                tooltip="Quantidade total de transações (entradas + saídas) no período."
                icon={faLayerGroup}
                variant="default"
              />
              <StatCard
                title="Ponto de Atenção"
                value={
                  data.kpis.max_expense
                    ? formatCurrency(data.kpis.max_expense.amount)
                    : '—'
                }
                subtitle={
                  data.kpis.max_expense
                    ? `${data.kpis.max_expense.type_description} — ${data.kpis.max_expense.store_name}`
                    : 'Maior despesa'
                }
                tooltip="Maior transação individual de saída (débito, boleto, financiamento, etc.) no período."
                icon={faTriangleExclamation}
                variant="warning"
              />
            </div>

            {/* 2. O DESEMPENHO */}
            <SectionDivider label="O Desempenho" />
            <div className="grid grid-cols-1 xl:grid-cols-5 gap-4">
              <div className="xl:col-span-2">
                <BarChartCard
                  title="Saldo por Unidade"
                  labels={data.balanceByStore.labels}
                  data={data.balanceByStore.data}
                />
              </div>
              <div className="xl:col-span-3">
                <PieChartCard
                  title="Composição de Gastos"
                  labels={data.transactionsByType.labels}
                  data={data.transactionsByType.data}
                  colors={data.transactionsByType.colors ?? []}
                />
              </div>
            </div>

            {/* 3. A OPERAÇÃO */}
            <SectionDivider label="A Operação" />
            <AreaChartCard
              title="Densidade de Transações por Hora"
              labels={data.hourly.labels}
              data={data.hourly.data}
            />

            <div className="surface-card overflow-hidden">
              <div className="px-5 pt-5 pb-3 flex items-center justify-between gap-4">
                <h3 className="section-title">Detalhamento de Transações</h3>
                <div className="flex items-center gap-3">
                  <NatureToggle value={natureFilter} onChange={setNatureFilter} />
                  <span className="text-muted text-xs">
                    {detailCount} registro{detailCount !== 1 ? 's' : ''} no total
                  </span>
                </div>
              </div>
              <DataTable<TransactionDetail>
                data={detailRows}
                columns={TRANSACTION_COLUMNS}
                rowKey={(row) => row.id}
                defaultSortKey="occurred_at"
                defaultSortDir="desc"
                pageSizeOptions={[10, 20, 50]}
                loading={detailLoading}
                totalCount={detailCount}
                onPageChange={handleDetailPageChange}
                onSortChange={handleDetailSortChange}
              />
            </div>
          </>
        ) : null}
      </div>
    </Layout>
  );
};

export default Dashboard;
