import { httpClient } from './http-client';
import type { SystemConfig, CameraConfig, NodeConfig, ConfigSchema } from '@/types';

export const configApi = {
  // System Config
  async getSystemConfig(): Promise<SystemConfig> {
    return httpClient.get('/api/config/system');
  },

  async setSystemConfig(config: Partial<SystemConfig>): Promise<SystemConfig> {
    return httpClient.post('/api/config/system', config);
  },

  async getSystemConfigValue(key: string): Promise<any> {
    return httpClient.get(`/api/config/system/${key}`);
  },

  async setSystemConfigValue(key: string, value: any): Promise<{ value: any }> {
    return httpClient.post(`/api/config/system/${key}`, { value });
  },

  async deleteSystemConfigValue(key: string): Promise<void> {
    return httpClient.delete(`/api/config/system/${key}`);
  },

  // Camera Config
  async getCameraConfig(nodeId: string, cameraId: string): Promise<CameraConfig> {
    return httpClient.get(`/api/config/camera/${nodeId}/${cameraId}`);
  },

  async setCameraConfig(
    nodeId: string,
    cameraId: string,
    config: Partial<CameraConfig>
  ): Promise<CameraConfig> {
    return httpClient.post(`/api/config/camera/${nodeId}/${cameraId}`, config);
  },

  async setCameraConfigValue(
    nodeId: string,
    cameraId: string,
    key: string,
    value: any
  ): Promise<{ value: any }> {
    return httpClient.post(`/api/config/camera/${nodeId}/${cameraId}/${key}`, {
      value,
    });
  },

  async deleteCameraConfigValue(
    nodeId: string,
    cameraId: string,
    key: string
  ): Promise<void> {
    return httpClient.delete(`/api/config/camera/${nodeId}/${cameraId}/${key}`);
  },

  // Node Config
  async getNodeConfig(nodeId: string): Promise<NodeConfig> {
    return httpClient.get(`/api/config/node/${nodeId}`);
  },

  async setNodeConfig(nodeId: string, config: Partial<NodeConfig>): Promise<NodeConfig> {
    return httpClient.post(`/api/config/node/${nodeId}`, config);
  },

  async setNodeConfigValue(nodeId: string, key: string, value: any): Promise<{ value: any }> {
    return httpClient.post(`/api/config/node/${nodeId}/${key}`, { value });
  },

  async deleteNodeConfigValue(nodeId: string, key: string): Promise<void> {
    return httpClient.delete(`/api/config/node/${nodeId}/${key}`);
  },

  // Config Schema
  async getConfigSchema(): Promise<{
    system: ConfigSchema;
    camera: ConfigSchema;
    node: ConfigSchema;
  }> {
    return httpClient.get('/api/config/schema');
  },

  async getSystemConfigSchema(): Promise<ConfigSchema> {
    return httpClient.get('/api/config/schema/system');
  },

  async getCameraConfigSchema(): Promise<ConfigSchema> {
    return httpClient.get('/api/config/schema/camera');
  },

  async getNodeConfigSchema(): Promise<ConfigSchema> {
    return httpClient.get('/api/config/schema/node');
  },
};
