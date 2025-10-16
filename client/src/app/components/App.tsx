import { useEffect, useState } from "react";

import type { PipecatBaseChildProps } from "@pipecat-ai/voice-ui-kit";
import {
  ConnectButton,
  UserAudioControl,
  usePipecatConnectionState,
} from "@pipecat-ai/voice-ui-kit";

import type { TransportType } from "../../config";
import { BotFacePanel } from "./BotFacePanel";
import { TransportDropdown } from "./TransportDropdown";

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
  const { isConnected, isConnecting } = usePipecatConnectionState();

  useEffect(() => {
    client?.initDevices();
  }, [client]);

  const hasTransportSelector = availableTransports.length > 1;

  return (
    <div className="flex flex-col w-full h-full">
      <div className="relative flex-1 overflow-hidden">
        <div className="face-stage">
          <BotFacePanel />
          <div className={`control-float ${isConnected ? "connected" : ""}`}>
            <ConnectButton
              size="lg"
              onConnect={handleConnect}
              onDisconnect={handleDisconnect}
            />
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
                <UserAudioControl size="lg" />
              </section>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
