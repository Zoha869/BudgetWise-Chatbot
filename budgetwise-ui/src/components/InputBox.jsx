import { useState } from "react";
import "./../styles/chat.css";

function InputBox({ onSend }) {
  const [text, setText] = useState("");

  const send = () => {
    if (!text.trim()) return;

    onSend(text);

    setText("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className="input-container">
      <textarea
        placeholder="Ask BudgetWise anything..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        rows={1}
      />

      <button onClick={send}>
        Send
      </button>
    </div>
  );
}

export default InputBox;