import { useEffect } from "react";

import type { PipecatBaseChildProps } from "@pipecat-ai/voice-ui-kit";
import {
  ConnectButton,
  ConversationPanel,
  EventsPanel,
  UserAudioControl,
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
  useEffect(() => {
    client?.initDevices();
  }, [client]);

  const showTransportSelector = availableTransports.length > 1;

  return (
    <div className="flex flex-col w-full h-full">
      <div className="flex items-center justify-between gap-4 p-4">
        {showTransportSelector ? (
          <TransportDropdown
            transportType={transportType}
            onTransportChange={onTransportChange}
            availableTransports={availableTransports}
          />
        ) : (
          <div /> /* Spacer */
        )}
        <div className="flex items-center gap-4">
          <UserAudioControl size="lg" />
          <ConnectButton
            size="lg"
            onConnect={handleConnect}
            onDisconnect={handleDisconnect}
          />
        </div>
      </div>
      <div className="flex-1 overflow-hidden px-4">
        <div className="grid h-full gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
          <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-black/30">
            <BotFacePanel />
          </div>
        </div>
      </div>
    </div>
  );
};
