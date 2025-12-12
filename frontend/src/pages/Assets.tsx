import React, { useEffect, useState, useMemo } from 'react';
import { Card, Table, Statistic, Row, Col, Spin, Empty, Tag, Radio, Space } from 'antd';
import { DollarOutlined, ReloadOutlined } from '@ant-design/icons';
import { getAssets } from '../api/asset';
import type { PortfolioSummary, ExchangeAsset, AssetBalance } from '../types';

const Assets: React.FC = () => {
  const [portfolio, setPortfolio] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [filterType, setFilterType] = useState<string>('all'); // 'all', 'spot', 'future'

  const fetchAssets = async () => {
    setLoading(true);
    try {
      const data = await getAssets();
      setPortfolio(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssets();
  }, []);

  const filteredExchanges = useMemo(() => {
    if (!portfolio) return [];
    if (filterType === 'all') return portfolio.exchanges;

    // Normalize market types for comparison (e.g., okx 'swap' -> 'future' logic if needed, but for now exact match or simple mapping)
    return portfolio.exchanges.filter(ex => {
        if (filterType === 'spot') return ex.market_type === 'spot';
        if (filterType === 'future') return ['future', 'swap'].includes(ex.market_type);
        return true;
    });
  }, [portfolio, filterType]);

  const totalValue = useMemo(() => {
    return filteredExchanges.reduce((sum, ex) => sum + ex.total_usdt_value, 0);
  }, [filteredExchanges]);

  const columns = [
    {
      title: 'Currency',
      dataIndex: 'currency',
      key: 'currency',
      render: (text: string) => <span style={{ fontWeight: 'bold' }}>{text}</span>,
    },
    {
      title: 'Total',
      dataIndex: 'total',
      key: 'total',
      render: (val: number) => val.toFixed(4),
    },
    {
      title: 'Available',
      dataIndex: 'free',
      key: 'free',
      render: (val: number) => <span style={{ color: '#3f8600' }}>{val.toFixed(4)}</span>,
    },
    {
      title: 'Frozen',
      dataIndex: 'used',
      key: 'used',
      render: (val: number) => <span style={{ color: '#cf1322' }}>{val.toFixed(4)}</span>,
    },
    {
      title: 'Est. USDT Value',
      dataIndex: 'usdt_value',
      key: 'usdt_value',
      render: (val: number) => (val > 0 ? `$${val.toFixed(2)}` : '-'),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Assets Overview</h2>
        <Space>
          <Radio.Group value={filterType} onChange={(e) => setFilterType(e.target.value)} buttonStyle="solid">
            <Radio.Button value="all">All</Radio.Button>
            <Radio.Button value="spot">Spot</Radio.Button>
            <Radio.Button value="future">Futures</Radio.Button>
          </Radio.Group>
          <Tag icon={<ReloadOutlined spin={loading} />} color="blue" style={{ cursor: 'pointer' }} onClick={fetchAssets}>
            Refresh
          </Tag>
        </Space>
      </div>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card bordered={false}>
            <Statistic
              title={`Total Portfolio Value (${filterType.toUpperCase()})`}
              value={totalValue}
              precision={2}
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
      </Row>

      {loading && !portfolio ? (
        <div style={{ textAlign: 'center', padding: 50 }}>
          <Spin size="large" />
        </div>
      ) : (
        <>
          {filteredExchanges.map((exchange: ExchangeAsset, index: number) => (
            <Card
              key={index}
              title={`${exchange.exchange_name.toUpperCase()} (${exchange.market_type.toUpperCase()}) - ${exchange.account_name}`}
              style={{ marginBottom: 16 }}
              extra={<span>Total: ${exchange.total_usdt_value.toFixed(2)}</span>}
            >
              <Table
                dataSource={exchange.balances}
                columns={columns}
                rowKey="currency"
                pagination={false}
                size="small"
              />
            </Card>
          ))}

          {filteredExchanges.length === 0 && (
            <Empty description="No assets found for the selected filter" />
          )}
        </>
      )}
    </div>
  );
};

export default Assets;
