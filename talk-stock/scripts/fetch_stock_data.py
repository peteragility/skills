#!/usr/bin/env python3
"""
talk-stock data fetcher — pulls all data needed for multi-agent analysis.
Usage: python3 fetch_stock_data.py TICKER
Output: JSON with all sections pre-computed.
"""

import sys
import json
import yfinance as yf
import numpy as np
from datetime import datetime

def safe_get(d, key, default=None):
    v = d.get(key, default)
    if v is None:
        return default
    # Convert numpy types
    if hasattr(v, 'item'):
        return v.item()
    return v

def compute_technicals(hist):
    """Compute RSI, MACD, SMAs from price history."""
    close = hist['Close']
    volume = hist['Volume']
    
    result = {}
    
    # Moving averages
    if len(close) >= 200:
        result['sma200'] = round(close.rolling(200).mean().iloc[-1], 2)
    if len(close) >= 50:
        result['sma50'] = round(close.rolling(50).mean().iloc[-1], 2)
    if len(close) >= 20:
        result['sma20'] = round(close.rolling(20).mean().iloc[-1], 2)
    if len(close) >= 10:
        result['ema10'] = round(close.ewm(span=10).mean().iloc[-1], 2)
    
    # RSI(14)
    if len(close) >= 15:
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        result['rsi'] = round(rsi.iloc[-1], 1)
    
    # MACD
    if len(close) >= 26:
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        macd_hist = macd - signal
        result['macd'] = round(macd.iloc[-1], 2)
        result['macd_signal'] = round(signal.iloc[-1], 2)
        result['macd_histogram'] = round(macd_hist.iloc[-1], 2)
    
    # Volume analysis
    if len(volume) >= 20:
        avg_vol_20 = volume.rolling(20).mean().iloc[-1]
        result['avg_volume_20d'] = int(avg_vol_20)
        result['latest_volume'] = int(volume.iloc[-1])
        result['volume_ratio'] = round(volume.iloc[-1] / avg_vol_20, 2)
    
    # VWAP approximation (today)
    if len(hist) > 0:
        typical = (hist['High'] + hist['Low'] + close) / 3
        if len(typical) >= 20:
            vwma = (typical * volume).rolling(20).sum() / volume.rolling(20).sum()
            result['vwma_20'] = round(vwma.iloc[-1], 2)
    
    # Death/Golden cross
    if 'sma50' in result and 'sma200' in result:
        result['cross'] = 'golden' if result['sma50'] > result['sma200'] else 'death'
    
    # Price position
    result['price'] = round(close.iloc[-1], 2)
    
    return result

