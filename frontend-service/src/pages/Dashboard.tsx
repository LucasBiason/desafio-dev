import { type FC, useEffect, useState } from 'react';
import {
  faStore,
  faMoneyBillTransfer,
  faArrowTrendUp,
  faArrowTrendDown,
  faScaleBalanced,
} from '@fortawesome/free-solid-svg-icons';
import Layout from '../components/Layout';
import PageTitle from '../components/PageTitle';
import StatCard from '../components/charts/StatCard';
import BarChartCard from '../components/charts/BarChartCard';
import PieChartCard from '../components/charts/PieChartCard';
import LineChartCard from '../components/charts/LineChartCard';
import {
  dashboardService,
  type DashboardSummary,
  type ChartData,
  type DashboardFilters,
  type AvailableFilters,
} from '../services/dashboardService';

function formatCurrency(value: string): string {
  const num = parseFloat(value);
  if (isNaN(num)) return value;
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(num);
}

interface DashboardData {
  summary: DashboardSummary;
  balanceByStore: ChartData;
  transactionsByType: ChartData;
  transactionsTimeline: ChartData;
}

const Dashboard: FC = () => {
  const [availableFilters, setAvailableFilters] = useState<AvailableFilters | null>(null);
  const [filtersLoading, setFiltersLoading] = useState(true);

  const [selectedStore, setSelectedStore] = useState<string>('');
  const [selectedOwner, setSelectedOwner] = useState<string>('');
  const [dateFrom, setDateFrom] = useState<string>('');
  const [dateTo, setDateTo] = useState<string>('');

  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
          setAvailableFilters({ stores: [], owners: [], date_range: { min_date: '', max_date: '' } });
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

    const loadData = async () => {
      setLoading(true);
      setError(null);
      try {
        const params: DashboardFilters = {
          store_id: selectedStore || undefined,
          owner_name: selectedOwner || undefined,
          date_from: dateFrom || undefined,
          date_to: dateTo || undefined,
        };

        const [summary, balanceByStore, transactionsByType, transactionsTimeline] =
          await Promise.all([
            dashboardService.getSummary(params),
            dashboardService.getBalanceByStore(params),
            dashboardService.getTransactionsByType(params),
            dashboardService.getTransactionsTimeline(params),
          ]);

        if (!cancelled) {
          setData({ summary, balanceByStore, transactionsByType, transactionsTimeline });
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

    loadData();

    return () => {
      cancelled = true;
    };
  }, [filtersLoading, selectedStore, selectedOwner, dateFrom, dateTo]);

  const balanceVariant = (value: string): 'success' | 'error' => {
    return parseFloat(value) >= 0 ? 'success' : 'error';
  };

  return (
    <Layout>
      <div className="space-y-6">
        <PageTitle
          title="Dashboard de Conciliação Bancária"
          subtitle="Visão geral das transações importadas e saúde financeira por unidade."
        />

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

          <div>
            <label className="text-muted text-xs block mb-1">Período de</label>
            <input
              type="date"
              className="filter-input rounded-lg px-3 py-1.5 text-sm [color-scheme:dark]"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              disabled={filtersLoading}
            />
          </div>

          <div>
            <label className="text-muted text-xs block mb-1">até</label>
            <input
              type="date"
              className="filter-input rounded-lg px-3 py-1.5 text-sm [color-scheme:dark]"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              disabled={filtersLoading}
            />
          </div>
        </div>

        {error && (
          <div className="alert-error rounded-xl p-4 text-sm">{error}</div>
        )}

        {loading ? (
          <>
            <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="skeleton-stat" />
              ))}
            </div>
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
              <div className="skeleton-chart" style={{ height: 380 }} />
              <div className="skeleton-chart" style={{ height: 380 }} />
            </div>
            <div className="skeleton-chart" style={{ height: 380 }} />
          </>
        ) : data && data.summary.total_transactions === 0 ? (
          <div className="surface-card p-10 flex flex-col items-center justify-center gap-3 text-center">
            <p className="text-muted text-sm">
              Nenhum dado importado. Faça upload de um arquivo CNAB para visualizar o dashboard.
            </p>
          </div>
        ) : data ? (
          <>
            <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-4">
              <StatCard
                title="Lojas"
                value={data.summary.total_stores}
                subtitle="Total importadas"
                icon={faStore}
                variant="default"
              />
              <StatCard
                title="Transações"
                value={data.summary.total_transactions}
                subtitle="Total processadas"
                icon={faMoneyBillTransfer}
                variant="default"
              />
              <StatCard
                title="Receitas"
                value={formatCurrency(data.summary.total_income)}
                subtitle="Entradas totais"
                icon={faArrowTrendUp}
                variant="success"
              />
              <StatCard
                title="Despesas"
                value={formatCurrency(data.summary.total_expense)}
                subtitle="Saídas totais"
                icon={faArrowTrendDown}
                variant="error"
              />
              <StatCard
                title="Saldo"
                value={formatCurrency(data.summary.overall_balance)}
                subtitle="Balanço geral"
                icon={faScaleBalanced}
                variant={balanceVariant(data.summary.overall_balance)}
              />
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
              <BarChartCard
                title="Saldo por Loja"
                labels={data.balanceByStore.labels}
                data={data.balanceByStore.data}
              />
              <PieChartCard
                title="Transações por Tipo"
                labels={data.transactionsByType.labels}
                data={data.transactionsByType.data}
                colors={data.transactionsByType.colors ?? []}
              />
            </div>

            <LineChartCard
              title="Transações por Data"
              labels={data.transactionsTimeline.labels}
              data={data.transactionsTimeline.data}
            />
          </>
        ) : null}
      </div>
    </Layout>
  );
};

export default Dashboard;
