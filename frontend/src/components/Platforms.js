import React, { useContext, useState } from 'react';
import { AppContext } from '../App';
import { Plus, Wifi, WifiOff, AlertTriangle, Shield, Settings } from 'lucide-react';

const Platforms = () => {
  const { platforms, loading, addPlatform, testPlatform, showToast } = useContext(AppContext);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    platform_type: 'binance',
    api_key: '',
    secret_key: '',
    is_testnet: true
  });

  const platformTypes = [
    { value: 'binance', label: 'Binance', logo: '🟡' },
    { value: 'bybit', label: 'Bybit', logo: '🟠' },
    { value: 'okx', label: 'OKX', logo: '⚫' },
    { value: 'kucoin', label: 'KuCoin', logo: '🟢' },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name || !formData.platform_type) {
      showToast('يرجى ملء جميع الحقول المطلوبة', 'error');
      return;
    }

    try {
      await addPlatform(formData);
      setFormData({
        name: '',
        platform_type: 'binance',
        api_key: '',
        secret_key: '',
        is_testnet: true
      });
      setShowAddForm(false);
    } catch (error) {
      console.error('Error adding platform:', error);
    }
  };

  const handleTestConnection = async (platformId) => {
    try {
      await testPlatform(platformId);
    } catch (error) {
      console.error('Error testing platform:', error);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected':
        return <Wifi className="text-green-400" size={20} />;
      case 'connecting':
        return <div className="spinner"></div>;
      default:
        return <WifiOff className="text-red-400" size={20} />;
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'connected':
        return 'status-connected';
      case 'connecting':
        return 'status-connecting';
      default:
        return 'status-disconnected';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'connected':
        return 'متصل';
      case 'connecting':
        return 'جاري الاتصال';
      default:
        return 'غير متصل';
    }
  };

  return (
    <div className="p-4 space-y-6 fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">المنصات</h1>
          <p className="text-gray-400 mt-1">إدارة منصات التداول المتصلة</p>
        </div>
        <button
          onClick={() => setShowAddForm(true)}
          className="btn-primary flex items-center gap-2"
          disabled={loading}
        >
          <Plus size={20} />
          إضافة منصة
        </button>
      </div>

      {/* Security Warning */}
      <div className="card bg-gradient-to-r from-amber-500/10 to-orange-500/10 border-amber-500/30">
        <div className="flex items-start gap-3">
          <Shield className="text-amber-400 mt-1" size={24} />
          <div>
            <h3 className="font-semibold text-amber-400 mb-2">تحذير أمني مهم</h3>
            <p className="text-amber-200 text-sm leading-relaxed">
              استخدم مفاتيح API للتداول فقط (Trade-Only Keys) بدون صلاحيات السحب. 
              لا تشارك مفاتيحك مع أي طرف ثالث. نوصي بالبدء بالـ Testnet أولاً.
            </p>
          </div>
        </div>
      </div>

      {/* Add Platform Form */}
      {showAddForm && (
        <div className="card border-blue-500/30">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-white">إضافة منصة جديدة</h2>
            <button
              onClick={() => setShowAddForm(false)}
              className="text-gray-400 hover:text-white transition-colors"
            >
              ✕
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                اسم المنصة *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="input-field"
                placeholder="مثال: حساب التداول الرئيسي"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                نوع المنصة *
              </label>
              <select
                value={formData.platform_type}
                onChange={(e) => setFormData({ ...formData, platform_type: e.target.value })}
                className="input-field"
                required
              >
                {platformTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.logo} {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                مفتاح API
              </label>
              <input
                type="text"
                value={formData.api_key}
                onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                className="input-field"
                placeholder="أدخل مفتاح API (اختياري للتشغيل التجريبي)"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                المفتاح السري
              </label>
              <input
                type="password"
                value={formData.secret_key}
                onChange={(e) => setFormData({ ...formData, secret_key: e.target.value })}
                className="input-field"
                placeholder="أدخل المفتاح السري (اختياري للتشغيل التجريبي)"
              />
            </div>

            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="testnet"
                checked={formData.is_testnet}
                onChange={(e) => setFormData({ ...formData, is_testnet: e.target.checked })}
                className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-blue-600"
              />
              <label htmlFor="testnet" className="text-sm text-gray-300">
                استخدام Testnet (موصى به للاختبار)
              </label>
            </div>

            <div className="flex gap-3 pt-4">
              <button
                type="submit"
                className="btn-primary flex-1"
                disabled={loading}
              >
                {loading ? <div className="spinner"></div> : 'إضافة المنصة'}
              </button>
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="btn-secondary px-6"
              >
                إلغاء
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Platforms List */}
      <div className="space-y-4">
        {platforms.length > 0 ? (
          platforms.map((platform) => (
            <div key={platform.id} className="card">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-xl font-bold">
                    {platformTypes.find(p => p.value === platform.platform_type)?.logo || '📈'}
                  </div>
                  <div>
                    <h3 className="font-semibold text-white text-lg">{platform.name}</h3>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="text-sm text-gray-400">
                        {platformTypes.find(p => p.value === platform.platform_type)?.label}
                      </span>
                      {platform.is_testnet && (
                        <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-full">
                          Testnet
                        </span>
                      )}
                      <span className={`text-xs ${getStatusClass(platform.status)}`}>
                        {getStatusText(platform.status)}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  {getStatusIcon(platform.status)}
                  
                  <button
                    onClick={() => handleTestConnection(platform.id)}
                    className="btn-secondary text-sm px-4 py-2"
                    disabled={loading}
                  >
                    {loading ? <div className="spinner"></div> : 'اختبار الاتصال'}
                  </button>

                  <button className="text-gray-400 hover:text-white transition-colors">
                    <Settings size={20} />
                  </button>
                </div>
              </div>

              {/* Platform Details */}
              <div className="mt-4 pt-4 border-t border-white/10">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">الحالة:</span>
                    <div className="flex items-center gap-2 mt-1">
                      {getStatusIcon(platform.status)}
                      <span className="text-white">{getStatusText(platform.status)}</span>
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-400">النوع:</span>
                    <p className="text-white mt-1">
                      {platform.is_testnet ? 'تشغيل تجريبي' : 'حقيقي'}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-400">API Key:</span>
                    <p className="text-white mt-1">
                      {platform.api_key ? `${platform.api_key.substring(0, 8)}...` : 'غير محدد'}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-400">تاريخ الإضافة:</span>
                    <p className="text-white mt-1">
                      {new Date(platform.created_at).toLocaleDateString('ar-SA')}
                    </p>
                  </div>
                </div>
              </div>

              {/* Connection Status Details */}
              {platform.status === 'connected' && (
                <div className="mt-4 p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Wifi className="text-green-400" size={16} />
                    <span className="text-green-400 font-medium">متصل بنجاح</span>
                  </div>
                  <p className="text-green-300 text-sm mt-1">
                    المنصة جاهزة للتداول. جميع الوظائف متاحة.
                  </p>
                </div>
              )}

              {platform.status === 'disconnected' && platform.api_key && (
                <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="text-red-400" size={16} />
                    <span className="text-red-400 font-medium">خطأ في الاتصال</span>
                  </div>
                  <p className="text-red-300 text-sm mt-1">
                    تعذر الاتصال بالمنصة. تحقق من صحة مفاتيح API أو حالة الشبكة.
                  </p>
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="card text-center py-12">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center">
              <Plus className="text-blue-400" size={24} />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">لا توجد منصات مضافة</h3>
            <p className="text-gray-400 mb-6">أضف منصة التداول الأولى للبدء</p>
            <button
              onClick={() => setShowAddForm(true)}
              className="btn-primary"
            >
              إضافة منصة
            </button>
          </div>
        )}
      </div>

      {/* Tips */}
      <div className="card bg-gradient-to-r from-blue-500/10 to-purple-500/10 border-blue-500/30">
        <h3 className="font-semibold text-blue-400 mb-3">💡 نصائح للأمان</h3>
        <ul className="space-y-2 text-sm text-blue-200">
          <li>• استخدم مفاتيح API بصلاحيات التداول فقط (بدون سحب)</li>
          <li>• ابدأ دائماً بالـ Testnet قبل التداول الحقيقي</li>
          <li>• لا تشارك مفاتيحك مع أي شخص أو موقع</li>
          <li>• راجع صلاحيات المفاتيح بانتظام في حساب المنصة</li>
          <li>• استخدم كلمات مرور قوية لحسابات المنصات</li>
        </ul>
      </div>
    </div>
  );
};

export default Platforms;