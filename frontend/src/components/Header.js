import React, { useContext, useState } from 'react';
import { AppContext } from '../App';
import { LogOut, Shield, User, Power, Lock, Settings as SettingsIcon } from 'lucide-react';

const Header = () => {
  const { logout, lockApp, portfolio, currentPage, currentUser, showToast } = useContext(AppContext);
  const [showLogoutMenu, setShowLogoutMenu] = useState(false);

  const handleFullLogout = async () => {
    try {
      await logout();
      showToast('تم تسجيل الخروج التام من التطبيق', 'success');
    } catch (error) {
      showToast('خطأ في تسجيل الخروج', 'error');
    }
  };

  const handleLockApp = () => {
    lockApp();
    showToast('تم قفل التطبيق مؤقتاً', 'info');
  };

  const getPageTitle = () => {
    switch (currentPage) {
      case 'home': return 'الرئيسية';
      case 'platforms': return 'المنصات';
      case 'assistant': return 'المساعد الذكي';
      case 'settings': return 'الإعدادات';
      default: return 'نيون تريدر V7';
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('ar-SA', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-40 md:right-24">
      <div className="glass-dark border-b border-white/10 p-4">
        <div className="flex items-center justify-between">
          {/* Page Title & User Info */}
          <div className="flex items-center gap-4">
            <div>
              <h1 className="text-xl font-bold text-white">{getPageTitle()}</h1>
              <p className="text-sm text-gray-400">
                مرحباً {currentUser?.username || 'المستخدم'}
              </p>
            </div>
          </div>

          {/* Right Side - Balance & User Menu */}
          <div className="flex items-center gap-4">
            {/* Quick Balance Display */}
            <div className="hidden md:flex items-center gap-4 px-4 py-2 bg-white/5 rounded-lg border border-white/10">
              <div className="text-right">
                <p className="text-xs text-gray-400">الرصيد الكلي</p>
                <p className="text-sm font-semibold text-white">
                  {formatCurrency(portfolio?.total_balance || 0)}
                </p>
              </div>
              <div className={`text-right ${(portfolio?.daily_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                <p className="text-xs text-gray-400">اليومي</p>
                <p className="text-sm font-semibold">
                  {formatCurrency(portfolio?.daily_pnl || 0)}
                </p>
              </div>
            </div>

            {/* User Menu */}
            <div className="relative">
              <button
                onClick={() => setShowLogoutMenu(!showLogoutMenu)}
                className="flex items-center gap-2 p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors border border-white/10"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  <User size={16} className="text-white" />
                </div>
                <div className="hidden md:block text-right">
                  <p className="text-sm font-medium text-white">{currentUser?.username || 'المستخدم'}</p>
                  <p className="text-xs text-gray-400">{currentUser?.email || 'جلسة نشطة'}</p>
                </div>
              </button>

              {/* Dropdown Menu */}
              {showLogoutMenu && (
                <div className="absolute left-0 mt-2 w-56 glass-dark rounded-xl border border-white/10 shadow-xl z-50">
                  <div className="p-2">
                    {/* Security Status */}
                    <div className="p-3 mb-2 bg-green-500/10 border border-green-500/30 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Shield className="text-green-400" size={16} />
                        <span className="text-green-400 text-sm font-medium">جلسة آمنة</span>
                      </div>
                      <p className="text-xs text-green-300 mt-1">
                        محمي بتشفير JWT - {currentUser?.email}
                      </p>
                    </div>

                    {/* Menu Items */}
                    <button
                      onClick={() => {
                        setShowLogoutMenu(false);
                        // Navigate to settings if needed
                      }}
                      className="w-full flex items-center gap-3 px-3 py-2 text-gray-300 hover:bg-white/5 rounded-lg transition-colors"
                    >
                      <SettingsIcon size={16} />
                      <span className="text-sm">إعدادات الأمان</span>
                    </button>

                    <div className="border-t border-white/10 my-2"></div>

                    {/* Logout - Full Exit */}
                    <button
                      onClick={handleFullLogout}
                      className="w-full flex items-center gap-3 px-3 py-2 text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                    >
                      <LogOut size={16} />
                      <div className="text-right">
                        <div className="text-sm font-medium">تسجيل خروج</div>
                        <div className="text-xs text-red-300">خروج تام من التطبيق</div>
                      </div>
                    </button>
                  </div>

                  {/* Session Info */}
                  <div className="border-t border-white/10 p-3">
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>آخر نشاط</span>
                      <span>{new Date().toLocaleTimeString('ar-SA')}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Power Button - Lock App Only */}
            <button
              onClick={handleLockApp}
              className="p-2 rounded-lg bg-orange-500/10 hover:bg-orange-500/20 transition-colors border border-orange-500/30 group"
              title="قفل التطبيق"
            >
              <Power size={18} className="text-orange-400 group-hover:text-orange-300" />
            </button>
          </div>
        </div>
      </div>

      {/* Click outside to close menu */}
      {showLogoutMenu && (
        <div
          className="fixed inset-0 z-30"
          onClick={() => setShowLogoutMenu(false)}
        ></div>
      )}
    </header>
  );
};

export default Header;