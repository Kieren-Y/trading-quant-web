import React, { useEffect, useState } from 'react';
import { Card, Form, Input, Select, Button, InputNumber, Row, Col, Table, Tag, message, Popconfirm, Tabs, Radio } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { getExchangeConfigs } from '../api/exchange';
import { createOrder, getOrders, cancelOrder } from '../api/order';
import type { ExchangeConfig, Order } from '../types';

const { TabPane } = Tabs;

const ManualTrade: React.FC = () => {
  const [exchanges, setExchanges] = useState<ExchangeConfig[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form] = Form.useForm();

  // Fetch initial data
  useEffect(() => {
    fetchExchanges();
    fetchOrders();
    // Poll orders every 5 seconds
    const interval = setInterval(fetchOrders, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchExchanges = async () => {
    try {
      const data = await getExchangeConfigs();
      setExchanges(data.filter(e => e.is_active));
    } catch (error) {
      console.error(error);
    }
  };

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const data = await getOrders();
      setOrders(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const onFinish = async (values: any) => {
    setSubmitting(true);
    try {
      await createOrder({
        ...values,
        market_type: values.market_type || 'spot', // Default to spot if not specified
      });
      message.success('Order placed successfully');
      form.resetFields();
      fetchOrders();
    } catch (error) {
      console.error(error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancel = async (id: number) => {
    try {
      await cancelOrder(id);
      message.success('Order cancel request sent');
      fetchOrders();
    } catch (error) {
      console.error(error);
    }
  };

  const columns = [
    {
      title: 'Time',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text: string) => new Date(text).toLocaleString(),
    },
    {
      title: 'Symbol',
      dataIndex: 'symbol',
      key: 'symbol',
      render: (text: string) => <span style={{ fontWeight: 'bold' }}>{text}</span>,
    },
    {
      title: 'Side',
      dataIndex: 'side',
      key: 'side',
      render: (side: string) => (
        <Tag color={side === 'buy' ? 'green' : 'red'}>{side.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      render: (text: string) => text.toUpperCase(),
    },
    {
      title: 'Price',
      dataIndex: 'price',
      key: 'price',
      render: (val: number) => val ? val : 'Market',
    },
    {
      title: 'Amount',
      dataIndex: 'amount',
      key: 'amount',
    },
    {
      title: 'Filled',
      dataIndex: 'filled',
      key: 'filled',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        let color = 'default';
        if (status === 'open') color = 'processing';
        if (status === 'closed') color = 'success';
        if (status === 'canceled') color = 'warning';
        return <Tag color={color}>{status.toUpperCase()}</Tag>;
      },
    },
    {
      title: 'Action',
      key: 'action',
      render: (_: any, record: Order) => (
        record.status === 'open' && (
          <Popconfirm title="Cancel this order?" onConfirm={() => handleCancel(record.id)}>
            <Button type="link" danger size="small">Cancel</Button>
          </Popconfirm>
        )
      ),
    },
  ];

  return (
    <div>
      <Row gutter={24}>
        {/* Order Form */}
        <Col span={8}>
          <Card title="Place Order" bordered={false}>
            <Form form={form} layout="vertical" onFinish={onFinish} initialValues={{ side: 'buy', type: 'limit', market_type: 'spot' }}>
              <Form.Item
                name="exchange_config_id"
                label="Account"
                rules={[{ required: true, message: 'Please select account' }]}
              >
                <Select placeholder="Select Account">
                  {exchanges.map(ex => (
                    <Select.Option key={ex.id} value={ex.id}>
                      {ex.exchange_name.toUpperCase()} - {ex.account_name}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>

              <Form.Item name="market_type" label="Market Type">
                <Radio.Group buttonStyle="solid">
                  <Radio.Button value="spot">Spot</Radio.Button>
                  <Radio.Button value="future">Futures</Radio.Button>
                </Radio.Group>
              </Form.Item>

              <Form.Item
                name="symbol"
                label="Symbol"
                rules={[{ required: true, message: 'e.g. BTC/USDT' }]}
                help="Spot: BTC/USDT, Future: BTC/USDT:USDT"
              >
                <Input placeholder="BTC/USDT" style={{ textTransform: 'uppercase' }} />
              </Form.Item>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item name="side" label="Side">
                    <Select>
                      <Select.Option value="buy">Buy</Select.Option>
                      <Select.Option value="sell">Sell</Select.Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="type" label="Type">
                    <Select>
                      <Select.Option value="limit">Limit</Select.Option>
                      <Select.Option value="market">Market</Select.Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item
                noStyle
                shouldUpdate={(prevValues, currentValues) => prevValues.type !== currentValues.type}
              >
                {({ getFieldValue }) =>
                  getFieldValue('type') === 'limit' ? (
                    <Form.Item
                      name="price"
                      label="Price"
                      rules={[{ required: true, message: 'Price is required' }]}
                    >
                      <InputNumber style={{ width: '100%' }} min={0} step={0.00000001} />
                    </Form.Item>
                  ) : null
                }
              </Form.Item>

              <Form.Item
                name="amount"
                label="Amount"
                rules={[{ required: true, message: 'Amount is required' }]}
              >
                <InputNumber style={{ width: '100%' }} min={0} />
              </Form.Item>

              <Form.Item>
                <Button type="primary" htmlType="submit" block loading={submitting}>
                  Place Order
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>

        {/* Order History */}
        <Col span={16}>
          <Card
            title="Order History"
            bordered={false}
            extra={<Button icon={<ReloadOutlined />} onClick={fetchOrders} type="text" />}
          >
            <Table
              dataSource={orders}
              columns={columns}
              rowKey="id"
              pagination={{ pageSize: 10 }}
              size="small"
              loading={loading}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default ManualTrade;
