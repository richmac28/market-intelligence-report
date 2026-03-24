#!/usr/bin/env python3
"""
📊 FINAL COMPREHENSIVE DAILY MARKET INTELLIGENCE REPORT SYSTEM
FIXED VERSION - Proper API Data Extraction
"""

import requests
import logging
import smtplib
import os
import sys
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FixedMarketCollector:
    """Market data collector with FIXED data extraction logic"""
    
    def __init__(self):
        self.data = {}
        self.fetch_errors = []
        
        # Conservative fallback only if API completely fails
        self.fallback = {
            'nifty50': {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A'},
            'sensex': {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A'},
            'nifty_bank': {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A'},
            'nifty_midcap100': {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A'},
            'nifty_smallcap250': {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A'},
            'vix': {'value': 'N/A', 'change': 'N/A'},
        }

    def fetch_nse_index(self, symbol_name, display_name):
        """Fetch NSE index with proper extraction"""
        try:
            logger.info(f"Fetching {display_name} from NSE...")
            url = f'https://www.nseindia.com/api/quote-derivative?symbol={symbol_name}'
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            r = requests.get(url, headers=headers, timeout=15)
            
            if r.status_code == 200:
                response_data = r.json()
                logger.info(f"Response received for {display_name}")
                
                # NSE API returns data in 'records' array
                if 'records' in response_data and len(response_data['records']) > 0:
                    record = response_data['records'][0]
                    
                    # Extract values correctly from NSE response
                    underlying_value = float(record.get('underlyingValue', 0))
                    change = float(record.get('change', 0))
                    pct_change = float(record.get('percentChange', 0))
                    
                    logger.info(f"✓ {display_name}: Value={underlying_value}, Change={change}, %={pct_change}")
                    
                    return {
                        'value': f'{underlying_value:,.2f}',
                        'change': f'{change:+.2f}',
                        'pct': f'{pct_change:+.2f}%',
                        'source_name': 'NSE Official',
                        'source_url': 'https://www.nseindia.com'
                    }
                else:
                    logger.warning(f"No records found for {display_name}")
                    return None
            else:
                logger.warning(f"HTTP {r.status_code} for {display_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching {display_name}: {str(e)}")
            self.fetch_errors.append(f"{display_name}: {str(e)}")
            return None

    def fetch_yahoo_finance_index(self, symbol, display_name):
        """Fetch index from Yahoo Finance with proper extraction"""
        try:
            logger.info(f"Fetching {display_name} from Yahoo Finance...")
            url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}&fields=regularMarketPrice,regularMarketChange,regularMarketChangePercent'
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            r = requests.get(url, headers=headers, timeout=15)
            
            if r.status_code == 200:
                response_data = r.json()
                logger.info(f"Response received for {display_name}")
                
                # Yahoo Finance returns data in quoteResponse.result array
                if 'quoteResponse' in response_data:
                    results = response_data['quoteResponse'].get('result', [])
                    
                    if len(results) > 0:
                        quote = results[0]
                        
                        # Extract values correctly from Yahoo Finance response
                        price = quote.get('regularMarketPrice')
                        change = quote.get('regularMarketChange')
                        pct_change = quote.get('regularMarketChangePercent')
                        
                        if price is not None:
                            logger.info(f"✓ {display_name}: Price={price}, Change={change}, %={pct_change}")
                            
                            return {
                                'value': f'{price:,.2f}',
                                'change': f'{change:+.2f}',
                                'pct': f'{pct_change:+.2f}%',
                                'source_name': 'Yahoo Finance',
                                'source_url': 'https://finance.yahoo.com'
                            }
                        else:
                            logger.warning(f"No price data for {display_name}")
                            return None
                    else:
                        logger.warning(f"No results for {display_name}")
                        return None
                else:
                    logger.warning(f"Invalid response structure for {display_name}")
                    return None
            else:
                logger.warning(f"HTTP {r.status_code} for {display_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching {display_name}: {str(e)}")
            self.fetch_errors.append(f"{display_name}: {str(e)}")
            return None

    def fetch_all_data(self):
        """Fetch all market data"""
        logger.info("\n" + "="*100)
        logger.info("FETCHING LIVE MARKET DATA")
        logger.info("="*100)
        
        # Indian Indices - NSE
        logger.info("\n--- INDIAN INDICES (NSE) ---")
        nifty50_data = self.fetch_nse_index('NIFTY', 'Nifty 50')
        if nifty50_data:
            self.data['nifty50'] = nifty50_data
        else:
            self.data['nifty50'] = {**self.fallback['nifty50'], 'source_url': 'https://www.nseindia.com'}
        
        time.sleep(1)
        
        sensex_data = self.fetch_nse_index('SENSEX', 'Sensex')
        if sensex_data:
            self.data['sensex'] = sensex_data
        else:
            self.data['sensex'] = {**self.fallback['sensex'], 'source_url': 'https://www.nseindia.com'}
        
        time.sleep(1)
        
        vix_data = self.fetch_nse_index('INDIAVIX', 'India VIX')
        if vix_data:
            self.data['vix'] = vix_data
        else:
            self.data['vix'] = {**self.fallback['vix'], 'source_url': 'https://www.nseindia.com'}
        
        time.sleep(1)
        
        nifty_bank = self.fetch_nse_index('NIFTYBANK', 'Nifty Bank')
        if nifty_bank:
            self.data['nifty_bank'] = nifty_bank
        else:
            self.data['nifty_bank'] = {**self.fallback['nifty_bank'], 'source_url': 'https://www.nseindia.com'}
        
        time.sleep(1)
        
        nifty_midcap = self.fetch_nse_index('NIFTYMIDCAP100', 'Nifty Midcap 100')
        if nifty_midcap:
            self.data['nifty_midcap100'] = nifty_midcap
        else:
            self.data['nifty_midcap100'] = {**self.fallback['nifty_midcap100'], 'source_url': 'https://www.nseindia.com'}
        
        time.sleep(1)
        
        nifty_smallcap = self.fetch_nse_index('NIFTYSMALLCAP250', 'Nifty Smallcap 250')
        if nifty_smallcap:
            self.data['nifty_smallcap250'] = nifty_smallcap
        else:
            self.data['nifty_smallcap250'] = {**self.fallback['nifty_smallcap250'], 'source_url': 'https://www.nseindia.com'}
        
        # US Indices - Yahoo Finance
        logger.info("\n--- US INDICES (Yahoo Finance) ---")
        sp500_data = self.fetch_yahoo_finance_index('^GSPC', 'S&P 500')
        if sp500_data:
            self.data['sp500'] = sp500_data
        else:
            self.data['sp500'] = {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A', 'source_url': 'https://finance.yahoo.com'}
        
        time.sleep(1)
        
        nasdaq_data = self.fetch_yahoo_finance_index('^IXIC', 'Nasdaq 100')
        if nasdaq_data:
            self.data['nasdaq'] = nasdaq_data
        else:
            self.data['nasdaq'] = {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A', 'source_url': 'https://finance.yahoo.com'}
        
        time.sleep(1)
        
        dow_data = self.fetch_yahoo_finance_index('^DJI', 'Dow Jones')
        if dow_data:
            self.data['dow_futures'] = dow_data
        else:
            self.data['dow_futures'] = {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A', 'source_url': 'https://finance.yahoo.com'}
        
        # Europe Indices
        logger.info("\n--- EUROPE INDICES (Yahoo Finance) ---")
        ftse_data = self.fetch_yahoo_finance_index('^FTSE', 'FTSE 100')
        if ftse_data:
            self.data['ftse'] = ftse_data
        else:
            self.data['ftse'] = {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A', 'source_url': 'https://finance.yahoo.com'}
        
        time.sleep(1)
        
        dax_data = self.fetch_yahoo_finance_index('^GDAXI', 'DAX')
        if dax_data:
            self.data['dax'] = dax_data
        else:
            self.data['dax'] = {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A', 'source_url': 'https://finance.yahoo.com'}
        
        time.sleep(1)
        
        cac_data = self.fetch_yahoo_finance_index('^FCHI', 'CAC 40')
        if cac_data:
            self.data['cac'] = cac_data
        else:
            self.data['cac'] = {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A', 'source_url': 'https://finance.yahoo.com'}
        
        # Cryptocurrency
        logger.info("\n--- CRYPTOCURRENCY (Yahoo Finance) ---")
        btc_data = self.fetch_yahoo_finance_index('BTC-USD', 'Bitcoin')
        if btc_data:
            self.data['btc'] = btc_data
        else:
            self.data['btc'] = {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A', 'source_url': 'https://finance.yahoo.com'}
        
        time.sleep(1)
        
        eth_data = self.fetch_yahoo_finance_index('ETH-USD', 'Ethereum')
        if eth_data:
            self.data['eth'] = eth_data
        else:
            self.data['eth'] = {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A', 'source_url': 'https://finance.yahoo.com'}
        
        # Commodities & Currency
        logger.info("\n--- COMMODITIES & CURRENCY (Yahoo Finance) ---")
        commodities = {
            'gold': ('GC=F', 'Gold'),
            'silver': ('SI=F', 'Silver'),
            'crude': ('CL=F', 'Crude Oil'),
            'usd': ('DXY=F', 'USD Index'),
            'inr_usd': ('INRUSD=X', 'INR/USD'),
            'us_10y': ('^TNX', 'US 10Y Treasury')
        }
        
        for key, (symbol, name) in commodities.items():
            data = self.fetch_yahoo_finance_index(symbol, name)
            if data:
                self.data[key] = data
            else:
                self.data[key] = {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A', 'source_url': 'https://finance.yahoo.com'}
            time.sleep(1)
        
        logger.info("="*100 + "\n")
        
        # Log any fetch errors
        if self.fetch_errors:
            logger.warning("Fetch Errors Encountered:")
            for error in self.fetch_errors:
                logger.warning(f"  - {error}")
        
        return self.data


def create_html(data):
    """Create comprehensive HTML email"""
    ts = datetime.now().strftime('%B %d, %Y at %H:%M IST')
    
    def val(key, field='value', default='N/A'):
        return data.get(key, {}).get(field, default)
    
    def source_link(key):
        url = data.get(key, {}).get('source_url', '#')
        name = data.get(key, {}).get('source_name', 'Source')
        return f'<a href="{url}" target="_blank" style="color: #2c5aa0; text-decoration: none; font-size: 0.8em;">{name}</a>'
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px; }}
        .wrapper {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #1a3a52, #2c5aa0); color: white; padding: 50px 40px; border-radius: 12px 12px 0 0; text-align: center; }}
        .header h1 {{ font-size: 2.8em; margin-bottom: 10px; font-weight: 700; }}
        .timestamp {{ background: rgba(255,255,255,0.15); padding: 10px 20px; border-radius: 20px; display: inline-block; margin-top: 15px; font-size: 0.95em; }}
        .content {{ background: white; padding: 50px 40px; }}
        .section {{ margin-bottom: 50px; }}
        .section h2 {{ color: #1a3a52; font-size: 1.9em; margin-bottom: 30px; padding-bottom: 15px; border-bottom: 3px solid #ff9800; font-weight: 700; }}
        .section h3 {{ color: #2c5aa0; font-size: 1.3em; margin: 30px 0 20px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 25px 0; border: 2px solid #e0e7ff; border-radius: 8px; overflow: hidden; }}
        th {{ background: linear-gradient(135deg, #2c5aa0, #1a3a52); color: white; padding: 18px; text-align: left; font-weight: 700; text-transform: uppercase; font-size: 0.95em; }}
        td {{ padding: 16px 18px; border-bottom: 1px solid #f0f0f0; }}
        tr:nth-child(even) {{ background: #f8f9ff; }}
        .value {{ font-weight: 700; color: #1a3a52; font-size: 1.05em; }}
        .source {{ font-size: 0.85em; color: #666; }}
        .footer {{ background: linear-gradient(135deg, #1a3a52, #2c5aa0); color: white; padding: 40px; border-radius: 0 0 12px 12px; text-align: center; font-size: 0.95em; }}
        .footer p {{ margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="header">
            <h1>📊 Daily Market Intelligence Report</h1>
            <p>LIVE MARKET DATA - Global Coverage</p>
            <div class="timestamp">{ts}</div>
        </div>

        <div class="content">
            <!-- INDIAN MARKET -->
            <div class="section">
                <h2>🇮🇳 Indian Market (NSE Official)</h2>
                <h3>Core Indices</h3>
                <table>
                    <tr><th>Index</th><th>Value</th><th>Change</th><th>% Change</th><th>Source</th></tr>
                    <tr><td><strong>Nifty 50</strong></td><td class="value">{val('nifty50')}</td><td>{val('nifty50', 'change')}</td><td>{val('nifty50', 'pct')}</td><td class="source">{source_link('nifty50')}</td></tr>
                    <tr><td><strong>BSE Sensex</strong></td><td class="value">{val('sensex')}</td><td>{val('sensex', 'change')}</td><td>{val('sensex', 'pct')}</td><td class="source">{source_link('sensex')}</td></tr>
                    <tr><td><strong>India VIX</strong></td><td class="value">{val('vix')}</td><td>{val('vix', 'change')}</td><td>-</td><td class="source">{source_link('vix')}</td></tr>
                </table>
                <h3>Sectoral Indices</h3>
                <table>
                    <tr><th>Index</th><th>Value</th><th>Change</th><th>% Change</th><th>Source</th></tr>
                    <tr><td><strong>Nifty Bank</strong></td><td class="value">{val('nifty_bank')}</td><td>{val('nifty_bank', 'change')}</td><td>{val('nifty_bank', 'pct')}</td><td class="source">{source_link('nifty_bank')}</td></tr>
                    <tr><td><strong>Nifty Midcap 100</strong></td><td class="value">{val('nifty_midcap100')}</td><td>{val('nifty_midcap100', 'change')}</td><td>{val('nifty_midcap100', 'pct')}</td><td class="source">{source_link('nifty_midcap100')}</td></tr>
                    <tr><td><strong>Nifty Smallcap 250</strong></td><td class="value">{val('nifty_smallcap250')}</td><td>{val('nifty_smallcap250', 'change')}</td><td>{val('nifty_smallcap250', 'pct')}</td><td class="source">{source_link('nifty_smallcap250')}</td></tr>
                </table>
            </div>

            <!-- US MARKET -->
            <div class="section">
                <h2>🇺🇸 US Market Indices</h2>
                <table>
                    <tr><th>Index</th><th>Value</th><th>Change</th><th>% Change</th><th>Source</th></tr>
                    <tr><td><strong>S&P 500</strong></td><td class="value">{val('sp500')}</td><td>{val('sp500', 'change')}</td><td>{val('sp500', 'pct')}</td><td class="source">{source_link('sp500')}</td></tr>
                    <tr><td><strong>Nasdaq 100</strong></td><td class="value">{val('nasdaq')}</td><td>{val('nasdaq', 'change')}</td><td>{val('nasdaq', 'pct')}</td><td class="source">{source_link('nasdaq')}</td></tr>
                    <tr><td><strong>Dow Jones Futures</strong></td><td class="value">{val('dow_futures')}</td><td>{val('dow_futures', 'change')}</td><td>{val('dow_futures', 'pct')}</td><td class="source">{source_link('dow_futures')}</td></tr>
                </table>
            </div>

            <!-- EUROPE MARKET -->
            <div class="section">
                <h2>🇪🇺 Europe Market Indices</h2>
                <table>
                    <tr><th>Market</th><th>Country</th><th>Value</th><th>Change</th><th>% Change</th><th>Source</th></tr>
                    <tr><td><strong>FTSE 100</strong></td><td>UK</td><td class="value">{val('ftse')}</td><td>{val('ftse', 'change')}</td><td>{val('ftse', 'pct')}</td><td class="source">{source_link('ftse')}</td></tr>
                    <tr><td><strong>DAX</strong></td><td>Germany</td><td class="value">{val('dax')}</td><td>{val('dax', 'change')}</td><td>{val('dax', 'pct')}</td><td class="source">{source_link('dax')}</td></tr>
                    <tr><td><strong>CAC 40</strong></td><td>France</td><td class="value">{val('cac')}</td><td>{val('cac', 'change')}</td><td>{val('cac', 'pct')}</td><td class="source">{source_link('cac')}</td></tr>
                </table>
            </div>

            <!-- CRYPTOCURRENCY -->
            <div class="section">
                <h2>₿ Cryptocurrencies</h2>
                <table>
                    <tr><th>Asset</th><th>Price</th><th>Change</th><th>% Change</th><th>Source</th></tr>
                    <tr><td><strong>Bitcoin</strong></td><td class="value">{val('btc')}</td><td>{val('btc', 'change')}</td><td>{val('btc', 'pct')}</td><td class="source">{source_link('btc')}</td></tr>
                    <tr><td><strong>Ethereum</strong></td><td class="value">{val('eth')}</td><td>{val('eth', 'change')}</td><td>{val('eth', 'pct')}</td><td class="source">{source_link('eth')}</td></tr>
                </table>
            </div>

            <!-- COMMODITIES & CURRENCY -->
            <div class="section">
                <h2>💎 Commodities & Currency</h2>
                <table>
                    <tr><th>Asset</th><th>Price</th><th>Change</th><th>% Change</th><th>Source</th></tr>
                    <tr><td><strong>Gold (per oz)</strong></td><td class="value">{val('gold')}</td><td>{val('gold', 'change')}</td><td>{val('gold', 'pct')}</td><td class="source">{source_link('gold')}</td></tr>
                    <tr><td><strong>Silver (per oz)</strong></td><td class="value">{val('silver')}</td><td>{val('silver', 'change')}</td><td>{val('silver', 'pct')}</td><td class="source">{source_link('silver')}</td></tr>
                    <tr><td><strong>Crude Oil (Brent)</strong></td><td class="value">{val('crude')}</td><td>{val('crude', 'change')}</td><td>{val('crude', 'pct')}</td><td class="source">{source_link('crude')}</td></tr>
                    <tr><td><strong>USD Index</strong></td><td class="value">{val('usd')}</td><td>{val('usd', 'change')}</td><td>{val('usd', 'pct')}</td><td class="source">{source_link('usd')}</td></tr>
                    <tr><td><strong>INR/USD</strong></td><td class="value">{val('inr_usd')}</td><td>{val('inr_usd', 'change')}</td><td>{val('inr_usd', 'pct')}</td><td class="source">{source_link('inr_usd')}</td></tr>
                    <tr><td><strong>US 10Y Yield</strong></td><td class="value">{val('us_10y')}</td><td>{val('us_10y', 'change')}</td><td>{val('us_10y', 'pct')}</td><td class="source">{source_link('us_10y')}</td></tr>
                </table>
            </div>
        </div>

        <div class="footer">
            <p><strong>Daily Market Intelligence Report</strong></p>
            <p>Live Data from NSE, Yahoo Finance & Multiple Sources</p>
            <p>8:00 AM IST Daily | mailbox.macwan@gmail.com</p>
        </div>
    </div>
</body>
</html>
"""
    return html


def send_email(recipient, subject, html_content):
    """Send email"""
    try:
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        
        if not sender_email or not sender_password:
            logger.error("Email credentials missing")
            return False
        
        logger.info("Sending email...")
        
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = recipient
        message.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, message.as_string())
        
        logger.info("✅ Email sent successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Email error: {e}")
        return False


def main():
    logger.info("\n" + "="*100)
    logger.info("COMPREHENSIVE DAILY MARKET INTELLIGENCE REPORT")
    logger.info("FIXED VERSION - LIVE DATA EXTRACTION")
    logger.info("="*100)
    
    try:
        logger.info("\n[1/2] Fetching LIVE market data...")
        collector = FixedMarketCollector()
        market_data = collector.fetch_all_data()
        
        logger.info("[2/2] Generating and sending email...")
        html_email = create_html(market_data)
        subject = f"Daily Market Intelligence Report - {datetime.now().strftime('%B %d, %Y')}"
        
        if send_email("mailbox.macwan@gmail.com", subject, html_email):
            logger.info("="*100)
            logger.info("✅ SUCCESS: REPORT WITH LIVE DATA SENT!")
            logger.info("="*100 + "\n")
            return 0
        return 1
            
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
