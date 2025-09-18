import React, { useContext, useState, useEffect } from 'react';
import { AppContext } from '../App';
import { Bot, TrendingUp, AlertCircle, CheckCircle, X, Edit3, Send, Mic, MicOff } from 'lucide-react';
import axios from 'axios';

const Assistant = () => {
  const { showToast, createTrade, loading, fetchTrades, fetchPortfolio } = useContext(AppContext);
  const [dailyPlan, setDailyPlan] = useState(null);
  const [selectedOpportunity, setSelectedOpportunity] = useState(null);
  const [showTradeDialog, setShowTradeDialog] = useState(false);
  const [customMessage, setCustomMessage] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isListening, setIsListening] = useState(false);

  const fetchDailyPlan = async () => {
    try {
      const response = await axios.get('/ai/daily-plan');
      setDailyPlan(response.data);
    } catch (error) {
      console.error('Error fetching daily plan:', error);
      showToast('خطأ في تحميل الخطة اليومية', 'error');
    }
  };

  const analyzeMarket = async (symbol) => {
    try {
      setIsAnalyzing(true);
      const response = await axios.post('/ai/analyze', {
        symbol: symbol,
        timeframe: '1h'
      });
      setAnalysis(response.data);
    } catch (error) {
      console.error('Error analyzing market:', error);
      showToast('خطأ في تحليل السوق', 'error');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleOpportunityAction = (opportunity, action) => {
    if (action === 'approve') {
      setSelectedOpportunity(opportunity);
      setShowTradeDialog(true);
    } else if (action === 'reject') {
      showToast('تم رفض التوصية', 'info');
    }
  };

  const executeTrade = async () => {
    if (!selectedOpportunity) return;

    try {
      const tradeData = {
        symbol: selectedOpportunity.symbol,
        trade_type: selectedOpportunity.action,
        order_type: 'market',
        quantity: 0.1, // Default quantity - can be customized
        stop_loss: selectedOpportunity.stop_loss,
        take_profit: selectedOpportunity.target
      };

      const result = await createTrade(tradeData);
      if (result) {
        setShowTradeDialog(false);
        setSelectedOpportunity(null);
        showToast('تم تنفيذ الصفقة بنجاح من المساعد!', 'success');
        
        // Refresh data
        await fetchTrades();
        await fetchPortfolio();
      }
    } catch (error) {
      console.error('Error executing trade from assistant:', error);
      showToast('خطأ في تنفيذ الصفقة من المساعد', 'error');
    }
  };

  const getConfidenceColor = (confidence) => {
    switch (confidence) {
      case 'high':
        return 'text-green-400 bg-green-500/20 border-green-500/30';
      case 'medium':
        return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
      default:
        return 'text-red-400 bg-red-500/20 border-red-500/30';
    }
  };

  const getConfidenceIcon = (confidence) => {
    switch (confidence) {
      case 'high':
        return '🟢';
      case 'medium':
        return '🟡';
      default:
        return '🔴';
    }
  };

  const getConfidenceText = (confidence) => {
    switch (confidence) {
      case 'high':
        return 'عالية';
      case 'medium':
        return 'متوسطة';
      default:
        return 'منخفضة';
    }
  };

  const handleSendMessage = async () => {
    if (!customMessage.trim()) return;

    try {
      // Extract symbol from message if possible
      const symbolMatch = customMessage.match(/([A-Z]{3,}USDT|BTC|ETH|ADA|BNB)/i);
      if (symbolMatch) {
        const symbol = symbolMatch[1].toUpperCase();
        if (!symbol.includes('USDT')) {
          await analyzeMarket(`${symbol}USDT`);
        } else {
          await analyzeMarket(symbol);
        }
      } else {
        showToast('لتحليل دقيق، اذكر رمز العملة (مثل: BTCUSDT)', 'info');
      }
      setCustomMessage('');
    } catch (error) {
      console.error('Error processing message:', error);
    }
  };

  // Mock voice recognition
  const toggleVoice = () => {
    setIsListening(!isListening);
    if (!isListening) {
      showToast('ميزة التعرف على الصوت قيد التطوير', 'info');
      setTimeout(() => setIsListening(false), 3000);
    }
  };

  useEffect(() => {
    fetchDailyPlan();
  }, []);

  return (
    <div className="p-4 space-y-6 fade-in">
      {/* Header */}
      <div className="text-center">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center neon-blue">
          <Bot className="text-white" size={28} />
        </div>
        <h1 className="text-2xl font-bold text-white">المساعد الذكي</h1>
        <p className="text-gray-400 mt-1">مدير أعمالك الشخصي للتداول</p>
      </div>

      {/* Welcome Message */}
      <div className="card border-blue-500/30">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
            <Bot className="text-white" size={20} />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-white mb-2 responsive-title">مرحباً بك! 👋</h3>
            <p className="text-gray-300 text-sm leading-relaxed responsive-text text-overflow-fix">
              أنا مساعدك الذكي لتحليل الأسواق وتقديم التوصيات. سأقوم بإعداد خطة يومية مخصصة
              وتحديد الفرص الاستثمارية المناسبة لك. جميع القرارات النهائية بيدك!
            </p>
          </div>
        </div>
      </div>

      {/* Daily Plan */}
      {dailyPlan && (
        <div className="card">
          <div className="flex items-center gap-3 mb-6">
            <TrendingUp className="text-blue-400" size={24} />
            <h2 className="text-xl font-semibold text-white">الخطة اليومية</h2>
            <span className="text-sm text-gray-400">
              {new Date(dailyPlan.date).toLocaleDateString('ar-SA')}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
              <h4 className="font-medium text-blue-400 mb-2">تحليل السوق</h4>
              <p className="text-white text-sm">{dailyPlan.market_analysis}</p>
            </div>
            <div className="p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
              <h4 className="font-medium text-purple-400 mb-2">استراتيجية التداول</h4>
              <p className="text-white text-sm">{dailyPlan.trading_strategy}</p>
            </div>
            <div className="p-4 bg-orange-500/10 border border-orange-500/30 rounded-lg">
              <h4 className="font-medium text-orange-400 mb-2">مستوى المخاطرة</h4>
              <p className="text-white text-sm font-semibold">{dailyPlan.risk_level}</p>
            </div>
          </div>

          {/* Opportunities */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">الفرص المتاحة اليوم</h3>
            <div className="space-y-4">
              {dailyPlan.opportunities.map((opportunity, index) => (
                <div key={index} className="card bg-white/5 border border-white/10">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <span className="font-bold text-white text-lg">{opportunity.symbol}</span>
                        <span className={`px-3 py-1 rounded-full text-xs border ${getConfidenceColor(opportunity.confidence)}`}>
                          {getConfidenceIcon(opportunity.confidence)} {getConfidenceText(opportunity.confidence)}
                        </span>
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          opportunity.action === 'buy' ? 'bg-green-500/20 text-green-400' : 
                          opportunity.action === 'sell' ? 'bg-red-500/20 text-red-400' : 
                          'bg-gray-500/20 text-gray-400'
                        }`}>
                          {opportunity.action === 'buy' ? 'شراء' : opportunity.action === 'sell' ? 'بيع' : 'انتظار'}
                        </span>
                      </div>
                      
                      <p className="text-gray-300 text-sm mb-3">{opportunity.reason}</p>
                      
                      <div className="flex gap-4 text-sm text-gray-400">
                        <span>الهدف: ${opportunity.target}</span>
                        <span>وقف الخسارة: ${opportunity.stop_loss}</span>
                      </div>
                    </div>

                    <div className="flex gap-2">
                      <button
                        onClick={() => handleOpportunityAction(opportunity, 'approve')}
                        className="btn-success text-sm px-4 py-2"
                        disabled={loading}
                      >
                        <CheckCircle size={16} className="mr-1" />
                        موافق
                      </button>
                      <button
                        onClick={() => handleOpportunityAction(opportunity, 'reject')}
                        className="btn-secondary text-sm px-4 py-2"
                      >
                        <X size={16} className="mr-1" />
                        رفض
                      </button>
                      <button
                        onClick={() => analyzeMarket(opportunity.symbol)}
                        className="btn-secondary text-sm px-4 py-2"
                        disabled={isAnalyzing}
                      >
                        <Edit3 size={16} className="mr-1" />
                        تفاصيل
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Custom Analysis */}
      <div className="card">
        <h2 className="text-xl font-semibold text-white mb-4">تحليل مخصص</h2>
        <div className="flex gap-2">
          <input
            type="text"
            value={customMessage}
            onChange={(e) => setCustomMessage(e.target.value)}
            placeholder="اكتب رمز العملة للتحليل (مثل: BTCUSDT)"
            className="input-field flex-1"
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          />
          <button
            onClick={toggleVoice}
            className={`btn-secondary px-4 ${isListening ? 'bg-red-500/20 text-red-400' : ''}`}
          >
            {isListening ? <MicOff size={20} /> : <Mic size={20} />}
          </button>
          <button
            onClick={handleSendMessage}
            className="btn-primary px-6"
            disabled={!customMessage.trim() || isAnalyzing}
          >
            {isAnalyzing ? <div className="spinner"></div> : <Send size={20} />}
          </button>
        </div>
      </div>

      {/* Analysis Results */}
      {analysis && (
        <div className="card border-green-500/30">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-500 to-blue-500 flex items-center justify-center">
              <Bot className="text-white" size={20} />
            </div>
            <div>
              <h3 className="font-semibold text-white">تحليل {analysis.symbol}</h3>
              <p className="text-sm text-gray-400">
                {new Date(analysis.timestamp).toLocaleString('ar-SA')}
              </p>
            </div>
          </div>

          <div className="bg-white/5 p-4 rounded-lg mb-4">
            <h4 className="font-medium text-green-400 mb-2">بيانات السوق الحالية</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-400">السعر الحالي:</span>
                <p className="text-white font-semibold">${analysis.market_data.price}</p>
              </div>
              <div>
                <span className="text-gray-400">التغيير 24س:</span>
                <p className={`font-semibold ${analysis.market_data.change_24h >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  ${analysis.market_data.change_24h}
                </p>
              </div>
              <div>
                <span className="text-gray-400">الأعلى 24س:</span>
                <p className="text-white">${analysis.market_data.high_24h}</p>
              </div>
              <div>
                <span className="text-gray-400">الأدنى 24س:</span>
                <p className="text-white">${analysis.market_data.low_24h}</p>
              </div>
            </div>
          </div>

          <div className="bg-blue-500/10 p-4 rounded-lg">
            <h4 className="font-medium text-blue-400 mb-2">التحليل الفني</h4>
            <p className="text-white text-sm leading-relaxed">{analysis.analysis}</p>
          </div>
        </div>
      )}

      {/* Trade Confirmation Dialog */}
      {showTradeDialog && selectedOpportunity && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="card max-w-md w-full border-blue-500/30">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-white">تأكيد الصفقة</h3>
              <button
                onClick={() => setShowTradeDialog(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            <div className="space-y-4">
              <div className="bg-white/5 p-4 rounded-lg">
                <h4 className="font-medium text-white mb-2">{selectedOpportunity.symbol}</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">النوع:</span>
                    <span className="text-white">
                      {selectedOpportunity.action === 'buy' ? 'شراء' : 'بيع'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">الكمية:</span>
                    <span className="text-white">0.1</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">الهدف:</span>
                    <span className="text-green-400">${selectedOpportunity.target}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">وقف الخسارة:</span>
                    <span className="text-red-400">${selectedOpportunity.stop_loss}</span>
                  </div>
                </div>
              </div>

              <div className="bg-amber-500/10 border border-amber-500/30 p-3 rounded-lg">
                <div className="flex items-center gap-2">
                  <AlertCircle className="text-amber-400" size={16} />
                  <span className="text-amber-400 font-medium">تنبيه</span>
                </div>
                <p className="text-amber-200 text-sm mt-1">
                  سيتم تنفيذ هذه الصفقة في وضع Paper Trading (وهمي).
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={executeTrade}
                  className="btn-primary flex-1"
                  disabled={loading}
                >
                  {loading ? <div className="spinner"></div> : 'تنفيذ الصفقة'}
                </button>
                <button
                  onClick={() => setShowTradeDialog(false)}
                  className="btn-secondary px-6"
                >
                  إلغاء
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Assistant;