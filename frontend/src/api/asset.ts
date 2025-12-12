import request from '../utils/request';
import type { PortfolioSummary } from '../types';

export const getAssets = () => {
  return request.get<any, PortfolioSummary>('/assets/');
};
