import { useEffect } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';

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
}

export function usePresence(options: UsePresenceOptions = {}) {
  const { url = 'ws://localhost:8765/ws', autoConnect = true } = options;

  const { lastJsonMessage, readyState } = useWebSocket<PresenceData>(
    autoConnect ? url : null,
    {
      shouldReconnect: () => true,
      reconnectInterval: 5000,
      reconnectAttempts: Infinity,
    }
  );

  const isConnected = readyState === ReadyState.OPEN;

  useEffect(() => {
    if (lastJsonMessage) {
      console.log('[Presence] Update:', {
        present: lastJsonMessage.present,
        faces: lastJsonMessage.face_count,
        timestamp: lastJsonMessage.last_update,
      });
    }
  }, [lastJsonMessage]);

  useEffect(() => {
    if (readyState === ReadyState.OPEN) {
      console.log('[Presence] Connected to presence service');
    } else if (readyState === ReadyState.CLOSED) {
      console.log('[Presence] Disconnected from presence service');
    }
  }, [readyState]);

  return {
    isConnected,
    presenceData: lastJsonMessage,
    isPresent: lastJsonMessage?.present ?? false,
    faceCount: lastJsonMessage?.face_count ?? 0,
  };
}
