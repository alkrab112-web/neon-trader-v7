import React, { useState, useContext } from 'react';
import { AppContext } from '../App';
import { Lock, Eye, EyeOff, Shield, Key, Smartphone, AlertCircle, UserPlus, LogIn } from 'lucide-react';

const Login = () => {
  const { register, login, showToast } = useContext(AppContext);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState('login'); // 'login' or 'register'

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      showToast('يرجى إدخال البريد الإلكتروني وكلمة المرور', 'error');
      return;
    }

    setLoading(true);
    
    try {
      const result = await login({ email, password });
      if (result.success) {
        showToast(result.message, 'success');
      } else {
        showToast(result.message, 'error');
      }
    } catch (error) {
      showToast('خطأ في تسجيل الدخول', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!email || !username || !password || !confirmPassword) {
      showToast('يرجى ملء جميع الحقول', 'error');
      return;
    }

    if (password !== confirmPassword) {
      showToast('كلمات المرور غير متطابقة', 'error');
      return;
    }

    if (password.length < 8) {
      showToast('يجب أن تكون كلمة المرور 8 أحرف على الأقل', 'error');
      return;
    }

    setLoading(true);
    
    try {
      const result = await register({ 
        email, 
        username, 
        password, 
        confirm_password: confirmPassword 
      });
      
      if (result.success) {
        showToast(result.message, 'success');
      } else {
        showToast(result.message, 'error');
      }
    } catch (error) {
      showToast('خطأ في إنشاء الحساب', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4" dir="rtl">
      {/* Background */}
      <div className="fixed inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-pink-900/20 backdrop-blur-sm"></div>
      
      <div className="relative z-10 w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center neon-blue">
            <span className="text-white font-bold text-2xl">N7</span>
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            نيون تريدر V7
          </h1>
          <p className="text-gray-400 mt-2">منصة التداول الذكية الآمنة</p>
        </div>

        {/* Mode Toggle */}
        <div className="flex mb-6 bg-slate-800/50 rounded-xl p-1">
          <button
            onClick={() => setMode('login')}
            className={`flex-1 py-3 px-4 rounded-lg transition-all flex items-center justify-center gap-2 ${
              mode === 'login' 
                ? 'bg-blue-600 text-white' 
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <LogIn size={18} />
            تسجيل دخول
          </button>
          <button
            onClick={() => setMode('register')}
            className={`flex-1 py-3 px-4 rounded-lg transition-all flex items-center justify-center gap-2 ${
              mode === 'register' 
                ? 'bg-purple-600 text-white' 
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <UserPlus size={18} />
            حساب جديد
          </button>
        </div>

        {/* Auth Form */}
        <div className="glass-dark rounded-2xl p-8 border border-white/10">
          <div className="text-center mb-6">
            <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              {mode === 'login' ? <LogIn className="text-white" size={24} /> : <UserPlus className="text-white" size={24} />}
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">
              {mode === 'login' ? 'تسجيل الدخول' : 'إنشاء حساب جديد'}
            </h2>
            <p className="text-gray-400 text-sm">
              {mode === 'login' 
                ? 'أدخل بياناتك للوصول إلى حسابك' 
                : 'املأ البيانات التالية لإنشاء حساب جديد'
              }
            </p>
          </div>

          <form onSubmit={mode === 'login' ? handleLogin : handleRegister} className="space-y-6">
            {/* Email */}
            <div>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="البريد الإلكتروني"
                className="input-field"
                required
              />
            </div>

            {/* Username (Register only) */}
            {mode === 'register' && (
              <div>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="اسم المستخدم"
                  className="input-field"
                  required
                  minLength={3}
                />
              </div>
            )}

            {/* Password */}
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="كلمة المرور"
                className="input-field pr-12"
                required
                minLength={8}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>

            {/* Confirm Password (Register only) */}
            {mode === 'register' && (
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="تأكيد كلمة المرور"
                  className="input-field pr-12"
                  required
                  minLength={8}
                />
              </div>
            )}

            {mode === 'register' && (
              <div className="bg-amber-500/10 border border-amber-500/30 p-4 rounded-lg">
                <div className="flex items-start gap-3">
                  <AlertCircle className="text-amber-400 mt-0.5" size={20} />
                  <div>
                    <h4 className="font-medium text-amber-400 mb-2">متطلبات كلمة المرور:</h4>
                    <ul className="text-sm text-amber-200 space-y-1">
                      <li>• 8 أحرف على الأقل</li>
                      <li>• تجمع بين الأحرف والأرقام</li>
                      <li>• احتفظ بها في مكان آمن</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            <button
              type="submit"
              className="btn-primary w-full"
              disabled={loading}
            >
              {loading ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="spinner"></div>
                  <span>جاري المعالجة...</span>
                </div>
              ) : (
                mode === 'login' ? 'تسجيل الدخول' : 'إنشاء الحساب'
              )}
            </button>
          </form>
        </div>

        {/* Security Notice */}
        <div className="mt-6 text-center">
          <div className="glass-dark rounded-xl p-4 border border-white/5">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Shield className="text-blue-400" size={16} />
              <span className="text-blue-400 font-medium text-sm">محمي بتشفير JWT</span>
            </div>
            <p className="text-xs text-gray-500">
              جميع البيانات مشفرة ومحمية. كلمات المرور محفوظة بتشفير آمن.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;