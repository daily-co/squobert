import { type PropsWithChildren, useState } from "react";
import { RTVIClient } from "@pipecat-ai/client-js";
import { RTVIClientProvider } from "@pipecat-ai/client-react";
import { DailyTransport } from "@pipecat-ai/daily-transport";

export type ProviderType = "webrtc";

interface RTVIProviderProps extends PropsWithChildren {}

const transport = new DailyTransport();

export function RTVIProvider({ children }: RTVIProviderProps) {
  const [participantId, setParticipantId] = useState("");
  const onConnect = async () => {
    const response = await fetch(
      "https://api.pipecat.daily.co/v1/public/squobert/start",
      {
        method: "POST",
        mode: "cors",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer pk_be409b96-5027-4268-b399-57b5652fa0c3`,
        },
        body: JSON.stringify({
          createDailyRoom: true,
        }),
      }
    );

    if (!response.ok) {
      throw new Error("Failed to connect to Pipecat");
    }
    const data = await response.json();
    if (data.error) {
      throw new Error(data.error);
    }

    return new Response(
      JSON.stringify({
        room_url: data.dailyRoom,
        token: data.dailyToken,
      }),
      { status: 200 }
    );
  };

  const client = new RTVIClient({
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
    enableMic: true,
    params: {
      baseUrl: "noop",
    },
    transport,
    customConnectHandler: (async (_params, timeout) => {
      try {
        const response = await onConnect();
        clearTimeout(timeout);
        if (response.ok) {
          return response.json();
        }
        return Promise.reject(
          new Error(`Connection failed: ${response.status}`)
        );
      } catch (err) {
        return Promise.reject(err);
      }
    }) as (
      params: RTVIClientParams,
      timeout: NodeJS.Timeout | undefined,
      abortController: AbortController
    ) => Promise<void>,
  });
  return <RTVIClientProvider client={client}>{children}</RTVIClientProvider>;
}
