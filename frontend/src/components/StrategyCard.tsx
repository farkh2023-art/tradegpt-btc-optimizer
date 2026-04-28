import { Link } from 'react-router-dom'
import { ChevronRight, Bitcoin } from 'lucide-react'
import type { Strategy } from '../types'

interface Props {
  strategy: Strategy
}

const RISK_COLORS: Record<string, string> = {
  conservative: 'bg-green-500/20 text-green-300',
  balanced:     'bg-blue-500/20 text-blue-300',
  aggressive:   'bg-red-500/20 text-red-300',
}

export default function StrategyCard({ strategy }: Props) {
  const date = new Date(strategy.created_at).toLocaleDateString('fr-FR')
  return (
    <Link
      to={`/editor?strategy=${strategy.id}`}
      className="block bg-navy-700 border border-white/5 rounded-xl p-4 hover:border-cyan-500/30 transition-all group"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <Bitcoin size={16} className="text-cyan-400 shrink-0" />
          <p className="font-semibold text-white truncate">{strategy.name}</p>
        </div>
        <ChevronRight size={16} className="text-slate-500 group-hover:text-cyan-400 transition-colors shrink-0" />
      </div>
      <p className="text-slate-400 text-xs mt-1.5 line-clamp-2">{strategy.description}</p>
      <div className="flex items-center gap-2 mt-3 flex-wrap">
        {strategy.template && (
          <span className="text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded-full">
            {strategy.template.toUpperCase()}
          </span>
        )}
        <span className={`text-xs px-2 py-0.5 rounded-full ${RISK_COLORS[strategy.risk_profile] ?? 'bg-slate-700 text-slate-300'}`}>
          {strategy.risk_profile}
        </span>
        <span className="text-xs text-slate-500 ml-auto">{date}</span>
      </div>
    </Link>
  )
}
