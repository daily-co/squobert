import { useRTVIClientTransportState } from "@pipecat-ai/client-react";
import { VideoProvider } from "./providers/VideoProvider";
import { BotDisplay } from "./components/BotDisplay/BotDisplay";
import { AudioComponent } from "./components/AudioComponent";
import "./App.css";
import { useEffect } from "react";
import { ConnectControls } from "./components/ConnectControls";
import { DisconnectControls } from "./components/DisconnectControls";

function AppContent() {
  // Use the transport state
  const rtviTransportState = useRTVIClientTransportState();
  
  // Determine connection status
  const isConnected = ["connected", "ready", "joining-meeting"].includes(rtviTransportState);
    
  useEffect(() => {
    console.log("RTVI transportState changed:", rtviTransportState);
  }, [rtviTransportState]);

  return (
    <div className="app">
      <div className="content-wrapper">
        <div className="app-container">
          <AudioComponent />
          <BotDisplay />
          <div className="connect-container">
            {!isConnected ? <ConnectControls /> : <DisconnectControls />}
          </div>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <VideoProvider>
      <AppContent />
    </VideoProvider>
  );
}

export default App;
