import type { Expression } from "./types";

interface MouthProps {
  expression: Expression;
}

export function Mouth({ expression }: MouthProps) {
  return (
    <svg className="mouth-shape" viewBox="-300 -150 600 300">
      {expression === "laughing" && (
        <path d="M -50 -6 A 50 50 0 0 0 50 -6" fill="#000" stroke="none" />
      )}
      {expression === "thinking" && (
        <path
          d="M -30 10 Q 10 0, 30 20"
          fill="none"
          stroke="#000"
          strokeWidth="8"
          strokeLinecap="round"
        />
      )}
      {expression === "resting" && (
        <path
          d="M -50 10 Q 0 40, 50 10"
          fill="none"
          stroke="#000"
          strokeWidth="8"
          strokeLinecap="round"
        />
      )}
      {expression === "listening" && (
        <path
          d="M -20 10 L 20 10"
          fill="none"
          stroke="#000"
          strokeWidth="8"
          strokeLinecap="round"
        />
      )}
      {expression === "kawaii" && (
        <>
          <path
            d="M -50 10 Q -25 30, 0 10"
            fill="none"
            stroke="#000"
            strokeWidth="8"
            strokeLinecap="round"
          />
          <path
            d="M 0 10 Q 25 30, 50 10"
            fill="none"
            stroke="#000"
            strokeWidth="8"
            strokeLinecap="round"
          />
        </>
      )}
      {expression === "nervous" && (
        <path
          d="M -40 0 L -30 10 L -20 0 L -10 10 L 0 0 L 10 10 L 20 0 L 30 10 L 40 0"
          fill="none"
          stroke="#000"
          strokeWidth="8"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      )}
      {expression === "sleeping" && (
        <>
          <path
            d="M -50 10 Q -25 30, 0 10"
            fill="none"
            stroke="#000"
            strokeWidth="8"
            strokeLinecap="round"
          />
          <path
            d="M 0 10 Q 25 30, 50 10"
            fill="none"
            stroke="#000"
            strokeWidth="8"
            strokeLinecap="round"
          />
        </>
      )}
    </svg>
  );
}
