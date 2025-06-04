import { useParticipantIds, DailyAudio as DailyReactAudio } from "@daily-co/daily-react";

export function DailyAudio() {
  // Get all remote participant IDs
  const participantIds = useParticipantIds({ filter: "remote" });
  
  // If there are no remote participants, return null
  if (participantIds.length === 0) {
    return null;
  }
  
  // Render the Daily audio component that handles all audio tracks
  return <DailyReactAudio />;
}
