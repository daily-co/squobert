import { createContext, useContext, useState, ReactNode } from 'react';
import { Expression } from '../components/BotDisplay/types';

interface BotExpressionContextType {
  expression: Expression;
  setExpression: (expression: Expression) => void;
}

const BotExpressionContext = createContext<BotExpressionContextType | undefined>(undefined);

interface BotExpressionProviderProps {
  children: ReactNode;
}

export function BotExpressionProvider({ children }: BotExpressionProviderProps) {
  const [expression, setExpression] = useState<Expression>('resting');

  return (
    <BotExpressionContext.Provider value={{ expression, setExpression }}>
      {children}
    </BotExpressionContext.Provider>
  );
}

export function useBotExpression() {
  const context = useContext(BotExpressionContext);
  if (context === undefined) {
    throw new Error('useBotExpression must be used within a BotExpressionProvider');
  }
  return context;
}
