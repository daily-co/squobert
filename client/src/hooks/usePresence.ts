import { useEffect, useRef, useState } from 'react';

interface PresenceData {
  present: boolean;
  face_count: number;
  last_update: string | null;
  error: string | null;
  camera_index: number;
}

interface UsePresenceOptions {
  url?: string;
  autoConnect?: boolean;
  reconnectInterval?: number;
}

export function usePresence(options: UsePresenceOptions = {}) {
  const {
    url = 'ws://localhost:8765/ws',
    autoConnect = true,
    reconnectInterval = 5000,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [presenceData, setPresenceData] = useState<PresenceData | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const shouldReconnectRef = useRef(autoConnect);

  useEffect(() => {
    if (!autoConnect) return;

    const connect = () => {
      // Clear any existing reconnect timeout
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }

      // Don't reconnect if we've been told to stop
      if (!shouldReconnectRef.current) return;

      try {
        console.log('[Presence] Attempting to connect to:', url);
        const ws = new WebSocket(url);

        ws.onopen = () => {
          console.log('[Presence] Connected to presence service');
          setIsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const data: PresenceData = JSON.parse(event.data);
            console.log('[Presence] Update:', {
              present: data.present,
              faces: data.face_count,
              timestamp: data.last_update,
            });
            setPresenceData(data);
          } catch (error) {
            console.error('[Presence] Failed to parse message:', error);
          }
        };

        ws.onerror = (error) => {
          console.error('[Presence] WebSocket error:', error);
        };

        ws.onclose = () => {
          console.log('[Presence] Disconnected from presence service');
          setIsConnected(false);
          wsRef.current = null;

          // Schedule reconnection if we should still be connected
          if (shouldReconnectRef.current) {
            console.log(
              `[Presence] Reconnecting in ${reconnectInterval / 1000}s...`
            );
            reconnectTimeoutRef.current = setTimeout(connect, reconnectInterval);
          }
        };

        wsRef.current = ws;
      } catch (error) {
        console.error('[Presence] Failed to create WebSocket:', error);
        // Try reconnecting
        if (shouldReconnectRef.current) {
          reconnectTimeoutRef.current = setTimeout(connect, reconnectInterval);
        }
      }
    };

    connect();

    // Cleanup function
    return () => {
      shouldReconnectRef.current = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [url, autoConnect, reconnectInterval]);

  return {
    isConnected,
    presenceData,
    isPresent: presenceData?.present ?? false,
    faceCount: presenceData?.face_count ?? 0,
  };
}
