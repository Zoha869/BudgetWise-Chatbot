import { FiMenu, FiLogOut } from "react-icons/fi";
import { FaUserCircle } from "react-icons/fa";
import { IoSettingsOutline } from "react-icons/io5";
import { HiOutlineSun, HiOutlineMoon } from "react-icons/hi2";

import { useTheme } from "../context/ThemeContext";
import "../styles/navbar.css";

export default function Navbar({
  user,
  onMenuClick,
  onLogout,
}) {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="navbar">

      <div className="navbar-left">
        <button className="menu-btn" onClick={onMenuClick}>
          <FiMenu />
        </button>

        <h2>💰 BudgetWise</h2>
      </div>

      <div className="navbar-right">

        <button
          className="theme-toggle-btn"
          onClick={toggleTheme}
          aria-label="Toggle dark mode"
        >
          {theme === "dark" ? <HiOutlineSun /> : <HiOutlineMoon />}
        </button>

        <button className="nav-icon">
          <IoSettingsOutline />
        </button>

        <div className="user-box">
          <FaUserCircle className="avatar" />
          <div>
            <h4>{user?.user_metadata?.full_name || "Guest"}</h4>
            <span>{user?.email || ""}</span>
          </div>
        </div>

        <button className="logout-btn" onClick={onLogout}>
          <FiLogOut />
        </button>

      </div>

    </header>
  );
}