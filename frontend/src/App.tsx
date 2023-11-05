import React, { useState } from "react";
import "./App.css";
import Header from "./components/Header";
import MessageList from "./components/MessageList";
import SendMessageForm from "./components/SendMessageForm";
import { getApiResponse } from "./utils";

function App() {
  const [messages, setMessages] = useState<Record<string, string>[]>([]);

  const addUserMessage = (message: string) => {
    setMessages([...messages, { role: "user", content: message }]);
  };

  const addAssistantMessage = async () => {
    setMessages([...messages, { role: "assistant", content: "Thinking..." }]);
    let responseContent = await getApiResponse(messages);
    setMessages([...messages, { role: "assistant", content: responseContent }]);
  };

  return (
    <div className="h-screen bg-gray-800 font-serif">
      <Header />
      <MessageList messages={messages} />
      <SendMessageForm
        addUserMessage={addUserMessage}
        addAssistantMessage={addAssistantMessage}
      />
    </div>
  );
}

export default App;