def get_quarterly_financials(ticker):
    """Extract last 4 quarters of financials."""
    quarters = []
    inc = ticker.quarterly_income_stmt
    
    for col in inc.columns[:4]:
        q = {'period': col.strftime('%Y-%m-%d')}
        for item, key in [
            ('Total Revenue', 'revenue'),
            ('Gross Profit', 'gross_profit'),
            ('Operating Income', 'operating_income'),
            ('Net Income', 'net_income'),
        ]:
            if item in inc.index:
                val = inc.loc[item, col]
                q[key] = float(val) if not np.isnan(val) else None
            else:
                q[key] = None
        
        if q.get('revenue') and q.get('gross_profit'):
            q['gross_margin'] = round(q['gross_profit'] / q['revenue'] * 100, 1)
        if q.get('revenue') and q.get('net_income'):
            q['net_margin'] = round(q['net_income'] / q['revenue'] * 100, 1)
        
        quarters.append(q)
    
    return quarters

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 fetch_stock_data.py TICKER", file=sys.stderr)
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    t = yf.Ticker(symbol)
    
    # 1. Basic info
    info = {}
    try:
        info = t.info
    except Exception as e:
        print(f"Warning: Could not fetch info: {e}", file=sys.stderr)
    data = {
        'symbol': symbol,
        'timestamp': datetime.now().isoformat(),
        'info': {
            'name': safe_get(info, 'shortName', symbol),
            'price': safe_get(info, 'currentPrice'),
            'previous_close': safe_get(info, 'previousClose'),
            'day_high': safe_get(info, 'dayHigh'),
            'day_low': safe_get(info, 'dayLow'),
            'fifty_two_week_high': safe_get(info, 'fiftyTwoWeekHigh'),
            'fifty_two_week_low': safe_get(info, 'fiftyTwoWeekLow'),
            'market_cap': safe_get(info, 'marketCap'),
            'beta': safe_get(info, 'beta'),
            # Valuation
            'trailing_pe': safe_get(info, 'trailingPE'),
            'forward_pe': safe_get(info, 'forwardPE'),
            'peg_ratio': safe_get(info, 'pegRatio'),
            'ps_ratio': safe_get(info, 'priceToSalesTrailing12Months'),
            'pb_ratio': safe_get(info, 'priceToBook'),
            # Growth
            'revenue_growth': safe_get(info, 'revenueGrowth'),
            'earnings_growth': safe_get(info, 'earningsGrowth'),
            # Margins
            'gross_margins': safe_get(info, 'grossMargins'),
            'operating_margins': safe_get(info, 'operatingMargins'),
            'profit_margins': safe_get(info, 'profitMargins'),
            # Health
            'roe': safe_get(info, 'returnOnEquity'),
            'current_ratio': safe_get(info, 'currentRatio'),
            'debt_to_equity': safe_get(info, 'debtToEquity'),
            'free_cashflow': safe_get(info, 'freeCashflow'),
            'total_revenue': safe_get(info, 'totalRevenue'),
            # Sentiment
            'recommendation': safe_get(info, 'recommendationKey'),
            'target_mean': safe_get(info, 'targetMeanPrice'),
            'target_high': safe_get(info, 'targetHighPrice'),
            'target_low': safe_get(info, 'targetLowPrice'),
            'short_pct_float': safe_get(info, 'shortPercentOfFloat'),
            # Sector
            'sector': safe_get(info, 'sector'),
            'industry': safe_get(info, 'industry'),
        }
    }
    
    # 2. Technicals
    try:
        hist = t.history(period='1y')
        data['technicals'] = compute_technicals(hist)
        data['technicals']['data_points'] = len(hist)
    except Exception as e:
        data['technicals'] = {'error': str(e)}
    
    # 3. Quarterly financials
    try:
        data['quarterly'] = get_quarterly_financials(t)
    except Exception as e:
        data['quarterly'] = {'error': str(e)}
    
    # 4. Analyst recommendations
    try:
        reco = t.recommendations
        if reco is not None and len(reco) > 0:
            latest = reco.iloc[-1]
            data['analyst_reco'] = {
                'strongBuy': int(latest.get('strongBuy', 0)),
                'buy': int(latest.get('buy', 0)),
                'hold': int(latest.get('hold', 0)),
                'sell': int(latest.get('sell', 0)),
                'strongSell': int(latest.get('strongSell', 0)),
            }
            total = sum(data['analyst_reco'].values())
            if total > 0:
                buy_pct = (data['analyst_reco']['strongBuy'] + data['analyst_reco']['buy']) / total * 100
                data['analyst_reco']['buy_pct'] = round(buy_pct, 1)
                data['analyst_reco']['total_analysts'] = total
        else:
            data['analyst_reco'] = None
    except Exception as e:
        data['analyst_reco'] = {'error': str(e)}
    
    # 5. Key balance sheet items
    try:
        bs = t.quarterly_balance_sheet
        if len(bs.columns) > 0:
            latest_bs = bs.columns[0]
            data['balance_sheet'] = {
                'period': latest_bs.strftime('%Y-%m-%d')
            }
            for item, key in [
                ('Total Assets', 'total_assets'),
                ('Total Liabilities Net Minority Interest', 'total_liabilities'),
                ('Total Equity Gross Minority Interest', 'total_equity'),
                ('Cash And Cash Equivalents', 'cash'),
            ]:
                if item in bs.index:
                    data['balance_sheet'][key] = float(bs.loc[item, latest_bs])
    except Exception as e:
        data['balance_sheet'] = {'error': str(e)}
    
    # 6. Cash flow
    try:
        cf = t.quarterly_cashflow
        if len(cf.columns) > 0:
            latest_cf = cf.columns[0]
            data['cashflow'] = {
                'period': latest_cf.strftime('%Y-%m-%d')
            }
            for item, key in [
                ('Free Cash Flow', 'fcf'),
                ('Operating Cash Flow', 'operating_cf'),
                ('Capital Expenditure', 'capex'),
            ]:
                if item in cf.index:
                    data['cashflow'][key] = float(cf.loc[item, latest_cf])
    except Exception as e:
        data['cashflow'] = {'error': str(e)}
    
    print(json.dumps(data, indent=2, default=str))

if __name__ == '__main__':
    main()
