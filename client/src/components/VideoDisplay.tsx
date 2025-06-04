import { RTVIClientVideo } from "@pipecat-ai/client-react";
import { DailyVideo } from "./DailyComponents/DailyVideo";
import { ProviderType } from "../providers/RTVIProvider";

interface VideoDisplayProps {
  className?: string;
  providerType: ProviderType;
}

export function VideoDisplay({ className, providerType }: VideoDisplayProps) {
  if (providerType === "daily") {
    return <DailyVideo className={className} />;
  } else {
    // RTVIClientVideo expects a participant prop
    return <RTVIClientVideo className={className} participant="bot" />;
  }
}
