import { NavLink, Outlet } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { aiApi } from '../api/ai'
import {
  LayoutDashboard, Wand2, BookTemplate, Code2, Bug,
  BarChart2, SlidersHorizontal, GitCompare, FileText,
  Settings, Wifi, WifiOff, Bitcoin, Wallet,
} from 'lucide-react'

const NAV = [
  { to: '/',            label: 'Dashboard',          icon: LayoutDashboard },
  { to: '/generate',    label: 'Générer stratégie',  icon: Wand2 },
  { to: '/templates',   label: 'Templates',          icon: BookTemplate },
  { to: '/editor',      label: 'Éditeur',            icon: Code2 },
  { to: '/debug',       label: 'Debug',              icon: Bug },
  { to: '/backtest',    label: 'Backtest',           icon: BarChart2 },
  { to: '/optimize',    label: 'Optimisation',       icon: SlidersHorizontal },
  { to: '/compare',     label: 'Comparaison A/B',    icon: GitCompare },
  { to: '/reports',     label: 'Rapports',           icon: FileText },
  { to: '/etoro',       label: 'eToro Portfolio',    icon: Wallet },
  { to: '/settings',    label: 'Paramètres',         icon: Settings },
]

const linkCls = ({ isActive }: { isActive: boolean }) =>
  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all
   ${isActive
     ? 'bg-cyan-500/20 text-cyan-300 font-semibold'
     : 'text-slate-400 hover:text-slate-100 hover:bg-white/5'}`

export default function Layout() {
  const { data: aiStatus } = useQuery({
    queryKey: ['ai-status'],
    queryFn: aiApi.status,
    refetchInterval: 30_000,
  })

  return (
    <div className="flex h-screen bg-navy-900 text-slate-100 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-60 shrink-0 flex flex-col bg-navy-800 border-r border-white/5">
        {/* Logo */}
        <div className="flex items-center gap-2.5 px-4 py-5 border-b border-white/5">
          <Bitcoin className="text-cyan-400" size={24} />
          <div>
            <p className="font-bold text-white text-sm leading-tight">TradeGPT</p>
            <p className="text-xs text-slate-500">BTC Optimizer</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-2 py-4 space-y-0.5 overflow-y-auto">
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} end={to === '/'} className={linkCls}>
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* AI Status */}
        <div className="px-4 py-3 border-t border-white/5">
          <div className="flex items-center gap-2 text-xs">
            {aiStatus?.mode === 'live'
              ? <Wifi size={13} className="text-green-400" />
              : <WifiOff size={13} className="text-yellow-400" />}
            <span className={aiStatus?.mode === 'live' ? 'text-green-400' : 'text-yellow-400'}>
              IA : {aiStatus?.provider ?? '…'} {aiStatus?.mode === 'mock' ? '(mock)' : ''}
            </span>
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto px-6 py-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
