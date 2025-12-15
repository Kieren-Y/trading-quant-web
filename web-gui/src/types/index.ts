export interface ExchangeConfig {
  id: number;
  user_id: number;
  exchange_name: string;
  account_name?: string;
  api_key: string;
  secret_key: string; // Will be masked '***' from server
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateExchangeConfigParams {
  exchange_name: string;
  api_key: string;
  secret_key: string;
  account_name?: string;
  is_active?: boolean;
}

export interface AssetBalance {
  currency: string;
  free: number;
  used: number;
  total: number;
  usdt_value: number;
}

export interface ExchangeAsset {
  exchange_name: string;
  account_name: string;
  market_type: string;
  total_usdt_value: number;
  balances: AssetBalance[];
}

export interface PortfolioSummary {
  total_usdt_value: number;
  exchanges: ExchangeAsset[];
}

export interface Order {
  id: number;
  user_id: number;
  exchange_config_id: number;
  exchange_order_id?: string;
  symbol: string;
  side: 'buy' | 'sell';
  type: 'limit' | 'market';
  price?: number;
  amount: number;
  status: string;
  filled: number;
  cost: number;
  created_at: string;
  updated_at: string;
}

export interface CreateOrderParams {
  exchange_config_id: number;
  symbol: string;
  side: 'buy' | 'sell';
  type: 'limit' | 'market';
  price?: number;
  amount: number;
  market_type: 'spot' | 'future';
}

export interface StrategyConfig {
  id: number;
  user_id: number;
  strategy_name: string;
  exchange_config_id: number;
  parameters: Record<string, any>;
  status: 'running' | 'stopped' | 'error';
  created_at: string;
  updated_at: string;
}

export interface CreateStrategyParams {
  strategy_name: string;
  exchange_config_id: number;
  parameters: Record<string, any>;
}
