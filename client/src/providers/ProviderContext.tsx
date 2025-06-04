import { createContext, PropsWithChildren } from "react";
import { ProviderType } from "./RTVIProvider";

interface ProviderContextType {
  providerType: ProviderType;
  setProviderType?: (type: ProviderType) => void;
}

// Create the context with a default value
export const ProviderContext = createContext<ProviderContextType>({
  providerType: "webrtc",
});

interface ProviderContextProviderProps extends PropsWithChildren {
  providerType: ProviderType;
  setProviderType?: (type: ProviderType) => void;
}

export function ProviderContextProvider({
  children,
  providerType,
  setProviderType,
}: ProviderContextProviderProps) {
  return (
    <ProviderContext.Provider value={{ providerType, setProviderType }}>
      {children}
    </ProviderContext.Provider>
  );
}
