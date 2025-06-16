import { createContext, useContext, useState, ReactNode, useEffect } from 'react';

interface MicSettingsContextType {
  startWithMicEnabled: boolean;
  setStartWithMicEnabled: (enabled: boolean) => void;
}

const MicSettingsContext = createContext<MicSettingsContextType | undefined>(undefined);

interface MicSettingsProviderProps {
  children: ReactNode;
}

export function MicSettingsProvider({ children }: MicSettingsProviderProps) {
  // Initialize from localStorage if available, default to true
  const [startWithMicEnabled, setStartWithMicEnabled] = useState<boolean>(() => {
    const savedSetting = localStorage.getItem('startWithMicEnabled');
    return savedSetting !== null ? savedSetting === 'true' : true;
  });

  // Save to localStorage when changed
  useEffect(() => {
    localStorage.setItem('startWithMicEnabled', startWithMicEnabled.toString());
  }, [startWithMicEnabled]);

  return (
    <MicSettingsContext.Provider value={{ startWithMicEnabled, setStartWithMicEnabled }}>
      {children}
    </MicSettingsContext.Provider>
  );
}

export function useMicSettings() {
  const context = useContext(MicSettingsContext);
  if (context === undefined) {
    throw new Error('useMicSettings must be used within a MicSettingsProvider');
  }
  return context;
}
