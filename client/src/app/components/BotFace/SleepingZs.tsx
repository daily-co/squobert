import { useEffect, useState } from "react";

export function SleepingZs() {
  const [activeGroup, setActiveGroup] = useState<number | null>(null);

  useEffect(() => {
    // Create a group of Z's every 4 seconds
    const groupInterval = setInterval(() => {
      const groupId = Date.now();
      setActiveGroup(groupId);

      // Remove the group after animation completes
      setTimeout(() => {
        setActiveGroup(null);
      }, 3000);
    }, 4000);

    return () => clearInterval(groupInterval);
  }, []);

  if (!activeGroup) return null;

  return (
    <svg
      className="sleeping-zs"
      viewBox="-300 -150 600 300"
      style={{ position: "absolute", pointerEvents: "none" }}
    >
      {/* First Z */}
      <text
        x="80"
        y="0"
        fontSize="24"
        fontFamily="'Fredoka', 'Comic Sans MS', 'Marker Felt', cursive"
        fontWeight="600"
        fill="#000"
        opacity="0"
      >
        z
        <animate attributeName="y" from="0" to="-90" dur="3s" begin="0s" />
        <animate
          attributeName="opacity"
          values="0;1;1;0"
          keyTimes="0;0.1;0.8;1"
          dur="3s"
          begin="0s"
        />
        <animate
          attributeName="font-size"
          from="24"
          to="40"
          dur="3s"
          begin="0s"
        />
      </text>
      {/* Second Z */}
      <text
        x="115"
        y="0"
        fontSize="24"
        fontFamily="'Fredoka', 'Comic Sans MS', 'Marker Felt', cursive"
        fontWeight="600"
        fill="#000"
        opacity="0"
      >
        z
        <animate attributeName="y" from="0" to="-100" dur="3s" begin="0.3s" />
        <animate
          attributeName="opacity"
          values="0;1;1;0"
          keyTimes="0;0.1;0.8;1"
          dur="3s"
          begin="0.3s"
        />
        <animate
          attributeName="font-size"
          from="26"
          to="44"
          dur="3s"
          begin="0.3s"
        />
      </text>
      {/* Third Z */}
      <text
        x="155"
        y="0"
        fontSize="24"
        fontFamily="'Fredoka', 'Comic Sans MS', 'Marker Felt', cursive"
        fontWeight="600"
        fill="#000"
        opacity="0"
      >
        z
        <animate attributeName="y" from="0" to="-110" dur="3s" begin="0.6s" />
        <animate
          attributeName="opacity"
          values="0;1;1;0"
          keyTimes="0;0.1;0.8;1"
          dur="3s"
          begin="0.6s"
        />
        <animate
          attributeName="font-size"
          from="28"
          to="48"
          dur="3s"
          begin="0.6s"
        />
      </text>
    </svg>
  );
}
