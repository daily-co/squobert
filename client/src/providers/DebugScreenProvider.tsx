import { createContext, useContext, useState, ReactNode } from 'react';
import { DebugScreen } from '../components/DebugScreen';

interface DebugScreenContextType {
  showDebugScreen: boolean;
  setShowDebugScreen: (show: boolean) => void;
}

const DebugScreenContext = createContext<DebugScreenContextType | undefined>(undefined);

export const useDebugScreen = () => {
  const context = useContext(DebugScreenContext);
  if (!context) {
    throw new Error('useDebugScreen must be used within a DebugScreenProvider');
  }
  return context;
};

interface DebugScreenProviderProps {
  children: ReactNode;
}

export function DebugScreenProvider({ children }: DebugScreenProviderProps) {
  const [showDebugScreen, setShowDebugScreen] = useState(false);

  const handleCloseDebugScreen = () => {
    setShowDebugScreen(false);
  };

  return (
    <DebugScreenContext.Provider value={{ showDebugScreen, setShowDebugScreen }}>
      {children}
      {showDebugScreen && <DebugScreen onClose={handleCloseDebugScreen} />}
    </DebugScreenContext.Provider>
  );
}
