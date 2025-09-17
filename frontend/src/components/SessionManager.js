import React, { useEffect, useState, useContext } from 'react';
import { AppContext } from '../App';
import { Lock, Clock, Shield } from 'lucide-react';

const SessionManager = ({ children }) => {
  const { isAuthenticated, lockApp, logout, showToast } = useContext(AppContext);
  const [lastActivity, setLastActivity] = useState(Date.now());
  const [showLockWarning, setShowLockWarning] = useState(false);
  const [countdown, setCountdown] = useState(0);

  // Session settings (from localStorage or defaults)
  const getSessionSettings = () => {
    return {
      autoLockMinutes: parseInt(localStorage.getItem('neon_trader_auto_lock') || '5'),
      sessionTimeoutMinutes: parseInt(localStorage.getItem('neon_trader_session_timeout') || '15'),
    };
  };

  const settings = getSessionSettings();
  const AUTO_LOCK_MS = settings.autoLockMinutes * 60 * 1000;
  const SESSION_TIMEOUT_MS = settings.sessionTimeoutMinutes * 60 * 1000;
  const WARNING_MS = 60 * 1000; // Show warning 1 minute before lock

  // Update activity timestamp
  const updateActivity = () => {
    setLastActivity(Date.now());
    setShowLockWarning(false);
    setCountdown(0);
  };

  // Activity listeners
  useEffect(() => {
    if (!isAuthenticated) return;

    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
    
    const handleActivity = () => {
      updateActivity();
    };

    events.forEach(event => {
      document.addEventListener(event, handleActivity, true);
    });

    return () => {
      events.forEach(event => {
        document.removeEventListener(event, handleActivity, true);
      });
    };
  }, [isAuthenticated]);

  // Session monitoring
  useEffect(() => {
    if (!isAuthenticated) return;

    const interval = setInterval(() => {
      const now = Date.now();
      const timeSinceActivity = now - lastActivity;

      // Session timeout (hard logout)
      if (timeSinceActivity >= SESSION_TIMEOUT_MS) {
        logout();
        showToast('انتهت صلاحية الجلسة. يرجى تسجيل الدخول مرة أخرى', 'warning');
        return;
      }

      // Auto-lock warning
      if (timeSinceActivity >= (AUTO_LOCK_MS - WARNING_MS) && !showLockWarning) {
        setShowLockWarning(true);
        setCountdown(60);
        showToast('سيتم قفل التطبيق خلال دقيقة واحدة', 'warning');
      }

      // Auto-lock
      if (timeSinceActivity >= AUTO_LOCK_MS) {
        lockApp();
        showToast('تم قفل التطبيق بسبب عدم النشاط', 'info');
        return;
      }

      // Update countdown
      if (showLockWarning) {
        const remainingMs = AUTO_LOCK_MS - timeSinceActivity;
        const remainingSeconds = Math.ceil(remainingMs / 1000);
        setCountdown(remainingSeconds);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [isAuthenticated, lastActivity, showLockWarning, AUTO_LOCK_MS, SESSION_TIMEOUT_MS]);

  // Manual extend session
  const extendSession = () => {
    updateActivity();
    showToast('تم تمديد الجلسة بنجاح', 'success');
  };

  if (!isAuthenticated) {
    return children;
  }

  return (
    <>
      {children}
      
      {/* Lock Warning Modal */}
      {showLockWarning && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4" dir="rtl">
          <div className="glass-dark rounded-2xl p-6 max-w-md w-full border border-amber-500/30">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
                <Clock className="text-white" size={24} />
              </div>
              
              <h3 className="text-xl font-semibold text-white mb-2">تحذير الجلسة</h3>
              <p className="text-gray-300 mb-6">
                سيتم قفل التطبيق بسبب عدم النشاط خلال:
              </p>
              
              <div className="text-4xl font-bold text-amber-400 mb-6">
                {countdown}s
              </div>
              
              <div className="flex gap-3">
                <button
                  onClick={extendSession}
                  className="btn-primary flex-1"
                >
                  متابعة الجلسة
                </button>
                <button
                  onClick={logout}
                  className="btn-secondary px-6"
                >
                  تسجيل خروج
                </button>
              </div>
              
              <div className="mt-4 p-3 bg-amber-500/10 rounded-lg">
                <div className="flex items-center gap-2 justify-center">
                  <Shield className="text-amber-400" size={16} />
                  <span className="text-amber-400 text-sm">حماية أمنية تلقائية</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default SessionManager;