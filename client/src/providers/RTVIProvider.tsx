import { type PropsWithChildren, useState } from "react";
import { PipecatClient } from "@pipecat-ai/client-js";
import { PipecatClientProvider } from "@pipecat-ai/client-react";
import { SmallWebRTCTransport } from "@pipecat-ai/small-webrtc-transport";
import { useMicSettings } from "./MicSettingsProvider";

export type ProviderType = "webrtc";

interface RTVIProviderProps extends PropsWithChildren {}

// const transport = new DailyTransport();
const transport = new SmallWebRTCTransport({ webrtcUrl: 'http://localhost:7860/api/offer' });

export function RTVIProvider({ children }: RTVIProviderProps) {
  const [participantId, setParticipantId] = useState("");
  const { startWithMicEnabled} = useMicSettings();
  console.log({ participantId });

  const client = new PipecatClient({
    callbacks: {
      onParticipantJoined: (participant) => {
        setParticipantId(participant.id || "");
      },
      onTrackStarted(_track, participant) {
        if (participant?.id && participant.local)
          setParticipantId(participant.id);
      },
    },
    enableCam: false,
    enableMic: startWithMicEnabled, // Use the mic setting from context
    transport,
  });

  // Override the connect method to use custom endpoint
  // const originalConnect = client.connect.bind(client);
  // client.connect = async () => {
  //   const response = await fetch(
  //     "http://localhost:7860/start",
  //     {
  //       method: "POST",
  //       mode: "cors",
  //       headers: {
  //         "Content-Type": "application/json",
  //         Authorization: `Bearer pk_7f7844e5-11e9-4ba1-8fda-4d62e214e05b`,
  //       },
  //       body: JSON.stringify({
  //         createDailyRoom: true,
  //       }),
  //     }
  //   );
  //
  //   if (!response.ok) {
  //     throw new Error("Failed to connect to Pipecat");
  //   }
  //   const data = await response.json();
  //   if (data.error) {
  //     throw new Error(data.error);
  //   }
  //
  //   const connectionParams = {
  //     room_url: data.dailyRoom,
  //     token: data.dailyToken,
  //   };
  //
  //   return originalConnect(connectionParams);
  // };

  return <PipecatClientProvider client={client}>{children}</PipecatClientProvider>;
}
