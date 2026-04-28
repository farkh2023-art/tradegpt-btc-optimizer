import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import type { EquityPoint } from '../types'

interface Props {
  data: EquityPoint[]
  initialCapital?: number
}

const fmt = (v: number) =>
  v >= 1000 ? `${(v / 1000).toFixed(1)}k $` : `${v.toFixed(0)} $`

export default function BacktestChart({ data, initialCapital = 10000 }: Props) {
  if (!data.length) return (
    <div className="h-52 flex items-center justify-center text-slate-500 text-sm">
      Aucune donnée de courbe disponible.
    </div>
  )

  const last  = data[data.length - 1]?.value ?? initialCapital
  const isPos = last >= initialCapital

  return (
    <div>
      <div className="flex items-baseline gap-2 mb-3">
        <span className="text-2xl font-bold text-white">{fmt(last)}</span>
        <span className={`text-sm font-semibold ${isPos ? 'text-green-400' : 'text-red-400'}`}>
          {isPos ? '+' : ''}{(((last - initialCapital) / initialCapital) * 100).toFixed(2)} %
        </span>
        <span className="text-slate-500 text-xs">depuis {fmt(initialCapital)}</span>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={data} margin={{ top: 4, right: 0, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="equityGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor={isPos ? '#22d3ee' : '#f87171'} stopOpacity={0.3} />
              <stop offset="95%" stopColor={isPos ? '#22d3ee' : '#f87171'} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#ffffff08" />
          <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 10 }} tickLine={false} axisLine={false} interval="preserveStartEnd" />
          <YAxis tickFormatter={fmt} tick={{ fill: '#64748b', fontSize: 10 }} tickLine={false} axisLine={false} width={60} />
          <Tooltip
            contentStyle={{ background: '#0d1526', border: '1px solid #1e3a5f', borderRadius: 8 }}
            labelStyle={{ color: '#94a3b8', fontSize: 11 }}
            formatter={(v: number) => [fmt(v), 'Capital']}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke={isPos ? '#22d3ee' : '#f87171'}
            strokeWidth={2}
            fill="url(#equityGrad)"
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
