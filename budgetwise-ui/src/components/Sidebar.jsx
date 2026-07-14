import { FiPlus } from "react-icons/fi";
import { FaRegCommentDots } from "react-icons/fa";

import "../styles/sidebar.css";

export default function Sidebar({
  user,
  conversations = [],
  activeId,
  onNewChat,
  onSelectConversation,
  onLogout,
}) {
  return (
    <aside className="sidebar">

      <div className="sidebar-top">

        <button
          className="new-chat-btn"
          onClick={onNewChat}
        >
          <FiPlus />
          <span>New Chat</span>
        </button>

      </div>


      <div className="history-section">

        <h4>Recent Chats</h4>
        

        <div className="history-list">

          {conversations.length === 0 ? (

            <p className="empty-history">
              No conversations yet.
            </p>

          ) : (

            conversations.map((chat) => (

              <button
                key={chat.id}
                className={`history-item ${
                  activeId === chat.id ? "active" : ""
                }`}
                onClick={() => onSelectConversation(chat.id)}
              >

                <FaRegCommentDots />

                <span>
                  {chat.title}
                </span>

              </button>

            ))

          )}

        </div>

      </div>


      {/* User Section */}

      <div className="sidebar-bottom">

        {user && (
          <p className="user-email">
            {user.email}
          </p>
        )}

        <button
          className="logout-btn"
          onClick={onLogout}
        >
          Logout
        </button>

      </div>


    </aside>
  );
}