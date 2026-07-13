import { useState } from "react";
import "./../styles/auth.css";

function LoginModal({
  isOpen,
  onClose,
  onGoogleLogin,
  onEmailLogin
}) {

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  if (!isOpen) return null;

  const submit = (e) => {
    e.preventDefault();

    onEmailLogin(email, password);
  };

  return (

    <div className="modal-overlay">

      <div className="modal">

        <button
          className="close-btn"
          onClick={onClose}
        >
          ×
        </button>

        <h2>Welcome to BudgetWise</h2>

        <p>
          Sign in to continue
        </p>

        <button
          className="google-btn"
          onClick={onGoogleLogin}
        >
          Continue with Google
        </button>

        <div className="divider">
          <span>OR</span>
        </div>

        <form onSubmit={submit}>

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e)=>setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e)=>setPassword(e.target.value)}
            required
          />

          <button
            className="login-submit"
            type="submit"
          >
            Sign In
          </button>

        </form>

      </div>

    </div>

  );
}

export default LoginModal;