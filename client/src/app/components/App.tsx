import { useEffect, useRef, useState } from "react";

import type { PipecatBaseChildProps } from "@pipecat-ai/voice-ui-kit";
import {
  ConnectButton,
  UserAudioControl,
  usePipecatConnectionState,
} from "@pipecat-ai/voice-ui-kit";

import type { TransportType } from "../../config";
import { PRESENCE_WS_URL } from "../../config";
import { BotFacePanel } from "./BotFacePanel";
import { TransportDropdown } from "./TransportDropdown";
import { usePresence } from "../../hooks/usePresence";

interface AppProps extends PipecatBaseChildProps {
  transportType: TransportType;
  onTransportChange: (type: TransportType) => void;
  availableTransports: TransportType[];
}

export const App = ({
  client,
  handleConnect,
  handleDisconnect,
  transportType,
  onTransportChange,
  availableTransports,
}: AppProps) => {
  const [showSettings, setShowSettings] = useState(false);
  const [showEvalModal, setShowEvalModal] = useState(false);
  const [evalRoomUrl, setEvalRoomUrl] = useState("");
  const [evalPrompt, setEvalPrompt] = useState("");
  const [squobertSpeaksFirst, setSquobertSpeaksFirst] = useState(false);
  const { isConnected } = usePipecatConnectionState();

  // Load auto-connect setting from localStorage
  const [autoConnectOnPresence, setAutoConnectOnPresence] = useState(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("autoConnectOnPresence");
      return stored !== null ? stored === "true" : true; // Default to true
    }
    return true;
  });

  // Load presence detection setting from localStorage
  const [usePresenceDetection, setUsePresenceDetection] = useState(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("usePresenceDetection");
      return stored !== null ? stored === "true" : true; // Default to true
    }
    return true;
  });

  // Connect to presence service only if enabled
  const {
    isConnected: presenceConnected,
    isPresent,
    faceCount,
  } = usePresence({
    url: PRESENCE_WS_URL,
    autoConnect: usePresenceDetection,
  });

  useEffect(() => {
    client?.initDevices();
  }, [client]);

  // Save auto-connect setting to localStorage
  useEffect(() => {
    if (typeof window !== "undefined") {
      localStorage.setItem(
        "autoConnectOnPresence",
        String(autoConnectOnPresence),
      );
    }
  }, [autoConnectOnPresence]);

  // Save presence detection setting to localStorage
  useEffect(() => {
    if (typeof window !== "undefined") {
      localStorage.setItem(
        "usePresenceDetection",
        String(usePresenceDetection),
      );
    }
  }, [usePresenceDetection]);

  // Track previous presence state to avoid duplicate calls
  const prevIsPresent = useRef(isPresent);

  // Auto-connect/disconnect based on presence
  useEffect(() => {
    console.log("[Presence] Effect triggered:", {
      usePresenceDetection,
      autoConnectOnPresence,
      isPresent,
      prevIsPresent: prevIsPresent.current,
      isConnected,
    });

    if (!usePresenceDetection || !autoConnectOnPresence) return;

    // Only act on presence changes, not initial mount
    if (prevIsPresent.current !== isPresent) {
      if (isPresent && !isConnected && handleConnect) {
        console.log("[Presence] User detected - auto-connecting");
        handleConnect();
      } else if (!isPresent && isConnected && handleDisconnect) {
        console.log("[Presence] User left - auto-disconnecting");
        handleDisconnect();
      }
    }

    prevIsPresent.current = isPresent;
  }, [
    isPresent,
    isConnected,
    usePresenceDetection,
    autoConnectOnPresence,
    handleConnect,
    handleDisconnect,
  ]);

  const hasTransportSelector = availableTransports.length > 1;

  const handleEvalConnect = async () => {
    if (!evalRoomUrl.trim() || !client) return;

    try {
      // Call the API with eval config
      const response = await fetch("/api/start", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          eval: {
            room_url: evalRoomUrl,
            prompt: evalPrompt || undefined,
            squobert_talks_first: squobertSpeaksFirst,
          },
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to start eval session");
      }

      const data = await response.json();

      // Connect to the room using the client
      await client.connect({
        room_url: data.room_url,
        token: data.token,
      });

      // Close the modal
      setShowEvalModal(false);
    } catch (error) {
      console.error("Eval connection error:", error);
      alert("Failed to connect in eval mode. Please check the console for details.");
    }
  };

  return (
    <div className="flex flex-col w-full h-full">
      <div className="relative flex-1 overflow-hidden">
        <div className="face-stage">
          <BotFacePanel
            isPresent={isPresent}
            usePresenceDetection={usePresenceDetection}
          />
          <div className={`control-float ${isConnected ? "connected" : ""}`}>
            <ConnectButton
              size="xl"
              onConnect={handleConnect}
              onDisconnect={handleDisconnect}
            />
            {!isConnected && (
              <button
                type="button"
                className="info-button"
                onClick={() => setShowSettings(true)}
                aria-haspopup="dialog"
                aria-expanded={showSettings}
                aria-label="Show connection settings"
              >
                i
              </button>
            )}
          </div>
        </div>
      </div>

      {showSettings ? (
        <div
          className="control-modal-backdrop"
          role="dialog"
          aria-modal="true"
          aria-label="Connection settings"
          onClick={() => setShowSettings(false)}
        >
          <div
            className="control-modal"
            onClick={(event) => event.stopPropagation()}
          >
            <header className="control-modal-header">
              <h2>Connection Settings</h2>
              <button
                type="button"
                className="close-button"
                onClick={() => setShowSettings(false)}
                aria-label="Close settings"
              >
                ×
              </button>
            </header>
            <div className="control-modal-content">
              {hasTransportSelector ? (
                <section className="control-section">
                  <h3>Transport</h3>
                  <TransportDropdown
                    transportType={transportType}
                    onTransportChange={onTransportChange}
                    availableTransports={availableTransports}
                  />
                </section>
              ) : null}

              <section className="control-section">
                <h3>Microphone</h3>
                <UserAudioControl size="xl" />
              </section>

              <section className="control-section">
                <h3>Presence</h3>
                <label
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    cursor: "pointer",
                    marginBottom: "8px",
                  }}
                >
                  <input
                    type="checkbox"
                    checked={usePresenceDetection}
                    onChange={(e) => setUsePresenceDetection(e.target.checked)}
                    style={{ cursor: "pointer" }}
                  />
                  <span>Enable presence detection</span>
                </label>
                <label
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    cursor: "pointer",
                    opacity: usePresenceDetection ? 1 : 0.5,
                  }}
                >
                  <input
                    type="checkbox"
                    checked={autoConnectOnPresence}
                    onChange={(e) => setAutoConnectOnPresence(e.target.checked)}
                    disabled={!usePresenceDetection}
                    style={{
                      cursor: usePresenceDetection ? "pointer" : "not-allowed",
                    }}
                  />
                  <span>Auto-connect when present</span>
                </label>
                {presenceConnected && (
                  <div
                    style={{
                      marginTop: "8px",
                      fontSize: "0.875rem",
                      opacity: 0.7,
                    }}
                  >
                    Status:{" "}
                    {isPresent
                      ? `Present (${faceCount} face${faceCount !== 1 ? "s" : ""})`
                      : "Not present"}
                  </div>
                )}
              </section>

              <section className="control-section">
                <h3>Eval</h3>
                <button
                  type="button"
                  onClick={() => {
                    setShowSettings(false);
                    setShowEvalModal(true);
                  }}
                  style={{
                    padding: "0.75rem 1.5rem",
                    borderRadius: "0.5rem",
                    border: "1px solid rgba(255, 255, 255, 0.2)",
                    background: "rgba(255, 255, 255, 0.05)",
                    color: "#f1f5f9",
                    cursor: "pointer",
                    fontSize: "0.95rem",
                    fontWeight: "500",
                    transition: "all 0.2s ease",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = "rgba(255, 255, 255, 0.1)";
                    e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.3)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = "rgba(255, 255, 255, 0.05)";
                    e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.2)";
                  }}
                >
                  Open Eval Mode
                </button>
              </section>
            </div>
          </div>
        </div>
      ) : null}

      {showEvalModal ? (
        <div
          className="control-modal-backdrop"
          role="dialog"
          aria-modal="true"
          aria-label="Eval mode settings"
          onClick={() => setShowEvalModal(false)}
        >
          <div
            className="control-modal"
            onClick={(event) => event.stopPropagation()}
          >
            <header className="control-modal-header">
              <h2>Eval Mode</h2>
              <button
                type="button"
                className="close-button"
                onClick={() => setShowEvalModal(false)}
                aria-label="Close eval mode"
              >
                ×
              </button>
            </header>
            <div className="control-modal-content">
              <section className="control-section">
                <label
                  htmlFor="eval-room-url"
                  style={{
                    fontSize: "0.95rem",
                    fontWeight: "500",
                    marginBottom: "0.5rem",
                  }}
                >
                  Daily Room URL
                </label>
                <input
                  id="eval-room-url"
                  type="text"
                  value={evalRoomUrl}
                  onChange={(e) => setEvalRoomUrl(e.target.value)}
                  placeholder="https://..."
                  style={{
                    width: "100%",
                    padding: "0.75rem",
                    borderRadius: "0.5rem",
                    border: "1px solid rgba(255, 255, 255, 0.2)",
                    background: "rgba(255, 255, 255, 0.05)",
                    color: "#f1f5f9",
                    fontSize: "0.95rem",
                  }}
                />
              </section>

              <section className="control-section">
                <label
                  htmlFor="eval-prompt"
                  style={{
                    fontSize: "0.95rem",
                    fontWeight: "500",
                    marginBottom: "0.5rem",
                  }}
                >
                  Prompt
                </label>
                <textarea
                  id="eval-prompt"
                  value={evalPrompt}
                  onChange={(e) => setEvalPrompt(e.target.value)}
                  placeholder="Enter prompt for the eval bot..."
                  rows={4}
                  style={{
                    width: "100%",
                    padding: "0.75rem",
                    borderRadius: "0.5rem",
                    border: "1px solid rgba(255, 255, 255, 0.2)",
                    background: "rgba(255, 255, 255, 0.05)",
                    color: "#f1f5f9",
                    fontSize: "0.95rem",
                    resize: "vertical",
                    fontFamily: "inherit",
                  }}
                />
              </section>

              <section className="control-section">
                <label
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    cursor: "pointer",
                  }}
                >
                  <input
                    type="checkbox"
                    checked={squobertSpeaksFirst}
                    onChange={(e) => setSquobertSpeaksFirst(e.target.checked)}
                    style={{ cursor: "pointer" }}
                  />
                  <span>Squobert speaks first</span>
                </label>
              </section>

              <section className="control-section">
                <button
                  type="button"
                  onClick={handleEvalConnect}
                  disabled={!evalRoomUrl.trim()}
                  style={{
                    width: "100%",
                    padding: "0.875rem 1.5rem",
                    borderRadius: "0.5rem",
                    border: "none",
                    background: evalRoomUrl.trim()
                      ? "rgba(59, 130, 246, 0.8)"
                      : "rgba(255, 255, 255, 0.1)",
                    color: evalRoomUrl.trim()
                      ? "#fff"
                      : "rgba(255, 255, 255, 0.5)",
                    cursor: evalRoomUrl.trim() ? "pointer" : "not-allowed",
                    fontSize: "1rem",
                    fontWeight: "600",
                    transition: "all 0.2s ease",
                  }}
                  onMouseEnter={(e) => {
                    if (evalRoomUrl.trim()) {
                      e.currentTarget.style.background = "rgba(59, 130, 246, 1)";
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (evalRoomUrl.trim()) {
                      e.currentTarget.style.background = "rgba(59, 130, 246, 0.8)";
                    }
                  }}
                >
                  Connect
                </button>
              </section>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
