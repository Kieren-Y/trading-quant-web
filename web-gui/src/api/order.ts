import request from '../utils/request';
import type { Order, CreateOrderParams } from '../types';

export const getOrders = () => {
  return request.get<any, Order[]>('/orders/');
};

export const createOrder = (data: CreateOrderParams) => {
  return request.post<any, Order>('/orders/', data);
};

export const cancelOrder = (id: number) => {
  return request.post<any, { status: string }>(`/orders/${id}/cancel`);
};
