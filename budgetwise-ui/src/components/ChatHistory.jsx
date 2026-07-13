import "./../styles/sidebar.css";

function ChatHistory({
  chats,
  activeChat,
  onSelectChat
}) {
  return (
    <div className="history-container">

      <h3>Recent Chats</h3>

      {chats.length === 0 ? (

        <p className="history-empty">
          No conversations yet.
        </p>

      ) : (

        chats.map(chat => (

          <button
            key={chat.id}
            className={`history-item ${
              activeChat === chat.id ? "active" : ""
            }`}
            onClick={() => onSelectChat(chat.id)}
          >

            <div className="history-title">

              {chat.title}

            </div>

            <div className="history-date">

              {chat.date}

            </div>

          </button>

        ))

      )}

    </div>
  );
}

export default ChatHistory;