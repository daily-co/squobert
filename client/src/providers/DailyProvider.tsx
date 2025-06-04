import { type PropsWithChildren } from "react";
import { DailyProvider as DailyReactProvider } from "@daily-co/daily-react";

interface DailyProviderProps extends PropsWithChildren {
  hostname?: string;
}

export function DailyProvider({
  children,
  hostname = "http://localhost:7860",
}: DailyProviderProps) {
  // The URL for the Daily room
  //const url = `${hostname}/daily/connect`;
  const url = "https://chad-hq.daily.co/aie";

  return <DailyReactProvider url={url}>{children}</DailyReactProvider>;
}
