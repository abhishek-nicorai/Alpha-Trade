import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Globe, History, Settings, Zap } from 'lucide-react';

const Sidebar = () => {
  const links = [
    { to: "/", icon: <LayoutDashboard size={20}/>, label: "Dashboard" },
    { to: "/market", icon: <Globe size={20}/>, label: "Market Explorer" },
    { to: "/settings", icon: <Settings size={20}/>, label: "Bot Settings" },
    { to: "/history", icon: <History size={20}/>, label: "Trade Logs" },
  ];

  return (
    <aside className="w-64 bg-bg-secondary border-r border-border-muted flex flex-col">
      <div className="p-6 border-b border-border-muted flex items-center gap-3">
        <div className="bg-blue-600 p-1.5 rounded"><Zap size={20} fill="white"/></div>
        <span className="font-bold tracking-tighter text-xl">ALPHA<span className="text-blue-500">TRADE</span></span>
      </div>
      <nav className="flex-1 p-4 space-y-2">
        {links.map(link => (
          <NavLink 
            key={link.to} 
            to={link.to} 
            className={({isActive}) => `flex items-center gap-3 p-3 rounded-lg transition-all ${isActive ? 'bg-blue-600/10 text-blue-500 border border-blue-600/20' : 'text-text-secondary hover:bg-bg-tertiary'}`}
          >
            {link.icon} <span className="text-sm font-medium">{link.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;