import { Expression } from "./types";

interface BlushProps {
  expression: Expression;
}

export function Blush({ expression }: BlushProps) {
  // Only show blush for laughing and nervous expressions
  if (
    expression !== "laughing" &&
    expression !== "nervous" &&
    expression !== "kawaii"
  ) {
    return null;
  }

  return (
    <svg className="blush" viewBox="0 0 600 400">
      {/* Left cheek blush */}
      <ellipse cx="100" cy="230" rx="30" ry="20" fill="#ff9999" opacity="0.6" />

      {/* Right cheek blush */}
      <ellipse cx="500" cy="230" rx="30" ry="20" fill="#ff9999" opacity="0.6" />
    </svg>
  );
}
