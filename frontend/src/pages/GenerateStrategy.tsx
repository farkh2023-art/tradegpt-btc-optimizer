import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { strategiesApi } from '../api/strategies'
import RiskDisclaimer from '../components/RiskDisclaimer'
import { Wand2, Copy, Check } from 'lucide-react'
import type { GenerateStrategyResponse } from '../types'

const RISK_OPTIONS = [
  { value: 'conservative', label: 'Conservateur', desc: 'Stop loss serré, positions petites' },
  { value: 'balanced',     label: 'Équilibré',     desc: 'Compromis risque/rendement' },
  { value: 'aggressive',   label: 'Agressif',      desc: 'Positions larges, TP élevé' },
]

const TEMPLATE_OPTS = [
  { value: '',           label: 'Détection automatique' },
  { value: 'sma',        label: 'SMA Cross' },
  { value: 'supertrend', label: 'Supertrend' },
  { value: 'rsi',        label: 'RSI Reversal' },
  { value: 'adx',        label: 'ADX Trend Filter' },
  { value: 'combined',   label: 'SMA + RSI + ADX' },
]

export default function GenerateStrategy() {
  const [prompt, setPrompt]           = useState('')
  const [template, setTemplate]       = useState('')
  const [riskProfile, setRiskProfile] = useState('balanced')
  const [result, setResult]           = useState<GenerateStrategyResponse | null>(null)
  const [copied, setCopied]           = useState(false)
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  const mutation = useMutation({
    mutationFn: strategiesApi.generate,
    onSuccess: (data) => {
      setResult(data)
      queryClient.invalidateQueries({ queryKey: ['strategies'] })
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!prompt.trim()) return
    mutation.mutate({ prompt, template: template || undefined, risk_profile: riskProfile })
  }

  const copyScript = () => {
    if (result) {
      navigator.clipboard.writeText(result.pine_script)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Générer une stratégie</h1>
        <p className="text-slate-400 text-sm mt-1">Décrivez votre stratégie en langage naturel.</p>
      </div>

      <RiskDisclaimer />

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm text-slate-300 mb-1.5">Description de la stratégie *</label>
          <textarea
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            placeholder="Ex : Stratégie de suivi de tendance Bitcoin utilisant le RSI et la SMA 50, avec stop loss à 2% et prise de profit à 5%..."
            rows={4}
            className="w-full bg-navy-800 border border-white/10 rounded-xl px-4 py-3 text-white text-sm placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 resize-none"
            required
          />
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-slate-300 mb-1.5">Template</label>
            <select
              value={template}
              onChange={e => setTemplate(e.target.value)}
              className="w-full bg-navy-800 border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-cyan-500/50"
            >
              {TEMPLATE_OPTS.map(o => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-1.5">Profil de risque</label>
            <div className="flex gap-2">
              {RISK_OPTIONS.map(o => (
                <button
                  key={o.value}
                  type="button"
                  onClick={() => setRiskProfile(o.value)}
                  className={`flex-1 py-2 px-2 rounded-xl text-xs font-medium border transition-all ${
                    riskProfile === o.value
                      ? 'border-cyan-500 bg-cyan-500/20 text-cyan-300'
                      : 'border-white/10 bg-navy-800 text-slate-400 hover:border-white/20'
                  }`}
                >
                  {o.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <button
          type="submit"
          disabled={mutation.isPending || !prompt.trim()}
          className="flex items-center gap-2 bg-cyan-500 hover:bg-cyan-400 disabled:opacity-50 disabled:cursor-not-allowed text-black font-semibold px-6 py-2.5 rounded-xl text-sm transition-colors"
        >
          <Wand2 size={16} />
          {mutation.isPending ? 'Génération en cours…' : 'Générer la stratégie'}
        </button>
      </form>

      {mutation.isError && (
        <div className="bg-red-900/30 border border-red-500/40 rounded-xl p-4 text-red-300 text-sm">
          {(mutation.error as Error).message}
        </div>
      )}

      {result && (
        <div className="space-y-4">
          <div className="bg-navy-800 border border-cyan-500/20 rounded-xl p-5">
            <div className="flex items-start justify-between gap-4 mb-3">
              <div>
                <h2 className="text-lg font-bold text-white">{result.name}</h2>
                <p className="text-slate-400 text-sm mt-0.5">{result.description}</p>
              </div>
              <div className="flex gap-2 shrink-0">
                <button
                  onClick={copyScript}
                  className="flex items-center gap-1.5 text-xs bg-white/5 hover:bg-white/10 px-3 py-1.5 rounded-lg text-slate-300 transition-colors"
                >
                  {copied ? <Check size={13} /> : <Copy size={13} />}
                  {copied ? 'Copié' : 'Copier script'}
                </button>
                <button
                  onClick={() => navigate(`/editor?strategy=${result.strategy_id}`)}
                  className="text-xs bg-cyan-500/20 hover:bg-cyan-500/30 px-3 py-1.5 rounded-lg text-cyan-300 transition-colors"
                >
                  Ouvrir éditeur
                </button>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 mb-4">
              {result.indicators.map(i => (
                <span key={i} className="text-xs bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded-full">{i}</span>
              ))}
            </div>

            <div className="bg-navy-900 rounded-lg p-4 overflow-x-auto">
              <pre className="text-sm text-green-300 font-mono whitespace-pre">{result.pine_script}</pre>
            </div>

            {result.explanation && (
              <div className="mt-4 bg-blue-900/20 border border-blue-500/20 rounded-lg p-3 text-sm text-slate-300">
                <p className="font-semibold text-blue-300 mb-1">Explication</p>
                <p className="whitespace-pre-line">{result.explanation}</p>
              </div>
            )}

            <p className="text-yellow-500 text-xs mt-3">{result.warning}</p>
          </div>
        </div>
      )}
    </div>
  )
}
