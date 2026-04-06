import { NavLink, Outlet } from 'react-router-dom';
import { Activity, ShieldAlert } from 'lucide-react';
import { cn } from '../lib/utils';

export function Layout() {
  return (
    <div className="app-container">
      <header className="site-header">
        <div className="header-brand">
          <Activity className="text-accent" />
          <span>Sentinel</span>
        </div>
        <nav className="flex gap-4">
          <NavLink 
            to="/" 
            className={({ isActive }) => cn("btn btn-secondary", isActive && "text-accent")}
          >
            Dashboard
          </NavLink>
          <NavLink 
            to="/incidents/report" 
            className="btn btn-primary"
          >
            <ShieldAlert size={16} />
            Report Incident
          </NavLink>
        </nav>
      </header>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
