import { type PropsWithChildren } from "react";
import { RTVIClient } from "@pipecat-ai/client-js";
import { RTVIClientProvider } from "@pipecat-ai/client-react";
import { SmallWebRTCTransport } from "@pipecat-ai/small-webrtc-transport";
import { DailyTransport } from "@pipecat-ai/daily-transport";

export type ProviderType = "webrtc" | "daily";

interface RTVIProviderProps extends PropsWithChildren {
  hostname?: string;
  providerType: ProviderType;
}

export function RTVIProvider({
  children,
  hostname = "http://localhost:7860",
  providerType,
}: RTVIProviderProps) {
  let rtviConfig;

  if (providerType === "webrtc") {
    console.log("Configuring WebRTC Transport...");
    const transport = new SmallWebRTCTransport();
    rtviConfig = {
      transport,
      enableCam: false,
      enableMic: true,
      params: {
        baseUrl: `${hostname}/api/offer`,
      },
    };
    // @ts-expect-error customConnectHandler is a secret or something
    rtviConfig.customConnectHandler = () => Promise.resolve();
  } else {
    // Daily transport configuration
    console.log("Configuring Daily Transport...");
    const transport = new DailyTransport(); // This would be replaced with DailyTransport in a real implementation
    rtviConfig = {
      transport,
      params: {
        baseUrl: hostname,
        endpoints: {
          connect: "/daily/connect",
        },
      },
      enableMic: true,
      enableCam: false,
    };
  }

  const client = new RTVIClient(rtviConfig);

  return <RTVIClientProvider client={client}>{children}</RTVIClientProvider>;
}
