import React, { useState, useContext } from 'react';
import { AppContext } from '../App';
import { Lock, Eye, EyeOff, Smartphone, LogOut, Unlock } from 'lucide-react';

const UnlockScreen = ({ onUnlock }) => {
  const { logout, showToast } = useContext(AppContext);
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [useQuickUnlock, setUseQuickUnlock] = useState(true); // Default to quick unlock

  const handleQuickUnlock = async () => {
    setLoading(true);
    try {
      const success = await onUnlock(); // No password needed for quick unlock
      if (success) {
        showToast('تم فتح القفل', 'success');
      }
    } catch (error) {
      showToast('خطأ في فتح القفل', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordUnlock = async (e) => {
    e.preventDefault();
    if (!password) {
      showToast('يرجى إدخال كلمة المرور', 'error');
      return;
    }

    setLoading(true);
    try {
      const success = await onUnlock(password);
      if (success) {
        showToast('تم فتح القفل بنجاح', 'success');
      }
    } catch (error) {
      showToast('خطأ في فتح القفل', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleFullLogout = async () => {
    await logout();
    showToast('تم الخروج التام من التطبيق', 'info');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4" dir="rtl">
      {/* Background */}
      <div className="fixed inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-pink-900/20 backdrop-blur-sm"></div>
      
      <div className="relative z-10 w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center animate-pulse">
            <Lock className="text-white" size={32} />
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-400 to-red-400 bg-clip-text text-transparent">
            التطبيق مقفل
          </h1>
          <p className="text-gray-400 mt-2">اختر طريقة فتح القفل</p>
        </div>

        {/* Unlock Options */}
        <div className="glass-dark rounded-2xl p-8 border border-orange-500/30">
          {useQuickUnlock ? (
            // Quick Unlock (Default)
            <div className="text-center">
              <Unlock className="w-12 h-12 text-green-400 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-white mb-2">فتح سريع</h2>
              <p className="text-gray-400 text-sm mb-6">
                الجلسة محفوظة، يمكنك المتابعة مباشرة
              </p>

              <button
                onClick={handleQuickUnlock}
                className="btn-primary w-full mb-4"
                disabled={loading}
              >
                {loading ? (
                  <div className="flex items-center justify-center gap-2">
                    <div className="spinner"></div>
                    <span>جاري فتح القفل...</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center gap-2">
                    <Unlock size={18} />
                    <span>متابعة الجلسة</span>
                  </div>
                )}
              </button>

              <button
                onClick={() => setUseQuickUnlock(false)}
                className="btn-secondary w-full text-sm"
              >
                استخدام كلمة المرور
              </button>
            </div>
          ) : (
            // Password Unlock
            <div>
              <div className="text-center mb-6">
                <Smartphone className="w-12 h-12 text-orange-400 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-white mb-2">فتح بكلمة المرور</h2>
                <p className="text-gray-400 text-sm">
                  أدخل كلمة المرور الرئيسية للتحقق من الهوية
                </p>
              </div>

              <form onSubmit={handlePasswordUnlock} className="space-y-6">
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="كلمة المرور الرئيسية"
                    className="input-field pr-12"
                    required
                    autoFocus
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                  >
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>

                <button
                  type="submit"
                  className="btn-primary w-full"
                  disabled={loading}
                >
                  {loading ? (
                    <div className="flex items-center justify-center gap-2">
                      <div className="spinner"></div>
                      <span>جاري التحقق...</span>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center gap-2">
                      <Lock size={18} />
                      <span>فتح القفل</span>
                    </div>
                  )}
                </button>

                <button
                  type="button"
                  onClick={() => setUseQuickUnlock(true)}
                  className="btn-secondary w-full text-sm"
                >
                  العودة للفتح السريع
                </button>
              </form>
            </div>
          )}

          {/* Alternative Actions */}
          <div className="mt-6 pt-6 border-t border-white/10">
            <button
              onClick={handleFullLogout}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 text-red-400 hover:bg-red-500/10 rounded-lg transition-colors border border-red-500/30"
            >
              <LogOut size={18} />
              <span>خروج تام من التطبيق</span>
            </button>
          </div>
        </div>

        {/* Lock Info */}
        <div className="mt-6 text-center">
          <div className="glass-dark rounded-xl p-4 border border-white/5">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Lock className="text-orange-400" size={16} />
              <span className="text-orange-400 font-medium text-sm">قفل أمني مؤقت</span>
            </div>
            <p className="text-xs text-gray-500">
              بياناتك محفوظة وآمنة. الفتح السريع متاح للجلسات النشطة.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UnlockScreen;