import { useCallback, useState, useRef, useEffect } from "react";
import {
  useRTVIClientEvent,
  useRTVIClientMediaTrack,
  useRTVIClient,
  useRTVIClientTransportState,
} from "@pipecat-ai/client-react";
import { RTVIEvent } from "@pipecat-ai/client-js";
import { useBotExpression } from "../../providers/BotExpressionProvider";
import "./BotDisplay.css";
import { TextPanel } from "../TextPanel/TextPanel";
import { BotFace } from "./BotFace";
import { DebugControls } from "./DebugControls";
import { Expression } from "./types";
import { VideoDisplay } from "../VideoDisplay";

// No props needed anymore

export function BotDisplay() {
  const { expression, setExpression } = useBotExpression();
  const [talking, setTalking] = useState(false);
  const transportState = useRTVIClientTransportState();

  const faceRef = useRef<HTMLDivElement>(null);
  const [isBlinking, setIsBlinking] = useState(false);
  const nextBlinkTimeout = useRef<NodeJS.Timeout>();

  const [isLoud, setIsLoud] = useState(false);

  const botAudioTrack = useRTVIClientMediaTrack("audio", "bot");
  const client = useRTVIClient();

  const [showingText, setShowingText] = useState(false);
  const [displayText, setDisplayText] = useState("");

  // Add new state for debug text input
  const [debugText, setDebugText] = useState("");

  // Get all participants with video tracks
  const participants = client?.tracks();
  const [hasVideoTracks, setHasVideoTracks] = useState(false);

  // Check for video tracks
  useEffect(() => {
    if (participants) {
      setHasVideoTracks(Object.values(participants).some((p) => p.video));
    }
  }, [participants]);

  // Set thinking face during connecting state
  useEffect(() => {
    if (
      transportState === "initializing" ||
      transportState === "authenticating"
    ) {
      setExpression("kawaii");
    } else if (transportState === "connected" || transportState === "ready") {
      setExpression("thinking");
    }
  }, [transportState]);

  useEffect(() => {
    if (botAudioTrack) {
      const audioContext = new AudioContext();
      const analyser = audioContext.createAnalyser();
      const source = audioContext.createMediaStreamSource(
        new MediaStream([botAudioTrack])
      );
      source.connect(analyser);
      analyser.fftSize = 32;

      const dataArray = new Uint8Array(analyser.frequencyBinCount);

      const updateAudioLevel = () => {
        analyser.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
        setIsLoud(average > 70);
      };

      const interval = setInterval(updateAudioLevel, 50);

      return () => {
        clearInterval(interval);
        source.disconnect();
        audioContext.close();
      };
    }
  }, [botAudioTrack]);

  useEffect(() => {
    console.log("isLoud", isLoud);
  }, [isLoud]);

  useEffect(() => {
    // Don't blink when laughing or sleeping
    if (expression !== "laughing" && expression !== "sleeping") {
      const blink = () => {
        console.log("blink callback");
        setIsBlinking(true);
        setTimeout(() => setIsBlinking(false), 150);

        // Schedule next blink
        const delay = Math.random() < 0.2 ? 300 : 8000 + Math.random() * 3000;
        nextBlinkTimeout.current = setTimeout(blink, delay);
      };

      console.log("first blink");
      const timer = setTimeout(blink, Math.random() * 10000);

      return () => {
        console.log("clearing blink timers");
        clearTimeout(timer);
        if (nextBlinkTimeout.current) {
          clearTimeout(nextBlinkTimeout.current);
        }
      };
    } else {
      setIsBlinking(false);
    }
  }, [expression]);

  const handleShowText = useCallback(() => {
    setDisplayText(debugText);
    setShowingText(true);
  }, [debugText]);

  const handleHideText = useCallback(() => {
    setShowingText(false);
  }, []);

  // Daily app message handling removed

  // Handle RTVI server messages
  useRTVIClientEvent(
    RTVIEvent.ServerMessage,
    useCallback(
      (serverMessage: {
        event: string;
        data?: { expression: string; text?: string; duration?: number };
      }) => {
        console.log("😹 RTVI Server message received", serverMessage);
        switch (serverMessage.event) {
          case "bot_started_speaking":
            setTalking(true);
            setExpression("resting");
            break;
          case "bot_stopped_speaking":
            setTalking(false);
            break;
          case "expression_change":
            if (typeof serverMessage.data?.expression === "string") {
              const newExpression = serverMessage.data.expression as Expression;
              if (newExpression !== "resting") {
                setExpression(newExpression);
                setTimeout(() => setExpression("resting"), 3000);
              } else {
                setExpression(newExpression);
              }
            }
            break;
          case "user_started_speaking":
            setTalking(false);
            setExpression("listening");
            break;
          case "user_stopped_speaking":
            setTalking(false);
            setExpression("thinking");
            break;
          case "show_text":
            if (serverMessage.data?.text) {
              setDisplayText(serverMessage.data.text);
              setShowingText(true);
              if (serverMessage.data?.duration) {
                setTimeout(
                  () => setShowingText(false),
                  serverMessage.data.duration * 1000
                );
              }
            }
            break;
          case "hide_text":
            setShowingText(false);
            break;
        }
      },
      []
    )
  );

  // Always render the component, regardless of connection status

  return (
    <div className={`bot-container ${hasVideoTracks ? "has-video" : ""}`}>
      <div className="face-container">
        <BotFace
          ref={faceRef}
          expression={expression}
          talking={talking}
          isLoud={isLoud}
          showingText={showingText}
          isBlinking={isBlinking}
        />

        {showingText && <TextPanel text={displayText} />}
      </div>

      <DebugControls
        talking={talking}
        expression={expression}
        debugText={debugText}
        onTalkingToggle={() => setTalking(!talking)}
        onExpressionChange={setExpression}
        onDebugTextChange={setDebugText}
        onShowText={handleShowText}
        onHideText={handleHideText}
      />

      {/* Video container for bot video tracks */}
      {hasVideoTracks && (
        <div className="video-container">
          <VideoDisplay className="video-display" />
        </div>
      )}
    </div>
  );
}
