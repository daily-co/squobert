import type { Expression } from "./types";

interface BlushProps {
  expression: Expression;
}

export function Blush({ expression }: BlushProps) {
  if (
    expression !== "laughing" &&
    expression !== "nervous" &&
    expression !== "kawaii"
  ) {
    return null;
  }

  return (
    <svg className="blush" viewBox="-300 -150 600 300">
      <ellipse cx="-200" cy="30" rx="30" ry="20" fill="#ff9999" opacity="0.6" />
      <ellipse cx="200" cy="30" rx="30" ry="20" fill="#ff9999" opacity="0.6" />
    </svg>
  );
}
