import { Expression } from "./types";

interface MouthProps {
  expression: Expression;
}

export function Mouth({ expression }: MouthProps) {
  return (
    <svg className="mouth-shape" viewBox="0 0 600 400">
      {expression === "laughing" && (
        <path d="M 250 194 A 50 50 0 0 0 350 194" fill="#000" stroke="none" />
      )}
      {expression === "thinking" && (
        <path
          d="M 270 210 Q 310 200, 330 220"
          fill="none"
          stroke="#000"
          strokeWidth="8"
          strokeLinecap="round"
        />
      )}
      {expression === "resting" && (
        <path
          d="M 250 210 Q 300 240, 350 210"
          fill="none"
          stroke="#000"
          strokeWidth="8"
          strokeLinecap="round"
        />
      )}
      {expression === "listening" && (
        <path
          d="M 280 210 L 320 210"
          fill="none"
          stroke="#000"
          strokeWidth="8"
          strokeLinecap="round"
        />
      )}
      {expression === "kawaii" && (
        <>
          <path
            d="M 250 210 Q 275 230, 300 210"
            fill="none"
            stroke="#000"
            strokeWidth="8"
            strokeLinecap="round"
          />
          <path
            d="M 300 210 Q 325 230, 350 210"
            fill="none"
            stroke="#000"
            strokeWidth="8"
            strokeLinecap="round"
          />
        </>
      )}
      {expression === "nervous" && (
        <path
          d="M 260 200 L 270 210 L 280 200 L 290 210 L 300 200 L 310 210 L 320 200 L 330 210 L 340 200"
          fill="none"
          stroke="#000"
          strokeWidth="8"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      )}
    </svg>
  );
}
