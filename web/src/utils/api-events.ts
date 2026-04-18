import { httpClient } from './http-client';
import type { Event } from '@/types';

export const eventsApi = {
  // Get all events
  async getAllEvents(params?: { since?: string; limit?: number }): Promise<Event[]> {
    return httpClient.get('/api/events/', params);
  },

  // Get node events
  async getNodeEvents(
    nodeId: string,
    params?: { since?: string; limit?: number }
  ): Promise<Event[]> {
    return httpClient.get(`/api/events/node/${nodeId}`, params);
  },

  // Get camera events
  async getCameraEvents(
    nodeId: string,
    cameraId: string,
    params?: { since?: string; limit?: number }
  ): Promise<Event[]> {
    return httpClient.get(`/api/events/camera/${nodeId}/${cameraId}`, params);
  },

  // Subscribe to events (WebSocket, if implemented)
  // For now, this is polling-based - can be upgraded to WebSocket later
  async subscribeToEvents(
    callback: (event: Event) => void,
    options?: {
      scope?: 'camera' | 'node' | 'global';
      nodeId?: string;
      cameraId?: string;
      interval?: number;
    }
  ): Promise<() => void> {
    const interval = options?.interval || 5000; // Poll every 5 seconds
    let lastTimestamp = new Date().toISOString();

    const pollInterval = setInterval(async () => {
      try {
        let events: Event[] = [];

        if (options?.scope === 'camera' && options?.nodeId && options?.cameraId) {
          events = await this.getCameraEvents(options.nodeId, options.cameraId, {
            since: lastTimestamp,
          });
        } else if (options?.scope === 'node' && options?.nodeId) {
          events = await this.getNodeEvents(options.nodeId, {
            since: lastTimestamp,
          });
        } else {
          events = await this.getAllEvents({ since: lastTimestamp });
        }

        if (events.length > 0) {
          lastTimestamp = new Date().toISOString();
          events.forEach(callback);
        }
      } catch (error) {
        console.error('Error polling events:', error);
      }
    }, interval);

    // Return unsubscribe function
    return () => clearInterval(pollInterval);
  },

  // Real-time event stream (placeholder for WebSocket implementation)
  async streamEvents(callback: (event: Event) => void, scope?: string): Promise<() => void> {
    // Currently uses polling, can be upgraded to WebSocket
    return this.subscribeToEvents(callback, { scope: (scope as any) || 'global' });
  },
};
