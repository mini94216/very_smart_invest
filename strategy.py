# strategy.py
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
    # 以使用者指定公式計算 EMA（遞迴）：
    # EMA_today = (EMA_yesterday * (n-1) + Close_today * 2) / (n+1)
    # 此公式等價於指數加權移動平均，alpha = 2/(n+1)
    # 我們用明確的遞迴實作，並以第一個值作為初始 EMA（或可改為簡單平均）
    import numpy as _np
    x = _np.asarray(arr, dtype=float)
    if x.size == 0:
        return x
    ema = _np.empty_like(x)
    # 初始值設定為第一個收盤價
    ema[0] = x[0]
    n = float(span)
    for i in range(1, x.size):
        ema[i] = (ema[i-1] * (n-1) + x[i] * 2.0) / (n+1.0)
    return ema


def _macd_array(arr, n_fast, n_slow):
    # DIF = EMA(n_fast) - EMA(n_slow)
    ema_fast = _ema_array(arr, n_fast)
    ema_slow = _ema_array(arr, n_slow)
    import numpy as _np
    return _np.asarray(ema_fast) - _np.asarray(ema_slow)


def _signal_array(arr, n_fast, n_slow, n_signal):
    # 使用使用者指定公式計算 MACD 的訊號線（稱為 x-period MACD），
    # 也就是對 DIF（MACD 線）再做 EMA 遞迴：
    # MACD_signal_today = (MACD_signal_yesterday * (x-1) + DIF_today * 2) / (x+1)
    dif = _macd_array(arr, n_fast, n_slow)
    return _ema_array(dif, n_signal)


class MACDStrategy(Strategy):
    n_fast = 12
    n_slow = 26
    n_signal = 9
    # Allow passing `finalize_trades` via Backtest.run(...)
    # Some backtesting.py versions require strategy parameters to be
    # declared as class variables before they can be passed to run().
    finalize_trades = False
    # Small fixed order size to avoid margin-related cancels during tests
    order_size = 1

    def init(self):
        # register indicators via self.I so they are aligned with strategy index
        self.macd = self.I(_macd_array, self.data.Close, self.n_fast, self.n_slow)
        self.signal = self.I(_signal_array, self.data.Close, self.n_fast, self.n_slow, self.n_signal)
        self.hist = self.macd - self.signal

    def next(self):
        # 我們依照使用者指定的方法判斷買賣時機：
        # - 若綠色柱狀（hist < 0，代表 DIF - MACD < 0）出現極大值（即最負）後，
        #   接著連續兩根柱狀數值變小（數值增加，趨勢由弱轉強），在第三根（h1）時買入。
        # - 若紅色柱狀（hist > 0，代表 DIF - MACD > 0）出現極大值（即最正）後，
        #   接著連續兩根柱狀數值變小（數值下降，趨勢由強轉弱），在第三根（h1）時賣出。
        # 具體實作：觀察最近四根 histogram 值 h4, h3, h2, h1（由舊到新），以 h3 為潛在峰值/谷底。

        # 我更新為：
        # 當出現極端峰/谷後，需連續三根柱狀「縮小」，在第四根(bar)執行買/賣
        # 具體：檢查最近 5 根 hist 值 h5,h4,h3,h2,h1（由舊到新），以 h4 為潛在峰/谷：
        #  BUY 條件（綠色 valley）：h4 < 0 且為局部最小（<= 左右鄰），且 h3 > h4, h2 > h3, h1 > h2 -> 在 h1 時買入
        #  SELL 條件（紅色 peak）：h4 > 0 且為局部最大（>= 左右鄰），且 h3 < h4, h2 < h3, h1 < h2 -> 在 h1 時賣出
        if len(self.hist) < 5:
            return

        # use last 5 histogram values: h5, h4, h3, h2, h1 (older -> newer)
        h5 = float(self.hist[-5])
        h4 = float(self.hist[-4])
        h3 = float(self.hist[-3])
        h2 = float(self.hist[-2])
        h1 = float(self.hist[-1])

        # BUY rule after valley and 3 shrinking bars (buy on h1)
        try:
            if (h4 < 0) and (h4 <= h5) and (h4 <= h3) and (h3 > h4) and (h2 > h3) and (h1 > h2):
                if not self.position:
                    self.buy(size=self.order_size)
        except Exception:
            pass

        # SELL rule after peak and 3 shrinking bars (sell on h1)
        try:
            if (h4 > 0) and (h4 >= h5) and (h4 >= h3) and (h3 < h4) and (h2 < h3) and (h1 < h2):
                if self.position:
                    self.sell(size=self.order_size)
        except Exception:
            pass

