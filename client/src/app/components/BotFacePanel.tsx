import { useCallback, useEffect, useRef, useState } from 'react';

import {
  usePipecatClient,
  usePipecatClientMediaTrack,
  usePipecatClientTransportState,
  useRTVIClientEvent,
} from '@pipecat-ai/client-react';
import { RTVIEvent } from '@pipecat-ai/client-js';

import { BotFace, type Expression } from './BotFace';
import { TextPanel } from './TextPanel';

type Timeout = ReturnType<typeof setTimeout>;

const EXPRESSION_RESET_DELAY_MS = 3000;

interface BotFacePanelProps {
  isPresent: boolean;
  usePresenceDetection: boolean;
}

export function BotFacePanel({ isPresent, usePresenceDetection }: BotFacePanelProps) {
  const [expression, setExpression] = useState<Expression>('resting');
  const [talking, setTalking] = useState(false);
  const [isBlinking, setIsBlinking] = useState(false);
  const [isLoud, setIsLoud] = useState(false);
  const [showingText, setShowingText] = useState(false);
  const [displayText, setDisplayText] = useState('');

  const transportState = usePipecatClientTransportState();
  const client = usePipecatClient();
  const botAudioTrack = usePipecatClientMediaTrack('audio', 'bot');

  const blinkTimeoutRef = useRef<Timeout | undefined>(undefined);
  const blinkResetRef = useRef<Timeout | undefined>(undefined);
  const expressionResetRef = useRef<Timeout | undefined>(undefined);
  const textResetRef = useRef<Timeout | undefined>(undefined);
  const prevIsPresent = useRef(isPresent);

  useEffect(() => {
    return () => {
      if (blinkTimeoutRef.current) {
        clearTimeout(blinkTimeoutRef.current);
      }
      if (blinkResetRef.current) {
        clearTimeout(blinkResetRef.current);
      }
      if (expressionResetRef.current) {
        clearTimeout(expressionResetRef.current);
      }
      if (textResetRef.current) {
        clearTimeout(textResetRef.current);
      }
    };
  }, []);

  useEffect(() => {
    const scheduleBlink = (initialDelay: number) => {
      blinkTimeoutRef.current = setTimeout(() => {
        setIsBlinking(true);
        blinkResetRef.current = setTimeout(() => {
          setIsBlinking(false);
        }, 150);

        const nextDelay = Math.random() < 0.2 ? 300 : 8000 + Math.random() * 3000;
        scheduleBlink(nextDelay);
      }, initialDelay);
    };

    if (expression === 'laughing') {
      if (blinkTimeoutRef.current) {
        clearTimeout(blinkTimeoutRef.current);
      }
      if (blinkResetRef.current) {
        clearTimeout(blinkResetRef.current);
      }
      setIsBlinking(false);
      return;
    }

    scheduleBlink(Math.random() * 10000);

    return () => {
      if (blinkTimeoutRef.current) {
        clearTimeout(blinkTimeoutRef.current);
      }
      if (blinkResetRef.current) {
        clearTimeout(blinkResetRef.current);
      }
    };
  }, [expression]);

  useEffect(() => {
    if (!botAudioTrack || typeof window === 'undefined') {
      setIsLoud(false);
      return;
    }

    const win = window as typeof window & { webkitAudioContext?: typeof AudioContext };
    const AudioContextCtor = win.AudioContext ?? win.webkitAudioContext;

    if (!AudioContextCtor) {
      return;
    }

    let cancelled = false;
    const audioContext = new AudioContextCtor();
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 32;
    const dataArray = new Uint8Array(analyser.frequencyBinCount);

    let source: MediaStreamAudioSourceNode | undefined;

    try {
      source = audioContext.createMediaStreamSource(new MediaStream([botAudioTrack]));
      source.connect(analyser);
    } catch (error) {
      void audioContext.close();
      console.error('Failed to analyse bot audio track', error);
      return;
    }

    void audioContext.resume().catch(() => undefined);

    const update = () => {
      if (cancelled) {
        return;
      }

      analyser.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
      setIsLoud(average > 70);
      window.setTimeout(update, 50);
    };

    update();

    return () => {
      cancelled = true;
      setIsLoud(false);
      if (source) {
        source.disconnect();
      }
      void audioContext.close();
    };
  }, [botAudioTrack]);

  useEffect(() => {
    if (transportState === 'initializing' || transportState === 'authenticating' || transportState === 'connecting') {
      setExpression('kawaii');
    } else if (transportState === 'connected' || transportState === 'ready') {
      setExpression((prev) => (prev === 'resting' ? 'thinking' : prev));
    } else if (transportState === 'disconnected') {
      // When disconnected, show sleeping if presence detection is enabled and not present, otherwise resting
      if (usePresenceDetection) {
        setExpression(isPresent ? 'resting' : 'sleeping');
      } else {
        setExpression('resting');
      }
      setShowingText(false);
    }
  }, [transportState, isPresent, usePresenceDetection]);

  // Handle presence changes - show kawaii when someone arrives, sleeping when they leave
  useEffect(() => {
    if (!usePresenceDetection) return;

    if (prevIsPresent.current !== isPresent) {
      if (isPresent) {
        // Someone arrived - show kawaii face (regardless of connection state)
        setExpression('kawaii');
        // Reset to resting after a delay
        if (expressionResetRef.current) {
          clearTimeout(expressionResetRef.current);
        }
        expressionResetRef.current = setTimeout(() => {
          setExpression('resting');
        }, EXPRESSION_RESET_DELAY_MS);
      } else if (!isPresent) {
        // No one present - show sleeping (regardless of connection state)
        setExpression('sleeping');
      }
    }
    prevIsPresent.current = isPresent;
  }, [isPresent, transportState, usePresenceDetection]);

  const scheduleExpressionReset = useCallback(() => {
    if (expressionResetRef.current) {
      clearTimeout(expressionResetRef.current);
    }
    expressionResetRef.current = setTimeout(() => {
      setExpression('resting');
    }, EXPRESSION_RESET_DELAY_MS);
  }, []);

  const handleServerMessage = useCallback(
    (serverMessage: { event: string; data?: { expression?: string; text?: string; duration?: number } }) => {
      switch (serverMessage.event) {
        case 'bot_started_speaking':
          setTalking(true);
          setExpression('resting');
          break;
        case 'bot_stopped_speaking':
          setTalking(false);
          break;
        case 'expression_change':
          if (typeof serverMessage.data?.expression === 'string') {
            const newExpression = serverMessage.data.expression as Expression;
            setExpression(newExpression);
            if (newExpression !== 'resting') {
              scheduleExpressionReset();
            }
          }
          break;
        case 'user_started_speaking':
          setTalking(false);
          setExpression('listening');
          break;
        case 'user_stopped_speaking':
          setTalking(false);
          setExpression('thinking');
          scheduleExpressionReset();
          break;
        case 'show_text':
          if (serverMessage.data?.text) {
            setDisplayText(serverMessage.data.text);
            setShowingText(true);
            if (textResetRef.current) {
              clearTimeout(textResetRef.current);
            }
            if (serverMessage.data.duration) {
              textResetRef.current = setTimeout(() => {
                setShowingText(false);
              }, serverMessage.data.duration * 1000);
            }
          }
          break;
        case 'hide_text':
          setShowingText(false);
          setDisplayText('');
          if (textResetRef.current) {
            clearTimeout(textResetRef.current);
          }
          break;
        default:
          break;
      }
    },
    [scheduleExpressionReset],
  );

  useRTVIClientEvent(RTVIEvent.ServerMessage, handleServerMessage);

  useRTVIClientEvent(
    RTVIEvent.BotStartedSpeaking,
    useCallback(() => {
      setTalking(true);
      setExpression('resting');
    }, []),
  );

  useRTVIClientEvent(
    RTVIEvent.BotStoppedSpeaking,
    useCallback(() => {
      setTalking(false);
    }, []),
  );

  useRTVIClientEvent(
    RTVIEvent.UserStartedSpeaking,
    useCallback(() => {
      setTalking(false);
      setExpression('listening');
    }, []),
  );

  useRTVIClientEvent(
    RTVIEvent.UserStoppedSpeaking,
    useCallback(() => {
      setTalking(false);
      setExpression('thinking');
      scheduleExpressionReset();
    }, [scheduleExpressionReset]),
  );

  useEffect(() => {
    if (!client) {
      setIsLoud(false);
    }
  }, [client]);

  return (
    <div className="face-container">
      <BotFace expression={expression} talking={talking} isLoud={isLoud} showingText={showingText} isBlinking={isBlinking} />
      {showingText && displayText ? <TextPanel text={displayText} /> : null}
    </div>
  );
}
