import {
  useParticipantIds,
  useVideoTrack,
  DailyVideo as DailyReactVideo,
} from "@daily-co/daily-react";

interface DailyVideoProps {
  className?: string;
}

export function DailyVideo({ className }: DailyVideoProps) {
  // Get all remote participant IDs
  const participantIds = useParticipantIds({ filter: "remote" });

  // If there are no remote participants, return null
  if (participantIds.length === 0) {
    console.log("No remote participants");
    return null;
  }

  // We'll let the individual DailyRemoteVideo components handle
  // whether they should render based on video track state
  return (
    <>
      {participantIds.map((participantId) => (
          <DailyRemoteVideo
            key={participantId}
            participantId={participantId}
            className={className}
          />
      ))}
    </>
  );
}

interface DailyRemoteVideoProps {
  participantId: string;
  className?: string;
}

function DailyRemoteVideo({ participantId, className }: DailyRemoteVideoProps) {
  const { state } = useVideoTrack(participantId);

  // Log the video track state for debugging
  console.log(`Participant ${participantId} video state: ${state}`);

  // If video is not available or not playable, return null
  if (state !== "playable") {
    return null;
  }

  return (
    <div className={className}>
      <DailyReactVideo automirror sessionId={participantId} type="video" />
    </div>
  );
}
