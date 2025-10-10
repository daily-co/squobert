import { Expression } from "./types";
import { useRTVIClient } from "@pipecat-ai/client-react";
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
}: DebugControlsProps) {
  const client = useRTVIClient();
  const [camEnabled, setCamEnabled] = useState(true);

  useEffect(() => {
    // Initialize state based on client's current state if possible
    // Note: This is a best effort as the client may not expose this state directly
    setCamEnabled(true);
  }, [client]);



  const toggleCam = () => {
    const newState = !camEnabled;
    if (client) {
      client.enableCam(newState);
      setCamEnabled(newState);
    }
  };

  return (
    <div className="debug-controls">
      <div className="debug-row">
        <button onClick={onTalkingToggle} className={talking ? "active" : ""}>
          {talking ? "Stop Talking" : "Start Talking"}
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
          "sleeping",
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
