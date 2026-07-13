import {
  FiArrowRight,
  FiDollarSign,
  FiPieChart,
  FiTrendingUp
} from "react-icons/fi";

import "../styles/landing.css";

function Landing({ onLogin }) {
  return (
    <div className="landing">

      <nav className="navbar">

        <div className="logo">
          💰 <span>BudgetWise</span>
        </div>

        <button className="login-btn" onClick={onLogin}>
          Sign In
        </button>

      </nav>

      <section className="hero">

        <div className="hero-left">

          <span className="badge">
            AI Powered Finance Assistant
          </span>

          <h1>
            Take Control of
            <br />
            Your Money
          </h1>

          <p>
            Budget smarter, track expenses, save more,
            and get personalized financial guidance
            powered by AI.
          </p>

          <div className="hero-buttons">

            <button
              className="primary-btn"
              onClick={onLogin}
            >
              Get Started
              <FiArrowRight />
            </button>

            <button className="secondary-btn">
              Learn More
            </button>

          </div>

        </div>

        <div className="hero-right">

          <div className="glass-card big">

            <h3>Monthly Budget</h3>

            <h1>$2,450</h1>

            <div className="progress">

              <div className="progress-fill"></div>

            </div>

            <p>72% used this month</p>

          </div>

          <div className="floating-card top">

            <FiTrendingUp />

            <div>
              <h4>Investments</h4>
              <span>+12.4%</span>
            </div>

          </div>

          <div className="floating-card bottom">

            <FiPieChart />

            <div>
              <h4>Savings</h4>
              <span>$8,430</span>
            </div>

          </div>

        </div>

      </section>

      <section className="features">

        <div className="feature-card">

          <FiDollarSign />

          <h3>Budget Planner</h3>

          <p>
            Build monthly budgets in seconds with AI.
          </p>

        </div>

        <div className="feature-card">

          <FiPieChart />

          <h3>Expense Tracking</h3>

          <p>
            Understand where every dollar goes.
          </p>

        </div>

        <div className="feature-card">

          <FiTrendingUp />

          <h3>Smart Advice</h3>

          <p>
            Personalized recommendations for your goals.
          </p>

        </div>

      </section>

    </div>
  );
}

export default Landing;