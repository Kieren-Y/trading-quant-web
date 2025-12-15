import React, { useEffect, useState } from 'react';
import { Card, Table, Button, Modal, Form, Input, Select, InputNumber, Tag, message, Popconfirm, Space, Row, Col } from 'antd';
import { PlusOutlined, PlayCircleOutlined, PauseCircleOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import { getStrategies, createStrategy, deleteStrategy, startStrategy, stopStrategy } from '../api/strategy';
import { getExchangeConfigs } from '../api/exchange';
import type { StrategyConfig, ExchangeConfig } from '../types';

const Dashboard: React.FC = () => {
  const [strategies, setStrategies] = useState<StrategyConfig[]>([]);
  const [exchanges, setExchanges] = useState<ExchangeConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();

  const fetchStrategies = async () => {
    setLoading(true);
    try {
      const data = await getStrategies();
      setStrategies(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const fetchExchanges = async () => {
    try {
      const data = await getExchangeConfigs();
      setExchanges(data.filter(e => e.is_active));
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchStrategies();
    fetchExchanges();

    // Auto refresh status every 5s
    const interval = setInterval(fetchStrategies, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleCreate = async (values: any) => {
    try {
      // Pack parameters into a JSON object
      const parameters = {
        symbol: values.symbol,
        grid_number: values.grid_number,
        upper_price: values.upper_price,
        lower_price: values.lower_price,
        amount_per_grid: values.amount_per_grid
      };

      await createStrategy({
        strategy_name: 'SimpleGrid',
        exchange_config_id: values.exchange_config_id,
        parameters: parameters
      });

      message.success('Strategy created successfully');
      setIsModalOpen(false);
      form.resetFields();
      fetchStrategies();
    } catch (error) {
      console.error(error);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteStrategy(id);
      message.success('Strategy deleted');
      fetchStrategies();
    } catch (error) {
      console.error(error);
    }
  };

  const handleStart = async (id: number) => {
    try {
      await startStrategy(id);
      message.success('Strategy started');
      fetchStrategies();
    } catch (error) {
      console.error(error);
    }
  };

  const handleStop = async (id: number) => {
    try {
      await stopStrategy(id);
      message.success('Strategy stopped');
      fetchStrategies();
    } catch (error) {
      console.error(error);
    }
  };

  const columns = [
    {
      title: 'Strategy',
      dataIndex: 'strategy_name',
      key: 'strategy_name',
      render: (text: string) => <span style={{ fontWeight: 'bold' }}>{text}</span>,
    },
    {
      title: 'Symbol',
      dataIndex: ['parameters', 'symbol'],
      key: 'symbol',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        let color = 'default';
        if (status === 'running') color = 'processing';
        if (status === 'error') color = 'error';
        return <Tag color={color}>{status.toUpperCase()}</Tag>;
      },
    },
    {
      title: 'Created At',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text: string) => new Date(text).toLocaleString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: StrategyConfig) => (
        <Space>
          {record.status === 'stopped' ? (
            <Button
              type="primary"
              size="small"
              icon={<PlayCircleOutlined />}
              onClick={() => handleStart(record.id)}
              style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}
            >
              Start
            </Button>
          ) : (
            <Button
              danger
              size="small"
              icon={<PauseCircleOutlined />}
              onClick={() => handleStop(record.id)}
            >
              Stop
            </Button>
          )}

          <Popconfirm
            title="Delete this strategy?"
            onConfirm={() => handleDelete(record.id)}
            okText="Yes"
            cancelText="No"
            disabled={record.status === 'running'}
          >
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              disabled={record.status === 'running'}
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Strategy Dashboard</h2>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchStrategies}>Refresh</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>
            Create Strategy
          </Button>
        </Space>
      </div>

      <Card title="My Strategies" bordered={false}>
        <Table
          dataSource={strategies}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={false}
        />
      </Card>

      <Modal
        title="Create Grid Strategy"
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={() => form.submit()}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleCreate} initialValues={{ grid_number: 10 }}>
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

          <Form.Item
            name="symbol"
            label="Symbol"
            rules={[{ required: true, message: 'e.g. BTC/USDT' }]}
            help="Trading pair (e.g., BTC/USDT)"
          >
            <Input placeholder="BTC/USDT" style={{ textTransform: 'uppercase' }} />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="lower_price"
                label="Lower Price"
                rules={[{ required: true }]}
              >
                <InputNumber style={{ width: '100%' }} min={0} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="upper_price"
                label="Upper Price"
                rules={[{ required: true }]}
              >
                <InputNumber style={{ width: '100%' }} min={0} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="grid_number"
                label="Grid Number"
                rules={[{ required: true }]}
              >
                <InputNumber style={{ width: '100%' }} min={2} max={100} precision={0} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="amount_per_grid"
                label="Amount Per Grid"
                rules={[{ required: true }]}
              >
                <InputNumber style={{ width: '100%' }} min={0} />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
};

export default Dashboard;
