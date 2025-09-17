import React, { useContext, useEffect, useState } from 'react';
import { AppContext } from '../App';
import { TrendingUp, TrendingDown, DollarSign, Activity, Eye, EyeOff, Plus, ShoppingCart } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import axios from 'axios';

const Home = () => {
  const { portfolio, trades, loading, createTrade, closeTrade, showToast, platforms } = useContext(AppContext);
  const [showBalance, setShowBalance] = useState(true);
  const [showQuickTrade, setShowQuickTrade] = useState(false);
  const [useRealTrading, setUseRealTrading] = useState(false);
  const [quickTradeData, setQuickTradeData] = useState({
    asset_type: 'crypto',
    symbol: 'BTCUSDT',
    trade_type: 'buy',
    quantity: 0.01
  });
  const [assetTypes, setAssetTypes] = useState({});
  const [availableSymbols, setAvailableSymbols] = useState([]);

  // Load asset types and symbols
  useEffect(() => {
    const loadAssetTypes = async () => {
      try {
        const response = await axios.get('/market/types/all');
        setAssetTypes(response.data);
        
        // Load default symbols for crypto
        const cryptoResponse = await axios.get('/market/symbols/crypto');
        setAvailableSymbols(cryptoResponse.data.symbols);
      } catch (error) {
        console.error('Error loading asset types:', error);
      }
    };
    
    loadAssetTypes();
  }, []);

  // Update symbols when asset type changes
  const handleAssetTypeChange = async (newAssetType) => {
    try {
      const response = await axios.get(`/market/symbols/${newAssetType}`);
      setAvailableSymbols(response.data.symbols);
      setQuickTradeData(prev => ({
        ...prev,
        asset_type: newAssetType,
        symbol: response.data.symbols[0] || ''
      }));
    } catch (error) {
      console.error('Error loading symbols:', error);
    }
  };

  // Check if any platform is connected for real trading
  const hasConnectedPlatforms = platforms.some(p => p.status === 'connected');

  // Mock chart data for portfolio performance
  const chartData = [
    { time: '09:00', value: 10000 },
    { time: '10:00', value: 10150 },
    { time: '11:00', value: 10080 },
    { time: '12:00', value: 10300 },
    { time: '13:00', value: 10250 },
    { time: '14:00', value: portfolio?.total_balance || 10200 },
  ];

  // Portfolio distribution data
  const portfolioData = [
    { name: 'متاح', value: portfolio?.available_balance || 0, color: '#3b82f6' },
    { name: 'مستثمر', value: portfolio?.invested_balance || 0, color: '#8b5cf6' },
  ];

  // Filter trades for recent activity
  const openTrades = trades.filter(trade => trade.status === 'open');
  const closedTrades = trades.filter(trade => trade.status === 'closed').slice(0, 5);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('ar-SA', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const formatPercentage = (value) => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  const handleQuickTrade = async () => {
    try {
      await createTrade({
        symbol: quickTradeData.symbol,
        trade_type: quickTradeData.trade_type,
        order_type: 'market',
        quantity: quickTradeData.quantity
      });
      setShowQuickTrade(false);
    } catch (error) {
      console.error('Error creating quick trade:', error);
    }
  };

  const handleCloseTrade = async (tradeId) => {
    try {
      await closeTrade(tradeId);
    } catch (error) {
      console.error('Error closing trade:', error);
    }
  };

  if (loading && !portfolio) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-6 fade-in">
      {/* Header */}
      <div className="text-center py-6">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
          نيون تريدر V7
        </h1>
        <p className="text-gray-400 mt-2">مرحباً بك في منصة التداول الذكية</p>
      </div>

      {/* Portfolio Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Total Balance */}
        <div className="card neon-blue">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white responsive-title">الرصيد الإجمالي</h3>
            <button
              onClick={() => setShowBalance(!showBalance)}
              className="text-gray-400 hover:text-white transition-colors"
            >
              {showBalance ? <Eye size={20} /> : <EyeOff size={20} />}
            </button>
          </div>
          <div className="space-y-2">
            <p className="text-3xl font-bold text-white text-overflow-fix">
              {showBalance ? formatCurrency(portfolio?.total_balance || 0) : '••••••'}
            </p>
            <div className="flex items-center gap-2">
              <DollarSign size={16} className="text-green-400" />
              <span className="text-sm text-gray-300 responsive-text">متاح: {showBalance ? formatCurrency(portfolio?.available_balance || 0) : '••••••'}</span>
            </div>
          </div>
        </div>

        {/* Daily PnL */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white responsive-title">الربح/الخسارة اليومية</h3>
            {(portfolio?.daily_pnl || 0) >= 0 ? (
              <TrendingUp className="text-green-400" size={20} />
            ) : (
              <TrendingDown className="text-red-400" size={20} />
            )}
          </div>
          <div className="space-y-2">
            <p className={`text-3xl font-bold text-overflow-fix ${(portfolio?.daily_pnl || 0) >= 0 ? 'pnl-positive' : 'pnl-negative'}`}>
              {showBalance ? formatCurrency(portfolio?.daily_pnl || 0) : '••••••'}
            </p>
            <p className={`text-sm responsive-text ${(portfolio?.daily_pnl || 0) >= 0 ? 'pnl-positive' : 'pnl-negative'}`}>
              {formatPercentage(((portfolio?.daily_pnl || 0) / (portfolio?.total_balance || 1)) * 100)}
            </p>
          </div>
        </div>

        {/* Active Trades */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white responsive-title">الصفقات النشطة</h3>
            <Activity className="text-blue-400" size={20} />
          </div>
          <div className="space-y-2">
            <p className="text-3xl font-bold text-white">{openTrades.length}</p>
            <p className="text-sm text-gray-300 responsive-text">
              مستثمر: {showBalance ? formatCurrency(portfolio?.invested_balance || 0) : '••••••'}
            </p>
          </div>
        </div>
      </div>

      {/* Portfolio Chart */}
      <div className="card">
        <h3 className="text-xl font-semibold text-white mb-6">أداء المحفظة</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <XAxis 
                dataKey="time" 
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#9ca3af', fontSize: 12 }}
              />
              <YAxis 
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#9ca3af', fontSize: 12 }}
              />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="url(#gradient)"
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2 }}
              />
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#3b82f6" />
                  <stop offset="100%" stopColor="#8b5cf6" />
                </linearGradient>
              </defs>
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Portfolio Distribution */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="text-xl font-semibold text-white mb-6">توزيع المحفظة</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={portfolioData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {portfolioData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-4 mt-4">
            {portfolioData.map((item, index) => (
              <div key={index} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                <span className="text-sm text-gray-300">{item.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Trades */}
        <div className="card">
          <h3 className="text-xl font-semibold text-white mb-6">الصفقات المغلقة مؤخراً</h3>
          <div className="space-y-3">
            {closedTrades.length > 0 ? (
              closedTrades.map((trade) => (
                <div key={trade.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <div>
                    <p className="font-medium text-white">{trade.symbol}</p>
                    <p className="text-sm text-gray-400">
                      {trade.trade_type === 'buy' ? 'شراء' : 'بيع'} • {formatCurrency(trade.entry_price)}
                    </p>
                  </div>
                  <div className="text-left">
                    <p className={`font-semibold ${trade.pnl >= 0 ? 'pnl-positive' : 'pnl-negative'}`}>
                      {formatCurrency(trade.pnl)}
                    </p>
                    <p className="text-sm text-gray-400">
                      {new Date(trade.closed_at).toLocaleDateString('ar-SA')}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-400">لا توجد صفقات مغلقة</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Open Trades */}
      {openTrades.length > 0 && (
        <div className="card">
          <h3 className="text-xl font-semibold text-white mb-6">الصفقات المفتوحة</h3>
          <div className="space-y-3">
            {openTrades.map((trade) => (
              <div key={trade.id} className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-blue-500/30">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="font-bold text-white">{trade.symbol}</span>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      trade.trade_type === 'buy' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                    }`}>
                      {trade.trade_type === 'buy' ? 'شراء' : 'بيع'}
                    </span>
                    <span className="px-2 py-1 rounded-full text-xs bg-blue-500/20 text-blue-400">
                      {trade.order_type}
                    </span>
                  </div>
                  <div className="flex gap-4 text-sm text-gray-300">
                    <span>الكمية: {trade.quantity}</span>
                    <span>سعر الدخول: {formatCurrency(trade.entry_price)}</span>
                    {trade.stop_loss && <span>وقف الخسارة: {formatCurrency(trade.stop_loss)}</span>}
                    {trade.take_profit && <span>جني الأرباح: {formatCurrency(trade.take_profit)}</span>}
                  </div>
                </div>
                <div className="text-left">
                  <p className={`font-semibold text-lg ${trade.pnl >= 0 ? 'pnl-positive' : 'pnl-negative'}`}>
                    {formatCurrency(trade.pnl)}
                  </p>
                  <p className="text-sm text-gray-400 mb-2">
                    {new Date(trade.created_at).toLocaleDateString('ar-SA')}
                  </p>
                  <button
                    onClick={() => handleCloseTrade(trade.id)}
                    className="btn-danger text-xs px-3 py-1"
                    disabled={loading}
                  >
                    إغلاق
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Trading Section */}
      <div className="card border-green-500/30">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <ShoppingCart className="text-green-400" size={20} />
            تداول سريع
          </h3>
          <button
            onClick={() => setShowQuickTrade(!showQuickTrade)}
            className="btn-primary text-sm px-4 py-2"
          >
            <Plus size={16} className="mr-1" />
            صفقة جديدة
          </button>
        </div>

        {showQuickTrade && (
          <div className="bg-white/5 p-4 rounded-lg space-y-4">
            
            {/* Real Trading Toggle */}
            {hasConnectedPlatforms && (
              <div className="flex items-center justify-between p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                <div>
                  <span className="text-blue-400 font-medium">التداول الحقيقي</span>
                  <p className="text-xs text-blue-300">استخدام منصة متصلة للتداول الفعلي</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={useRealTrading}
                    onChange={(e) => setUseRealTrading(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-600 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">نوع الأصل</label>
                <select
                  value={quickTradeData.asset_type}
                  onChange={(e) => handleAssetTypeChange(e.target.value)}
                  className="input-field"
                >
                  {Object.entries(assetTypes).map(([key, data]) => (
                    <option key={key} value={key}>{data.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">الرمز</label>
                <select
                  value={quickTradeData.symbol}
                  onChange={(e) => setQuickTradeData({...quickTradeData, symbol: e.target.value})}
                  className="input-field"
                >
                  {availableSymbols.map(symbol => (
                    <option key={symbol} value={symbol}>{symbol}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">النوع</label>
                <select
                  value={quickTradeData.trade_type}
                  onChange={(e) => setQuickTradeData({...quickTradeData, trade_type: e.target.value})}
                  className="input-field"
                >
                  <option value="buy">شراء</option>
                  <option value="sell">بيع</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">الكمية</label>
                <input
                  type="number"
                  value={quickTradeData.quantity}
                  onChange={(e) => setQuickTradeData({...quickTradeData, quantity: parseFloat(e.target.value)})}
                  className="input-field"
                  step="0.001"
                  min="0.001"
                />
              </div>
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleQuickTrade}
                className={`flex-1 px-6 py-3 rounded-lg font-semibold transition-all ${
                  quickTradeData.trade_type === 'buy' 
                    ? 'bg-green-500 hover:bg-green-600 text-white' 
                    : 'bg-red-500 hover:bg-red-600 text-white'
                }`}
                disabled={loading}
              >
                {loading ? <div className="spinner mr-2"></div> : null}
                {quickTradeData.trade_type === 'buy' ? 'شراء' : 'بيع'} {quickTradeData.symbol}
              </button>
              <button
                onClick={() => setShowQuickTrade(false)}
                className="btn-secondary px-6"
              >
                إلغاء
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;