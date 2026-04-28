import type { OptimizationResult } from '../types'

interface Props {
  results: OptimizationResult[]
}

export default function OptimizationTable({ results }: Props) {
  if (!results.length) return (
    <p className="text-slate-500 text-sm">Aucun résultat.</p>
  )

  const paramKeys = Object.keys(results[0]?.params ?? {})

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/10 text-slate-400 text-xs">
            <th className="text-left pb-2 pr-3">#</th>
            {paramKeys.map(k => <th key={k} className="text-left pb-2 pr-3">{k}</th>)}
            <th className="text-right pb-2 pr-3">Rendement</th>
            <th className="text-right pb-2 pr-3">Win rate</th>
            <th className="text-right pb-2 pr-3">Drawdown</th>
            <th className="text-right pb-2">Profit F.</th>
          </tr>
        </thead>
        <tbody>
          {results.map((r, i) => (
            <tr key={i} className={`border-b border-white/5 ${i === 0 ? 'bg-cyan-500/10' : 'hover:bg-white/3'}`}>
              <td className="py-2 pr-3 text-slate-500">{i + 1}</td>
              {paramKeys.map(k => (
                <td key={k} className="py-2 pr-3 font-mono text-slate-300">{r.params[k]}</td>
              ))}
              <td className={`py-2 pr-3 text-right font-semibold ${r.return_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {r.return_pct >= 0 ? '+' : ''}{r.return_pct?.toFixed(2)} %
              </td>
              <td className="py-2 pr-3 text-right text-slate-300">{r.win_rate?.toFixed(1)} %</td>
              <td className="py-2 pr-3 text-right text-red-400">{r.max_drawdown?.toFixed(1)} %</td>
              <td className="py-2 text-right text-slate-300">{r.profit_factor?.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
