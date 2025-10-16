import type { Expression } from './types';

interface BlushProps {
  expression: Expression;
}

export function Blush({ expression }: BlushProps) {
  if (expression !== 'laughing' && expression !== 'nervous' && expression !== 'kawaii') {
    return null;
  }

  return (
    <svg className="blush" viewBox="0 0 600 400">
      <ellipse cx="100" cy="230" rx="30" ry="20" fill="#ff9999" opacity="0.6" />
      <ellipse cx="500" cy="230" rx="30" ry="20" fill="#ff9999" opacity="0.6" />
    </svg>
  );
}
