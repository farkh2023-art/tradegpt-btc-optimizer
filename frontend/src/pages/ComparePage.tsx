import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { strategiesApi } from '../api/strategies'
import { backtestsApi } from '../api/backtests'
import RiskDisclaimer from '../components/RiskDisclaimer'
import { GitCompare, Trophy } from 'lucide-react'
import type { CompareResult } from '../types'

function MetricRow({ label, a, b, winner }: { label: string; a: number | string; b: number | string; winner: 'A' | 'B' | null }) {
  return (
    <tr className="border-b border-white/5">
      <td className="py-2 text-slate-400 text-sm">{label}</td>
      <td className={`py-2 text-center font-semibold ${winner === 'A' ? 'text-cyan-300' : 'text-slate-300'}`}>{a}</td>
      <td className={`py-2 text-center font-semibold ${winner === 'B' ? 'text-cyan-300' : 'text-slate-300'}`}>{b}</td>
    </tr>
  )
}

export default function ComparePage() {
  const [idA, setIdA]     = useState<number | null>(null)
  const [idB, setIdB]     = useState<number | null>(null)
  const [template, setTpl] = useState('sma')
  const [result, setResult] = useState<CompareResult | null>(null)

  const { data } = useQuery({ queryKey: ['strategies'], queryFn: strategiesApi.list })
  const strategies = data?.items ?? []

  const mutation = useMutation({
    mutationFn: () => backtestsApi.compare({
      strategy_id_a: idA!, strategy_id_b: idB!,
      template, params_a: {}, params_b: {},
    }),
    onSuccess: setResult,
  })

  const m = result
  const mA = m?.strategy_a?.metrics as Record<string, number> | undefined
  const mB = m?.strategy_b?.metrics as Record<string, number> | undefined

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <GitCompare size={22} className="text-cyan-400" /> Comparaison A/B
        </h1>
        <p className="text-slate-400 text-sm mt-1">Comparez deux stratégies sur les mêmes données historiques.</p>
      </div>

      <RiskDisclaimer />

      <div className="bg-navy-800 border border-white/5 rounded-xl p-5 space-y-4">
        <div className="grid md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm text-slate-300 mb-1.5">Stratégie A</label>
            <select
              value={idA ?? ''}
              onChange={e => setIdA(Number(e.target.value) || null)}
              className="w-full bg-navy-900 border border-white/10 rounded-xl px-3 py-2.5 text-white text-sm focus:outline-none"
            >
              <option value="">Sélectionner…</option>
              {strategies.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-1.5">Stratégie B</label>
            <select
              value={idB ?? ''}
              onChange={e => setIdB(Number(e.target.value) || null)}
              className="w-full bg-navy-900 border border-white/10 rounded-xl px-3 py-2.5 text-white text-sm focus:outline-none"
            >
              <option value="">Sélectionner…</option>
              {strategies.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-1.5">Template</label>
            <select
              value={template}
              onChange={e => setTpl(e.target.value)}
              className="w-full bg-navy-900 border border-white/10 rounded-xl px-3 py-2.5 text-white text-sm focus:outline-none"
            >
              {['sma', 'rsi', 'adx', 'supertrend', 'combined'].map(t => (
                <option key={t} value={t}>{t.toUpperCase()}</option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={() => mutation.mutate()}
          disabled={mutation.isPending || !idA || !idB || idA === idB}
          className="bg-cyan-500 hover:bg-cyan-400 disabled:opacity-50 text-black font-semibold px-6 py-2.5 rounded-xl text-sm transition-colors"
        >
          {mutation.isPending ? 'Comparaison en cours…' : 'Comparer les stratégies'}
        </button>
      </div>

      {mutation.isError && (
        <div className="bg-red-900/30 border border-red-500/40 rounded-xl p-4 text-red-300 text-sm">
          {(mutation.error as Error).message}
        </div>
      )}

      {result && mA && mB && (
        <div className="space-y-4">
          <div className={`bg-navy-800 border rounded-xl p-5 ${result.winner === 'A' ? 'border-cyan-500/40' : 'border-purple-500/40'}`}>
            <div className="flex items-center gap-2 mb-2">
              <Trophy size={18} className="text-yellow-400" />
              <h2 className="font-bold text-white">Variante {result.winner} recommandée</h2>
            </div>
            <p className="text-slate-300 text-sm">{result.justification}</p>
          </div>

          <div className="bg-navy-800 border border-white/5 rounded-xl p-5 overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/10 text-xs text-slate-400">
                  <th className="text-left pb-2">Métrique</th>
                  <th className={`text-center pb-2 ${result.winner === 'A' ? 'text-cyan-300' : ''}`}>
                    Stratégie A {result.winner === 'A' ? '🏆' : ''}
                  </th>
                  <th className={`text-center pb-2 ${result.winner === 'B' ? 'text-cyan-300' : ''}`}>
                    Stratégie B {result.winner === 'B' ? '🏆' : ''}
                  </th>
                </tr>
              </thead>
              <tbody>
                <MetricRow label="Rendement %" a={`${mA.return_pct?.toFixed(2)} %`} b={`${mB.return_pct?.toFixed(2)} %`} winner={mA.return_pct > mB.return_pct ? 'A' : 'B'} />
                <MetricRow label="Capital final ($)" a={mA.final_capital?.toFixed(0)} b={mB.final_capital?.toFixed(0)} winner={mA.final_capital > mB.final_capital ? 'A' : 'B'} />
                <MetricRow label="Trades" a={mA.num_trades} b={mB.num_trades} winner={null} />
                <MetricRow label="Win rate %" a={`${mA.win_rate?.toFixed(1)} %`} b={`${mB.win_rate?.toFixed(1)} %`} winner={mA.win_rate > mB.win_rate ? 'A' : 'B'} />
                <MetricRow label="Drawdown max" a={`${mA.max_drawdown?.toFixed(1)} %`} b={`${mB.max_drawdown?.toFixed(1)} %`} winner={mA.max_drawdown < mB.max_drawdown ? 'A' : 'B'} />
                <MetricRow label="Profit Factor" a={mA.profit_factor?.toFixed(3)} b={mB.profit_factor?.toFixed(3)} winner={mA.profit_factor > mB.profit_factor ? 'A' : 'B'} />
                <MetricRow label="Sharpe ratio" a={mA.sharpe_ratio?.toFixed(3)} b={mB.sharpe_ratio?.toFixed(3)} winner={mA.sharpe_ratio > mB.sharpe_ratio ? 'A' : 'B'} />
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
