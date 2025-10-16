import { forwardRef } from 'react';

import { Blush } from './Blush';
import { Eyes } from './Eyes';
import { Mouth } from './Mouth';
import type { Expression } from './types';

interface BotFaceProps {
  expression: Expression;
  talking: boolean;
  isLoud: boolean;
  showingText: boolean;
  isBlinking: boolean;
}

export const BotFace = forwardRef<HTMLDivElement, BotFaceProps>(
  ({ expression, talking, isLoud, showingText, isBlinking }, ref) => {
    return (
      <div
        ref={ref}
        className={`face ${expression} ${talking && isLoud ? 'talking' : ''} ${showingText ? 'showing-text' : ''}`}
      >
        <Blush expression={expression} />
        <Eyes expression={expression} isBlinking={isBlinking} />
        <Mouth expression={expression} />
      </div>
    );
  },
);

BotFace.displayName = 'BotFace';
