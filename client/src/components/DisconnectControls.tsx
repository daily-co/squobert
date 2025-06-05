import { useRTVIClient } from "@pipecat-ai/client-react";
import { useState, useEffect } from "react";
import { useBotExpression } from "../providers/BotExpressionProvider";

export function DisconnectControls() {
  const client = useRTVIClient();
  const [micEnabled, setMicEnabled] = useState(false);
  const { setExpression } = useBotExpression();

  useEffect(() => {
    // Initialize state based on client's current state if possible
    setMicEnabled(false);
  }, [client]);

  const handleDisconnect = async () => {
    try {
      if (!client) {
        throw new Error("RTVI client not available");
      }
      // Reset face to resting before disconnecting
      setExpression("resting");
      await client.disconnect();
    } catch (error) {
      console.error("Failed to disconnect:", error);
    }
  };

  const handleMicToggle = () => {
    // Simple toggle of mic state
    const newState = !micEnabled;
    setMicEnabled(newState);
    if (client) {
      client.enableMic(newState);
    }
  };

  return (
    <div className="connect-controls">
      <div className="transport-selection">
        <button onClick={handleDisconnect} className="connect-button connect-disconnect-button">
          Disconnect
        </button>
        <button
          onClick={handleMicToggle}
          className={`connect-button mic-button ${!micEnabled ? "inactive" : ""}`}
        >
          {micEnabled ? "Mic On" : "Mic Off"}
        </button>
      </div>
    </div>
  );
}
