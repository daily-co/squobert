import { Expression } from "./types";
import { useRTVIClient } from "@pipecat-ai/client-react";
import { useDaily } from "@daily-co/daily-react";
import { useState, useEffect } from "react";

interface DebugControlsProps {
  talking: boolean;
  expression: Expression;
  debugText: string;
  onTalkingToggle: () => void;
  onExpressionChange: (expression: Expression) => void;
  onDebugTextChange: (text: string) => void;
  onShowText: () => void;
  onHideText: () => void;
  providerType?: "webrtc" | "daily";
}

export function DebugControls({
  talking,
  expression,
  debugText,
  onTalkingToggle,
  onExpressionChange,
  onDebugTextChange,
  onShowText,
  onHideText,
  providerType = "webrtc",
}: DebugControlsProps) {
  const client = useRTVIClient();
  const daily = useDaily();
  const [micEnabled, setMicEnabled] = useState(true);
  const [camEnabled, setCamEnabled] = useState(true);

  useEffect(() => {
    // Initialize state based on client's current state if possible
    // Note: This is a best effort as the client may not expose this state directly
    setMicEnabled(true);
    setCamEnabled(true);
  }, [client]);

  const handleDisconnect = () => {
    if (providerType === "webrtc") {
      client?.disconnect();
    } else if (providerType === "daily") {
      daily?.leave();
    }
  };

  const toggleMic = () => {
    const newState = !micEnabled;
    if (providerType === "webrtc" && client) {
      client.enableMic(newState);
      setMicEnabled(newState);
    } else if (providerType === "daily" && daily) {
      daily.setLocalAudio(newState);
      setMicEnabled(newState);
    }
  };

  const toggleCam = () => {
    const newState = !camEnabled;
    if (providerType === "webrtc" && client) {
      client.enableCam(newState);
      setCamEnabled(newState);
    } else if (providerType === "daily" && daily) {
      daily.setLocalVideo(newState);
      setCamEnabled(newState);
    }
  };

  return (
    <div className="debug-controls">
      <div className="debug-row">
        <button onClick={handleDisconnect}>Disconnect</button>
        <button onClick={onTalkingToggle} className={talking ? "active" : ""}>
          {talking ? "Stop Talking" : "Start Talking"}
        </button>
        <button onClick={toggleMic} className={micEnabled ? "active" : ""}>
          {micEnabled ? "Mic On" : "Mic Off"}
        </button>
        <button onClick={toggleCam} className={camEnabled ? "active" : ""}>
          {camEnabled ? "Camera On" : "Camera Off"}
        </button>
        {[
          "resting",
          "listening",
          "thinking",
          "laughing",
          "nervous",
          "kawaii",
        ].map((expr) => (
          <button
            key={expr}
            onClick={() => onExpressionChange(expr as Expression)}
            className={expression === expr ? "active" : ""}
          >
            {expr}
          </button>
        ))}
      </div>
      <div className="debug-row">
        <input
          type="text"
          value={debugText}
          onChange={(e) => onDebugTextChange(e.target.value)}
          placeholder="Enter text to show..."
        />
        <button onClick={onShowText}>Show Text</button>
        <button onClick={onHideText}>Hide Text</button>
      </div>
    </div>
  );
}
