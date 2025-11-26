import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

const Header = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const navLinkClass = ({ isActive }) =>
    `nav-link text-white ${isActive ? "fw-semibold" : "text-opacity-75"}`;

  return (
    <nav className="navbar navbar-expand bg-primary navbar-dark shadow-sm">
      <div className="container-fluid">
        <NavLink to="/" className="navbar-brand">
          Z-GPT Assistant
        </NavLink>
        <div className="collapse navbar-collapse show">
          <div className="navbar-nav me-auto">
            <NavLink to="/" className={navLinkClass} end>
              Chat
            </NavLink>
            <NavLink to="/image" className={navLinkClass}>
              Image
            </NavLink>
          </div>
          {user && (
            <div className="d-flex align-items-center gap-3">
              <span className="text-white small text-truncate" style={{ maxWidth: 200 }}>
                {user.full_name || user.email}
              </span>
              <button type="button" className="btn btn-sm btn-outline-light" onClick={handleLogout}>
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Header;
