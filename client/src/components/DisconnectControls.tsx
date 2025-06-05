import { useRTVIClient } from "@pipecat-ai/client-react";
import { useState, useEffect, useRef } from "react";

export function DisconnectControls() {
  const client = useRTVIClient();
  const [micEnabled, setMicEnabled] = useState(true);
  const [tempMicState, setTempMicState] = useState<boolean | null>(null);
  const longPressTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const originalMicStateRef = useRef<boolean>(micEnabled);

  useEffect(() => {
    // Initialize state based on client's current state if possible
    setMicEnabled(true);
  }, [client]);

  const handleDisconnect = () => {
    client?.disconnect();
  };

  const setMicState = (enabled: boolean) => {
    if (client) {
      client.enableMic(enabled);
      setMicEnabled(enabled);
    }
  };

  const handleMicMouseDown = () => {
    // Store original state when button is pressed
    originalMicStateRef.current = micEnabled;

    // Set a timeout to detect long press (200ms)
    longPressTimeoutRef.current = setTimeout(() => {
      // Long press detected - temporarily toggle the mic state
      setTempMicState(!micEnabled);
      setMicState(!micEnabled);
    }, 200);
  };

  const handleMicMouseUp = () => {
    // If we have a timeout, it means the button wasn't held long enough
    if (longPressTimeoutRef.current) {
      clearTimeout(longPressTimeoutRef.current);
      longPressTimeoutRef.current = null;

      // Short press - toggle the mic state permanently
      if (tempMicState === null) {
        setMicState(!micEnabled);
      }
      // Long press ended - revert to original state
      else {
        setMicState(originalMicStateRef.current);
        setTempMicState(null);
      }
    }
  };

  const handleMicMouseLeave = () => {
    // If mouse leaves while holding, treat it as a mouse up
    if (longPressTimeoutRef.current) {
      handleMicMouseUp();
    }
  };

  // Determine the actual mic state to display
  const displayMicState = tempMicState !== null ? tempMicState : micEnabled;

  return (
    <div className="connect-controls">
      <div className="transport-selection">
        <button onClick={handleDisconnect} className="connect-button connect-disconnect-button">
          Disconnect
        </button>
        <button
          onMouseDown={handleMicMouseDown}
          onMouseUp={handleMicMouseUp}
          onMouseLeave={handleMicMouseLeave}
          onTouchStart={handleMicMouseDown}
          onTouchEnd={handleMicMouseUp}
          className={`connect-button mic-button ${!displayMicState ? "inactive" : ""}`}
        >
          {displayMicState ? "Mic On" : "Mic Off"}
        </button>
      </div>
    </div>
  );
}
