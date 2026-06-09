# 本檔定義：
# - 使用使用者指定的 EMA/MACD 計算方式（見 _ema_array）
# - DIF = EMA(n_fast) - EMA(n_slow)
# - MACD 訊號線為對 DIF 做 x 期 EMA
# - 交易規則（依使用者要求）：
#   * 當綠色柱狀（hist < 0）出現最負值後，若出現連續兩根柱狀值變小（數值上升，表示動能由弱轉強），於第三根(bar)買入
#   * 當紅色柱狀（hist > 0）出現最正值後，若出現連續兩根柱狀值變小（數值下降，表示動能由強轉弱），於第三根(bar)賣出
# - 回測統計包含總報酬率、年化報酬率（使用 (1+total)^(1/years)-1 計算）、及最大回撤資訊

from backtesting import Backtest, Strategy
import pandas as pd


def _ema_array(arr, span):
    import numpy as _np
    x = _np.asarray(arr, dtype=float)
    if x.size == 0:
        return x
    ema = _np.empty_like(x)
    ema[0] = x[0]
    n = float(span)
    for i in range(1, x.size):
        ema[i] = (ema[i-1] * (n-1) + x[i] * 2.0) / (n+1.0)
    return ema


def _macd_array(arr, n_fast, n_slow):
    ema_fast = _ema_array(arr, n_fast)
    ema_slow = _ema_array(arr, n_slow)
    import numpy as _np
    return _np.asarray(ema_fast) - _np.asarray(ema_slow)


def _signal_array(arr, n_fast, n_slow, n_signal):
    dif = _macd_array(arr, n_fast, n_slow)
    return _ema_array(dif, n_signal)


class MACDStrategy(Strategy):
    n_fast = 12
    n_slow = 26
    n_signal = 9
    finalize_trades = False
    order_size = 1

    def init(self):
        self.macd = self.I(_macd_array, self.data.Close, self.n_fast, self.n_slow)
        self.signal = self.I(_signal_array, self.data.Close, self.n_fast, self.n_slow, self.n_signal)
        self.hist = self.macd - self.signal
        self.buy_signals = []
        self.sell_signals = []

    def next(self):
        if len(self.hist) < 5:
            return

        h5 = float(self.hist[-5])
        h4 = float(self.hist[-4])
        h3 = float(self.hist[-3])
        h2 = float(self.hist[-2])
        h1 = float(self.hist[-1])

        try:
            if (h4 < 0) and (h3 > h4) and (h2 > h3) and (h1 > h2):
                if not self.position:
                    self.buy(size=self.order_size)
                    self.buy_signals.append(self.data.index[-1])
        except Exception:
            pass

        try:
            if (h4 > 0) and (h3 < h4) and (h2 < h3) and (h1 < h2):
                if self.position:
                    self.sell(size=self.order_size)
                    self.sell_signals.append(self.data.index[-1])
        except Exception:
            pass


