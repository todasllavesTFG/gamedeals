import { useMemo, useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  Legend,
} from 'recharts';
import { useFetch } from '../../hooks/useFetch';
import { getGameHistory } from '../../lib/api';

const COLORS = ['#a3ff12', '#8b5cf6', '#fbbf24', '#ef4444', '#3b82f6'];
const DAY_OPTIONS = [
  { value: 7, label: '7 días' },
  { value: 30, label: '30 días' },
  { value: 90, label: '90 días' },
  { value: 365, label: '1 año' },
];

function formatEur(value) {
  return `${Number(value).toFixed(2)} €`;
}

function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('es-ES', { day: '2-digit', month: 'short' });
}

export default function PriceHistoryChart({ gameId, allTimeLow }) {
  const [days, setDays] = useState(30);

  const { data, loading, error } = useFetch(
    (signal) => getGameHistory(gameId, { days }, signal),
    [gameId, days]
  );

  const { chartData, stores } = useMemo(() => {
    if (!data?.history) return { chartData: [], stores: [] };

    const storeNames = Object.keys(data.history);
    const dateSet = new Set();

    storeNames.forEach((store) => {
      data.history[store].forEach((point) => {
        dateSet.add(point.recorded_at.slice(0, 10));
      });
    });

    const dates = Array.from(dateSet).sort();

    const points = dates.map((date) => {
      const row = { date };
      storeNames.forEach((store) => {
        const match = data.history[store].find((p) => p.recorded_at.slice(0, 10) === date);
        row[store] = match ? match.price : null;
      });
      return row;
    });

    return { chartData: points, stores: storeNames };
  }, [data]);

  return (
    <div className="space-y-4">
      {/* Selector de rango */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h3 className="text-sm font-medium text-text-muted">Rango de tiempo</h3>
        <div className="flex gap-1">
          {DAY_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setDays(opt.value)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                days === opt.value
                  ? 'bg-accent text-bg'
                  : 'bg-surface-2 text-text-muted hover:text-text'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center h-40">
          <span className="w-7 h-7 rounded-full border-2 border-accent border-t-transparent animate-spin" />
        </div>
      )}

      {error && (
        <p className="text-sm text-red-400 text-center py-8">
          Error al cargar el historial de precios
        </p>
      )}

      {!loading && !error && chartData.length === 0 && (
        <p className="text-sm text-text-muted text-center py-8">
          No hay datos de historial para este período
        </p>
      )}

      {!loading && !error && chartData.length > 0 && (
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={chartData} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
            <CartesianGrid stroke="var(--color-border)" strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tickFormatter={formatDate}
              tick={{ fill: 'var(--color-text-muted)', fontSize: 11 }}
              axisLine={{ stroke: 'var(--color-border)' }}
              tickLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              tickFormatter={formatEur}
              tick={{ fill: 'var(--color-text-muted)', fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              width={65}
            />
            <Tooltip
              formatter={(value) => (value != null ? formatEur(value) : '—')}
              labelFormatter={formatDate}
              contentStyle={{
                backgroundColor: 'var(--color-surface-2)',
                border: '1px solid var(--color-border)',
                borderRadius: '8px',
                fontSize: '12px',
                color: 'var(--color-text)',
              }}
            />
            <Legend
              wrapperStyle={{ fontSize: '12px', color: 'var(--color-text-muted)' }}
            />
            {allTimeLow?.price != null && (
              <ReferenceLine
                y={allTimeLow.price}
                stroke="#a3ff12"
                strokeDasharray="4 4"
                label={{
                  value: 'All-time low',
                  fill: '#a3ff12',
                  fontSize: 11,
                  position: 'insideTopRight',
                }}
              />
            )}
            {stores.map((store, idx) => (
              <Line
                key={store}
                type="monotone"
                dataKey={store}
                name={store}
                stroke={COLORS[idx % COLORS.length]}
                strokeWidth={2}
                dot={false}
                connectNulls
                activeDot={{ r: 4 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
