import "./../styles/chat.css";

function TypingIndicator() {
  return (
    <div className="message-row bot">
      <div className="typing-box">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  );
}

export default TypingIndicator;