import "../App.css";
import uuid from 'react-uuid';
import { useRef, useEffect } from "react";

interface MessageListProps {
  messages: Record<string, string>[];
}

function MessageList(props: MessageListProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
  ref.current?.scrollIntoView({
  behavior: "smooth",
  block: "end",
  });
  }, [props.messages]);

  return (
    <div className="flex flex-col w-full h-3/4 bg-gray-800 text-white overflow-y-auto py-8 text-2xl">
      {props.messages.map((message, index) => (
        <div className={`${message['role'] === 'user' ? 'bg-gray-600': ''} w-full shadow-lg justify-start py-4`}>
          <p className="break-words overflow-hidden" key={uuid()}>{message["content"]}</p>
        </div>
      ))}
      <div ref={ref}/>
    </div>
  );
}

export default MessageList;
