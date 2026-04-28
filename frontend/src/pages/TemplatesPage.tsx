import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { strategiesApi } from '../api/strategies'
import { BookTemplate, Copy, Check } from 'lucide-react'
import type { Template } from '../types'

const ICON_MAP: Record<string, string> = {
  sma: '📈', supertrend: '🌊', rsi: '🔄', adx: '💪', combined: '🔗',
}

function TemplateCard({ tpl, onSelect, selected }: {
  tpl: Template; onSelect: (key: string) => void; selected: boolean
}) {
  return (
    <button
      onClick={() => onSelect(tpl.key)}
      className={`text-left w-full bg-navy-800 border rounded-xl p-4 transition-all ${
        selected ? 'border-cyan-500/60 bg-cyan-500/10' : 'border-white/5 hover:border-white/20'
      }`}
    >
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xl">{ICON_MAP[tpl.key] ?? '📊'}</span>
        <p className="font-semibold text-white text-sm">{tpl.name}</p>
      </div>
      <p className="text-xs text-slate-400 line-clamp-2">{tpl.description}</p>
      <div className="flex flex-wrap gap-1 mt-2">
        {tpl.indicators.map(i => (
          <span key={i} className="text-xs bg-slate-700 text-slate-300 px-1.5 py-0.5 rounded">{i}</span>
        ))}
      </div>
    </button>
  )
}

export default function TemplatesPage() {
  const [selected, setSelected] = useState<string | null>(null)
  const [script, setScript]     = useState<string | null>(null)
  const [copied, setCopied]     = useState(false)

  const { data } = useQuery({
    queryKey: ['templates'],
    queryFn: strategiesApi.listTemplates,
  })

  const schemaQuery = useQuery({
    queryKey: ['template-schema', selected],
    queryFn: () => strategiesApi.getTemplateSchema(selected!),
    enabled: !!selected,
  })

  const genMutation = useMutation({
    mutationFn: ({ key, params }: { key: string; params: Record<string, unknown> }) =>
      strategiesApi.generateFromTemplate(key, params),
    onSuccess: (data) => setScript(data.pine_script),
  })

  const handleGenerate = () => {
    if (!selected) return
    genMutation.mutate({ key: selected, params: {} })
  }

  const copy = () => {
    if (script) {
      navigator.clipboard.writeText(script)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <BookTemplate size={22} className="text-cyan-400" /> Templates
        </h1>
        <p className="text-slate-400 text-sm mt-1">Choisissez un template pour générer rapidement un Pine Script v5.</p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
        {(data?.templates ?? []).map(tpl => (
          <TemplateCard
            key={tpl.key}
            tpl={tpl}
            selected={selected === tpl.key}
            onSelect={setSelected}
          />
        ))}
      </div>

      {selected && (
        <div className="bg-navy-800 border border-white/10 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-white">
              {ICON_MAP[selected]} Aperçu — {selected.toUpperCase()}
            </h2>
            <button
              onClick={handleGenerate}
              disabled={genMutation.isPending}
              className="text-sm bg-cyan-500 hover:bg-cyan-400 text-black font-semibold px-4 py-1.5 rounded-lg transition-colors disabled:opacity-50"
            >
              {genMutation.isPending ? 'Chargement…' : 'Générer le script'}
            </button>
          </div>

          {schemaQuery.data && (
            <div>
              <p className="text-xs text-slate-400 mb-2">Paramètres disponibles :</p>
              <div className="grid md:grid-cols-2 gap-2">
                {Object.entries(schemaQuery.data.params_schema).map(([k, v]) => (
                  <div key={k} className="bg-navy-900 rounded-lg px-3 py-2 text-xs">
                    <span className="font-mono text-cyan-300">{k}</span>
                    <span className="text-slate-400 ml-2">
                      {(v as { label?: string })?.label ?? k}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {script && (
            <div>
              <div className="flex justify-end mb-2">
                <button onClick={copy} className="flex items-center gap-1.5 text-xs bg-white/5 hover:bg-white/10 px-3 py-1.5 rounded-lg text-slate-300 transition-colors">
                  {copied ? <Check size={12} /> : <Copy size={12} />}
                  {copied ? 'Copié' : 'Copier'}
                </button>
              </div>
              <div className="bg-navy-900 rounded-lg p-4 overflow-x-auto max-h-80">
                <pre className="text-xs text-green-300 font-mono whitespace-pre">{script}</pre>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
