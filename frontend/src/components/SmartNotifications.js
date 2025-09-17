import React, { useState, useContext, useEffect } from 'react';
import { AppContext } from '../App';
import { 
  Bell, BellRing, Zap, TrendingUp, AlertTriangle, 
  Clock, Target, Star, Globe, DollarSign, Settings 
} from 'lucide-react';
import axios from 'axios';

const SmartNotifications = () => {
  const { showToast, userId } = useContext(AppContext);
  const [notifications, setNotifications] = useState([]);
  const [settings, setSettings] = useState({
    marketNews: true,
    longTermSignals: true,
    shortTermSignals: false,
    opportunityAlerts: true,
    riskAlerts: true,
    priceAlerts: true
  });
  const [activeFilter, setActiveFilter] = useState('all');

  // Mock notifications - في الإنتاج ستأتي من الـ Backend + AI
  const mockNotifications = [
    {
      id: 1,
      type: 'opportunity',
      title: 'فرصة ذهبية - Bitcoin',
      message: 'تحليل الذكاء الاصطناعي يشير إلى احتمالية ارتفاع BTC بنسبة 15% خلال الأسبوعين القادمين بناء على كسر مستوى المقاومة',
      symbol: 'BTCUSDT',
      timeframe: 'متوسط المدى',
      confidence: 85,
      timestamp: new Date(Date.now() - 1000 * 60 * 30),
      priority: 'high',
      action: 'buy'
    },
    {
      id: 2,
      type: 'news',
      title: 'أخبار مؤثرة - الذهب',
      message: 'قرار الفيدرالي الأمريكي بخفض أسعار الفائدة يدعم ارتفاع أسعار الذهب. توقعات إيجابية للأشهر القادمة',
      symbol: 'XAUUSD',
      timeframe: 'طويل المدى',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2),
      priority: 'medium',
      source: 'Reuters'
    },
    {
      id: 3,
      type: 'technical',
      title: 'إشارة فنية - Apple',
      message: 'تكوين نموذج "الكوب والمقبض" في سهم Apple يشير لاحتمالية كسر صاعد. الهدف: $210',
      symbol: 'AAPL',
      timeframe: 'متوسط المدى',
      confidence: 72,
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 6),
      priority: 'medium',
      pattern: 'Cup and Handle'
    },
    {
      id: 4,
      type: 'risk',
      title: 'تحذير مخاطر - EUR/USD',
      message: 'مؤشرات الزخم تشير لإمكانية انعكاس الاتجاه الصاعد لليورو. يُنصح بوضع وقف خسارة محكم',
      symbol: 'EURUSD',
      timeframe: 'قصير المدى',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 8),
      priority: 'high',
      action: 'caution'
    },
    {
      id: 5,
      type: 'opportunity',
      title: 'قطاع التكنولوجيا صاعد',
      message: 'تحليل القطاعات يشير لبداية موجة صاعدة في أسهم التكنولوجيا. Microsoft و Google في المقدمة',
      symbols: ['MSFT', 'GOOGL', 'NVDA'],
      timeframe: 'طويل المدى',
      confidence: 78,
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 12),
      priority: 'medium',
      sector: 'Technology'
    }
  ];

  useEffect(() => {
    // تحميل الإشعارات (mock data للآن)
    setNotifications(mockNotifications);
    
    // في الإنتاج: جلب الإشعارات من الخادم
    // fetchNotifications();
    
    // تفعيل التحديث التلقائي كل 5 دقائق
    const interval = setInterval(() => {
      // fetchLatestNotifications();
    }, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'opportunity': return <Star className="text-yellow-400" size={20} />;
      case 'news': return <Globe className="text-blue-400" size={20} />;
      case 'technical': return <TrendingUp className="text-green-400" size={20} />;
      case 'risk': return <AlertTriangle className="text-red-400" size={20} />;
      default: return <Bell className="text-gray-400" size={20} />;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'border-red-500/50 bg-red-500/5';
      case 'medium': return 'border-yellow-500/50 bg-yellow-500/5';
      case 'low': return 'border-gray-500/50 bg-gray-500/5';
      default: return 'border-blue-500/50 bg-blue-500/5';
    }
  };

  const getTimeframeColor = (timeframe) => {
    switch (timeframe) {
      case 'قصير المدى': return 'bg-red-500/20 text-red-400';
      case 'متوسط المدى': return 'bg-yellow-500/20 text-yellow-400';
      case 'طويل المدى': return 'bg-green-500/20 text-green-400';
      default: return 'bg-blue-500/20 text-blue-400';
    }
  };

  const formatTime = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (minutes < 60) return `منذ ${minutes} دقيقة`;
    if (hours < 24) return `منذ ${hours} ساعة`;
    return `منذ ${days} يوم`;
  };

  const filteredNotifications = notifications.filter(notification => {
    if (activeFilter === 'all') return true;
    return notification.type === activeFilter;
  });

  const filters = [
    { id: 'all', name: 'الكل', icon: Bell },
    { id: 'opportunity', name: 'الفرص', icon: Star },
    { id: 'news', name: 'الأخبار', icon: Globe },
    { id: 'technical', name: 'فني', icon: TrendingUp },
    { id: 'risk', name: 'مخاطر', icon: AlertTriangle }
  ];

  const generateSmartAlert = async () => {
    try {
      // محاكاة إنشاء تنبيه ذكي جديد
      const newAlert = {
        id: Date.now(),
        type: 'opportunity',
        title: 'تنبيه ذكي جديد',
        message: 'تم اكتشاف فرصة جديدة بناء على تحليل الذكاء الاصطناعي',
        timestamp: new Date(),
        priority: 'high',
        confidence: 88
      };
      
      setNotifications(prev => [newAlert, ...prev]);
      showToast('تم إنشاء تنبيه ذكي جديد!', 'success');
    } catch (error) {
      showToast('خطأ في إنشاء التنبيه', 'error');
    }
  };

  return (
    <div className="p-4 space-y-6 fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">الإشعارات الذكية</h1>
          <p className="text-gray-400 mt-1">تنبيهات مدعومة بالذكاء الاصطناعي للأسواق المالية</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={generateSmartAlert}
            className="btn-primary flex items-center gap-2"
          >
            <Zap size={16} />
            تنبيه ذكي
          </button>
          <button className="btn-secondary p-2">
            <Settings size={16} />
          </button>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card text-center">
          <div className="text-2xl font-bold text-yellow-400">{notifications.filter(n => n.type === 'opportunity').length}</div>
          <div className="text-sm text-gray-400">فرص استثمارية</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-blue-400">{notifications.filter(n => n.type === 'news').length}</div>
          <div className="text-sm text-gray-400">أخبار مؤثرة</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-green-400">{notifications.filter(n => n.type === 'technical').length}</div>
          <div className="text-sm text-gray-400">إشارات فنية</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-red-400">{notifications.filter(n => n.type === 'risk').length}</div>
          <div className="text-sm text-gray-400">تحذيرات مخاطر</div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex overflow-x-auto gap-2 pb-2">
        {filters.map((filter) => {
          const Icon = filter.icon;
          return (
            <button
              key={filter.id}
              onClick={() => setActiveFilter(filter.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
                activeFilter === filter.id
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                  : 'bg-white/10 text-gray-400 hover:text-white hover:bg-white/20'
              }`}
            >
              <Icon size={16} />
              {filter.name}
            </button>
          );
        })}
      </div>

      {/* Notifications List */}
      <div className="space-y-4">
        {filteredNotifications.length > 0 ? (
          filteredNotifications.map((notification) => (
            <div
              key={notification.id}
              className={`card ${getPriorityColor(notification.priority)} border transition-all hover:scale-[1.01]`}
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 mt-1">
                  {getNotificationIcon(notification.type)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-white">{notification.title}</h3>
                    <div className="flex items-center gap-2">
                      {notification.timeframe && (
                        <span className={`text-xs px-2 py-1 rounded-full ${getTimeframeColor(notification.timeframe)}`}>
                          {notification.timeframe}
                        </span>
                      )}
                      <span className="text-xs text-gray-500">{formatTime(notification.timestamp)}</span>
                    </div>
                  </div>
                  
                  <p className="text-gray-300 text-sm leading-relaxed mb-3">
                    {notification.message}
                  </p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {notification.symbol && (
                        <span className="text-xs bg-white/10 text-blue-400 px-2 py-1 rounded">
                          {notification.symbol}
                        </span>
                      )}
                      {notification.symbols && (
                        <div className="flex gap-1">
                          {notification.symbols.map(symbol => (
                            <span key={symbol} className="text-xs bg-white/10 text-blue-400 px-2 py-1 rounded">
                              {symbol}
                            </span>
                          ))}
                        </div>
                      )}
                      {notification.confidence && (
                        <span className="text-xs text-green-400">
                          الثقة: {notification.confidence}%
                        </span>
                      )}
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {notification.action === 'buy' && (
                        <button className="btn-success text-xs px-3 py-1">
                          متابعة الشراء
                        </button>
                      )}
                      <button className="text-gray-400 hover:text-white transition-colors">
                        <BellRing size={16} />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="card text-center py-12">
            <Bell className="w-16 h-16 text-gray-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-400 mb-2">لا توجد إشعارات</h3>
            <p className="text-gray-500">سيتم عرض التنبيهات الذكية هنا عند توفرها</p>
          </div>
        )}
      </div>

      {/* Settings Panel */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">إعدادات الإشعارات</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(settings).map(([key, value]) => {
            const labels = {
              marketNews: 'أخبار الأسواق',
              longTermSignals: 'إشارات طويلة المدى',
              shortTermSignals: 'إشارات قصيرة المدى',
              opportunityAlerts: 'تنبيهات الفرص',
              riskAlerts: 'تحذيرات المخاطر',
              priceAlerts: 'تنبيهات الأسعار'
            };
            
            return (
              <div key={key} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                <span className="text-white">{labels[key]}</span>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={value}
                    onChange={(e) => setSettings(prev => ({ ...prev, [key]: e.target.checked }))}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-600 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            );
          })}
        </div>
      </div>

      {/* AI Insights */}
      <div className="card bg-gradient-to-r from-purple-500/10 to-pink-500/10 border-purple-500/30">
        <h3 className="font-semibold text-purple-400 mb-3">🤖 رؤى الذكاء الاصطناعي</h3>
        <div className="text-sm text-purple-200 space-y-2">
          <p><strong>تحليل السوق العام:</strong> الأسواق تشهد تقلبات معتدلة مع ميل إيجابي للعملات الرقمية</p>
          <p><strong>أفضل الفرص:</strong> Bitcoin و الذهب يظهران إشارات إيجابية للأسبوع القادم</p>
          <p><strong>تحذير:</strong> زيادة التقلبات المتوقعة في أسواق الفوركس بسبب القرارات الاقتصادية</p>
        </div>
      </div>
    </div>
  );
};

export default SmartNotifications;