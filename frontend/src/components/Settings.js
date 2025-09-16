import React, { useState, useContext } from 'react';
import { AppContext } from '../App';
import { 
  User, Shield, Bell, Palette, Database, Download, Upload, 
  Lock, Key, Clock, Smartphone, Globe, DollarSign, Bot 
} from 'lucide-react';

const Settings = () => {
  const { showToast } = useContext(AppContext);
  const [activeTab, setActiveTab] = useState('account');
  
  // Settings state
  const [settings, setSettings] = useState({
    // Account & Security
    masterPassword: '',
    twoFactorEnabled: false,
    autoLockMinutes: 5,
    sessionTimeoutMinutes: 15,
    
    // Trading & Risk
    maxRiskPerTrade: 0.5,
    dailyLossLimit: 2.0,
    enableOCO: true,
    enableTrailingStop: true,
    
    // AI Assistant
    aiProvider: 'gpt4',
    analysisFrequency: 'hourly',
    confidenceThreshold: 'medium',
    
    // Notifications
    enableNotifications: true,
    tradingAlerts: true,
    priceAlerts: true,
    systemAlerts: true,
    
    // Appearance
    theme: 'dark',
    language: 'ar',
    currency: 'USD'
  });

  const tabs = [
    { id: 'account', name: 'الحساب والأمان', icon: User },
    { id: 'trading', name: 'التداول والمخاطر', icon: DollarSign },
    { id: 'ai', name: 'الذكاء الاصطناعي', icon: Bot },
    { id: 'notifications', name: 'الإشعارات', icon: Bell },
    { id: 'appearance', name: 'المظهر', icon: Palette },
    { id: 'backup', name: 'النسخ الاحتياطي', icon: Database }
  ];

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    showToast('تم حفظ الإعداد', 'success');
  };

  const exportVault = () => {
    showToast('ميزة تصدير Vault قيد التطوير', 'info');
  };

  const importVault = () => {
    showToast('ميزة تصدير Vault قيد التطوير', 'info');
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'account':
        return (
          <div className="space-y-6">
            <div className="card">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Lock className="text-blue-400" size={20} />
                كلمة المرور الرئيسية
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    كلمة المرور الحالية
                  </label>
                  <input
                    type="password"
                    className="input-field"
                    placeholder="أدخل كلمة المرور الحالية"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    كلمة المرور الجديدة
                  </label>
                  <input
                    type="password"
                    className="input-field"
                    placeholder="أدخل كلمة المرور الجديدة"
                  />
                </div>
                <button className="btn-primary">تحديث كلمة المرور</button>
              </div>
            </div>

            <div className="card">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Key className="text-green-400" size={20} />
                المصادقة الثنائية (2FA)
              </h3>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white">تفعيل المصادقة الثنائية</p>
                  <p className="text-sm text-gray-400">طبقة حماية إضافية لحسابك</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.twoFactorEnabled}
                    onChange={(e) => handleSettingChange('twoFactorEnabled', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>

            <div className="card">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Clock className="text-orange-400" size={20} />
                إعدادات الجلسة
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    قفل تلقائي بعد (دقائق)
                  </label>
                  <select
                    value={settings.autoLockMinutes}
                    onChange={(e) => handleSettingChange('autoLockMinutes', parseInt(e.target.value))}
                    className="input-field"
                  >
                    <option value={1}>1 دقيقة</option>
                    <option value={5}>5 دقائق</option>
                    <option value={10}>10 دقائق</option>
                    <option value={30}>30 دقيقة</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    انتهاء الجلسة بعد (دقائق)
                  </label>
                  <select
                    value={settings.sessionTimeoutMinutes}
                    onChange={(e) => handleSettingChange('sessionTimeoutMinutes', parseInt(e.target.value))}
                    className="input-field"
                  >
                    <option value={15}>15 دقيقة</option>
                    <option value={30}>30 دقيقة</option>
                    <option value={60}>60 دقيقة</option>
                    <option value={120}>120 دقيقة</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        );

      case 'trading':
        return (
          <div className="space-y-6">
            <div className="card">
              <h3 className="text-lg font-semibold text-white mb-4">إدارة المخاطر</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    الحد الأقصى للمخاطرة لكل صفقة (%)
                  </label>
                  <input
                    type="number"
                    value={settings.maxRiskPerTrade}
                    onChange={(e) => handleSettingChange('maxRiskPerTrade', parseFloat(e.target.value))}
                    className="input-field"
                    step="0.1"
                    min="0.1"
                    max="5"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    حد الخسارة اليومي (%)
                  </label>
                  <input
                    type="number"
                    value={settings.dailyLossLimit}
                    onChange={(e) => handleSettingChange('dailyLossLimit', parseFloat(e.target.value))}
                    className="input-field"
                    step="0.1"
                    min="0.5"
                    max="10"
                  />
                </div>
              </div>
            </div>

            <div className="card">
              <h3 className="text-lg font-semibold text-white mb-4">أدوات التداول</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white">تفعيل أوامر OCO</p>
                    <p className="text-sm text-gray-400">أوامر One-Cancels-Other</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.enableOCO}
                      onChange={(e) => handleSettingChange('enableOCO', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-600 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white">تفعيل Trailing Stop</p>
                    <p className="text-sm text-gray-400">وقف خسارة متحرك</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.enableTrailingStop}
                      onChange={(e) => handleSettingChange('enableTrailingStop', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-600 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
              </div>
            </div>
          </div>
        );

      case 'notifications':
        return (
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4">إعدادات الإشعارات</h3>
            <div className="space-y-4">
              {[
                { key: 'enableNotifications', label: 'تفعيل الإشعارات', desc: 'تفعيل جميع الإشعارات' },
                { key: 'tradingAlerts', label: 'تنبيهات التداول', desc: 'إشعارات الصفقات والأوامر' },
                { key: 'priceAlerts', label: 'تنبيهات الأسعار', desc: 'تحركات الأسعار المهمة' },
                { key: 'systemAlerts', label: 'تنبيهات النظام', desc: 'تحديثات وصيانة النظام' }
              ].map((item) => (
                <div key={item.key} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <div>
                    <p className="text-white">{item.label}</p>
                    <p className="text-sm text-gray-400">{item.desc}</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings[item.key]}
                      onChange={(e) => handleSettingChange(item.key, e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-600 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
              ))}
            </div>
          </div>
        );

      case 'appearance':
        return (
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4">المظهر واللغة</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">المظهر</label>
                <select
                  value={settings.theme}
                  onChange={(e) => handleSettingChange('theme', e.target.value)}
                  className="input-field"
                >
                  <option value="dark">داكن (موصى به)</option>
                  <option value="light">فاتح</option>
                  <option value="auto">تلقائي</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">اللغة</label>
                <select
                  value={settings.language}
                  onChange={(e) => handleSettingChange('language', e.target.value)}
                  className="input-field"
                >
                  <option value="ar">العربية</option>
                  <option value="en">English</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">العملة الافتراضية</label>
                <select
                  value={settings.currency}
                  onChange={(e) => handleSettingChange('currency', e.target.value)}
                  className="input-field"
                >
                  <option value="USD">دولار أمريكي (USD)</option>
                  <option value="EUR">يورو (EUR)</option>
                  <option value="SAR">ريال سعودي (SAR)</option>
                </select>
              </div>
            </div>
          </div>
        );

      case 'backup':
        return (
          <div className="space-y-6">
            <div className="card">
              <h3 className="text-lg font-semibold text-white mb-4">النسخ الاحتياطي</h3>
              <p className="text-gray-400 mb-6">
                قم بتصدير أو استيراد بيانات Vault المشفرة للاحتفاظ بنسخة احتياطية آمنة.
              </p>
              <div className="flex gap-4">
                <button onClick={exportVault} className="btn-primary flex items-center gap-2">
                  <Download size={16} />
                  تصدير Vault
                </button>
                <button onClick={importVault} className="btn-secondary flex items-center gap-2">
                  <Upload size={16} />
                  استيراد Vault
                </button>
              </div>
            </div>

            <div className="card bg-amber-500/10 border-amber-500/30">
              <div className="flex items-start gap-3">
                <Shield className="text-amber-400 mt-1" size={20} />
                <div>
                  <h4 className="font-semibold text-amber-400 mb-2">معلومات الأمان</h4>
                  <ul className="text-sm text-amber-200 space-y-1">
                    <li>• جميع البيانات مشفرة بـ AES-256-GCM</li>
                    <li>• كلمات المرور محمية بـ Argon2id</li>
                    <li>• لا يتم حفظ المفاتيح الخاصة على الخوادم</li>
                    <li>• احتفظ بالنسخة الاحتياطية في مكان آمن</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="p-4 space-y-6 fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">الإعدادات</h1>
        <p className="text-gray-400 mt-1">إدارة تفضيلات الحساب والتطبيق</p>
      </div>

      {/* Tabs */}
      <div className="flex overflow-x-auto scrollbar-hide gap-2 pb-2">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                  : 'bg-white/10 text-gray-400 hover:text-white hover:bg-white/20'
              }`}
            >
              <Icon size={16} />
              {tab.name}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div>{renderTabContent()}</div>

      {/* App Info */}
      <div className="card text-center">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
          <span className="text-2xl font-bold text-white">N7</span>
        </div>
        <h3 className="font-semibold text-white mb-2">Neon Trader V7</h3>
        <p className="text-sm text-gray-400 mb-4">الإصدار 7.0.0 - Build 2025.01</p>
        <div className="flex justify-center gap-4 text-xs text-gray-500">
          <span>مطور بواسطة Emergent AI</span>
          <span>•</span>
          <span>جميع الحقوق محفوظة</span>
        </div>
      </div>
    </div>
  );
};

export default Settings;