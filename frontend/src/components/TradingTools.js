import React, { useState, useContext, useEffect } from 'react';
import { AppContext } from '../App';
import { 
  BarChart3, TrendingUp, Calculator, Target, Layers, 
  PieChart, Activity, Zap, Eye, Settings, ChevronRight 
} from 'lucide-react';
import axios from 'axios';

const TradingTools = () => {
  const { showToast } = useContext(AppContext);
  const [activeCategory, setActiveCategory] = useState('technical');
  const [selectedTool, setSelectedTool] = useState(null);
  const [toolData, setToolData] = useState(null);
  const [loading, setLoading] = useState(false);

  // أدوات التحليل الفني
  const technicalTools = {
    'candlestick': {
      name: 'الشمعات اليابانية',
      icon: '🕯️',
      description: 'تحليل أنماط الشمعات اليابانية لتحديد اتجاهات السوق',
      patterns: [
        { name: 'المطرقة (Hammer)', type: 'صاعد', strength: 'قوي' },
        { name: 'النجم الهابط (Shooting Star)', type: 'هابط', strength: 'متوسط' },
        { name: 'دوجي (Doji)', type: 'محايد', strength: 'ضعيف' },
        { name: 'الابتلاع الصاعد (Bullish Engulfing)', type: 'صاعد', strength: 'قوي جداً' },
        { name: 'الابتلاع الهابط (Bearish Engulfing)', type: 'هابط', strength: 'قوي جداً' },
        { name: 'الحرامي الصاعد (Bullish Harami)', type: 'صاعد', strength: 'متوسط' },
        { name: 'نجمة الصباح (Morning Star)', type: 'صاعد', strength: 'قوي جداً' },
        { name: 'نجمة المساء (Evening Star)', type: 'هابط', strength: 'قوي جداً' }
      ]
    },
    'indicators': {
      name: 'المؤشرات الفنية',
      icon: '📊',
      description: 'مؤشرات فنية متقدمة لتحليل الزخم والاتجاه',
      tools: [
        { name: 'RSI', fullName: 'مؤشر القوة النسبية', range: '0-100', best: 'تحديد ذروة الشراء/البيع' },
        { name: 'MACD', fullName: 'تقارب وتباعد المتوسطات', type: 'خط', best: 'تحديد نقاط التقاطع' },
        { name: 'Bollinger Bands', fullName: 'نطاقات بولينجر', type: 'نطاق', best: 'تحديد التقلبات' },
        { name: 'Stochastic', fullName: 'المذبذب العشوائي', range: '0-100', best: 'ذروة الشراء/البيع' },
        { name: 'Williams %R', fullName: 'مؤشر ويليامز', range: '-100 to 0', best: 'الزخم' },
        { name: 'ADX', fullName: 'مؤشر الاتجاه المتوسط', range: '0-100', best: 'قوة الاتجاه' },
        { name: 'CCI', fullName: 'مؤشر قناة السلع', type: 'مذبذب', best: 'تحديد الاتجاهات الجديدة' },
        { name: 'Fibonacci', fullName: 'مستويات فيبوناتشي', type: 'مستويات', best: 'تحديد الدعم والمقاومة' }
      ]
    },
    'patterns': {
      name: 'أنماط الرسم البياني',
      icon: '📈',
      description: 'التعرف على أنماط الرسم البياني الكلاسيكية',
      patterns: [
        { name: 'الرأس والكتفين', type: 'انعكاسي', reliability: '85%' },
        { name: 'المثلث الصاعد', type: 'استمراري', reliability: '72%' },
        { name: 'المثلث الهابط', type: 'استمراري', reliability: '72%' },
        { name: 'القاع المزدوج', type: 'انعكاسي', reliability: '78%' },
        { name: 'القمة المزدوجة', type: 'انعكاسي', reliability: '78%' },
        { name: 'الوتد الصاعد', type: 'انعكاسي', reliability: '70%' },
        { name: 'الوتد الهابط', type: 'انعكاسي', reliability: '70%' },
        { name: 'الكوب والمقبض', type: 'استمراري', reliability: '65%' }
      ]
    }
  };

  const calculatorTools = {
    'risk': {
      name: 'حاسبة إدارة المخاطر',
      icon: '🛡️',
      description: 'حساب حجم المركز والمخاطر المناسبة',
      fields: ['accountBalance', 'riskPercentage', 'entryPrice', 'stopLoss']
    },
    'fibonacci': {
      name: 'حاسبة فيبوناتشي',
      icon: '🔢',
      description: 'حساب مستويات الدعم والمقاومة بناء على فيبوناتشي',
      fields: ['highPrice', 'lowPrice', 'direction']
    },
    'pip': {
      name: 'حاسبة النقاط (Pip)',
      icon: '💰',
      description: 'حساب قيمة النقطة والأرباح/الخسائر المحتملة',
      fields: ['pair', 'lotSize', 'pips', 'accountCurrency']
    }
  };

  const categories = [
    { id: 'technical', name: 'التحليل الفني', icon: BarChart3 },
    { id: 'calculators', name: 'الحاسبات', icon: Calculator },
    { id: 'alerts', name: 'التنبيهات', icon: Zap },
    { id: 'screener', name: 'فحص الأسواق', icon: Eye }
  ];

  const renderTechnicalTools = () => (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {Object.entries(technicalTools).map(([key, tool]) => (
        <div key={key} className="card hover:border-blue-500/50 transition-all cursor-pointer">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-2xl">{tool.icon}</span>
            <div>
              <h3 className="font-semibold text-white">{tool.name}</h3>
              <p className="text-sm text-gray-400">{tool.description}</p>
            </div>
          </div>
          
          {key === 'candlestick' && (
            <div className="space-y-2">
              {tool.patterns.slice(0, 4).map((pattern, idx) => (
                <div key={idx} className="flex items-center justify-between p-2 bg-white/5 rounded">
                  <span className="text-sm text-white">{pattern.name}</span>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-2 py-1 rounded ${
                      pattern.type === 'صاعد' ? 'bg-green-500/20 text-green-400' :
                      pattern.type === 'هابط' ? 'bg-red-500/20 text-red-400' :
                      'bg-gray-500/20 text-gray-400'
                    }`}>
                      {pattern.type}
                    </span>
                    <span className="text-xs text-gray-400">{pattern.strength}</span>
                  </div>
                </div>
              ))}
              <button className="w-full text-blue-400 text-sm hover:text-blue-300 transition-colors">
                عرض جميع الأنماط ({tool.patterns.length})
              </button>
            </div>
          )}
          
          {key === 'indicators' && (
            <div className="space-y-2">
              {tool.tools.slice(0, 4).map((indicator, idx) => (
                <div key={idx} className="flex items-center justify-between p-2 bg-white/5 rounded">
                  <div>
                    <span className="text-sm font-medium text-white">{indicator.name}</span>
                    <p className="text-xs text-gray-400">{indicator.fullName}</p>
                  </div>
                  <span className="text-xs text-blue-400">{indicator.best}</span>
                </div>
              ))}
              <button className="w-full text-blue-400 text-sm hover:text-blue-300 transition-colors">
                عرض جميع المؤشرات ({tool.tools.length})
              </button>
            </div>
          )}
          
          {key === 'patterns' && (
            <div className="space-y-2">
              {tool.patterns.slice(0, 4).map((pattern, idx) => (
                <div key={idx} className="flex items-center justify-between p-2 bg-white/5 rounded">
                  <span className="text-sm text-white">{pattern.name}</span>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-2 py-1 rounded ${
                      pattern.type === 'انعكاسي' ? 'bg-orange-500/20 text-orange-400' :
                      'bg-blue-500/20 text-blue-400'
                    }`}>
                      {pattern.type}
                    </span>
                    <span className="text-xs text-green-400">{pattern.reliability}</span>
                  </div>
                </div>
              ))}
              <button className="w-full text-blue-400 text-sm hover:text-blue-300 transition-colors">
                عرض جميع الأنماط ({tool.patterns.length})
              </button>
            </div>
          )}
        </div>
      ))}
    </div>
  );

  const renderCalculators = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Object.entries(calculatorTools).map(([key, tool]) => (
        <div key={key} className="card hover:border-green-500/50 transition-all">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-2xl">{tool.icon}</span>
            <div>
              <h3 className="font-semibold text-white">{tool.name}</h3>
              <p className="text-sm text-gray-400">{tool.description}</p>
            </div>
          </div>
          
          <button 
            onClick={() => setSelectedTool(key)}
            className="btn-primary w-full"
          >
            فتح الحاسبة
          </button>
        </div>
      ))}
    </div>
  );

  const renderAlerts = () => (
    <div className="card">
      <h3 className="text-xl font-semibold text-white mb-4">إعداد التنبيهات الذكية</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-4">
          <div className="p-4 border border-blue-500/30 rounded-lg">
            <h4 className="font-medium text-blue-400 mb-2">تنبيهات الأسعار</h4>
            <p className="text-sm text-gray-300 mb-3">إشعار عند وصول السعر لمستوى معين</p>
            <button className="btn-secondary text-sm">إضافة تنبيه سعر</button>
          </div>
          
          <div className="p-4 border border-green-500/30 rounded-lg">
            <h4 className="font-medium text-green-400 mb-2">تنبيهات المؤشرات</h4>
            <p className="text-sm text-gray-300 mb-3">إشعار عند إشارات المؤشرات الفنية</p>
            <button className="btn-secondary text-sm">إضافة تنبيه مؤشر</button>
          </div>
        </div>
        
        <div className="space-y-4">
          <div className="p-4 border border-purple-500/30 rounded-lg">
            <h4 className="font-medium text-purple-400 mb-2">تنبيهات الأخبار</h4>
            <p className="text-sm text-gray-300 mb-3">إشعار بالأخبار المؤثرة على الأسواق</p>
            <button className="btn-secondary text-sm">تفعيل تنبيهات الأخبار</button>
          </div>
          
          <div className="p-4 border border-orange-500/30 rounded-lg">
            <h4 className="font-medium text-orange-400 mb-2">تنبيهات الفرص</h4>
            <p className="text-sm text-gray-300 mb-3">إشعار بالفرص الاستثمارية المحتملة</p>
            <button className="btn-secondary text-sm">تفعيل فحص الفرص</button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderScreener = () => (
    <div className="space-y-6">
      <div className="card">
        <h3 className="text-xl font-semibold text-white mb-4">فاحص الأسواق</h3>
        <p className="text-gray-400 mb-6">ابحث عن الأسهم والعملات بناء على معايير محددة</p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <select className="input-field">
            <option>نوع الأصل</option>
            <option>الأسهم</option>
            <option>العملات الرقمية</option>
            <option>الفوركس</option>
            <option>السلع</option>
          </select>
          
          <select className="input-field">
            <option>المؤشر</option>
            <option>RSI أكبر من 70</option>
            <option>RSI أقل من 30</option>
            <option>MACD إيجابي</option>
            <option>كسر مستوى المقاومة</option>
          </select>
          
          <button className="btn-primary">فحص الأسواق</button>
        </div>
        
        <div className="bg-white/5 rounded-lg p-4">
          <p className="text-center text-gray-400">سيتم عرض نتائج الفحص هنا</p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="p-4 space-y-6 fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">أدوات التداول المتقدمة</h1>
        <p className="text-gray-400 mt-1">مجموعة شاملة من أدوات التحليل الفني والحاسبات</p>
      </div>

      {/* Categories */}
      <div className="flex overflow-x-auto gap-2 pb-2">
        {categories.map((category) => {
          const Icon = category.icon;
          return (
            <button
              key={category.id}
              onClick={() => setActiveCategory(category.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
                activeCategory === category.id
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                  : 'bg-white/10 text-gray-400 hover:text-white hover:bg-white/20'
              }`}
            >
              <Icon size={16} />
              {category.name}
            </button>
          );
        })}
      </div>

      {/* Content */}
      <div>
        {activeCategory === 'technical' && renderTechnicalTools()}
        {activeCategory === 'calculators' && renderCalculators()}
        {activeCategory === 'alerts' && renderAlerts()}
        {activeCategory === 'screener' && renderScreener()}
      </div>

      {/* Educational Tips */}
      <div className="card bg-gradient-to-r from-blue-500/10 to-purple-500/10 border-blue-500/30">
        <h3 className="font-semibold text-blue-400 mb-3">💡 نصائح تعليمية</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-200">
          <div>
            <h4 className="font-medium mb-2">المؤشرات الفنية:</h4>
            <ul className="space-y-1">
              <li>• استخدم RSI لتحديد ذروة الشراء/البيع</li>
              <li>• MACD ممتاز لتحديد تغيير الاتجاه</li>
              <li>• نطاقات بولينجر تساعد في تحديد التقلبات</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium mb-2">إدارة المخاطر:</h4>
            <ul className="space-y-1">
              <li>• لا تخاطر بأكثر من 2% من رأس المال</li>
              <li>• استخدم وقف الخسارة دائماً</li>
              <li>• نوع محفظتك عبر أصول مختلفة</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradingTools;