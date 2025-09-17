import React, { useContext } from 'react';
import { AppContext } from '../App';
import { Home, Settings, Bot, Layers, Wrench, Bell } from 'lucide-react';

const Navigation = () => {
  const { currentPage, setCurrentPage } = useContext(AppContext);

  const navItems = [
    { id: 'home', name: 'الرئيسية', icon: Home },
    { id: 'platforms', name: 'المنصات', icon: Layers },
    { id: 'assistant', name: 'المساعد', icon: Bot },
    { id: 'tools', name: 'الأدوات', icon: Wrench },
    { id: 'notifications', name: 'الإشعارات', icon: Bell },
    { id: 'settings', name: 'الإعدادات', icon: Settings },
  ];

  return (
    <>
      {/* Desktop Sidebar Navigation */}
      <nav className="hidden md:flex fixed right-0 top-0 h-full w-20 z-50 flex-col py-8">
        <div className="glass-dark rounded-l-2xl h-full flex flex-col items-center justify-center gap-6">
          {/* Logo */}
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mb-8 neon-blue">
            <span className="text-white font-bold text-lg">N7</span>
          </div>
          
          {/* Navigation Items */}
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => setCurrentPage(item.id)}
                className={`group relative flex items-center justify-center w-12 h-12 transition-all duration-300 rounded-xl ${
                  isActive
                    ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white neon-blue'
                    : 'text-gray-400 hover:text-white hover:bg-white/10'
                }`}
                data-testid={`nav-${item.id}`}
                title={item.name}
              >
                <Icon size={20} />
                
                {/* Tooltip */}
                <div className="absolute right-16 bg-gray-900 text-white text-sm px-3 py-2 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap">
                  {item.name}
                  <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1 w-2 h-2 bg-gray-900 rotate-45"></div>
                </div>
              </button>
            );
          })}
        </div>
      </nav>

      {/* Mobile Bottom Navigation */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 px-4 py-2">
        <div className="glass-dark rounded-2xl p-2">
          <div className="flex justify-around items-center">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentPage(item.id)}
                  className={`flex flex-col items-center justify-center p-3 transition-all duration-300 rounded-xl min-w-[70px] ${
                    isActive
                      ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white neon-blue'
                      : 'text-gray-400 hover:text-white hover:bg-white/10'
                  }`}
                  data-testid={`nav-${item.id}`}
                >
                  <Icon size={18} className="mb-1" />
                  <span className="text-xs font-medium truncate max-w-full">{item.name}</span>
                </button>
              );
            })}
          </div>
        </div>
      </nav>
    </>
  );
};

export default Navigation;