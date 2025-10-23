import type { Expression } from "./types";

interface EyesProps {
  expression: Expression;
  isBlinking: boolean;
}

export function Eyes({ expression, isBlinking }: EyesProps) {
  return (
    <>
      <svg className="eyes" viewBox="-300 -150 600 300">
        {expression === "sleeping" ? (
          <>
            {/* Closed eyes for sleeping */}
            <path
              d="M -210 -20 Q -190 -10, -170 -20"
              fill="none"
              stroke="#000"
              strokeWidth="8"
              strokeLinecap="round"
            />
            <path
              d="M 170 -20 Q 190 -10, 210 -20"
              fill="none"
              stroke="#000"
              strokeWidth="8"
              strokeLinecap="round"
            />
          </>
        ) : expression === "laughing" ? (
          <>
            <path
              d="M -210 -20 Q -190 -40, -170 -20"
              fill="none"
              stroke="#000"
              strokeWidth="8"
              strokeLinecap="round"
            />
            <path
              d="M 170 -20 Q 190 -40, 210 -20"
              fill="none"
              stroke="#000"
              strokeWidth="8"
              strokeLinecap="round"
            />
          </>
        ) : (
          <>
            {isBlinking ? (
              <>
                <path
                  d="M -210 -20 L -170 -20"
                  stroke="#000"
                  strokeWidth="8"
                  strokeLinecap="round"
                />
                <path
                  d="M 170 -20 L 210 -20"
                  stroke="#000"
                  strokeWidth="8"
                  strokeLinecap="round"
                />
              </>
            ) : (
              <>
                <circle
                  cx="-190"
                  cy="-20"
                  r="20"
                  fill="#000"
                  stroke="#000"
                  strokeWidth="4"
                />
                <circle
                  cx="190"
                  cy="-20"
                  r="20"
                  fill="#000"
                  stroke="#000"
                  strokeWidth="4"
                />
                {expression === "kawaii" && (
                  <>
                    <circle cx="-200" cy="-29" r="7" fill="#fff" />
                    <circle cx="-188" cy="-17" r="4" fill="#fff" />
                    <circle cx="180" cy="-29" r="7" fill="#fff" />
                    <circle cx="192" cy="-17" r="4" fill="#fff" />
                  </>
                )}
                {expression === "thinking" && (
                  <>
                    <path
                      d="M -210 -20 A 20 20 0 0 1 -190 -40 L -190 -20 Z"
                      fill="#fff"
                    />
                    <path
                      d="M 170 -20 A 20 20 0 0 1 190 -40 L 190 -20 Z"
                      fill="#fff"
                    />
                  </>
                )}
              </>
            )}
          </>
        )}
      </svg>

      {(expression === "listening" ||
        expression === "thinking" ||
        expression === "nervous") && (
        <svg className="eyebrows" viewBox="-300 -150 600 300">
          <path
            d={
              expression === "nervous"
                ? "M -236 -60 Q -216 -55, -196 -70"
                : "M -220 -50 Q -200 -60, -180 -60"
            }
            fill="none"
            stroke="#000"
            strokeWidth="8"
            strokeLinecap="round"
          />
          {(expression === "listening" || expression === "nervous") && (
            <path
              d={
                expression === "nervous"
                  ? "M 234 -60 Q 214 -55, 194 -70"
                  : "M 220 -50 Q 200 -60, 180 -60"
              }
              fill="none"
              stroke="#000"
              strokeWidth="8"
              strokeLinecap="round"
            />
          )}
        </svg>
      )}
    </>
  );
}
