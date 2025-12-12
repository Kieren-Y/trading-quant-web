import request from '../utils/request';
import type { StrategyConfig, CreateStrategyParams } from '../types';

export const getStrategies = () => {
  return request.get<any, StrategyConfig[]>('/strategies/');
};

export const createStrategy = (data: CreateStrategyParams) => {
  return request.post<any, StrategyConfig>('/strategies/', data);
};

export const deleteStrategy = (id: number) => {
  return request.delete<any, { status: string }>(`/strategies/${id}`);
};

export const startStrategy = (id: number) => {
  return request.post<any, { status: string }>(`/strategies/${id}/start`);
};

export const stopStrategy = (id: number) => {
  return request.post<any, { status: string }>(`/strategies/${id}/stop`);
};
