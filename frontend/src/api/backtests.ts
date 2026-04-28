import { api } from './client'
import type { Backtest, CompareResult } from '../types'

export const backtestsApi = {
  run: (body: {
    strategy_id: number
    version_id?: number
    template: string
    params: Record<string, number>
    initial_capital?: number
  }) => api.post<Backtest>('/backtests/run', body),

  import: (body: {
    strategy_id: number
    initial_capital: number
    final_capital: number
    return_pct: number
    num_trades: number
    win_rate: number
    max_drawdown: number
    profit_factor?: number
  }) => api.post<Backtest>('/backtests/import', body),

  listForStrategy: (strategy_id: number) =>
    api.get<Backtest[]>(`/backtests/strategy/${strategy_id}`),

  get: (id: number) => api.get<Backtest>(`/backtests/${id}`),

  compare: (body: {
    strategy_id_a: number
    strategy_id_b: number
    template: string
    params_a: Record<string, number>
    params_b: Record<string, number>
    initial_capital?: number
  }) => api.post<CompareResult>('/backtests/compare', body),
}