def backtest_macd(df):
    """
    df: DataFrame 必須包含 ['Open','High','Low','Close','Volume']
    回傳: equity_curve, stats_summary, signal
    """
    if df.empty:
        return None, None, None

    df = df[['Open','High','Low','Close','Volume']].copy()
    # increase starting cash to reduce margin-related order cancellations during backtest
    bt = Backtest(df, MACDStrategy, cash=1000000, commission=.001)
    # finalize_trades=True will close any open trades at the end and include them in stats
    stats = bt.run(finalize_trades=True)
    equity_curve = stats.get('_equity_curve')
    if equity_curve is None:
        return None, None, None

    # 保留 DatetimeIndex
    equity_curve.index = pd.to_datetime(equity_curve.index)

    # normalize to DataFrame with Date index and Equity column
    equity_df = equity_curve[['Equity']].copy()
    equity_df.index.name = 'Date'

    signal = "買進" if stats.get('Return [%]', 0) > 0 else "賣出"

    # compute trade count (varies by backtesting library key names)
    trades = None
    for k in ['# Trades', 'Trades', 'Trades #']:
        if k in stats:
            try:
                trades = int(stats.get(k, 0))
            except Exception:
                trades = None
            break

    # 計算總報酬率 (Total Return)：
    # total_return = (Final Equity / Initial Equity) - 1
    try:
        initial_equity = float(equity_df['Equity'].iloc[0])
        final_equity = float(equity_df['Equity'].iloc[-1])
        total_return_dec = (final_equity / initial_equity) - 1.0
        total_return = total_return_dec * 100.0
        # add formula strings for UI display
        return_formula = f"{final_equity:,.0f} / {initial_equity:,.0f} - 1 = {total_return_dec * 100:.2f}%"
    except Exception:
        total_return = 0.0
        total_return_dec = 0.0
        return_formula = None

    # 年化公式字串（供 UI 顯示）
    ann_formula = None

    # 年化報酬率 (Annualized Return)：按照使用者的公式：
    # (1 + 總報酬率)^(1/年數) - 1
    try:
        span_days = (equity_df.index.max() - equity_df.index.min()).days
        years = span_days / 365.25 if span_days and span_days > 0 else None
        if years and years > 0:
            ann = (1.0 + total_return_dec) ** (1.0 / years) - 1.0
            annualized = round(ann * 100.0, 2)
            # prepare formula string with example numbers
            try:
                ann_formula = f"({final_equity:,.0f} / {initial_equity:,.0f})^(1/{years:.2f}) - 1 = {annualized:.2f}%"
            except Exception:
                ann_formula = None
        else:
            annualized = None
            ann_formula = None
    except Exception:
        annualized = None

    # 計算回撤（Drawdown）：
    # drawdown_t = (running_max_t - equity_t) / running_max_t
    # 最大回撤即為 drawdown 的最大值
    try:
        eq = equity_df['Equity'].copy()
        running_max = eq.cummax()
        drawdown = (running_max - eq) / running_max
        maxdd = float(drawdown.max() * 100.0)
        # 取得最大回撤的時間點（谷底）與對應的峰值時間
        trough_idx = drawdown.idxmax()
        # 峰值為在谷底發生之前的最後一個 running_max 的位置
        peak_idx = eq.loc[:trough_idx].idxmax()
        maxdd_info = {
            'max_drawdown_pct': round(maxdd, 4),
            'peak_date': str(peak_idx),
            'trough_date': str(trough_idx)
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

    stats_summary = {
        "total_return": _r(total_return),
        "total_return_formula": return_formula,
        "max_drawdown": _r(maxdd) if maxdd is not None else None,
        "max_drawdown_info": maxdd_info,
        "sharpe": _r(sharpe) if sharpe is not None else None,
        "win_rate": _r(win_rate) if win_rate is not None else None,
        "trades": trades,
        "annualized_return": annualized,
        "annualized_formula": ann_formula
    }

    # extract detailed trades if present in stats
    trades_detail = None
    try:
        trades_df = None
        if hasattr(stats, '_trades'):
            trades_df = getattr(stats, '_trades')
        elif hasattr(stats, 'get'):
            trades_df = stats.get('_trades')

        if trades_df is not None:
            trades_detail = []
            for _, r in trades_df.iterrows():
                try:
                    entry_time = r.get('EntryTime')
                    exit_time = r.get('ExitTime')
                    e_price = float(r.get('EntryPrice')) if r.get('EntryPrice') is not None else None
                    x_price = float(r.get('ExitPrice')) if r.get('ExitPrice') is not None else None
                    size = r.get('Size') if 'Size' in r.index else None

                    # 計算報酬與損益（以持倉張數計算總損益）：
                    try:
                        qty = int(size) if (size is not None and not pd.isna(size)) else 1
                    except Exception:
                        qty = 1
                    pnl_calc = round(x_price - e_price, 2) if (e_price is not None and x_price is not None) else None
                    ret_pct_calc = round(((x_price - e_price) / e_price) * 100.0, 4) if (e_price is not None and x_price is not None) else None

                    trades_detail.append({
                        'entry_time': str(entry_time).split(' ')[0] if entry_time is not None else None,
                        'exit_time': str(exit_time).split(' ')[0] if exit_time is not None else None,
                        'entry_price': round(e_price, 4) if e_price is not None else None,
                        'exit_price': round(x_price, 4) if x_price is not None else None,
                        '報酬': ret_pct_calc,
                        '損益': pnl_calc,
                        'size': int(size) if (size is not None and not pd.isna(size)) else None
                    })
                except Exception:
                    # skip malformed trade rows
                    continue
    except Exception:
        trades_detail = None

    if trades_detail is not None:
        stats_summary['trades_detail'] = trades_detail

    # --- Strict backtest simulation (已修正年數與公式自動同步) ---
    try:
        # 1. 自動計算資料的實際年數 (避免固定在 5 年)
        span_days = (df.index.max() - df.index.min()).days
        actual_years = span_days / 365.25 if span_days > 0 else 1.0
        
        # 2. 執行嚴格回測，傳入實際年數
        eq_df_strict, metrics_strict, calcs_strict, trades_events, paired_trades = run_strict_backtest(df, n_years=actual_years, E0=1000000)
        
        # 3. 取得最終資產與年化報酬數值
        f_eq = metrics_strict.get('final_equity', 1000000)
        cagr_val = metrics_strict.get('CAGR_pct', 0)
        
        # 4. 把資料塞進 stats_summary
        stats_summary['metrics'] = metrics_strict
        stats_summary['calculations'] = calcs_strict
        stats_summary['total_return'] = metrics_strict.get('total_return_pct')
        stats_summary['annualized_return'] = cagr_val
        stats_summary['max_drawdown'] = metrics_strict.get('max_drawdown_pct')
        
        # --- 關鍵修正：重新寫入正確的公式字串 ---
        # 這裡會強制讓公式顯示的數字 = 最終資產與實際年數
        stats_summary['annualized_formula'] = f"({f_eq:,.0f} / 1,000,000)^(1/{actual_years:.2f}) - 1 = {cagr_val}%"

        # 處理權益曲線與交易紀錄
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
    """
    Strict backtest simulation following user's rules:
    - Signals generated from MACD histogram pattern (3 shrinking bars then act on 4th)
    - Signal detected on day t leads to execution on day t+1 OPEN (no look-ahead)
    - All-in on BUY (use all cash to buy integer shares), all-out on SELL
    - Daily equity E_t computed at CLOSE of each day = cash + shares * Close_t
    - Daily return r_t = (E_t - E_{t-1}) / E_{t-1}
    - Equity curve normalized: Equity_Curve_t = E_t / E0
    - CAGR computed as (E_T / E0)^(1/N) - 1 with N = n_years
    - Max Drawdown computed from running max of E_t
    Returns: equity_df (Date index, columns 'E_t','r_t','Equity_Curve'), metrics dict, calculations dict, trades list
    """
    import numpy as _np
    # require Date index
    if df is None or df.empty:
        raise ValueError('df is empty')
    if 'Close' not in df.columns:
        raise ValueError('Close column required')

    close = df['Close'].astype(float).values
    # compute macd arrays
    macd_vals = _macd_array(pd.Series(close), 12, 26)
    sig_vals = _signal_array(pd.Series(close), 12, 26, 9)
    hist = _np.nan_to_num(macd_vals - sig_vals, nan=0.0)

    n = len(hist)
    # generate scheduled actions to execute on next day (index i -> execute on i+1)
    actions = [None] * n
    for i in range(4, n-1):  # ensure i+1 exists
        h5 = float(hist[i-4]); h4 = float(hist[i-3]); h3 = float(hist[i-2]); h2 = float(hist[i-1]); h1 = float(hist[i])
        # BUY condition (green valley)
        if (h4 < 0) and (h4 <= h5) and (h4 <= h3) and (h3 > h4) and (h2 > h3) and (h1 > h2):
            actions[i+1] = 'BUY'
        # SELL condition (red peak)
        if (h4 > 0) and (h4 >= h5) and (h4 >= h3) and (h3 < h4) and (h2 < h3) and (h1 < h2):
            actions[i+1] = 'SELL'

    # simulate
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
            # buy as many whole shares as possible
            if open_p <= 0:
                bought = 0
            else:
                qty = int(cash // open_p)
                cost = qty * open_p
                cash -= cost
                shares += qty
                bought = qty
                if qty > 0:
                    trades_exec.append({'type':'BUY','date':str(date),'price':open_p,'size':qty})
        elif act == 'SELL':
            if shares > 0:
                cash += shares * open_p
                trades_exec.append({'type':'SELL','date':str(date),'price':open_p,'size':shares})
                shares = 0
        # end of day mark-to-market
        equity = cash + shares * close_p
        r_t = (equity - prev_equity) / prev_equity if prev_equity != 0 else 0.0
        records.append({'Date': date, 'E_t': equity, 'r_t': r_t, 'cash': cash, 'shares': shares, 'close': close_p})
        prev_equity = equity

    eq_df = pd.DataFrame(records).set_index('Date')
    # normalize equity curve
    eq_df['Equity_Curve'] = eq_df['E_t'] / float(E0)

    # final metrics
    E_T = float(eq_df['E_t'].iloc[-1])
    total_return_dec = (E_T / float(E0)) - 1.0
    total_return_pct = round(total_return_dec * 100.0, 4)
    # CAGR (use fixed n_years per user requirement)
    try:
        CAGR = (E_T / float(E0)) ** (1.0 / float(n_years)) - 1.0
        CAGR_pct = round(CAGR * 100.0, 4)
    except Exception:
        CAGR_pct = None
    # max drawdown (computed on E_t) -- use user's formula: (E_t - rolling_max(E_t)) / rolling_max(E_t)
    running_max = eq_df['E_t'].cummax()
    drawdown_user = (eq_df['E_t'] - running_max) / running_max  # typically negative or zero
    # MDD is the minimum (most negative) value of drawdown_user
    mdd_value = float(drawdown_user.min()) if not drawdown_user.empty else 0.0
    # report as positive percentage for convenience
    max_dd = abs(mdd_value) * 100.0
    trough_idx = drawdown_user.idxmin()
    peak_idx = eq_df.loc[:trough_idx]['E_t'].idxmax() if not eq_df.empty else None
    maxdd_info = {'max_drawdown_pct': round(max_dd,4), 'peak_date': str(peak_idx), 'trough_date': str(trough_idx)}

    # prepare metrics and calculation steps
    metrics = {
        'initial_equity': float(E0),
        'final_equity': round(E_T, 2),
        'total_return_pct': total_return_pct,
        'CAGR_pct': CAGR_pct,
        'max_drawdown_pct': round(max_dd,4),
        'trades_executed': len(trades_exec)
    }

    # Use explicit formula strings matching user's requested formulas
    calcs = {
        'total_return_formula': f"({E_T:,.2f} / {E0:,.2f}) - 1 = {total_return_pct:.4f}%",
        'CAGR_formula': f"({E_T:,.2f} / {E0:,.2f})^(1/{n_years}) - 1 = {CAGR_pct:.4f}%" if CAGR_pct is not None else None,
        'max_drawdown_formula': '(E_t - rolling_max(E_t)) / rolling_max(E_t)',
        'max_drawdown_info': maxdd_info
    }

    # pair buy/sell events into completed round-trip trades
    paired = []
    last_buy = None
    for ev in trades_exec:
        if ev.get('type') == 'BUY':
            last_buy = ev
        elif ev.get('type') == 'SELL' and last_buy is not None:
            try:
                entry_price = float(last_buy.get('price'))
                exit_price = float(ev.get('price'))
                size = int(last_buy.get('size')) if last_buy.get('size') is not None else None
                # 損益按每股計算：賣出價 - 買入價
                pnl = round(exit_price - entry_price, 2) if (entry_price is not None and exit_price is not None) else None
                ret_pct = round(((exit_price - entry_price) / entry_price) * 100.0, 4) if entry_price != 0 else None
                paired.append({
                    'entry_time': str(last_buy.get('date')).split(' ')[0],
                    'exit_time': str(ev.get('date')).split(' ')[0],
                    'entry_price': round(entry_price, 4),
                    'exit_price': round(exit_price, 4),
                    '報酬': ret_pct,
                    '損益': pnl,
                    'size': int(size) if size is not None else None
                })
            except Exception:
                pass
            last_buy = None
    # metrics: trades_executed becomes number of completed paired trades
    metrics['trades_executed'] = len(paired)

    return eq_df, metrics, calcs, trades_exec, paired
