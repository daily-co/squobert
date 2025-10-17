# Presence Service Integration

The React client now integrates with the presence detection service via WebSocket.

## What Was Added

### 1. Custom Hook: `src/hooks/usePresence.ts`

A React hook that manages WebSocket connection to the presence service:

- **Auto-reconnection**: Automatically reconnects if connection is lost (default: 5s interval)
- **Console logging**: All presence events are logged to the browser console with `[Presence]` prefix
- **Type-safe**: Full TypeScript support with proper interfaces
- **Configurable**: URL, auto-connect, and reconnect interval can be configured

**Usage:**
```tsx
const { isConnected, isPresent, faceCount, presenceData } = usePresence({
  url: 'ws://localhost:8765/ws',
  autoConnect: true,
  reconnectInterval: 5000, // ms
});
```

**Console Output Example:**
```
[Presence] Attempting to connect to: ws://localhost:8765/ws
[Presence] Connected to presence service
[Presence] Update: {present: true, faces: 1, timestamp: "2025-10-17T12:34:56.789Z"}
[Presence] Update: {present: false, faces: 0, timestamp: "2025-10-17T12:35:01.234Z"}
```

### 2. Configuration: `src/config.ts`

Added `PRESENCE_WS_URL` constant that reads from environment variable:

```typescript
export const PRESENCE_WS_URL = process.env.NEXT_PUBLIC_PRESENCE_WS_URL || "ws://localhost:8765/ws";
```

### 3. App Integration: `src/app/components/App.tsx`

The main App component now uses the `usePresence` hook:

```tsx
const { isConnected: presenceConnected, isPresent, faceCount } = usePresence({
  url: PRESENCE_WS_URL,
  autoConnect: true,
});
```

The values are available but not yet used in the UI. You can access:
- `presenceConnected`: Boolean indicating WebSocket connection status
- `isPresent`: Boolean indicating if faces are detected
- `faceCount`: Number of faces currently detected

### 4. Environment Configuration

Updated `env.example` to include:
```bash
NEXT_PUBLIC_PRESENCE_WS_URL="ws://localhost:8765/ws"
```

## Testing

1. Start the presence service:
   ```bash
   cd presence
   python server.py
   ```

2. Start the React client:
   ```bash
   cd client
   npm run dev
   ```

3. Open browser console (F12) and navigate to the app

4. Look for `[Presence]` logs in the console:
   - Connection status
   - Real-time presence updates as you move in/out of camera view

## Next Steps

The presence data is now available in the App component. You can use it to:

1. **Visual feedback**: Change UI based on presence (e.g., highlight when user is present)
2. **Bot behavior**: Trigger actions when presence changes
3. **Analytics**: Track user presence patterns
4. **Debug panel**: Show presence status in the UI

Example usage in App.tsx:
```tsx
// Show presence indicator
{isPresent && (
  <div className="presence-indicator">
    User detected ({faceCount} face{faceCount !== 1 ? 's' : ''})
  </div>
)}
```

## Graceful Degradation

The integration is designed to work gracefully:
- If presence service is not running, the app will continue to work normally
- Connection attempts will continue in the background
- No errors are thrown to the user
- Console logs provide visibility for debugging
