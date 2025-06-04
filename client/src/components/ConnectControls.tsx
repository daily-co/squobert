import { useState } from "react";
import {
  useRTVIClient,
  useRTVIClientTransportState,
} from "@pipecat-ai/client-react";
import { useDaily, useAppMessage } from "@daily-co/daily-react";
import { ProviderType } from "../providers/RTVIProvider";

interface ConnectControlsProps {
  hostname: string;
  onHostnameChange: (hostname: string) => void;
  providerType: ProviderType;
  onProviderTypeChange: (type: ProviderType) => void;
}

export function ConnectControls({
  hostname,
  onHostnameChange,
  providerType,
  onProviderTypeChange,
}: ConnectControlsProps) {
  const client = useRTVIClient();
  const transportState = useRTVIClientTransportState();
  const daily = useDaily();
  const [isConnecting, setIsConnecting] = useState(false);
  const [dailyConnected, setDailyConnected] = useState(false);

  // Listen for Daily connection state changes
  useAppMessage({
    onAppMessage: (event) => {
      if (
        event.data?.type === "daily-state-update" &&
        event.data?.state === "connected"
      ) {
        setDailyConnected(true);
      }
    },
  });

  // Determine if connected based on the active provider
  const isConnected =
    providerType === "webrtc"
      ? ["connected", "ready"].includes(transportState)
      : dailyConnected;

  const handleConnect = async () => {
    setIsConnecting(true);
    try {
      if (providerType === "webrtc") {
        if (!client) {
          throw new Error("RTVI client not available");
        }
        await client.connect();
      } else if (providerType === "daily") {
        if (!daily) {
          throw new Error("Daily client not available");
        }
        // We need to POST to the RTVI endpoint to start a bot
        await fetch(`${hostname}/daily/connect`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({}),
        });
        // Daily connection is handled by the DailyProvider
        // We just need to join the room
        await daily.join();

        // Send a message to notify that Daily is connected
        daily.sendAppMessage({
          type: "daily-state-update",
          state: "connected",
        });
      }
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
      <div className="hostname-input">
        <label htmlFor="hostname">Bot Server URL:</label>
        <input
          id="hostname"
          type="text"
          value={hostname}
          onChange={(e) => onHostnameChange(e.target.value)}
          placeholder="http://localhost:7860"
        />
      </div>
      <div className="transport-selection">
        <div className="segmented-control">
          <button
            onClick={() => onProviderTypeChange("webrtc")}
            className={`segment ${providerType === "webrtc" ? "active" : ""}`}
            disabled={isConnecting}
          >
            WebRTC
          </button>
          <button
            onClick={() => onProviderTypeChange("daily")}
            className={`segment ${providerType === "daily" ? "active" : ""}`}
            disabled={isConnecting}
          >
            Daily
          </button>
        </div>
        <button
          onClick={handleConnect}
          disabled={isConnecting || !hostname.trim()}
          className="connect-btn"
        >
          {isConnecting ? "Connecting..." : "Connect"}
        </button>
      </div>
    </div>
  );
}
