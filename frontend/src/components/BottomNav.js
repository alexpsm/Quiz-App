import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, Search, ShoppingBag, User } from 'lucide-react';

export const BottomNav = () => {
  const location = useLocation();

  const tabs = [
    { icon: Home, label: 'Home', path: '/dashboard', testId: 'nav-home' },
    { icon: Search, label: 'Play', path: '/matchmaking', testId: 'nav-matchmaking' },
    { icon: ShoppingBag, label: 'Store', path: '/store', testId: 'nav-store' },
    { icon: User, label: 'Profile', path: '/profile', testId: 'nav-profile' },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 h-16 bg-black/90 backdrop-blur-lg border-t border-white/10 flex items-center justify-around z-50 max-w-md mx-auto">
      {tabs.map(({ icon: Icon, label, path, testId }) => {
        const isActive = location.pathname === path;
        return (
          <Link
            key={path}
            to={path}
            data-testid={testId}
            className={`flex flex-col items-center justify-center flex-1 h-full transition-colors ${
              isActive ? 'text-primary' : 'text-gray-400 hover:text-white'
            }`}
          >
            <Icon size={24} strokeWidth={2} />
            <span className="text-xs mt-1 font-medium">{label}</span>
          </Link>
        );
      })}
    </div>
  );
};