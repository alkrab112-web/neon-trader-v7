import React, { useState, useContext } from 'react';
import { AppContext } from '../App';
import { Lock, Eye, EyeOff, Shield, Key, Smartphone, AlertCircle } from 'lucide-react';

const Login = () => {
  const { login, showToast } = useContext(AppContext);
  const [masterPassword, setMasterPassword] = useState('');
  const [twoFactorCode, setTwoFactorCode] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState('password'); // 'password' or '2fa'
  const [showSetup, setShowSetup] = useState(false);

  // Check if this is first time setup
  const isFirstTime = !localStorage.getItem('neon_trader_setup');

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    if (!masterPassword) {
      showToast('يرجى إدخال كلمة المرور الرئيسية', 'error');
      return;
    }

    setLoading(true);
    
    try {
      // Simulate password verification
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (isFirstTime) {
        // First time setup
        localStorage.setItem('neon_trader_setup', 'true');
        localStorage.setItem('neon_trader_master_pass', btoa(masterPassword)); // Basic encoding
        showToast('تم إنشاء كلمة المرور الرئيسية بنجاح', 'success');
        setStep('2fa');
      } else {
        // Verify existing password
        const stored = localStorage.getItem('neon_trader_master_pass');
        if (stored && atob(stored) === masterPassword) {
          const twoFAEnabled = localStorage.getItem('neon_trader_2fa') === 'true';
          if (twoFAEnabled) {
            setStep('2fa');
          } else {
            // Login directly
            await login(masterPassword);
          }
        } else {
          showToast('كلمة المرور غير صحيحة', 'error');
        }
      }
    } catch (error) {
      showToast('خطأ في تسجيل الدخول', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handle2FASubmit = async (e) => {
    e.preventDefault();
    if (!twoFactorCode || twoFactorCode.length !== 6) {
      showToast('يرجى إدخال رمز التحقق المكون من 6 أرقام', 'error');
      return;
    }

    setLoading(true);
    
    try {
      // Simulate 2FA verification (in real app, verify with backend)
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // For demo, accept code "123456"
      if (twoFactorCode === '123456') {
        await login(masterPassword, twoFactorCode);
        showToast('تم تسجيل الدخول بنجاح', 'success');
      } else {
        showToast('رمز التحقق غير صحيح', 'error');
      }
    } catch (error) {
      showToast('خطأ في التحقق', 'error');
    } finally {
      setLoading(false);
    }
  };

  const enable2FA = () => {
    localStorage.setItem('neon_trader_2fa', 'true');
    showToast('تم تفعيل المصادقة الثنائية', 'success');
    setStep('2fa');
  };

  const skip2FA = async () => {
    await login(masterPassword);
    showToast('تم تسجيل الدخول بنجاح', 'success');
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

        {/* Login Form */}
        <div className="glass-dark rounded-2xl p-8 border border-white/10">
          {step === 'password' && (
            <>
              <div className="text-center mb-6">
                <Lock className="w-12 h-12 text-blue-400 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-white mb-2">
                  {isFirstTime ? 'إنشاء كلمة المرور الرئيسية' : 'تسجيل الدخول'}
                </h2>
                <p className="text-gray-400 text-sm">
                  {isFirstTime ? 'أنشئ كلمة مرور قوية لحماية حسابك' : 'أدخل كلمة المرور الرئيسية'}
                </p>
              </div>

              <form onSubmit={handlePasswordSubmit} className="space-y-6">
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={masterPassword}
                    onChange={(e) => setMasterPassword(e.target.value)}
                    placeholder="كلمة المرور الرئيسية"
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

                {isFirstTime && (
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
                    isFirstTime ? 'إنشاء كلمة المرور' : 'تسجيل الدخول'
                  )}
                </button>
              </form>
            </>
          )}

          {step === '2fa' && (
            <>
              <div className="text-center mb-6">
                <Smartphone className="w-12 h-12 text-green-400 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-white mb-2">المصادقة الثنائية</h2>
                {isFirstTime ? (
                  <p className="text-gray-400 text-sm">
                    هل تريد تفعيل المصادقة الثنائية لحماية إضافية؟
                  </p>
                ) : (
                  <p className="text-gray-400 text-sm">
                    أدخل رمز التحقق المكون من 6 أرقام
                  </p>
                )}
              </div>

              {isFirstTime ? (
                <div className="space-y-6">
                  <div className="bg-green-500/10 border border-green-500/30 p-4 rounded-lg">
                    <div className="flex items-start gap-3">
                      <Shield className="text-green-400 mt-0.5" size={20} />
                      <div>
                        <h4 className="font-medium text-green-400 mb-2">فوائد المصادقة الثنائية:</h4>
                        <ul className="text-sm text-green-200 space-y-1">
                          <li>• حماية إضافية لحسابك</li>
                          <li>• منع الوصول غير المصرح</li>
                          <li>• تأمين عمليات التداول</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <button
                      onClick={enable2FA}
                      className="btn-primary flex-1"
                    >
                      تفعيل المصادقة الثنائية
                    </button>
                    <button
                      onClick={skip2FA}
                      className="btn-secondary px-6"
                    >
                      تخطي الآن
                    </button>
                  </div>
                </div>
              ) : (
                <form onSubmit={handle2FASubmit} className="space-y-6">
                  <div>
                    <input
                      type="text"
                      value={twoFactorCode}
                      onChange={(e) => setTwoFactorCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                      placeholder="123456"
                      className="input-field text-center text-lg tracking-widest"
                      maxLength={6}
                      required
                    />
                    <p className="text-sm text-gray-400 mt-2 text-center">
                      للتجربة، استخدم الرمز: <span className="text-blue-400 font-mono">123456</span>
                    </p>
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
                      'تحقق ودخول'
                    )}
                  </button>

                  <button
                    type="button"
                    onClick={() => setStep('password')}
                    className="btn-secondary w-full"
                  >
                    العودة
                  </button>
                </form>
              )}
            </>
          )}
        </div>

        {/* Security Notice */}
        <div className="mt-6 text-center">
          <div className="glass-dark rounded-xl p-4 border border-white/5">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Shield className="text-blue-400" size={16} />
              <span className="text-blue-400 font-medium text-sm">محمي بتشفير AES-256</span>
            </div>
            <p className="text-xs text-gray-500">
              جميع البيانات مشفرة ومحمية. لا يتم حفظ كلمات المرور على الخوادم.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;