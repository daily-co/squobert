import { PipecatClientVideo } from "@pipecat-ai/client-react";

interface VideoDisplayProps {
  className?: string;
}

export function VideoDisplay({ className }: VideoDisplayProps) {
  // PipecatClientVideo expects a participant prop
  return <PipecatClientVideo className={className} participant="bot" />;
}
