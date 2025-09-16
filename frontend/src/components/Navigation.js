import React, { useContext } from 'react';
import { AppContext } from '../App';
import { Home, Settings, Bot, Layers } from 'lucide-react';

const Navigation = () => {
  const { currentPage, setCurrentPage } = useContext(AppContext);

  const navItems = [
    { id: 'home', name: 'الرئيسية', icon: Home },
    { id: 'platforms', name: 'المنصات', icon: Layers },
    { id: 'assistant', name: 'المساعد', icon: Bot },
    { id: 'settings', name: 'الإعدادات', icon: Settings },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 px-4 py-2">
      <div className="glass-dark rounded-2xl p-2">
        <div className="flex justify-around items-center">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => setCurrentPage(item.id)}
                className={`flex flex-col items-center justify-center p-3 transition-all duration-300 rounded-xl ${
                  isActive
                    ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white neon-blue'
                    : 'text-gray-400 hover:text-white hover:bg-white/10'
                }`}
              >
                <Icon size={20} className="mb-1" />
                <span className="text-xs font-medium">{item.name}</span>
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
};

export default Navigation;