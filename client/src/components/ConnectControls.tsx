import { useState } from "react";
import {
  useRTVIClient,
  useRTVIClientTransportState,
} from "@pipecat-ai/client-react";
import { useDebugScreen } from "../providers/DebugScreenProvider";

export function ConnectControls() {
  const client = useRTVIClient();
  const transportState = useRTVIClientTransportState();
  const [isConnecting, setIsConnecting] = useState(false);
  const { setShowDebugScreen } = useDebugScreen();

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

  const handleShowDebugScreen = () => {
    setShowDebugScreen(true);
  };

  if (isConnected) {
    return null;
  }

  return (
    <div className="connect-controls">
      <div className="transport-selection">
        <div className="connect-button-container">
          <div className="spacer"></div>
          <button
            onClick={handleConnect}
            disabled={isConnecting}
            className="connect-button connect-disconnect-button"
          >
            {isConnecting ? "Connecting..." : "Connect"}
          </button>
          <button 
            onClick={handleShowDebugScreen}
            className="info-button"
          >
            i
          </button>
        </div>
      </div>
    </div>
  );
}
