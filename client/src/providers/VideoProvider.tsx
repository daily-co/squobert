import { type PropsWithChildren } from "react";
import { RTVIProvider, ProviderType } from "./RTVIProvider";
import { DailyProvider } from "./DailyProvider";
import { ProviderContextProvider } from "./ProviderContext";

interface VideoProviderProps extends PropsWithChildren {
  hostname?: string;
  providerType: ProviderType;
  onProviderTypeChange?: (type: ProviderType) => void;
}

export function VideoProvider({
  children,
  hostname = "http://localhost:7860",
  providerType,
  onProviderTypeChange,
}: VideoProviderProps) {
  // Wrap children with ProviderContext to share provider type information
  const wrappedChildren = (
    <ProviderContextProvider 
      providerType={providerType} 
      setProviderType={onProviderTypeChange}
    >
      {children}
    </ProviderContextProvider>
  );

  // Conditionally render the appropriate provider based on providerType
  if (providerType === "webrtc") {
    return (
      <RTVIProvider hostname={hostname} providerType={providerType}>
        {wrappedChildren}
      </RTVIProvider>
    );
  } else {
    return (
      <DailyProvider hostname={hostname}>
        {wrappedChildren}
      </DailyProvider>
    );
  }
}
