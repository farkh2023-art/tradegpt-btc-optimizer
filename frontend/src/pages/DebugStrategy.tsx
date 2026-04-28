import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import Editor from '@monaco-editor/react'
import { aiApi } from '../api/ai'
import { Bug, CheckCircle, AlertTriangle, XCircle, Copy, Check } from 'lucide-react'
import type { DebugResult } from '../types'

const SEVERITY_MAP = {
  ok:      { icon: CheckCircle, color: 'text-green-400', bg: 'bg-green-900/20 border-green-500/30' },
  warning: { icon: AlertTriangle, color: 'text-yellow-400', bg: 'bg-yellow-900/20 border-yellow-500/30' },
  error:   { icon: XCircle, color: 'text-red-400', bg: 'bg-red-900/20 border-red-500/30' },
}

export default function DebugStrategy() {
  const [script, setScript]     = useState('')
  const [corrected, setCorrected] = useState('')
  const [copied, setCopied]     = useState(false)

  const mutation = useMutation({
    mutationFn: () => aiApi.debug(script),
    onSuccess: (data: DebugResult) => setCorrected(data.corrected_script),
  })

  const copy = () => {
    navigator.clipboard.writeText(corrected)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const result = mutation.data as DebugResult | undefined
  const sev    = SEVERITY_MAP[result?.severity ?? 'ok']

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Bug size={22} className="text-cyan-400" /> Debug Pine Script
        </h1>
        <p className="text-slate-400 text-sm mt-1">Collez votre script pour détecter et corriger les erreurs.</p>
      </div>

      <div className="rounded-xl overflow-hidden border border-white/10">
        <Editor
          height="30vh"
          defaultLanguage="plaintext"
          theme="vs-dark"
          value={script}
          onChange={v => setScript(v ?? '')}
          options={{ fontSize: 13, minimap: { enabled: false }, padding: { top: 12 } }}
        />
      </div>

      <button
        onClick={() => mutation.mutate()}
        disabled={mutation.isPending || !script.trim()}
        className="flex items-center gap-2 bg-cyan-500 hover:bg-cyan-400 disabled:opacity-50 text-black font-semibold px-6 py-2.5 rounded-xl text-sm transition-colors"
      >
        <Bug size={16} />
        {mutation.isPending ? 'Analyse en cours…' : 'Analyser et corriger'}
      </button>

      {result && (
        <div className="space-y-4">
          <div className={`rounded-xl border p-4 ${sev.bg}`}>
            <div className="flex items-center gap-2 mb-3">
              <sev.icon size={16} className={sev.color} />
              <h3 className={`font-semibold text-sm ${sev.color}`}>Problèmes détectés</h3>
            </div>
            <ul className="space-y-1">
              {result.issues.map((issue, i) => (
                <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                  <span className="text-slate-500 mt-0.5">•</span>
                  {issue}
                </li>
              ))}
            </ul>
          </div>

          {result.explanation && (
            <div className="bg-blue-900/20 border border-blue-500/20 rounded-xl p-4 text-sm text-slate-300">
              <p className="font-semibold text-blue-300 mb-1">Analyse</p>
              <p>{result.explanation}</p>
            </div>
          )}

          {corrected && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-slate-300">Script corrigé</h3>
                <button onClick={copy} className="flex items-center gap-1.5 text-xs bg-white/5 hover:bg-white/10 px-3 py-1.5 rounded-lg text-slate-300 transition-colors">
                  {copied ? <Check size={12} /> : <Copy size={12} />}
                  {copied ? 'Copié' : 'Copier'}
                </button>
              </div>
              <div className="rounded-xl overflow-hidden border border-white/10">
                <Editor
                  height="30vh"
                  defaultLanguage="plaintext"
                  theme="vs-dark"
                  value={corrected}
                  onChange={v => setCorrected(v ?? '')}
                  options={{ fontSize: 13, minimap: { enabled: false }, padding: { top: 12 } }}
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
