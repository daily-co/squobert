import { useRTVIClientTransportState } from "@pipecat-ai/client-react";
import { useMeetingState } from "@daily-co/daily-react";
import { ProviderType } from "./providers/RTVIProvider";
import { VideoProvider } from "./providers/VideoProvider";
import { BotDisplay } from "./components/BotDisplay/BotDisplay";
import { AudioComponent } from "./components/AudioComponent";
import "./App.css";
import { useState, useEffect } from "react";
import { ConnectControls } from "./components/ConnectControls";

function AppContent({
  hostname,
  onHostnameChange,
  providerType,
  onProviderTypeChange,
}: {
  hostname: string;
  onHostnameChange: (hostname: string) => void;
  providerType: ProviderType;
  onProviderTypeChange: (type: ProviderType) => void;
}) {
  // Use the appropriate transport state based on provider type
  const rtviTransportState = useRTVIClientTransportState();
  const dailyMeetingState = useMeetingState();
  
  // Determine connection status based on active provider
  const isConnected = providerType === "webrtc"
    ? ["connected", "ready", "joining-meeting"].includes(rtviTransportState)
    : dailyMeetingState === "joined-meeting";
    
  useEffect(() => {
    if (providerType === "webrtc") {
      console.log("RTVI transportState changed:", rtviTransportState);
    } else {
      console.log("Daily meetingState changed:", dailyMeetingState);
    }
  }, [rtviTransportState, dailyMeetingState, providerType]);

  return (
    <div className="app">
      <div className="content-wrapper">
        {!isConnected && (
          <div className="connect-container">
            <ConnectControls
              hostname={hostname}
              onHostnameChange={onHostnameChange}
              providerType={providerType}
              onProviderTypeChange={onProviderTypeChange}
            />
          </div>
        )}
        <div className="app-container">
          <AudioComponent providerType={providerType} />
          <BotDisplay providerType={providerType} />
        </div>
      </div>
    </div>
  );
}

function App() {
  const [hostname, setHostname] = useState("http://localhost:7860");
  const [providerType, setProviderType] = useState<ProviderType>("webrtc");

  return (
    <VideoProvider
      hostname={hostname}
      providerType={providerType}
      onProviderTypeChange={setProviderType}
    >
      <AppContent
        hostname={hostname}
        onHostnameChange={setHostname}
        providerType={providerType}
        onProviderTypeChange={setProviderType}
      />
    </VideoProvider>
  );
}

export default App;
