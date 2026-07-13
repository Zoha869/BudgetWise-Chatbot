import "./../styles/message.css";

function Message({ message }) {
  return (
    <div className={`message-row ${message.role}`}>
      <div className={`message ${message.role}`}>
        {message.text}
      </div>
    </div>
  );
}

export default Message;