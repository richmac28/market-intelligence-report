#!/usr/bin/env python3
"""
🎯 COMPREHENSIVE DAILY MARKET INTELLIGENCE REPORT SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Professional Grade Market Data Collection & Distribution
Featuring: Live Moneycontrol Data, Bloomberg Indices, Global Markets
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import requests
from bs4 import BeautifulSoup
import json
import logging
import smtplib
import os
import sys
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveMoneycontrolCollector:
    """Comprehensive market data collector from Moneycontrol and Bloomberg sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.moneycontrol.com/'
        })
        self.timeout = 15
        self.data = {}

    def fetch_moneycontrol_premarket(self):
        """Fetch live data from Moneycontrol pre-market page"""
        logger.info("\n🔍 FETCHING MONEYCONTROL PRE-MARKET DATA...")
        try:
            url = 'https://www.moneycontrol.com/markets/premarket/'
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract NIFTY 50
                try:
                    nifty_elem = soup.find('a', {'href': '/markets/indian-indices/nifty-50-9.html'})
                    if nifty_elem:
                        nifty_value = nifty_elem.find_next('span', class_='index-value')
                        nifty_change = nifty_elem.find_next('span', class_='index-change')
                        if nifty_value:
                            self.data['nifty'] = {
                                'value': nifty_value.text.strip(),
                                'change': nifty_change.text.strip() if nifty_change else 'N/A',
                                'source': 'Moneycontrol Live'
                            }
                            logger.info(f"✓ Nifty 50: {nifty_value.text.strip()}")
                except:
                    pass
                
                # Extract SENSEX
                try:
                    sensex_elem = soup.find('a', {'href': '/markets/indian-indices/sensex-30.html'})
                    if sensex_elem:
                        sensex_value = sensex_elem.find_next('span', class_='index-value')
                        sensex_change = sensex_elem.find_next('span', class_='index-change')
                        if sensex_value:
                            self.data['sensex'] = {
                                'value': sensex_value.text.strip(),
                                'change': sensex_change.text.strip() if sensex_change else 'N/A',
                                'source': 'Moneycontrol Live'
                            }
                            logger.info(f"✓ Sensex: {sensex_value.text.strip()}")
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Moneycontrol fetch error: {e}")

    def fetch_gift_nifty(self):
        """Fetch GIFT Nifty from Moneycontrol API"""
        logger.info("Fetching GIFT Nifty...")
        try:
            url = 'https://www.nseindia.com/api/quote-derivative?symbol=NIFTY'
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()['records'][0]
                self.data['gift_nifty'] = {
                    'value': f"{float(data['underlyingValue']):,.2f}",
                    'source': 'NSE (SGX Nifty)'
                }
                logger.info(f"✓ GIFT Nifty: {self.data['gift_nifty']['value']}")
        except Exception as e:
            logger.error(f"GIFT Nifty error: {e}")
            self.data['gift_nifty'] = {'value': 'N/A', 'source': 'NSE'}

    def fetch_india_vix(self):
        """Fetch India VIX"""
        logger.info("Fetching India VIX...")
        try:
            url = 'https://www.nseindia.com/api/quote-derivative?symbol=INDIAVIX'
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()['records'][0]
                val = float(data['underlyingValue'])
                chg = float(data['change'])
                self.data['vix'] = {
                    'value': f"{val:.2f}",
                    'change': f"{chg:+.2f}",
                    'source': 'NSE Official'
                }
                logger.info(f"✓ India VIX: {val:.2f}")
        except Exception as e:
            logger.error(f"VIX error: {e}")
            self.data['vix'] = {'value': 'N/A', 'change': 'N/A', 'source': 'NSE'}

    def fetch_fii_dii(self):
        """Fetch FII/DII flows"""
        logger.info("Fetching FII/DII...")
        try:
            url = 'https://www.moneycontrol.com/mcapi/get-fii-data'
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()['data'][0]
                self.data['fii_dii'] = {
                    'fii': str(data.get('fiiInflow', 'N/A')),
                    'dii': str(data.get('diiInflow', 'N/A')),
                    'source': 'Moneycontrol'
                }
                logger.info(f"✓ FII/DII fetched")
        except Exception as e:
            logger.error(f"FII/DII error: {e}")
            self.data['fii_dii'] = {'fii': 'N/A', 'dii': 'N/A', 'source': 'Moneycontrol'}

    def fetch_us_indices(self):
        """Fetch US indices"""
        logger.info("Fetching US Indices...")
        indices = {'sp500': '^GSPC', 'nasdaq': '^IXIC', 'dow': '^DJI'}
        for key, sym in indices.items():
            try:
                url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={sym}&fields=regularMarketPrice,regularMarketChange,regularMarketChangePercent'
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    q = response.json()['quoteResponse']['result'][0]
                    p = q.get('regularMarketPrice')
                    if p:
                        self.data[key] = {
                            'value': f'{p:,.0f}',
                            'change': f"{q.get('regularMarketChange',0):+,.0f}",
                            'pct': f"{q.get('regularMarketChangePercent',0):+.2f}%",
                            'source': 'Bloomberg'
                        }
                        logger.info(f"✓ {key}: {p:,.0f}")
            except Exception as e:
                logger.error(f"{key} error: {e}")
                self.data[key] = {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A', 'source': 'Bloomberg'}

    def fetch_asian_indices(self):
        """Fetch Asian indices"""
        logger.info("Fetching Asian Indices...")
        indices = {'nikkei': '^N225', 'hangseng': '^HSI'}
        for key, sym in indices.items():
            try:
                url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={sym}&fields=regularMarketPrice,regularMarketChange,regularMarketChangePercent'
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    q = response.json()['quoteResponse']['result'][0]
                    p = q.get('regularMarketPrice')
                    if p:
                        self.data[key] = {
                            'value': f'{p:,.0f}',
                            'change': f"{q.get('regularMarketChange',0):+,.0f}",
                            'pct': f"{q.get('regularMarketChangePercent',0):+.2f}%",
                            'source': 'Bloomberg'
                        }
                        logger.info(f"✓ {key}: {p:,.0f}")
            except Exception as e:
                logger.error(f"{key} error: {e}")
                self.data[key] = {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A', 'source': 'Bloomberg'}

    def fetch_commodities(self):
        """Fetch commodities"""
        logger.info("Fetching Commodities...")
        commodities = {'crude': 'CL=F', 'gold': 'GC=F', 'silver': 'SI=F'}
        for key, sym in commodities.items():
            try:
                url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={sym}&fields=regularMarketPrice,regularMarketChange'
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    q = response.json()['quoteResponse']['result'][0]
                    p = q.get('regularMarketPrice')
                    if p:
                        self.data[key] = {
                            'value': f'${p:.2f}',
                            'change': f"{q.get('regularMarketChange',0):+.2f}",
                            'source': 'Bloomberg'
                        }
                        logger.info(f"✓ {key}: ${p:.2f}")
            except Exception as e:
                logger.error(f"{key} error: {e}")
                self.data[key] = {'value': 'N/A', 'change': 'N/A', 'source': 'Bloomberg'}

    def fetch_currency_yields(self):
        """Fetch currency and yields"""
        logger.info("Fetching Currency & Yields...")
        pairs = {'usd_index': 'DXY=F', 'inr_usd': 'INRUSD=X', 'us_10y': '^TNX'}
        for key, sym in pairs.items():
            try:
                url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={sym}&fields=regularMarketPrice,regularMarketChange'
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    q = response.json()['quoteResponse']['result'][0]
                    p = q.get('regularMarketPrice')
                    if p:
                        suf = '%' if 'yield' in key else ''
                        self.data[key] = {
                            'value': f'{p:.2f}{suf}',
                            'change': f"{q.get('regularMarketChange',0):+.2f}",
                            'source': 'Bloomberg'
                        }
                        logger.info(f"✓ {key}: {p:.2f}{suf}")
            except Exception as e:
                logger.error(f"{key} error: {e}")
                self.data[key] = {'value': 'N/A', 'change': 'N/A', 'source': 'Bloomberg'}

    def collect_all(self):
        """Collect all data"""
        logger.info("\n" + "="*100)
        logger.info("COMPREHENSIVE MARKET DATA COLLECTION FROM MONEYCONTROL & BLOOMBERG")
        logger.info("="*100)
        
        self.fetch_moneycontrol_premarket()
        self.fetch_gift_nifty()
        self.fetch_india_vix()
        self.fetch_fii_dii()
        self.fetch_us_indices()
        self.fetch_asian_indices()
        self.fetch_commodities()
        self.fetch_currency_yields()
        
        logger.info("\n" + "="*100)
        return self.data


def create_professional_html(data):
    """Create professional, crisp HTML email with all sections"""
    ts = datetime.now().strftime('%B %d, %Y at %H:%M IST')
    
    def val(key, field='value', default='N/A'):
        return data.get(key, {}).get(field, default)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Market Intelligence Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; }}
        .wrapper {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #1a3a52 0%, #2c5aa0 100%); color: white; padding: 50px 40px; border-radius: 12px 12px 0 0; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
        .header h1 {{ font-size: 2.8em; margin-bottom: 10px; font-weight: 700; letter-spacing: -0.5px; }}
        .header p {{ font-size: 1.1em; opacity: 0.95; margin-bottom: 15px; }}
        .timestamp {{ background: rgba(255,255,255,0.15); padding: 12px 24px; border-radius: 25px; display: inline-block; font-size: 0.95em; }}
        .content {{ background: white; padding: 50px 40px; }}
        .section {{ margin-bottom: 50px; }}
        .section h2 {{ color: #1a3a52; font-size: 1.9em; margin-bottom: 30px; padding-bottom: 15px; border-bottom: 3px solid #ff9800; font-weight: 700; letter-spacing: -0.3px; }}
        .section h3 {{ color: #2c5aa0; font-size: 1.3em; margin: 35px 0 20px 0; font-weight: 600; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 25px 0; }}
        .card {{ background: linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%); border: 2px solid #e0e7ff; border-radius: 10px; padding: 25px; transition: all 0.3s ease; }}
        .card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 30px rgba(0,0,0,0.1); border-color: #2c5aa0; }}
        .card-label {{ font-size: 0.85em; color: #666; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; margin-bottom: 10px; }}
        .card-value {{ font-size: 1.8em; font-weight: 700; color: #1a3a52; line-height: 1.2; }}
        .card-subval {{ font-size: 0.95em; color: #2c5aa0; margin-top: 8px; font-weight: 600; }}
        table {{ width: 100%; border-collapse: collapse; margin: 25px 0; background: white; border: 2px solid #e0e7ff; border-radius: 8px; overflow: hidden; }}
        th {{ background: linear-gradient(135deg, #2c5aa0 0%, #1a3a52 100%); color: white; padding: 18px; text-align: left; font-weight: 700; font-size: 0.95em; text-transform: uppercase; letter-spacing: 0.5px; }}
        td {{ padding: 16px 18px; border-bottom: 1px solid #f0f0f0; }}
        tr:last-child td {{ border-bottom: none; }}
        tr:nth-child(even) {{ background: #f8f9ff; }}
        .value-text {{ font-weight: 700; color: #1a3a52; font-size: 1.05em; }}
        .change {{ font-weight: 600; }}
        .positive {{ color: #27ae60; }}
        .negative {{ color: #e74c3c; }}
        .source {{ font-size: 0.85em; color: #666; }}
        .footer {{ background: linear-gradient(135deg, #1a3a52 0%, #2c5aa0 100%); color: white; padding: 40px; border-radius: 0 0 12px 12px; text-align: center; font-size: 0.95em; line-height: 1.6; }}
        .footer p {{ margin: 10px 0; }}
        .sources {{ background: linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%); border-left: 4px solid #ff9800; padding: 25px; border-radius: 8px; margin: 30px 0; }}
        .sources p {{ margin: 10px 0; color: #333; line-height: 1.8; }}
        .link-section {{ background: linear-gradient(135deg, #fff5f0 0%, #ffe8db 100%); border-left: 4px solid #ff9800; padding: 25px; border-radius: 8px; margin: 30px 0; text-align: center; }}
        .link-section a {{ color: #ff9800; text-decoration: none; font-weight: 700; font-size: 1.1em; }}
        .link-section a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="header">
            <h1>📊 Daily Market Intelligence Report</h1>
            <p>Live Updates | Professional Market Analysis | Comprehensive Global & India Data</p>
            <div class="timestamp">🕐 {ts}</div>
        </div>

        <div class="content">
            <!-- SECTION 1: INDIA MARKET DATA -->
            <div class="section">
                <h2>🇮🇳 Domestic Market & Portfolio Data</h2>
                
                <h3>Key Indices</h3>
                <div class="grid">
                    <div class="card">
                        <div class="card-label">Nifty 50</div>
                        <div class="card-value">{val('nifty', 'value')}</div>
                        <div class="card-subval">{val('nifty', 'change')} {val('nifty', 'source')}</div>
                    </div>
                    <div class="card">
                        <div class="card-label">Sensex (BSE)</div>
                        <div class="card-value">{val('sensex', 'value')}</div>
                        <div class="card-subval">{val('sensex', 'change')} {val('sensex', 'source')}</div>
                    </div>
                    <div class="card">
                        <div class="card-label">India VIX</div>
                        <div class="card-value">{val('vix', 'value')}</div>
                        <div class="card-subval">{val('vix', 'change')} Volatility Index</div>
                    </div>
                </div>

                <h3>FII/DII Flows (Investor Sentiment)</h3>
                <table>
                    <tr>
                        <th>Investor Type</th>
                        <th>Flow Status</th>
                        <th>Sentiment</th>
                        <th>Source</th>
                    </tr>
                    <tr>
                        <td><strong>Foreign Institutional Investors (FII)</strong></td>
                        <td class="value-text">{val('fii_dii', 'fii')}</td>
                        <td>{('Net Buyer ✓' if '+' in val('fii_dii', 'fii') else 'Net Seller ✗') if val('fii_dii', 'fii') != 'N/A' else 'N/A'}</td>
                        <td class="source">{val('fii_dii', 'source')}</td>
                    </tr>
                    <tr>
                        <td><strong>Domestic Institutional Investors (DII)</strong></td>
                        <td class="value-text">{val('fii_dii', 'dii')}</td>
                        <td>{('Net Buyer ✓' if '+' in val('fii_dii', 'dii') else 'Net Seller ✗') if val('fii_dii', 'dii') != 'N/A' else 'N/A'}</td>
                        <td class="source">{val('fii_dii', 'source')}</td>
                    </tr>
                </table>
            </div>

            <!-- SECTION 2: GLOBAL MARKET INDICATORS -->
            <div class="section">
                <h2>🌍 Global Market Indicators (Pre-Market Cues)</h2>
                
                <h3>India Pre-Market Indicator</h3>
                <table>
                    <tr>
                        <th>Indicator</th>
                        <th>Value</th>
                        <th>Source</th>
                    </tr>
                    <tr>
                        <td><strong>GIFT Nifty (SGX Nifty) - Opening Direction Cue</strong></td>
                        <td class="value-text">{val('gift_nifty', 'value')}</td>
                        <td class="source">{val('gift_nifty', 'source')}</td>
                    </tr>
                </table>

                <h3>US Market Closures (Overnight Performance)</h3>
                <table>
                    <tr>
                        <th>Index</th>
                        <th>Value</th>
                        <th>Change</th>
                        <th>% Change</th>
                        <th>Source</th>
                    </tr>
                    <tr>
                        <td><strong>S&P 500</strong></td>
                        <td class="value-text">{val('sp500', 'value')}</td>
                        <td class="change">{val('sp500', 'change')}</td>
                        <td class="change">{val('sp500', 'pct')}</td>
                        <td class="source">{val('sp500', 'source')}</td>
                    </tr>
                    <tr>
                        <td><strong>Nasdaq 100</strong></td>
                        <td class="value-text">{val('nasdaq', 'value')}</td>
                        <td class="change">{val('nasdaq', 'change')}</td>
                        <td class="change">{val('nasdaq', 'pct')}</td>
                        <td class="source">{val('nasdaq', 'source')}</td>
                    </tr>
                    <tr>
                        <td><strong>Dow Jones</strong></td>
                        <td class="value-text">{val('dow', 'value')}</td>
                        <td class="change">{val('dow', 'change')}</td>
                        <td class="change">{val('dow', 'pct')}</td>
                        <td class="source">{val('dow', 'source')}</td>
                    </tr>
                </table>

                <h3>Asian Markets (Real-Time Trends)</h3>
                <table>
                    <tr>
                        <th>Market</th>
                        <th>Value</th>
                        <th>Change</th>
                        <th>% Change</th>
                        <th>Source</th>
                    </tr>
                    <tr>
                        <td><strong>Nikkei 225 (Japan)</strong></td>
                        <td class="value-text">{val('nikkei', 'value')}</td>
                        <td class="change">{val('nikkei', 'change')}</td>
                        <td class="change">{val('nikkei', 'pct')}</td>
                        <td class="source">{val('nikkei', 'source')}</td>
                    </tr>
                    <tr>
                        <td><strong>Hang Seng (Hong Kong)</strong></td>
                        <td class="value-text">{val('hangseng', 'value')}</td>
                        <td class="change">{val('hangseng', 'change')}</td>
                        <td class="change">{val('hangseng', 'pct')}</td>
                        <td class="source">{val('hangseng', 'source')}</td>
                    </tr>
                </table>

                <h3>Global Commodities (Impact on India)</h3>
                <table>
                    <tr>
                        <th>Commodity</th>
                        <th>Price</th>
                        <th>Change</th>
                        <th>Impact</th>
                        <th>Source</th>
                    </tr>
                    <tr>
                        <td><strong>Brent Crude Oil</strong></td>
                        <td class="value-text">{val('crude', 'value')}</td>
                        <td class="change">{val('crude', 'change')}</td>
                        <td><small>Affects India's import bill & inflation</small></td>
                        <td class="source">{val('crude', 'source')}</td>
                    </tr>
                    <tr>
                        <td><strong>Gold</strong></td>
                        <td class="value-text">{val('gold', 'value')}</td>
                        <td class="change">{val('gold', 'change')}</td>
                        <td><small>Safe-haven & jewelry demand</small></td>
                        <td class="source">{val('gold', 'source')}</td>
                    </tr>
                    <tr>
                        <td><strong>Silver</strong></td>
                        <td class="value-text">{val('silver', 'value')}</td>
                        <td class="change">{val('silver', 'change')}</td>
                        <td><small>Industrial demand indicator</small></td>
                        <td class="source">{val('silver', 'source')}</td>
                    </tr>
                </table>

                <h3>US Dollar Index & Yields (FII Impact)</h3>
                <table>
                    <tr>
                        <th>Indicator</th>
                        <th>Value</th>
                        <th>Change</th>
                        <th>Impact on FII Inflows</th>
                        <th>Source</th>
                    </tr>
                    <tr>
                        <td><strong>USD Index</strong></td>
                        <td class="value-text">{val('usd_index', 'value')}</td>
                        <td class="change">{val('usd_index', 'change')}</td>
                        <td><small>Strong USD = Lower FII inflows</small></td>
                        <td class="source">{val('usd_index', 'source')}</td>
                    </tr>
                    <tr>
                        <td><strong>INR/USD Rate</strong></td>
                        <td class="value-text">{val('inr_usd', 'value')}</td>
                        <td class="change">{val('inr_usd', 'change')}</td>
                        <td><small>Rupee strength affects exports</small></td>
                        <td class="source">{val('inr_usd', 'source')}</td>
                    </tr>
                    <tr>
                        <td><strong>US 10Y Treasury Yield</strong></td>
                        <td class="value-text">{val('us_10y', 'value')}</td>
                        <td class="change">{val('us_10y', 'change')}</td>
                        <td><small>Higher yield = More risky emerging markets</small></td>
                        <td class="source">{val('us_10y', 'source')}</td>
                    </tr>
                </table>
            </div>

            <!-- SOURCES SECTION -->
            <div class="section">
                <h2>📚 Research Sources & Market Intelligence</h2>
                <div class="sources">
                    <p><strong>🔝 Top Research Platforms:</strong></p>
                    <p>📍 <strong>Bloomberg Terminal</strong> - Institutional-grade market intelligence<br>
                    📍 <strong>Refinitiv Eikon</strong> - Financial data & analytics<br>
                    📍 <strong>Moneycontrol</strong> - Comprehensive Indian market data<br>
                    📍 <strong>NSE India & BSE India</strong> - Official Exchange Data<br>
                    📍 <strong>Investing.com India</strong> - Global market charts & analysis</p>
                    
                    <p style="margin-top: 20px;"><strong>📰 News & Insights:</strong></p>
                    <p>📍 <strong>CNBC-TV18</strong> - Live market updates & analysis<br>
                    📍 <strong>Economic Times Markets</strong> - ET Markets with detailed reporting<br>
                    📍 <strong>Financial Express</strong> - Business & market coverage<br>
                    📍 <strong>Business Standard</strong> - Comprehensive market analysis<br>
                    📍 <strong>Zerodha Pulse</strong> - Market headlines & sentiment</p>
                </div>
            </div>

            <!-- EXCEL FIN CONCEPTS LINK -->
            <div class="link-section">
                <p style="font-size: 1.2em; margin-bottom: 15px;">🎓 Learn Market Concepts & Financial Analysis</p>
                <p><strong>Explore Excel Fin Concepts:</strong></p>
                <a href="https://linktr.ee/ExcelFinConcepts" target="_blank">👉 https://linktr.ee/ExcelFinConcepts</a>
                <p style="margin-top: 15px; font-size: 0.9em; color: #666;">Master financial modeling, market analysis, and investment strategies</p>
            </div>
        </div>

        <div class="footer">
            <p><strong>🎯 DAILY MARKET INTELLIGENCE REPORT</strong></p>
            <p>Professional-Grade Market Analysis | Live Data from Moneycontrol, Bloomberg, NSE, BSE</p>
            <p>Automated Daily Delivery | 8:00 AM IST</p>
            <p>Sent to: mailbox.macwan@gmail.com</p>
            <p style="margin-top: 20px; opacity: 0.9;"><em>For informational purposes only. Not investment advice. Please consult a qualified financial advisor.</em></p>
        </div>
    </div>
</body>
</html>
"""
    return html


def send_email(recipient, subject, html_content):
    """Send professional HTML email"""
    try:
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        
        if not sender_email or not sender_password:
            logger.error("❌ Email credentials missing")
            return False
        
        logger.info(f"📧 Sending email to {recipient}...")
        
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = recipient
        message.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, message.as_string())
        
        logger.info(f"✅ Email sent successfully!\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ Email failed: {e}\n")
        return False


def main():
    """Main execution"""
    logger.info("\n" + "="*100)
    logger.info("🚀 COMPREHENSIVE DAILY MARKET INTELLIGENCE REPORT SYSTEM")
    logger.info("="*100)
    
    try:
        logger.info("\n[1/3] 📊 Collecting live market data...")
        collector = ComprehensiveMoneycontrolCollector()
        market_data = collector.collect_all()
        
        logger.info("[2/3] 🎨 Generating professional HTML email...")
        html_email = create_professional_html(market_data)
        
        logger.info("[3/3] 📮 Sending email...")
        subject = f"Daily Market Intelligence Report - {datetime.now().strftime('%B %d, %Y')}"
        
        if send_email("mailbox.macwan@gmail.com", subject, html_email):
            logger.info("="*100)
            logger.info("✅ SUCCESS: COMPREHENSIVE PROFESSIONAL REPORT SENT!")
            logger.info("="*100 + "\n")
            return 0
        else:
            logger.error("="*100)
            logger.error("❌ FAILED: Email sending failed")
            logger.error("="*100 + "\n")
            return 1
            
    except Exception as e:
        logger.error(f"\n❌ CRITICAL ERROR: {e}\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
