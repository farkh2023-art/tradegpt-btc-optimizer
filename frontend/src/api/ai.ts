import { api } from './client'
import type { AIStatus, DebugResult } from '../types'

export const aiApi = {
  status: () => api.get<AIStatus>('/pine/status'),
  debug: (script: string) =>
    api.post<DebugResult>('/pine/debug', { script }),
  recommend: (metrics: Record<string, number>, params: Record<string, number>, template: string) =>
    api.post<{ recommendations: string[]; suggested_params: Record<string, unknown>; analysis: string }>(
      '/pine/recommend',
      { metrics, params, template }
    ),
}
