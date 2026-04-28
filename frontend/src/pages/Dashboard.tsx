import { useQuery } from '@tanstack/react-query'
import { strategiesApi } from '../api/strategies'
import { aiApi } from '../api/ai'
import { reportsApi } from '../api/reports'
import StrategyCard from '../components/StrategyCard'
import RiskDisclaimer from '../components/RiskDisclaimer'
import { TrendingUp, Layers, FileText, Wifi, WifiOff } from 'lucide-react'

function StatCard({ icon: Icon, label, value, color = 'text-cyan-400' }: {
  icon: React.ElementType; label: string; value: string | number; color?: string
}) {
  return (
    <div className="bg-navy-800 border border-white/5 rounded-xl p-5">
      <div className="flex items-center gap-2 text-slate-400 text-sm mb-2">
        <Icon size={16} className={color} />
        {label}
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
    </div>
  )
}

export default function Dashboard() {
  const { data: strategiesData } = useQuery({
    queryKey: ['strategies'],
    queryFn: strategiesApi.list,
  })
  const { data: aiStatus } = useQuery({
    queryKey: ['ai-status'],
    queryFn: aiApi.status,
  })
  const { data: reports } = useQuery({
    queryKey: ['reports'],
    queryFn: reportsApi.list,
  })

  const strategies = strategiesData?.items ?? []
  const recent = strategies.slice(0, 6)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-slate-400 text-sm mt-1">Vue d'ensemble de vos stratégies Bitcoin.</p>
      </div>

      <RiskDisclaimer />

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard icon={Layers} label="Stratégies" value={strategiesData?.total ?? 0} />
        <StatCard icon={FileText} label="Rapports" value={reports?.length ?? 0} color="text-purple-400" />
        <StatCard icon={TrendingUp} label="Backtests" value="—" color="text-green-400" />
        <div className="bg-navy-800 border border-white/5 rounded-xl p-5">
          <div className="flex items-center gap-2 text-slate-400 text-sm mb-2">
            {aiStatus?.mode === 'live'
              ? <Wifi size={16} className="text-green-400" />
              : <WifiOff size={16} className="text-yellow-400" />}
            Fournisseur IA
          </div>
          <p className="text-lg font-bold text-white capitalize">{aiStatus?.provider ?? '…'}</p>
          <p className={`text-xs mt-1 ${aiStatus?.mode === 'live' ? 'text-green-400' : 'text-yellow-400'}`}>
            {aiStatus?.mode === 'live' ? 'Connecté' : 'Mode mock'}
          </p>
        </div>
      </div>

      {/* Stratégies récentes */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-3">Stratégies récentes</h2>
        {recent.length === 0 ? (
          <div className="bg-navy-800 border border-white/5 rounded-xl p-8 text-center">
            <p className="text-slate-400">Aucune stratégie encore créée.</p>
            <a href="/generate" className="mt-3 inline-block text-cyan-400 text-sm hover:underline">
              → Générer votre première stratégie
            </a>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-3">
            {recent.map(s => <StrategyCard key={s.id} strategy={s} />)}
          </div>
        )}
      </div>
    </div>
  )
}
