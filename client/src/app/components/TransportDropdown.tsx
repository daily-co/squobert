import {
  Button,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@pipecat-ai/voice-ui-kit';
import { ChevronDown, Network } from 'lucide-react';

import type { TransportType } from '../../config';

interface TransportDropdownProps {
  transportType: TransportType;
  onTransportChange: (type: TransportType) => void;
  availableTransports: TransportType[];
}

const TRANSPORT_LABELS: Record<TransportType, string> = {
  daily: 'Daily',
  smallwebrtc: 'SmallWebRTC',
};

export const TransportDropdown = ({
  transportType,
  onTransportChange,
  availableTransports,
}: TransportDropdownProps) => {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="lg" className="gap-2">
          <Network />
          Transport: {TRANSPORT_LABELS[transportType]}
          <ChevronDown />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        {availableTransports.map((transport) => (
          <DropdownMenuItem
            key={transport}
            onClick={() => onTransportChange(transport)}>
            {TRANSPORT_LABELS[transport]}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