def backtest_macd(df):
    """
    df: DataFrame 必須包含 ['Open','High','Low','Close','Volume']
    回傳: equity_df, stats_summary, signal
    """
    if df.empty:
        return None, None, None

    df = df[['Open','High','Low','Close','Volume']].copy()

    bt = Backtest(df, MACDStrategy, cash=1000000, commission=.001)
    stats = bt.run(finalize_trades=True)
    strategy = bt._strategy
    
    # ===== equity curve =====
    equity_curve = getattr(stats, "_equity_curve", None)
    if equity_curve is None:
        return None, None, None

    equity_curve.index = pd.to_datetime(equity_curve.index)
    equity_df = equity_curve[['Equity']].copy()
    equity_df.index.name = 'Date'

    # ===== signal =====
    signal = "買進" if stats.get('Return [%]', 0) > 0 else "賣出"

    # ===== trades count =====
    trades = None
    for k in ['# Trades', 'Trades', 'Trades #']:
        if k in stats:
            try:
                trades = int(stats.get(k, 0))
            except Exception:
                trades = None
            break

    trades_df = getattr(stats, "_trades", None)

    stats_summary = dict(stats)
    stats_summary["trades"] = trades
    stats_summary["trades_df"] = trades_df

    # 🛠️ 修正點 1：移除了原本在這裡的 return，讓下方的進階統計計算能被順利執行！

    # 計算總報酬率 (Total Return)
    try:
        initial_equity = float(equity_df['Equity'].iloc[0])
        final_equity = float(equity_df['Equity'].iloc[-1])
        total_return_dec = (final_equity / initial_equity) - 1.0
        total_return = total_return_dec * 100.0
        return_formula = f"({final_equity:,.0f} / {initial_equity:,.0f}) - 1 = {total_return_dec * 100:.2f}%"
    except Exception:
        total_return = 0.0
        total_return_dec = 0.0
        return_formula = None

    ann_formula = None

    # 年化報酬率 (Annualized Return)
    try:
        span_days = (equity_df.index.max() - equity_df.index.min()).days
        years = span_days / 365.25 if span_days and span_days > 0 else None
        if years and years > 0:
            ann = (1.0 + total_return_dec) ** (1.0 / years) - 1.0
            annualized = round(ann * 100.0, 2)
            try:
                ann_formula = f"({final_equity:,.0f} / {initial_equity:,.0f})^(1/{years:.2f}) - 1 = {annualized:.2f}%"
            except Exception:
                ann_formula = None
        else:
            annualized = None
            ann_formula = None
    except Exception:
        annualized = None

    # 計算回撤（Drawdown）
    try:
        eq = equity_df['Equity'].copy()
        running_max = eq.cummax()
        drawdown = (running_max - eq) / running_max
        maxdd = float(drawdown.max() * 100.0)
        trough_idx = drawdown.idxmax()
        peak_idx = eq.loc[:trough_idx].idxmax()
        maxdd_info = {
            'max_drawdown_pct': round(maxdd, 4),
            'peak_date': str(peak_idx).split()[0],
            'trough_date': str(trough_idx).split()[0]
        }
    except Exception:
        maxdd = None
        maxdd_info = None

    sharpe = stats.get('Sharpe Ratio', None)
    win_rate = stats.get('Win Rate [%]', None)

    def _r(v, nd=2):
        try:
            return round(float(v), nd)
        except Exception:
            return None

    stats_summary.update({
        "total_return": _r(total_return),
        "total_return_formula": return_formula,
        "max_drawdown": _r(maxdd) if maxdd is not None else None,
        "max_drawdown_info": maxdd_info,
        "sharpe": _r(sharpe) if sharpe is not None else None,
        "win_rate": _r(win_rate) if win_rate is not None else None,
        "trades": trades,
        "annualized_return": annualized,
        "annualized_formula": ann_formula
    })

    # ===== trades detail =====
    trades_detail = []
    try:
        if trades_df is not None and len(trades_df) > 0:
            for _, r in trades_df.iterrows():
                entry_time = pd.to_datetime(r.get("EntryTime"))
                exit_time = pd.to_datetime(r.get("ExitTime"))
                entry_price = float(r.get("EntryPrice")) if r.get("EntryPrice") is not None else None
                exit_price = float(r.get("ExitPrice")) if r.get("ExitPrice") is not None else None
                size = r.get("Size", 1)

                pnl = None
                ret_pct = None
                if entry_price is not None and exit_price is not None:
                    pnl = round(exit_price - entry_price, 2)
                    ret_pct = round((exit_price - entry_price) / entry_price * 100, 4)

                trades_detail.append({
                    "entry_time": entry_time,
                    "exit_time": exit_time,
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "pnl": pnl,
                    "return_pct": ret_pct,
                    "size": size
                })
        stats_summary["trades_detail"] = trades_detail
    except Exception as e:
        print("trades parsing error:", e)
        stats_summary["trades_detail"] = []

    # --- Strict backtest simulation ---
    try:
        span_days = (df.index.max() - df.index.min()).days
        actual_years = span_days / 365.25 if span_days > 0 else 1.0
        
        eq_df_strict, metrics_strict, calcs_strict, trades_events, paired_trades = run_strict_backtest(df, n_years=actual_years, E0=1000000)
        f_eq = metrics_strict.get('final_equity', 1000000)
        cagr_val = metrics_strict.get('CAGR_pct', 0)
        
        stats_summary['metrics'] = metrics_strict
        stats_summary['calculations'] = calcs_strict
        stats_summary['total_return'] = metrics_strict.get('total_return_pct')
        stats_summary['annualized_return'] = cagr_val
        stats_summary['max_drawdown'] = metrics_strict.get('max_drawdown_pct')
        stats_summary['annualized_formula'] = f"({f_eq:,.0f} / 1,000,000)^(1/{actual_years:.2f}) - 1 = {cagr_val}%"

        try:
            stats_summary['_equity_strict'] = [{'date': str(idx), 'equity_curve': float(v)} for idx, v in eq_df_strict['Equity_Curve'].items()]
        except:
            stats_summary['_equity_strict'] = None

        stats_summary['_strict_trades'] = trades_events
        stats_summary['trades_detail'] = paired_trades
        stats_summary['trades'] = len(paired_trades)
        
        if stats_summary.get('metrics') is not None:
            stats_summary['metrics']['trades_executed'] = len(paired_trades)

    except Exception as e:
        print(f"Strict Backtest Error: {e}")
        pass

    return equity_df, stats_summary, signal


