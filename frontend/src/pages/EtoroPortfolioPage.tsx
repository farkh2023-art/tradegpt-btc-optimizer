import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import { Wallet, TrendingUp, DollarSign, BarChart2, Shield } from 'lucide-react'
import { etoroApi } from '../api/etoro'
import RiskDisclaimer from '../components/RiskDisclaimer'
import type { EtoroAnalysis } from '../types'

const PIE_COLORS = ['#06b6d4', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#64748b']

function StatCard({ icon: Icon, label, value, sub, color = 'text-cyan-400' }: {
  icon: React.ElementType; label: string; value: string; sub?: string; color?: string
}) {
  return (
    <div className="bg-navy-800 border border-white/5 rounded-xl p-5">
      <div className="flex items-center gap-2 text-slate-400 text-sm mb-2">
        <Icon size={16} className={color} />
        {label}
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
      {sub && <p className="text-xs text-slate-500 mt-1">{sub}</p>}
    </div>
  )
}

export default function EtoroPortfolioPage() {
  const [analysis, setAnalysis] = useState<EtoroAnalysis | null>(null)

  const { data: status } = useQuery({
    queryKey: ['etoro-status'],
    queryFn:  etoroApi.status,
  })

  const { data: portfolio, isLoading, isError } = useQuery({
    queryKey: ['etoro-portfolio'],
    queryFn:  etoroApi.portfolio,
  })

  const analyzeMutation = useMutation({
    mutationFn: () => etoroApi.analyze(),
    onSuccess:  setAnalysis,
  })

  const fmtUsd = (v: number) =>
    v.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })

  if (isLoading) return (
    <div className="flex items-center justify-center h-64 text-slate-400 text-sm">
      Chargement du portefeuille…
    </div>
  )

  if (isError || !portfolio) return (
    <div className="bg-red-900/30 border border-red-500/40 rounded-xl p-6 text-red-300 text-sm">
      Impossible de charger le portefeuille eToro. Vérifiez la configuration dans .env.
    </div>
  )

  const weightSum  = portfolio.positions.reduce((s, p) => s + p.weight_pct, 0)
  const cashSlice  = parseFloat(Math.max(0, 100 - weightSum).toFixed(1))
  const pieData = [
    ...portfolio.positions.map(p => ({ name: p.symbol, value: p.weight_pct })),
    ...(cashSlice > 0.1 ? [{ name: 'Cash', value: cashSlice }] : []),
  ]

  const perfColor = portfolio.performance_pct >= 0 ? 'text-green-400' : 'text-red-400'
  const btcColor  = portfolio.btc_exposure_pct > 50 ? 'text-red-400'
    : portfolio.btc_exposure_pct >= 10 ? 'text-cyan-400' : 'text-slate-400'

  return (
    <div className="space-y-6">

      {/* En-tête */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Wallet size={22} className="text-cyan-400" /> eToro Portfolio
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Analyse en lecture seule de votre portefeuille eToro.
          </p>
        </div>
        <span className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border ${
          status?.mock
            ? 'bg-yellow-900/30 text-yellow-300 border-yellow-600/40'
            : 'bg-green-900/30 text-green-300 border-green-600/40'
        }`}>
          <span className={`w-2 h-2 rounded-full ${status?.mock ? 'bg-yellow-400' : 'bg-green-400'}`} />
          {status?.mock ? 'Mode mock' : 'Connecté'}
        </span>
      </div>

      {/* Notice sécurité */}
      <div className="bg-blue-900/20 border border-blue-500/30 rounded-xl p-4 flex gap-3 items-center text-sm text-blue-200">
        <Shield size={15} className="text-blue-400 shrink-0" />
        <span>
          <strong className="text-blue-300">Lecture seule —</strong>{' '}
          Aucun ordre d'achat ou de vente ne peut être exécuté.{' '}
          <code className="text-blue-400 text-xs bg-blue-900/30 px-1 rounded">
            ETORO_ALLOW_REAL_ORDERS=false
          </code>
        </span>
      </div>

      <RiskDisclaimer />

      {/* Cartes résumé */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          icon={DollarSign} label="Valeur totale"
          value={fmtUsd(portfolio.total_value)}
          sub={`Cash : ${fmtUsd(portfolio.cash)}`}
        />
        <StatCard
          icon={TrendingUp} label="Investi"
          value={fmtUsd(portfolio.invested)}
          color="text-purple-400"
        />
        <StatCard
          icon={BarChart2} label="Performance"
          value={`${portfolio.performance_pct >= 0 ? '+' : ''}${portfolio.performance_pct.toFixed(2)} %`}
          color={perfColor}
        />
        <StatCard
          icon={Wallet} label="Exposition BTC"
          value={`${portfolio.btc_exposure_pct.toFixed(1)} %`}
          color={btcColor}
        />
      </div>

      {/* Positions + Graphique */}
      <div className="grid md:grid-cols-2 gap-4">

        {/* Tableau des positions */}
        <div className="bg-navy-800 border border-white/5 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-slate-300 mb-4">
            Positions ({portfolio.positions.length})
          </h2>
          <div className="divide-y divide-white/5">
            {portfolio.positions.map(p => (
              <div key={p.symbol} className="flex items-center justify-between py-2.5">
                <div>
                  <span className={`font-mono text-sm font-bold ${p.is_crypto ? 'text-cyan-400' : 'text-white'}`}>
                    {p.symbol}
                  </span>
                  <p className="text-xs text-slate-500">{p.name}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-white font-medium">{p.weight_pct.toFixed(1)} %</p>
                  <p className={`text-xs font-medium ${p.performance_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {p.performance_pct >= 0 ? '+' : ''}{p.performance_pct.toFixed(1)} %
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Graphique de répartition */}
        <div className="bg-navy-800 border border-white/5 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-slate-300 mb-2">Répartition</h2>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={pieData}
                dataKey="value"
                nameKey="name"
                cx="50%" cy="50%"
                outerRadius={75}
                strokeWidth={0}
              >
                {pieData.map((_entry, i) => (
                  <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ background: '#0d1526', border: '1px solid #1e3a5f', borderRadius: 8 }}
                labelStyle={{ color: '#94a3b8', fontSize: 11 }}
                formatter={(v: number) => [`${v.toFixed(1)} %`, '']}
              />
              <Legend
                wrapperStyle={{ fontSize: 11, paddingTop: 8 }}
                formatter={(value) => <span style={{ color: '#94a3b8' }}>{value}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
          <p className="text-center text-xs text-slate-500 mt-1">
            Concentration :{' '}
            <span className={`font-semibold ${
              portfolio.concentration_score > 60 ? 'text-red-400'
                : portfolio.concentration_score > 30 ? 'text-yellow-400'
                : 'text-green-400'
            }`}>
              {portfolio.concentration_score.toFixed(0)}/100
            </span>
          </p>
        </div>
      </div>

      {/* Bloc Analyse TradeGPT */}
      <div className="bg-navy-800 border border-white/5 rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-300">Analyse TradeGPT</h2>
          <button
            onClick={() => analyzeMutation.mutate()}
            disabled={analyzeMutation.isPending}
            className="bg-cyan-500 hover:bg-cyan-400 disabled:opacity-50 text-black font-semibold px-4 py-2 rounded-xl text-sm transition-colors"
          >
            {analyzeMutation.isPending ? 'Analyse…' : 'Analyser le portefeuille'}
          </button>
        </div>

        {analyzeMutation.isError && (
          <p className="text-red-400 text-sm">
            {(analyzeMutation.error as Error).message}
          </p>
        )}

        {analysis ? (
          <div className="space-y-3">
            <p className="text-slate-300 text-sm leading-relaxed">{analysis.summary}</p>
            <div className="space-y-2">
              {analysis.recommendations.map((rec, i) => (
                <div key={i} className="flex gap-2 text-sm text-slate-300">
                  <span className="text-cyan-400 shrink-0 font-bold">→</span>
                  {rec}
                </div>
              ))}
            </div>
            <div className="flex flex-wrap items-center gap-6 text-xs text-slate-500 border-t border-white/5 pt-3">
              <span>
                Risque :{' '}
                <span className={`font-semibold ${
                  analysis.risk_level === 'élevé'  ? 'text-red-400'
                    : analysis.risk_level === 'modéré' ? 'text-yellow-400'
                    : 'text-green-400'
                }`}>
                  {analysis.risk_level}
                </span>
              </span>
              <span className="italic">{analysis.disclaimer}</span>
            </div>
          </div>
        ) : (
          <p className="text-slate-500 text-sm">
            Cliquez sur "Analyser le portefeuille" pour obtenir une analyse TradeGPT personnalisée.
          </p>
        )}
      </div>

    </div>
  )
}
