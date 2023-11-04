import "../App.css";
import React, { useEffect, useState, useRef } from "react";

function SendMessageForm(props: any) {
  const [message, setMessage] = useState<string>("");
  const [sent, setSent] = useState<boolean>(false);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    props.addUserMessage(message);
    setSent(true);
    setMessage("");
  };

  const addAssistantMessage = props.addAssistantMessage;

  useEffect(() => {
    if (sent === true) {
      addAssistantMessage();
      setSent(false);
    }
  }, [sent, addAssistantMessage]);

  const ref = useRef<HTMLFormElement>(null);

function handleKeyUp(e: React.KeyboardEvent<HTMLFormElement>) {
if (e.key === "Enter" && ! e.shiftKey && message.trim() !== "") {
handleSubmit(e);
}
}
  return (
    <div className="bg-gray-900 h-48">
      <form ref={ref} className="flex items-center justify-center"onSubmit={handleSubmit} onKeyUp={handleKeyUp}>
        <textarea className="h-48 w-full bg-gray-700 text-gray-200 text-2xl shadow-lg"
          placeholder="Ask me a question"
	  value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <button disabled={message.trim() === ""} className="w-40 h-48 text-gray-200 bg-gray-900 text-3xl disabled:opacity-50 disabled:bg-gray-700" type="submit">
          Ask
        </button>
      </form>
    </div>
  );
}

export default SendMessageForm;
