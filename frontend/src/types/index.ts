export interface Strategy {
  id: number
  name: string
  description: string
  template: string | null
  risk_profile: string
  created_at: string
  updated_at: string
}

export interface StrategyVersion {
  id: number
  strategy_id: number
  version_number: number
  pine_script: string
  parameters: string
  explanation: string
  is_current: boolean
  created_at: string
}

export interface Backtest {
  id: number
  strategy_id: number
  version_id: number | null
  params: string
  initial_capital: number
  final_capital: number
  return_pct: number
  num_trades: number
  win_rate: number
  max_drawdown: number
  profit_factor: number
  sharpe_ratio: number
  source: string
  equity_curve: string
  created_at: string
}

export interface EquityPoint {
  date: string
  value: number
}

export interface Report {
  id: number
  strategy_id: number
  content: string
  created_at: string
}

export interface GenerateStrategyRequest {
  prompt: string
  template?: string
  risk_profile?: string
}

export interface GenerateStrategyResponse {
  strategy_id: number
  name: string
  description: string
  pine_script: string
  parameters: Record<string, unknown>
  explanation: string
  indicators: string[]
  warning: string
}

export interface Template {
  key: string
  name: string
  indicators: string[]
  description: string
}

export interface AIStatus {
  provider: string
  available: boolean
  mode: string
}

export interface OptimizationResult {
  params: Record<string, number>
  return_pct: number
  win_rate: number
  max_drawdown: number
  profit_factor: number
  num_trades: number
  sharpe_ratio: number
}

export interface CompareResult {
  strategy_a: { strategy_id: number; params: Record<string, number>; metrics: Omit<Backtest, 'id' | 'strategy_id' | 'version_id' | 'source' | 'created_at' | 'params'> }
  strategy_b: { strategy_id: number; params: Record<string, number>; metrics: Omit<Backtest, 'id' | 'strategy_id' | 'version_id' | 'source' | 'created_at' | 'params'> }
  winner: 'A' | 'B'
  justification: string
}

export interface DebugResult {
  issues: string[]
  corrected_script: string
  explanation: string
  severity: 'ok' | 'warning' | 'error'
}

export interface EtoroStatus {
  enabled: boolean
  mode: string
  connected: boolean
  allow_real_orders: boolean
  mock: boolean
}

export interface EtoroPosition {
  symbol: string
  name: string
  weight_pct: number
  performance_pct: number
  invested: number
  current_value: number
  buy_price: number | null
  sell_price: number | null
  is_crypto: boolean
}

export interface EtoroPortfolio {
  total_value: number
  cash: number
  invested: number
  performance_pct: number
  btc_exposure_pct: number
  concentration_score: number
  currency: string
  positions: EtoroPosition[]
}

export interface EtoroAnalysis {
  btc_exposure_pct: number
  concentration_score: number
  recommendations: string[]
  risk_level: string
  summary: string
  disclaimer: string
}
