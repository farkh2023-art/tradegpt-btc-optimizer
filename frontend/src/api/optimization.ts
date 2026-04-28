import { api } from './client'
import type { OptimizationResult } from '../types'

export const optimizationApi = {
  run: (body: {
    template: string
    param_ranges: Record<string, { min: number; max: number; step: number }>
    initial_capital?: number
    max_combinations?: number
  }) =>
    api.post<{ template: string; results: OptimizationResult[]; total_tested: number }>(
      '/optimization/run',
      body
    ),
}
