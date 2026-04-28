import { api } from './client'
import type { EtoroStatus, EtoroPortfolio, EtoroAnalysis } from '../types'

export const etoroApi = {
  status:   () => api.get<EtoroStatus>('/etoro/status'),
  portfolio: () => api.get<EtoroPortfolio>('/etoro/portfolio'),
  analyze:  (focus = 'btc') => api.post<EtoroAnalysis>('/etoro/analyze', { focus }),
}
