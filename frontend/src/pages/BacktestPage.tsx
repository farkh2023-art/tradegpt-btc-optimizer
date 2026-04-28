import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { strategiesApi } from '../api/strategies'
import { backtestsApi } from '../api/backtests'
import BacktestChart from '../components/BacktestChart'
import RiskDisclaimer from '../components/RiskDisclaimer'
import { BarChart2 } from 'lucide-react'
import type { EquityPoint, Backtest } from '../types'

const TEMPLATES = ['sma', 'supertrend', 'rsi', 'adx', 'combined']

function MetricBadge({ label, value, positive }: { label: string; value: string; positive?: boolean }) {
  return (
    <div className="bg-navy-900 rounded-xl p-3">
      <p className="text-xs text-slate-400 mb-1">{label}</p>
      <p className={`text-lg font-bold ${positive === undefined ? 'text-white' : positive ? 'text-green-400' : 'text-red-400'}`}>
        {value}
      </p>
    </div>
  )
}

export default function BacktestPage() {
  const [strategyId, setStrategyId] = useState<number | null>(null)
  const [template, setTemplate]     = useState('sma')
  const [capital, setCapital]       = useState('10000')
  const [result, setResult]         = useState<Backtest | null>(null)

  const { data: strategiesData } = useQuery({
    queryKey: ['strategies'],
    queryFn: strategiesApi.list,
  })
  const strategies = strategiesData?.items ?? []

  const mutation = useMutation({
    mutationFn: () => backtestsApi.run({
      strategy_id: strategyId!,
      template,
      params: {},
      initial_capital: Number(capital),
    }),
    onSuccess: setResult,
  })

  const equityCurve: EquityPoint[] = result
    ? JSON.parse(result.equity_curve || '[]')
    : []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <BarChart2 size={22} className="text-cyan-400" /> Backtest local
        </h1>
        <p className="text-slate-400 text-sm mt-1">Simulez une stratégie sur données BTC historiques.</p>
      </div>

      <RiskDisclaimer />

      <div className="bg-navy-800 border border-white/5 rounded-xl p-5 space-y-4">
        <div className="grid md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm text-slate-300 mb-1.5">Stratégie</label>
            <select
              value={strategyId ?? ''}
              onChange={e => setStrategyId(Number(e.target.value) || null)}
              className="w-full bg-navy-900 border border-white/10 rounded-xl px-3 py-2.5 text-white text-sm focus:outline-none"
            >
              <option value="">Sélectionner…</option>
              {strategies.map(s => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-1.5">Template indicateur</label>
            <select
              value={template}
              onChange={e => setTemplate(e.target.value)}
              className="w-full bg-navy-900 border border-white/10 rounded-xl px-3 py-2.5 text-white text-sm focus:outline-none"
            >
              {TEMPLATES.map(t => (
                <option key={t} value={t}>{t.toUpperCase()}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-1.5">Capital initial ($)</label>
            <input
              type="number"
              value={capital}
              onChange={e => setCapital(e.target.value)}
              min="100"
              className="w-full bg-navy-900 border border-white/10 rounded-xl px-3 py-2.5 text-white text-sm focus:outline-none"
            />
          </div>
        </div>

        <button
          onClick={() => mutation.mutate()}
          disabled={mutation.isPending || !strategyId}
          className="bg-cyan-500 hover:bg-cyan-400 disabled:opacity-50 text-black font-semibold px-6 py-2.5 rounded-xl text-sm transition-colors"
        >
          {mutation.isPending ? 'Simulation en cours…' : 'Lancer le backtest'}
        </button>
      </div>

      {mutation.isError && (
        <div className="bg-red-900/30 border border-red-500/40 rounded-xl p-4 text-red-300 text-sm">
          {(mutation.error as Error).message}
        </div>
      )}

      {result && (
        <div className="space-y-4">
          <div className="bg-navy-800 border border-white/5 rounded-xl p-5">
            <BacktestChart data={equityCurve} initialCapital={result.initial_capital} />
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <MetricBadge label="Rendement" value={`${result.return_pct >= 0 ? '+' : ''}${result.return_pct.toFixed(2)} %`} positive={result.return_pct >= 0} />
            <MetricBadge label="Capital final" value={`${result.final_capital.toLocaleString('fr-FR')} $`} />
            <MetricBadge label="Trades" value={String(result.num_trades)} />
            <MetricBadge label="Win rate" value={`${result.win_rate.toFixed(1)} %`} positive={result.win_rate >= 50} />
            <MetricBadge label="Drawdown max" value={`${result.max_drawdown.toFixed(1)} %`} positive={result.max_drawdown < 15} />
            <MetricBadge label="Profit Factor" value={result.profit_factor.toFixed(3)} positive={result.profit_factor >= 1} />
            <MetricBadge label="Sharpe ratio" value={result.sharpe_ratio.toFixed(3)} positive={result.sharpe_ratio >= 1} />
            <MetricBadge label="Source" value={result.source} />
          </div>
        </div>
      )}
    </div>
  )
}
