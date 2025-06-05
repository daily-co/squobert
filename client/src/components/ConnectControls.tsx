import { useState } from "react";
import {
  useRTVIClient,
  useRTVIClientTransportState,
} from "@pipecat-ai/client-react";

export function ConnectControls() {
  const client = useRTVIClient();
  const transportState = useRTVIClientTransportState();
  const [isConnecting, setIsConnecting] = useState(false);

  // Determine if connected
  const isConnected = ["connected", "ready"].includes(transportState);

  const handleConnect = async () => {
    setIsConnecting(true);
    try {
      if (!client) {
        throw new Error("RTVI client not available");
      }
      await client.connect();
    } catch (error) {
      console.error("Failed to connect:", error);
    } finally {
      setIsConnecting(false);
    }
  };

  if (isConnected) {
    return null;
  }

  return (
    <div className="connect-controls">
      <div className="transport-selection">
        <button
          onClick={handleConnect}
          disabled={isConnecting}
          className="connect-btn"
        >
          {isConnecting ? "Connecting..." : "Connect"}
        </button>
      </div>
    </div>
  );
}
