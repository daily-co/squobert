import { type PropsWithChildren } from "react";
import { RTVIProvider, ProviderType } from "./RTVIProvider";
import { ProviderContextProvider } from "./ProviderContext";

interface VideoProviderProps extends PropsWithChildren {
  onProviderTypeChange?: (type: ProviderType) => void;
}

export function VideoProvider({
  children,
  onProviderTypeChange,
}: VideoProviderProps) {
  const providerType: ProviderType = "webrtc";
  
  // Wrap children with ProviderContext to share provider type information
  const wrappedChildren = (
    <ProviderContextProvider 
      providerType={providerType} 
      setProviderType={onProviderTypeChange}
    >
      {children}
    </ProviderContextProvider>
  );

  return (
    <RTVIProvider>
      {wrappedChildren}
    </RTVIProvider>
  );
}