def run_strict_backtest(df, n_years=5, E0=1000000):
    import numpy as _np
    if df is None or df.empty:
        raise ValueError('df is empty')
    if 'Close' not in df.columns:
        raise ValueError('Close column required')

    close = df['Close'].astype(float).values
    macd_vals = _macd_array(pd.Series(close), 12, 26)
    sig_vals = _signal_array(pd.Series(close), 12, 26, 9)
    hist = _np.nan_to_num(macd_vals - sig_vals, nan=0.0)
    
    n = len(hist)
    actions = [None] * n
    for i in range(4, n-1):
        h5 = float(hist[i-4]); h4 = float(hist[i-3]); h3 = float(hist[i-2]); h2 = float(hist[i-1]); h1 = float(hist[i])
        if (h4 < 0) and (h4 <= h5) and (h4 <= h3) and (h3 > h4) and (h2 > h3) and (h1 > h2):
            actions[i+1] = 'BUY'
        if (h4 > 0) and (h4 >= h5) and (h4 >= h3) and (h3 < h4) and (h2 < h3) and (h1 < h2):
            actions[i+1] = 'SELL'

    cash = float(E0)
    shares = 0
    prev_equity = float(E0)
    records = []
    trades_exec = []

    for t in range(n):
        date = df.index[t]
        open_p = float(df['Open'].iloc[t]) if 'Open' in df.columns else float(df['Close'].iloc[t])
        close_p = float(df['Close'].iloc[t])
        act = actions[t]
        
        if act == 'BUY':
            if open_p > 0:
                qty = int(cash // open_p)
                cost = qty * open_p
                cash -= cost
                shares += qty
                if qty > 0:
                    trades_exec.append({'type':'BUY','date':str(date),'price':open_p,'size':qty})
        elif act == 'SELL':
            if shares > 0:
                cash += shares * open_p
                trades_exec.append({'type':'SELL','date':str(date),'price':open_p,'size':shares})
                shares = 0
                
        equity = cash + shares * close_p
        r_t = (equity - prev_equity) / prev_equity if prev_equity != 0 else 0.0
        records.append({'Date': date, 'E_t': equity, 'r_t': r_t, 'cash': cash, 'shares': shares, 'close': close_p})
        prev_equity = equity

    eq_df = pd.DataFrame(records).set_index('Date')
    eq_df['Equity_Curve'] = eq_df['E_t'] / float(E0)

    E_T = float(eq_df['E_t'].iloc[-1])
    total_return_dec = (E_T / float(E0)) - 1.0
    total_return_pct = round(total_return_dec * 100.0, 4)
    
    try:
        CAGR = (E_T / float(E0)) ** (1.0 / float(n_years)) - 1.0
        CAGR_pct = round(CAGR * 100.0, 4)
    except Exception:
        CAGR_pct = None
        
    running_max = eq_df['E_t'].cummax()
    drawdown_user = (eq_df['E_t'] - running_max) / running_max
    mdd_value = float(drawdown_user.min()) if not drawdown_user.empty else 0.0
    max_dd = abs(mdd_value) * 100.0
    trough_idx = drawdown_user.idxmin()
    peak_idx = eq_df.loc[:trough_idx]['E_t'].idxmax() if not eq_df.empty else None
    maxdd_info = {'max_drawdown_pct': round(max_dd,4), 'peak_date': str(peak_idx).split()[0], 'trough_date': str(trough_idx).split()[0]}

    metrics = {
        'initial_equity': float(E0),
        'final_equity': round(E_T, 2),
        'total_return_pct': total_return_pct,
        'CAGR_pct': CAGR_pct,
        'max_drawdown_pct': round(max_dd,4),
        'trades_executed': 0
    }

    calcs = {
        'total_return_formula': f"({E_T:,.2f} / {E0:,.2f}) - 1 = {total_return_pct:.4f}%",
        'CAGR_formula': f"({E_T:,.2f} / {E0:,.2f})^(1/{n_years}) - 1 = {CAGR_pct:.4f}%" if CAGR_pct is not None else None,
        'max_drawdown_formula': '(E_t - rolling_max(E_t)) / rolling_max(E_t)',
        'max_drawdown_info': maxdd_info
    }

    paired = []
    last_buy = None
    for ev in trades_exec:
        if ev.get('type') == 'BUY':
            last_buy = ev
        elif ev.get('type') == 'SELL' and last_buy is not None:
            try:
                entry_price = float(last_buy.get('price'))
                exit_price = float(ev.get('price'))
                size = int(last_buy.get('size'))
                pnl = round((exit_price - entry_price) * size, 2)
                ret_pct = round(((exit_price - entry_price) / entry_price) * 100.0, 4)
                
                # 🛠️ 修正點 2：將 '報酬' 與 '損益' 統一改為英文標準 Key 名稱
                paired.append({
                    'entry_time': pd.Timestamp(last_buy.get('date')),
                    'exit_time': pd.Timestamp(ev.get('date')),
                    'entry_price': round(entry_price, 4),
                    'exit_price': round(exit_price, 4),
                    'return_pct': ret_pct,
                    'pnl': pnl,
                    'size': size
                })
            except Exception:
                pass
            last_buy = None
            
    metrics['trades_executed'] = len(paired)
    return eq_df, metrics, calcs, trades_exec, paired