import { api } from './client'
import type {
  Strategy, StrategyVersion, GenerateStrategyRequest,
  GenerateStrategyResponse, Template,
} from '../types'

export const strategiesApi = {
  list: () => api.get<{ items: Strategy[]; total: number }>('/strategies'),
  get: (id: number) => api.get<Strategy>(`/strategies/${id}`),
  delete: (id: number) => api.delete<{ deleted: number }>(`/strategies/${id}`),
  generate: (body: GenerateStrategyRequest) =>
    api.post<GenerateStrategyResponse>('/strategies/generate', body),

  listVersions: (id: number) =>
    api.get<StrategyVersion[]>(`/strategies/${id}/versions`),
  createVersion: (id: number, body: { pine_script: string; parameters: Record<string, unknown>; explanation: string }) =>
    api.post<StrategyVersion>(`/strategies/${id}/versions`, body),

  listTemplates: () =>
    api.get<{ templates: Template[] }>('/strategies/templates'),
  getTemplateSchema: (key: string) =>
    api.get<{ key: string; params_schema: Record<string, unknown>; indicators: string[]; description: string }>(`/strategies/templates/${key}`),
  generateFromTemplate: (key: string, params: Record<string, unknown>) =>
    api.post<{ pine_script: string; template: string }>(`/strategies/templates/${key}/generate`, params),
}
