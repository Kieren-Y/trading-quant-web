import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, Select, Switch, message, Popconfirm, Card } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import { getExchangeConfigs, createExchangeConfig, deleteExchangeConfig } from '../api/exchange';
import type { ExchangeConfig } from '../types';

const Settings: React.FC = () => {
  const [configs, setConfigs] = useState<ExchangeConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();

  const fetchConfigs = async () => {
    setLoading(true);
    try {
      const data = await getExchangeConfigs();
      setConfigs(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConfigs();
  }, []);

  const handleCreate = async (values: any) => {
    try {
      await createExchangeConfig(values);
      message.success('Exchange configuration added successfully');
      setIsModalOpen(false);
      form.resetFields();
      fetchConfigs();
    } catch (error) {
      console.error(error);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteExchangeConfig(id);
      message.success('Configuration deleted');
      fetchConfigs();
    } catch (error) {
      console.error(error);
    }
  };

  const columns = [
    {
      title: 'Exchange',
      dataIndex: 'exchange_name',
      key: 'exchange_name',
      render: (text: string) => text.toUpperCase(),
    },
    {
      title: 'Account Name',
      dataIndex: 'account_name',
      key: 'account_name',
    },
    {
      title: 'API Key',
      dataIndex: 'api_key',
      key: 'api_key',
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => (
        <span style={{ color: active ? 'green' : 'gray' }}>
          {active ? 'Active' : 'Inactive'}
        </span>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: ExchangeConfig) => (
        <Popconfirm
          title="Delete this configuration?"
          onConfirm={() => handleDelete(record.id)}
          okText="Yes"
          cancelText="No"
        >
          <Button type="link" danger icon={<DeleteOutlined />} />
        </Popconfirm>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Settings</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>
          Add Exchange
        </Button>
      </div>

      <Card title="Exchange Configurations" bordered={false}>
        <Table
          columns={columns}
          dataSource={configs}
          rowKey="id"
          loading={loading}
          pagination={false}
        />
      </Card>

      <Modal
        title="Add Exchange Configuration"
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={() => form.submit()}
      >
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item
            name="exchange_name"
            label="Exchange"
            rules={[{ required: true, message: 'Please select an exchange' }]}
          >
            <Select>
              <Select.Option value="binance">Binance</Select.Option>
              <Select.Option value="okx">OKX</Select.Option>
              <Select.Option value="bybit">Bybit</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="account_name"
            label="Account Name (Optional)"
          >
            <Input placeholder="e.g., Main Account" />
          </Form.Item>
          <Form.Item
            name="api_key"
            label="API Key"
            rules={[{ required: true, message: 'Please enter API Key' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="secret_key"
            label="Secret Key"
            rules={[{ required: true, message: 'Please enter Secret Key' }]}
          >
            <Input.Password />
          </Form.Item>
          <Form.Item
            name="is_active"
            label="Active"
            valuePropName="checked"
            initialValue={true}
          >
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Settings;
