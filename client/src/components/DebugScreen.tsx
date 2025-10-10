import React from "react";
import { usePipecatClient } from "@pipecat-ai/client-react";
import { useMicSettings } from "../providers/MicSettingsProvider";

interface DebugScreenProps {
  onClose: () => void;
}

export function DebugScreen({ onClose }: DebugScreenProps) {
  const client = usePipecatClient();
  const { startWithMicEnabled, setStartWithMicEnabled } = useMicSettings();
  const [clientInfo, setClientInfo] = React.useState<any>({});
  console.log({ clientInfo });
  const [ipAddresses, setIpAddresses] = React.useState<string[]>([]);

  // Function to get local IP addresses
  const getLocalIPs = async () => {
    try {
      // Use WebRTC to get local IP addresses
      const pc = new RTCPeerConnection({
        iceServers: [],
      });

      // Create a bogus data channel
      pc.createDataChannel("");

      // Create an offer to trigger candidate gathering
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      // Wait for a bit to gather candidates
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Get the IP addresses from ICE candidates
      const ips: string[] = [];
      pc.localDescription?.sdp.split("\n").forEach((line) => {
        if (line.indexOf("a=candidate:") === 0) {
          const parts = line.split(" ");
          const ip = parts[4];
          if (
            ip &&
            !ip.includes(":") &&
            !ips.includes(ip) &&
            ip !== "0.0.0.0"
          ) {
            ips.push(ip);
          }
        }
      });

      // Clean up
      pc.close();

      return ips;
    } catch (error) {
      console.error("Error getting local IPs:", error);
      return ["Unable to determine local IP"];
    }
  };

  React.useEffect(() => {
    // Get local IP addresses when component mounts
    getLocalIPs().then((ips) => {
      setIpAddresses(ips);
    });

    if (client) {
      // Gather debug information
      const info = {
        // Access properties that we know exist
        participantCount: Object.keys(client.tracks() || {}).length,
        clientVersion: "1.0.0", // Replace with actual version if available
        // Use methods instead of properties
        tracks: client.tracks(),
        // Add any other available information
        timestamp: new Date().toISOString(),
      };

      setClientInfo(info);
    }
  }, [client]);

  const handleOverlayClick = (e: React.MouseEvent) => {
    // Only close if clicking the overlay itself, not its children
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="debug-screen-overlay" onClick={handleOverlayClick}>
      <div className="debug-screen">
        <div className="debug-screen-header">
          <h2>Debug Information</h2>
          <button onClick={onClose} className="close-button">
            ×
          </button>
        </div>

        <div className="debug-screen-content">
          <div className="debug-section">
            <h3>Network</h3>
            <p>
              <strong>Local IP Addresses:</strong>
            </p>
            <ul>
              {ipAddresses.length > 0 ? (
                ipAddresses.map((ip, index) => <li key={index}>{ip}</li>)
              ) : (
                <li>Detecting IP addresses...</li>
              )}
            </ul>
          </div>

          <div className="debug-section">
            <h3>Settings</h3>
            <div className="setting-item">
              <label>
                <input
                  type="checkbox"
                  checked={startWithMicEnabled}
                  onChange={(e) => setStartWithMicEnabled(e.target.checked)}
                />
                Start with microphone enabled
              </label>
              <p className="setting-description">
                When checked, the microphone will be enabled when connecting.
                When unchecked, you'll need to manually enable the mic after connecting.
              </p>
            </div>
          </div>

          <div className="debug-section">
            <button
              onClick={() => window.location.reload()}
              className="debug-action-button"
            >
              Reload
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
