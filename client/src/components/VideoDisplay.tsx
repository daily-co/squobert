import { RTVIClientVideo } from "@pipecat-ai/client-react";

interface VideoDisplayProps {
  className?: string;
}

export function VideoDisplay({ className }: VideoDisplayProps) {
  // RTVIClientVideo expects a participant prop
  return <RTVIClientVideo className={className} participant="bot" />;
}
