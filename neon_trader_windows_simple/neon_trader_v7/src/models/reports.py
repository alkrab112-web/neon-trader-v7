"""
نموذج التقارير والسجلات لـ Neon Trader V7
يوفر تحليل الأداء وتوليد التقارير المفصلة
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
from dataclasses import dataclass
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

# تعيين الخط العربي
plt.rcParams['font.family'] = ['Noto Sans Arabic', 'Arial Unicode MS', 'Tahoma']
plt.rcParams['axes.unicode_minus'] = False

@dataclass
class TradeRecord:
    """سجل صفقة"""
    id: str
    symbol: str
    side: str  # buy/sell
    entry_time: datetime
    exit_time: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    pnl: float
    pnl_percentage: float
    fees: float
    strategy: str
    status: str  # open/closed/cancelled

@dataclass
class PerformanceMetrics:
    """مقاييس الأداء"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    total_pnl_percentage: float
    max_drawdown: float
    sharpe_ratio: float
    profit_factor: float
    average_win: float
    average_loss: float
    largest_win: float
    largest_loss: float
    consecutive_wins: int
    consecutive_losses: int

class ReportsManager:
    """مدير التقارير والسجلات"""
    
    def __init__(self, data_dir: str = None):
        self.logger = logging.getLogger(__name__)
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), '..', 'data')
        self.trades_file = os.path.join(self.data_dir, 'trades.json')
        self.performance_file = os.path.join(self.data_dir, 'performance.json')
        
        # إنشاء مجلد البيانات إذا لم يكن موجوداً
        os.makedirs(self.data_dir, exist_ok=True)
        
        # تحميل البيانات الموجودة
        self.trades = self._load_trades()
        self.performance_history = self._load_performance_history()
    
    def add_trade_record(self, trade_data: Dict[str, Any]) -> str:
        """إضافة سجل صفقة جديدة"""
        try:
            trade_id = f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.trades)}"
            
            trade_record = TradeRecord(
                id=trade_id,
                symbol=trade_data.get('symbol', ''),
                side=trade_data.get('side', ''),
                entry_time=datetime.fromisoformat(trade_data.get('entry_time', datetime.now().isoformat())),
                exit_time=datetime.fromisoformat(trade_data['exit_time']) if trade_data.get('exit_time') else None,
                entry_price=float(trade_data.get('entry_price', 0)),
                exit_price=float(trade_data.get('exit_price', 0)) if trade_data.get('exit_price') else None,
                quantity=float(trade_data.get('quantity', 0)),
                pnl=float(trade_data.get('pnl', 0)),
                pnl_percentage=float(trade_data.get('pnl_percentage', 0)),
                fees=float(trade_data.get('fees', 0)),
                strategy=trade_data.get('strategy', 'manual'),
                status=trade_data.get('status', 'open')
            )
            
            self.trades.append(trade_record)
            self._save_trades()
            
            self.logger.info(f"تم إضافة سجل صفقة جديدة: {trade_id}")
            return trade_id
            
        except Exception as e:
            self.logger.error(f"خطأ في إضافة سجل الصفقة: {e}")
            return ""
    
    def update_trade_record(self, trade_id: str, update_data: Dict[str, Any]) -> bool:
        """تحديث سجل صفقة موجودة"""
        try:
            for i, trade in enumerate(self.trades):
                if trade.id == trade_id:
                    # تحديث البيانات
                    if 'exit_time' in update_data:
                        self.trades[i].exit_time = datetime.fromisoformat(update_data['exit_time'])
                    if 'exit_price' in update_data:
                        self.trades[i].exit_price = float(update_data['exit_price'])
                    if 'pnl' in update_data:
                        self.trades[i].pnl = float(update_data['pnl'])
                    if 'pnl_percentage' in update_data:
                        self.trades[i].pnl_percentage = float(update_data['pnl_percentage'])
                    if 'status' in update_data:
                        self.trades[i].status = update_data['status']
                    if 'fees' in update_data:
                        self.trades[i].fees = float(update_data['fees'])
                    
                    self._save_trades()
                    self.logger.info(f"تم تحديث سجل الصفقة: {trade_id}")
                    return True
            
            self.logger.warning(f"لم يتم العثور على الصفقة: {trade_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"خطأ في تحديث سجل الصفقة: {e}")
            return False
    
    def calculate_performance_metrics(self, start_date: Optional[datetime] = None, 
                                    end_date: Optional[datetime] = None) -> PerformanceMetrics:
        """حساب مقاييس الأداء"""
        try:
            # تصفية الصفقات حسب التاريخ
            filtered_trades = self._filter_trades_by_date(start_date, end_date)
            closed_trades = [t for t in filtered_trades if t.status == 'closed']
            
            if not closed_trades:
                return PerformanceMetrics(
                    total_trades=0, winning_trades=0, losing_trades=0,
                    win_rate=0, total_pnl=0, total_pnl_percentage=0,
                    max_drawdown=0, sharpe_ratio=0, profit_factor=0,
                    average_win=0, average_loss=0, largest_win=0, largest_loss=0,
                    consecutive_wins=0, consecutive_losses=0
                )
            
            # حساب المقاييس الأساسية
            total_trades = len(closed_trades)
            winning_trades = len([t for t in closed_trades if t.pnl > 0])
            losing_trades = len([t for t in closed_trades if t.pnl < 0])
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            
            total_pnl = sum(t.pnl for t in closed_trades)
            total_pnl_percentage = sum(t.pnl_percentage for t in closed_trades)
            
            # حساب الأرباح والخسائر
            wins = [t.pnl for t in closed_trades if t.pnl > 0]
            losses = [t.pnl for t in closed_trades if t.pnl < 0]
            
            average_win = np.mean(wins) if wins else 0
            average_loss = np.mean(losses) if losses else 0
            largest_win = max(wins) if wins else 0
            largest_loss = min(losses) if losses else 0
            
            # حساب عامل الربح
            gross_profit = sum(wins) if wins else 0
            gross_loss = abs(sum(losses)) if losses else 0
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
            
            # حساب أقصى انخفاض
            max_drawdown = self._calculate_max_drawdown(closed_trades)
            
            # حساب نسبة شارب
            sharpe_ratio = self._calculate_sharpe_ratio(closed_trades)
            
            # حساب الانتصارات والخسائر المتتالية
            consecutive_wins, consecutive_losses = self._calculate_consecutive_trades(closed_trades)
            
            return PerformanceMetrics(
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                win_rate=win_rate,
                total_pnl=total_pnl,
                total_pnl_percentage=total_pnl_percentage,
                max_drawdown=max_drawdown,
                sharpe_ratio=sharpe_ratio,
                profit_factor=profit_factor,
                average_win=average_win,
                average_loss=average_loss,
                largest_win=largest_win,
                largest_loss=largest_loss,
                consecutive_wins=consecutive_wins,
                consecutive_losses=consecutive_losses
            )
            
        except Exception as e:
            self.logger.error(f"خطأ في حساب مقاييس الأداء: {e}")
            return PerformanceMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    
    def generate_daily_report(self, date: datetime = None) -> Dict[str, Any]:
        """توليد تقرير يومي"""
        try:
            if date is None:
                date = datetime.now()
            
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            
            # الصفقات اليومية
            daily_trades = self._filter_trades_by_date(start_date, end_date)
            
            # مقاييس الأداء اليومي
            daily_metrics = self.calculate_performance_metrics(start_date, end_date)
            
            # إحصائيات إضافية
            open_trades = [t for t in daily_trades if t.status == 'open']
            closed_trades = [t for t in daily_trades if t.status == 'closed']
            
            # تحليل الرموز
            symbols_analysis = self._analyze_symbols_performance(daily_trades)
            
            # تحليل الاستراتيجيات
            strategies_analysis = self._analyze_strategies_performance(daily_trades)
            
            return {
                'date': date.strftime('%Y-%m-%d'),
                'summary': {
                    'total_trades': len(daily_trades),
                    'open_trades': len(open_trades),
                    'closed_trades': len(closed_trades),
                    'daily_pnl': daily_metrics.total_pnl,
                    'daily_pnl_percentage': daily_metrics.total_pnl_percentage,
                    'win_rate': daily_metrics.win_rate
                },
                'performance_metrics': daily_metrics.__dict__,
                'symbols_analysis': symbols_analysis,
                'strategies_analysis': strategies_analysis,
                'trades_details': [self._trade_to_dict(t) for t in daily_trades]
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في توليد التقرير اليومي: {e}")
            return {}
    
    def generate_weekly_report(self, week_start: datetime = None) -> Dict[str, Any]:
        """توليد تقرير أسبوعي"""
        try:
            if week_start is None:
                today = datetime.now()
                week_start = today - timedelta(days=today.weekday())
            
            week_end = week_start + timedelta(days=7)
            
            # الصفقات الأسبوعية
            weekly_trades = self._filter_trades_by_date(week_start, week_end)
            
            # مقاييس الأداء الأسبوعي
            weekly_metrics = self.calculate_performance_metrics(week_start, week_end)
            
            # تحليل يومي للأسبوع
            daily_analysis = []
            for i in range(7):
                day = week_start + timedelta(days=i)
                day_report = self.generate_daily_report(day)
                daily_analysis.append({
                    'date': day.strftime('%Y-%m-%d'),
                    'day_name': day.strftime('%A'),
                    'pnl': day_report.get('summary', {}).get('daily_pnl', 0),
                    'trades_count': day_report.get('summary', {}).get('total_trades', 0)
                })
            
            return {
                'week_start': week_start.strftime('%Y-%m-%d'),
                'week_end': week_end.strftime('%Y-%m-%d'),
                'summary': {
                    'total_trades': len(weekly_trades),
                    'weekly_pnl': weekly_metrics.total_pnl,
                    'weekly_pnl_percentage': weekly_metrics.total_pnl_percentage,
                    'win_rate': weekly_metrics.win_rate,
                    'best_day': max(daily_analysis, key=lambda x: x['pnl']) if daily_analysis else None,
                    'worst_day': min(daily_analysis, key=lambda x: x['pnl']) if daily_analysis else None
                },
                'performance_metrics': weekly_metrics.__dict__,
                'daily_analysis': daily_analysis,
                'symbols_analysis': self._analyze_symbols_performance(weekly_trades),
                'strategies_analysis': self._analyze_strategies_performance(weekly_trades)
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في توليد التقرير الأسبوعي: {e}")
            return {}
    
    def generate_monthly_report(self, month: int = None, year: int = None) -> Dict[str, Any]:
        """توليد تقرير شهري"""
        try:
            if month is None or year is None:
                now = datetime.now()
                month = month or now.month
                year = year or now.year
            
            month_start = datetime(year, month, 1)
            if month == 12:
                month_end = datetime(year + 1, 1, 1)
            else:
                month_end = datetime(year, month + 1, 1)
            
            # الصفقات الشهرية
            monthly_trades = self._filter_trades_by_date(month_start, month_end)
            
            # مقاييس الأداء الشهري
            monthly_metrics = self.calculate_performance_metrics(month_start, month_end)
            
            # تحليل أسبوعي للشهر
            weekly_analysis = []
            current_week_start = month_start
            week_number = 1
            
            while current_week_start < month_end:
                current_week_end = min(current_week_start + timedelta(days=7), month_end)
                week_trades = self._filter_trades_by_date(current_week_start, current_week_end)
                week_pnl = sum(t.pnl for t in week_trades if t.status == 'closed')
                
                weekly_analysis.append({
                    'week_number': week_number,
                    'start_date': current_week_start.strftime('%Y-%m-%d'),
                    'end_date': current_week_end.strftime('%Y-%m-%d'),
                    'pnl': week_pnl,
                    'trades_count': len(week_trades)
                })
                
                current_week_start = current_week_end
                week_number += 1
            
            return {
                'month': month,
                'year': year,
                'month_name': month_start.strftime('%B %Y'),
                'summary': {
                    'total_trades': len(monthly_trades),
                    'monthly_pnl': monthly_metrics.total_pnl,
                    'monthly_pnl_percentage': monthly_metrics.total_pnl_percentage,
                    'win_rate': monthly_metrics.win_rate,
                    'best_week': max(weekly_analysis, key=lambda x: x['pnl']) if weekly_analysis else None,
                    'worst_week': min(weekly_analysis, key=lambda x: x['pnl']) if weekly_analysis else None
                },
                'performance_metrics': monthly_metrics.__dict__,
                'weekly_analysis': weekly_analysis,
                'symbols_analysis': self._analyze_symbols_performance(monthly_trades),
                'strategies_analysis': self._analyze_strategies_performance(monthly_trades)
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في توليد التقرير الشهري: {e}")
            return {}
    
    def generate_performance_chart(self, period_days: int = 30) -> str:
        """توليد رسم بياني للأداء"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # الحصول على البيانات اليومية
            daily_data = []
            current_date = start_date
            cumulative_pnl = 0
            
            while current_date <= end_date:
                day_start = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timedelta(days=1)
                
                day_trades = self._filter_trades_by_date(day_start, day_end)
                day_pnl = sum(t.pnl for t in day_trades if t.status == 'closed')
                cumulative_pnl += day_pnl
                
                daily_data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'daily_pnl': day_pnl,
                    'cumulative_pnl': cumulative_pnl,
                    'trades_count': len(day_trades)
                })
                
                current_date += timedelta(days=1)
            
            # إنشاء الرسم البياني
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            
            dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in daily_data]
            cumulative_pnl_values = [d['cumulative_pnl'] for d in daily_data]
            daily_pnl_values = [d['daily_pnl'] for d in daily_data]
            
            # الرسم البياني للأرباح التراكمية
            ax1.plot(dates, cumulative_pnl_values, linewidth=2, color='#00ff88')
            ax1.fill_between(dates, cumulative_pnl_values, alpha=0.3, color='#00ff88')
            ax1.set_title('الأرباح والخسائر التراكمية', fontsize=14, fontweight='bold')
            ax1.set_ylabel('الأرباح/الخسائر ($)', fontsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.axhline(y=0, color='white', linestyle='--', alpha=0.5)
            
            # الرسم البياني للأرباح اليومية
            colors = ['#00ff88' if pnl >= 0 else '#ff4444' for pnl in daily_pnl_values]
            ax2.bar(dates, daily_pnl_values, color=colors, alpha=0.7)
            ax2.set_title('الأرباح والخسائر اليومية', fontsize=14, fontweight='bold')
            ax2.set_ylabel('الأرباح/الخسائر اليومية ($)', fontsize=12)
            ax2.set_xlabel('التاريخ', fontsize=12)
            ax2.grid(True, alpha=0.3)
            ax2.axhline(y=0, color='white', linestyle='-', alpha=0.5)
            
            # تنسيق التواريخ
            fig.autofmt_xdate()
            
            # تطبيق الثيم الداكن
            fig.patch.set_facecolor('#1a1a2e')
            for ax in [ax1, ax2]:
                ax.set_facecolor('#16213e')
                ax.tick_params(colors='white')
                ax.xaxis.label.set_color('white')
                ax.yaxis.label.set_color('white')
                ax.title.set_color('white')
                ax.spines['bottom'].set_color('white')
                ax.spines['top'].set_color('white')
                ax.spines['right'].set_color('white')
                ax.spines['left'].set_color('white')
            
            plt.tight_layout()
            
            # حفظ الرسم كـ base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', facecolor='#1a1a2e', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return chart_base64
            
        except Exception as e:
            self.logger.error(f"خطأ في توليد الرسم البياني: {e}")
            return ""
    
    def export_trades_to_csv(self, start_date: datetime = None, end_date: datetime = None) -> str:
        """تصدير الصفقات إلى ملف CSV"""
        try:
            filtered_trades = self._filter_trades_by_date(start_date, end_date)
            
            if not filtered_trades:
                return ""
            
            # تحويل إلى DataFrame
            trades_data = []
            for trade in filtered_trades:
                trades_data.append({
                    'ID': trade.id,
                    'الرمز': trade.symbol,
                    'الجهة': trade.side,
                    'وقت الدخول': trade.entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'وقت الخروج': trade.exit_time.strftime('%Y-%m-%d %H:%M:%S') if trade.exit_time else '',
                    'سعر الدخول': trade.entry_price,
                    'سعر الخروج': trade.exit_price or '',
                    'الكمية': trade.quantity,
                    'الربح/الخسارة': trade.pnl,
                    'النسبة المئوية': trade.pnl_percentage,
                    'الرسوم': trade.fees,
                    'الاستراتيجية': trade.strategy,
                    'الحالة': trade.status
                })
            
            df = pd.DataFrame(trades_data)
            
            # حفظ الملف
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"trades_export_{timestamp}.csv"
            filepath = os.path.join(self.data_dir, filename)
            
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            self.logger.info(f"تم تصدير الصفقات إلى: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"خطأ في تصدير الصفقات: {e}")
            return ""
    
    def _load_trades(self) -> List[TradeRecord]:
        """تحميل الصفقات من الملف"""
        try:
            if os.path.exists(self.trades_file):
                with open(self.trades_file, 'r', encoding='utf-8') as f:
                    trades_data = json.load(f)
                
                trades = []
                for trade_dict in trades_data:
                    trade = TradeRecord(
                        id=trade_dict['id'],
                        symbol=trade_dict['symbol'],
                        side=trade_dict['side'],
                        entry_time=datetime.fromisoformat(trade_dict['entry_time']),
                        exit_time=datetime.fromisoformat(trade_dict['exit_time']) if trade_dict.get('exit_time') else None,
                        entry_price=trade_dict['entry_price'],
                        exit_price=trade_dict.get('exit_price'),
                        quantity=trade_dict['quantity'],
                        pnl=trade_dict['pnl'],
                        pnl_percentage=trade_dict['pnl_percentage'],
                        fees=trade_dict['fees'],
                        strategy=trade_dict['strategy'],
                        status=trade_dict['status']
                    )
                    trades.append(trade)
                
                return trades
            
            return []
            
        except Exception as e:
            self.logger.error(f"خطأ في تحميل الصفقات: {e}")
            return []
    
    def _save_trades(self):
        """حفظ الصفقات إلى الملف"""
        try:
            trades_data = []
            for trade in self.trades:
                trade_dict = {
                    'id': trade.id,
                    'symbol': trade.symbol,
                    'side': trade.side,
                    'entry_time': trade.entry_time.isoformat(),
                    'exit_time': trade.exit_time.isoformat() if trade.exit_time else None,
                    'entry_price': trade.entry_price,
                    'exit_price': trade.exit_price,
                    'quantity': trade.quantity,
                    'pnl': trade.pnl,
                    'pnl_percentage': trade.pnl_percentage,
                    'fees': trade.fees,
                    'strategy': trade.strategy,
                    'status': trade.status
                }
                trades_data.append(trade_dict)
            
            with open(self.trades_file, 'w', encoding='utf-8') as f:
                json.dump(trades_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"خطأ في حفظ الصفقات: {e}")
    
    def _load_performance_history(self) -> List[Dict]:
        """تحميل تاريخ الأداء"""
        try:
            if os.path.exists(self.performance_file):
                with open(self.performance_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"خطأ في تحميل تاريخ الأداء: {e}")
            return []
    
    def _filter_trades_by_date(self, start_date: Optional[datetime], 
                              end_date: Optional[datetime]) -> List[TradeRecord]:
        """تصفية الصفقات حسب التاريخ"""
        filtered_trades = self.trades
        
        if start_date:
            filtered_trades = [t for t in filtered_trades if t.entry_time >= start_date]
        
        if end_date:
            filtered_trades = [t for t in filtered_trades if t.entry_time < end_date]
        
        return filtered_trades
    
    def _calculate_max_drawdown(self, trades: List[TradeRecord]) -> float:
        """حساب أقصى انخفاض"""
        if not trades:
            return 0
        
        cumulative_pnl = 0
        peak = 0
        max_drawdown = 0
        
        for trade in sorted(trades, key=lambda x: x.entry_time):
            cumulative_pnl += trade.pnl
            
            if cumulative_pnl > peak:
                peak = cumulative_pnl
            
            drawdown = peak - cumulative_pnl
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown
    
    def _calculate_sharpe_ratio(self, trades: List[TradeRecord]) -> float:
        """حساب نسبة شارب"""
        if not trades:
            return 0
        
        returns = [t.pnl_percentage for t in trades]
        
        if len(returns) < 2:
            return 0
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0
        
        # افتراض معدل خالي من المخاطر 2%
        risk_free_rate = 2.0
        
        return (mean_return - risk_free_rate) / std_return
    
    def _calculate_consecutive_trades(self, trades: List[TradeRecord]) -> Tuple[int, int]:
        """حساب الصفقات المتتالية الرابحة والخاسرة"""
        if not trades:
            return 0, 0
        
        sorted_trades = sorted(trades, key=lambda x: x.entry_time)
        
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        current_consecutive_wins = 0
        current_consecutive_losses = 0
        
        for trade in sorted_trades:
            if trade.pnl > 0:
                current_consecutive_wins += 1
                current_consecutive_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, current_consecutive_wins)
            elif trade.pnl < 0:
                current_consecutive_losses += 1
                current_consecutive_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, current_consecutive_losses)
            else:
                current_consecutive_wins = 0
                current_consecutive_losses = 0
        
        return max_consecutive_wins, max_consecutive_losses
    
    def _analyze_symbols_performance(self, trades: List[TradeRecord]) -> Dict[str, Any]:
        """تحليل أداء الرموز"""
        symbols_data = {}
        
        for trade in trades:
            if trade.symbol not in symbols_data:
                symbols_data[trade.symbol] = {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'total_pnl': 0,
                    'total_volume': 0
                }
            
            symbols_data[trade.symbol]['total_trades'] += 1
            symbols_data[trade.symbol]['total_pnl'] += trade.pnl
            symbols_data[trade.symbol]['total_volume'] += trade.quantity * trade.entry_price
            
            if trade.pnl > 0:
                symbols_data[trade.symbol]['winning_trades'] += 1
        
        # حساب معدل الفوز لكل رمز
        for symbol in symbols_data:
            total = symbols_data[symbol]['total_trades']
            winning = symbols_data[symbol]['winning_trades']
            symbols_data[symbol]['win_rate'] = (winning / total * 100) if total > 0 else 0
        
        return symbols_data
    
    def _analyze_strategies_performance(self, trades: List[TradeRecord]) -> Dict[str, Any]:
        """تحليل أداء الاستراتيجيات"""
        strategies_data = {}
        
        for trade in trades:
            if trade.strategy not in strategies_data:
                strategies_data[trade.strategy] = {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'total_pnl': 0,
                    'total_volume': 0
                }
            
            strategies_data[trade.strategy]['total_trades'] += 1
            strategies_data[trade.strategy]['total_pnl'] += trade.pnl
            strategies_data[trade.strategy]['total_volume'] += trade.quantity * trade.entry_price
            
            if trade.pnl > 0:
                strategies_data[trade.strategy]['winning_trades'] += 1
        
        # حساب معدل الفوز لكل استراتيجية
        for strategy in strategies_data:
            total = strategies_data[strategy]['total_trades']
            winning = strategies_data[strategy]['winning_trades']
            strategies_data[strategy]['win_rate'] = (winning / total * 100) if total > 0 else 0
        
        return strategies_data
    
    def _trade_to_dict(self, trade: TradeRecord) -> Dict[str, Any]:
        """تحويل سجل الصفقة إلى قاموس"""
        return {
            'id': trade.id,
            'symbol': trade.symbol,
            'side': trade.side,
            'entry_time': trade.entry_time.isoformat(),
            'exit_time': trade.exit_time.isoformat() if trade.exit_time else None,
            'entry_price': trade.entry_price,
            'exit_price': trade.exit_price,
            'quantity': trade.quantity,
            'pnl': trade.pnl,
            'pnl_percentage': trade.pnl_percentage,
            'fees': trade.fees,
            'strategy': trade.strategy,
            'status': trade.status
        }

