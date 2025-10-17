import { useCallback, useEffect, useRef, useState } from "react";

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
  const { isConnected } = usePipecatConnectionState();

  // Load auto-connect setting from localStorage
  const [autoConnectOnPresence, setAutoConnectOnPresence] = useState(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('autoConnectOnPresence');
      return stored !== null ? stored === 'true' : true; // Default to true
    }
    return true;
  });

  // Load presence detection setting from localStorage
  const [usePresenceDetection, setUsePresenceDetection] = useState(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('usePresenceDetection');
      return stored !== null ? stored === 'true' : true; // Default to true
    }
    return true;
  });

  // Connect to presence service only if enabled
  const { isConnected: presenceConnected, isPresent, faceCount } = usePresence({
    url: PRESENCE_WS_URL,
    autoConnect: usePresenceDetection,
  });

  useEffect(() => {
    client?.initDevices();
  }, [client]);

  // Save auto-connect setting to localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('autoConnectOnPresence', String(autoConnectOnPresence));
    }
  }, [autoConnectOnPresence]);

  // Save presence detection setting to localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('usePresenceDetection', String(usePresenceDetection));
    }
  }, [usePresenceDetection]);

  // Track previous presence state to avoid duplicate calls
  const prevIsPresent = useRef(isPresent);

  // Auto-connect/disconnect based on presence
  useEffect(() => {
    console.log('[Presence] Effect triggered:', {
      usePresenceDetection,
      autoConnectOnPresence,
      isPresent,
      prevIsPresent: prevIsPresent.current,
      isConnected,
    });

    if (!usePresenceDetection || !autoConnectOnPresence) return;

    // Only act on presence changes, not initial mount
    if (prevIsPresent.current !== isPresent) {
      if (isPresent && !isConnected) {
        console.log('[Presence] User detected - auto-connecting');
        handleConnect();
      } else if (!isPresent && isConnected) {
        console.log('[Presence] User left - auto-disconnecting');
        handleDisconnect();
      }
    }

    prevIsPresent.current = isPresent;
  }, [isPresent, isConnected, usePresenceDetection, autoConnectOnPresence, handleConnect, handleDisconnect]);

  const hasTransportSelector = availableTransports.length > 1;

  return (
    <div className="flex flex-col w-full h-full">
      <div className="relative flex-1 overflow-hidden">
        <div className="face-stage">
          <BotFacePanel isPresent={isPresent} usePresenceDetection={usePresenceDetection} />
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
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', marginBottom: '8px' }}>
                  <input
                    type="checkbox"
                    checked={usePresenceDetection}
                    onChange={(e) => setUsePresenceDetection(e.target.checked)}
                    style={{ cursor: 'pointer' }}
                  />
                  <span>Enable presence detection</span>
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', opacity: usePresenceDetection ? 1 : 0.5 }}>
                  <input
                    type="checkbox"
                    checked={autoConnectOnPresence}
                    onChange={(e) => setAutoConnectOnPresence(e.target.checked)}
                    disabled={!usePresenceDetection}
                    style={{ cursor: usePresenceDetection ? 'pointer' : 'not-allowed' }}
                  />
                  <span>Auto-connect when present</span>
                </label>
                {presenceConnected && (
                  <div style={{ marginTop: '8px', fontSize: '0.875rem', opacity: 0.7 }}>
                    Status: {isPresent ? `Present (${faceCount} face${faceCount !== 1 ? 's' : ''})` : 'Not present'}
                  </div>
                )}
              </section>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
