import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Editor from '@monaco-editor/react'
import { strategiesApi } from '../api/strategies'
import { Save, History, Code2 } from 'lucide-react'
import type { StrategyVersion } from '../types'

export default function StrategyEditorPage() {
  const [params]             = useSearchParams()
  const strategyId           = Number(params.get('strategy'))
  const [code, setCode]      = useState('')
  const [explanation, setEx] = useState('')
  const [showHistory, setHist] = useState(false)
  const queryClient          = useQueryClient()

  const strategyQuery = useQuery({
    queryKey: ['strategy', strategyId],
    queryFn: () => strategiesApi.get(strategyId),
    enabled: !!strategyId,
  })

  const versionsQuery = useQuery({
    queryKey: ['versions', strategyId],
    queryFn: () => strategiesApi.listVersions(strategyId),
    enabled: !!strategyId,
  })

  const currentVersion = versionsQuery.data?.find(v => v.is_current)

  useEffect(() => {
    if (currentVersion) setCode(currentVersion.pine_script)
  }, [currentVersion])

  const saveMutation = useMutation({
    mutationFn: () =>
      strategiesApi.createVersion(strategyId, { pine_script: code, parameters: {}, explanation }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['versions', strategyId] })
      queryClient.invalidateQueries({ queryKey: ['strategies'] })
    },
  })

  const loadVersion = (v: StrategyVersion) => {
    setCode(v.pine_script)
    setHist(false)
  }

  if (!strategyId) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Code2 size={22} className="text-cyan-400" /> Éditeur Pine Script
        </h1>
        <div className="bg-navy-800 border border-white/5 rounded-xl p-8 text-center">
          <p className="text-slate-400">Sélectionnez une stratégie depuis le Dashboard.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Code2 size={22} className="text-cyan-400" /> Éditeur
          </h1>
          {strategyQuery.data && (
            <p className="text-slate-400 text-sm mt-0.5">{strategyQuery.data.name}</p>
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setHist(!showHistory)}
            className="flex items-center gap-1.5 text-sm bg-white/5 hover:bg-white/10 px-3 py-2 rounded-lg text-slate-300 transition-colors"
          >
            <History size={15} /> Historique
          </button>
          <button
            onClick={() => saveMutation.mutate()}
            disabled={saveMutation.isPending}
            className="flex items-center gap-1.5 text-sm bg-cyan-500 hover:bg-cyan-400 text-black font-semibold px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
          >
            <Save size={15} />
            {saveMutation.isPending ? 'Sauvegarde…' : 'Sauvegarder'}
          </button>
        </div>
      </div>

      {saveMutation.isSuccess && (
        <div className="bg-green-900/30 border border-green-500/30 rounded-lg px-4 py-2 text-green-300 text-sm">
          Nouvelle version sauvegardée avec succès.
        </div>
      )}

      {showHistory && (
        <div className="bg-navy-800 border border-white/10 rounded-xl p-4 space-y-2">
          <h3 className="text-sm font-semibold text-slate-300">Historique des versions</h3>
          {(versionsQuery.data ?? []).map(v => (
            <button
              key={v.id}
              onClick={() => loadVersion(v)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                v.is_current ? 'bg-cyan-500/20 text-cyan-300' : 'hover:bg-white/5 text-slate-300'
              }`}
            >
              <span className="font-mono">v{v.version_number}</span>
              <span className="text-slate-500 ml-2 text-xs">
                {new Date(v.created_at).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}
              </span>
              {v.is_current && <span className="ml-2 text-xs text-cyan-400">• courante</span>}
            </button>
          ))}
        </div>
      )}

      <div className="rounded-xl overflow-hidden border border-white/10">
        <Editor
          height="55vh"
          defaultLanguage="plaintext"
          theme="vs-dark"
          value={code}
          onChange={v => setCode(v ?? '')}
          options={{
            fontSize: 13,
            minimap: { enabled: false },
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            wordWrap: 'on',
            padding: { top: 12, bottom: 12 },
          }}
        />
      </div>

      <div>
        <label className="block text-sm text-slate-300 mb-1.5">Note sur cette version</label>
        <input
          value={explanation}
          onChange={e => setEx(e.target.value)}
          placeholder="Ex : Ajout filtre ADX, resserrement stop loss…"
          className="w-full bg-navy-800 border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm placeholder-slate-500 focus:outline-none focus:border-cyan-500/50"
        />
      </div>
    </div>
  )
}
