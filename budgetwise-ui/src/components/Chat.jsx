import Message from "./Message";
import InputBox from "./InputBox";
import TypingIndicator from "./TypingIndicator";
import "./../styles/chat.css";

function Chat({
  messages,
  loading,
  onSend
}) {

  return (
    <div className="chat-container">

      <div className="chat-header">
        <h2>BudgetWise AI</h2>
        <p>Your Personal Finance Assistant</p>
      </div>

      <div className="chat-body">

        {messages.length === 0 && (
          <div className="empty-chat">

            <div className="empty-icon">
              💰
            </div>

            <h2>Welcome to BudgetWise</h2>

            <p>
              Ask me anything about budgeting,
              saving, investing, debt management,
              or personal finance.
            </p>

            <div className="suggestions">

              <button
                onClick={() => onSend("Help me create a monthly budget")}
              >
                💵 Create Budget
              </button>

              <button
                onClick={() => onSend("How can I save more money?")}
              >
                📈 Saving Tips
              </button>

              <button
                onClick={() => onSend("How should I pay off debt?")}
              >
                💳 Debt Plan
              </button>

              <button
                onClick={() => onSend("Teach me investing")}
              >
                📊 Investing
              </button>

            </div>

          </div>
        )}

        {messages.map((message, index) => (
          <Message
            key={index}
            message={message}
          />
        ))}

        {loading && <TypingIndicator />}

      </div>

      <InputBox onSend={onSend} />

    </div>
  );
}

export default Chat;