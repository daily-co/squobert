import { RTVIClientAudio } from "@pipecat-ai/client-react";
import { DailyAudio } from "./DailyComponents/DailyAudio";
import { ProviderType } from "../providers/RTVIProvider";

interface AudioComponentProps {
  providerType: ProviderType;
}

export function AudioComponent({ providerType }: AudioComponentProps) {
  if (providerType === "daily") {
    return <DailyAudio />;
  } else {
    return <RTVIClientAudio />;
  }
}
