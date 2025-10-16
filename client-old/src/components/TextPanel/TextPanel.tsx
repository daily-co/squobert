import "./TextPanel.css";

interface TextPanelProps {
  text: string;
}

export function TextPanel({ text }: TextPanelProps) {
  return (
    <div className="text-panel thinking-bubble">
      <div className="bubble-content">
        <div className="text-content">{text}</div>
      </div>
      <div className="bubble-tail">
        <div className="bubble-dot large"></div>
        <div className="bubble-dot medium"></div>
        <div className="bubble-dot small"></div>
      </div>
    </div>
  );
}
