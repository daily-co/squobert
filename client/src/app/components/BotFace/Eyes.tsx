import type { Expression } from './types';

interface EyesProps {
  expression: Expression;
  isBlinking: boolean;
}

export function Eyes({ expression, isBlinking }: EyesProps) {
  return (
    <>
      <svg className="eyes" viewBox="0 0 600 400">
        {expression === 'laughing' ? (
          <>
            <path d="M 90 180 Q 110 160, 130 180" fill="none" stroke="#000" strokeWidth="8" strokeLinecap="round" />
            <path d="M 470 180 Q 490 160, 510 180" fill="none" stroke="#000" strokeWidth="8" strokeLinecap="round" />
          </>
        ) : (
          <>
            {isBlinking ? (
              <>
                <path d="M 90 180 L 130 180" stroke="#000" strokeWidth="8" strokeLinecap="round" />
                <path d="M 470 180 L 510 180" stroke="#000" strokeWidth="8" strokeLinecap="round" />
              </>
            ) : (
              <>
                <circle cx="110" cy="180" r="20" fill="#000" stroke="#000" strokeWidth="4" />
                <circle cx="490" cy="180" r="20" fill="#000" stroke="#000" strokeWidth="4" />
                {expression === 'kawaii' && (
                  <>
                    <circle cx="100" cy="171" r="7" fill="#fff" />
                    <circle cx="112" cy="183" r="4" fill="#fff" />
                    <circle cx="480" cy="171" r="7" fill="#fff" />
                    <circle cx="492" cy="183" r="4" fill="#fff" />
                  </>
                )}
                {expression === 'thinking' && (
                  <>
                    <path d="M 90 180 A 20 20 0 0 1 110 160 L 110 180 Z" fill="#fff" />
                    <path d="M 470 180 A 20 20 0 0 1 490 160 L 490 180 Z" fill="#fff" />
                  </>
                )}
              </>
            )}
          </>
        )}
      </svg>

      {(expression === 'listening' || expression === 'thinking' || expression === 'nervous') && (
        <svg className="eyebrows" viewBox="0 0 600 400">
          <path
            d={expression === 'nervous' ? 'M 64 140 Q 84 145, 104 130' : 'M 80 150 Q 100 140, 120 140'}
            fill="none"
            stroke="#000"
            strokeWidth="8"
            strokeLinecap="round"
          />
          {(expression === 'listening' || expression === 'nervous') && (
            <path
              d={expression === 'nervous' ? 'M 534 140 Q 514 145, 494 130' : 'M 520 150 Q 500 140, 480 140'}
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
