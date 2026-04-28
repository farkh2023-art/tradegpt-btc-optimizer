import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { strategiesApi } from '../api/strategies'
import { reportsApi } from '../api/reports'
import { FileText, Download, RefreshCw } from 'lucide-react'
import type { Report } from '../types'

export default function ReportsPage() {
  const [strategyId, setSid] = useState<number | null>(null)
  const qc = useQueryClient()

  const { data: strategiesData } = useQuery({ queryKey: ['strategies'], queryFn: strategiesApi.list })
  const strategies = strategiesData?.items ?? []

  const { data: reports } = useQuery({
    queryKey: ['reports'],
    queryFn: reportsApi.list,
  })

  const genMutation = useMutation({
    mutationFn: () => reportsApi.generate(strategyId!),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['reports'] }),
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <FileText size={22} className="text-cyan-400" /> Rapports
        </h1>
        <p className="text-slate-400 text-sm mt-1">Générez et téléchargez des rapports Markdown par stratégie.</p>
      </div>

      <div className="bg-navy-800 border border-white/5 rounded-xl p-5 flex flex-wrap gap-3 items-end">
        <div className="flex-1 min-w-48">
          <label className="block text-sm text-slate-300 mb-1.5">Stratégie</label>
          <select
            value={strategyId ?? ''}
            onChange={e => setSid(Number(e.target.value) || null)}
            className="w-full bg-navy-900 border border-white/10 rounded-xl px-3 py-2.5 text-white text-sm focus:outline-none"
          >
            <option value="">Sélectionner…</option>
            {strategies.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </div>
        <button
          onClick={() => genMutation.mutate()}
          disabled={genMutation.isPending || !strategyId}
          className="flex items-center gap-2 bg-cyan-500 hover:bg-cyan-400 disabled:opacity-50 text-black font-semibold px-5 py-2.5 rounded-xl text-sm transition-colors"
        >
          <RefreshCw size={15} className={genMutation.isPending ? 'animate-spin' : ''} />
          {genMutation.isPending ? 'Génération…' : 'Générer rapport'}
        </button>
      </div>

      {genMutation.isSuccess && (
        <div className="bg-green-900/30 border border-green-500/30 rounded-lg px-4 py-2 text-green-300 text-sm">
          Rapport généré avec succès.
        </div>
      )}

      <div className="space-y-3">
        {(reports ?? []).length === 0 ? (
          <div className="bg-navy-800 border border-white/5 rounded-xl p-8 text-center">
            <p className="text-slate-400">Aucun rapport encore généré.</p>
          </div>
        ) : (
          (reports ?? []).map((r: Report) => (
            <div key={r.id} className="bg-navy-800 border border-white/5 rounded-xl p-4">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-white font-semibold text-sm">Rapport #{r.id}</p>
                  <p className="text-slate-500 text-xs mt-0.5">
                    Stratégie #{r.strategy_id} •{' '}
                    {new Date(r.created_at).toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                  </p>
                  <p className="text-slate-400 text-xs mt-1 line-clamp-2 font-mono">
                    {r.content.slice(0, 120)}…
                  </p>
                </div>
                <button
                  onClick={() => reportsApi.download(r.id)}
                  className="flex items-center gap-1.5 shrink-0 text-xs bg-white/5 hover:bg-white/10 px-3 py-1.5 rounded-lg text-slate-300 transition-colors"
                >
                  <Download size={12} /> Télécharger
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
