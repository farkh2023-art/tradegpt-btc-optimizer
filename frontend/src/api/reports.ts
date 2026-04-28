import { api, downloadFile } from './client'
import type { Report } from '../types'

export const reportsApi = {
  generate: (strategy_id: number, backtest_id?: number) =>
    api.post<Report>('/reports/generate', { strategy_id, backtest_id }),
  list: () => api.get<Report[]>('/reports'),
  listForStrategy: (strategy_id: number) =>
    api.get<Report[]>(`/reports/strategy/${strategy_id}`),
  get: (id: number) => api.get<Report>(`/reports/${id}`),
  download: (id: number) => downloadFile(`/reports/${id}/download`, `rapport_${id}.md`),
}
