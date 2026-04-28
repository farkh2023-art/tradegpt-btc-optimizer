import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { optimizationApi } from '../api/optimization'
import OptimizationTable from '../components/OptimizationTable'
import RiskDisclaimer from '../components/RiskDisclaimer'
import { SlidersHorizontal } from 'lucide-react'
import type { OptimizationResult } from '../types'

interface RangeInput { min: number; max: number; step: number }

const DEFAULT_RANGES: Record<string, Record<string, RangeInput>> = {
  sma: {
    fast_length: { min: 10, max: 30, step: 5 },
    slow_length: { min: 40, max: 80, step: 10 },
    stop_loss_pct: { min: 1.0, max: 3.0, step: 0.5 },
    take_profit_pct: { min: 3.0, max: 8.0, step: 1.0 },
  },
  rsi: {
    rsi_length: { min: 7, max: 21, step: 7 },
    oversold: { min: 25, max: 40, step: 5 },
    overbought: { min: 60, max: 75, step: 5 },
  },
  adx: {
    adx_threshold: { min: 15, max: 35, step: 5 },
    adx_length: { min: 7, max: 21, step: 7 },
  },
  supertrend: {
    atr_period: { min: 7, max: 21, step: 7 },
    factor: { min: 2.0, max: 4.0, step: 0.5 },
  },
  combined: {
    sma_length: { min: 30, max: 70, step: 20 },
    rsi_length: { min: 10, max: 20, step: 5 },
    adx_threshold: { min: 15, max: 30, step: 5 },
  },
}

export default function OptimizePage() {
  const [template, setTemplate] = useState('sma')
  const [capital, setCapital]   = useState('10000')
  const [maxC, setMaxC]         = useState('50')
  const [ranges, setRanges]     = useState<Record<string, RangeInput>>(DEFAULT_RANGES['sma'])
  const [results, setResults]   = useState<OptimizationResult[]>([])

  const handleTemplateChange = (t: string) => {
    setTemplate(t)
    setRanges(DEFAULT_RANGES[t] ?? {})
  }

  const updateRange = (param: string, field: keyof RangeInput, val: string) => {
    setRanges(r => ({ ...r, [param]: { ...r[param], [field]: Number(val) } }))
  }

  const mutation = useMutation({
    mutationFn: () => optimizationApi.run({
      template,
      param_ranges: ranges,
      initial_capital: Number(capital),
      max_combinations: Number(maxC),
    }),
    onSuccess: d => setResults(d.results),
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <SlidersHorizontal size={22} className="text-cyan-400" /> Optimisation
        </h1>
        <p className="text-slate-400 text-sm mt-1">Grid search sur les paramètres de votre stratégie.</p>
      </div>

      <RiskDisclaimer />

      <div className="bg-navy-800 border border-white/5 rounded-xl p-5 space-y-5">
        <div className="grid md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm text-slate-300 mb-1.5">Template</label>
            <select
              value={template}
              onChange={e => handleTemplateChange(e.target.value)}
              className="w-full bg-navy-900 border border-white/10 rounded-xl px-3 py-2.5 text-white text-sm focus:outline-none"
            >
              {Object.keys(DEFAULT_RANGES).map(t => (
                <option key={t} value={t}>{t.toUpperCase()}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-1.5">Capital ($)</label>
            <input type="number" value={capital} onChange={e => setCapital(e.target.value)}
              className="w-full bg-navy-900 border border-white/10 rounded-xl px-3 py-2.5 text-white text-sm focus:outline-none" />
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-1.5">Max combinaisons</label>
            <input type="number" value={maxC} min="10" max="200" onChange={e => setMaxC(e.target.value)}
              className="w-full bg-navy-900 border border-white/10 rounded-xl px-3 py-2.5 text-white text-sm focus:outline-none" />
          </div>
        </div>

        <div>
          <p className="text-sm text-slate-300 mb-3">Plages de paramètres</p>
          <div className="grid md:grid-cols-2 gap-3">
            {Object.entries(ranges).map(([param, range]) => (
              <div key={param} className="bg-navy-900 rounded-xl p-3">
                <p className="text-xs font-mono text-cyan-300 mb-2">{param}</p>
                <div className="grid grid-cols-3 gap-2">
                  {(['min', 'max', 'step'] as const).map(f => (
                    <div key={f}>
                      <label className="text-xs text-slate-500 mb-0.5 block">{f}</label>
                      <input
                        type="number"
                        value={range[f]}
                        step={f === 'step' ? 'any' : 1}
                        onChange={e => updateRange(param, f, e.target.value)}
                        className="w-full bg-navy-800 border border-white/10 rounded-lg px-2 py-1.5 text-white text-xs focus:outline-none"
                      />
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <button
          onClick={() => mutation.mutate()}
          disabled={mutation.isPending}
          className="bg-cyan-500 hover:bg-cyan-400 disabled:opacity-50 text-black font-semibold px-6 py-2.5 rounded-xl text-sm transition-colors"
        >
          {mutation.isPending ? 'Optimisation en cours…' : 'Lancer l\'optimisation'}
        </button>
      </div>

      {mutation.isError && (
        <div className="bg-red-900/30 border border-red-500/40 rounded-xl p-4 text-red-300 text-sm">
          {(mutation.error as Error).message}
        </div>
      )}

      {results.length > 0 && (
        <div className="bg-navy-800 border border-white/5 rounded-xl p-5">
          <h2 className="font-semibold text-white mb-3">Top {results.length} résultats</h2>
          <OptimizationTable results={results} />
        </div>
      )}
    </div>
  )
}
