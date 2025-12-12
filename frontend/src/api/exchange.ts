import request from '../utils/request';
import type { ExchangeConfig, CreateExchangeConfigParams } from '../types';

export const getExchangeConfigs = () => {
  return request.get<any, ExchangeConfig[]>('/exchanges/');
};

export const createExchangeConfig = (data: CreateExchangeConfigParams) => {
  return request.post<any, ExchangeConfig>('/exchanges/', data);
};

export const deleteExchangeConfig = (id: number) => {
  return request.delete<any, { status: string }>(`/exchanges/${id}`);
};
