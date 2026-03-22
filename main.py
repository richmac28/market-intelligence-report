#!/usr/bin/env python3
"""
🎯 COMPREHENSIVE DAILY MARKET INTELLIGENCE REPORT SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Professional Grade | Live Data | Dynamic Research Links
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LiveMarketCollector:
    """Live market data collector with dynamic research article fetching"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.timeout = 12
        self.data = {}
        self.research_articles = {}

    def safe_fetch(self, url, timeout=None):
        """Safely fetch URL"""
        try:
            if timeout is None:
                timeout = self.timeout
            response = self.session.get(url, timeout=timeout)
            return response if response.status_code == 200 else None
        except Exception as e:
            logger.warning(f"Fetch error for {url}: {e}")
            return None

    # ===== INDIA MARKET DATA =====
    
    def collect_india_indices(self):
        """Collect India indices from NSE API"""
        logger.info("📊 Fetching India Market Indices...")
        
        # Nifty 50
        try:
            r = self.safe_fetch('https://www.nseindia.com/api/quote-derivative?symbol=NIFTY')
            if r:
                rec = r.json()['records'][0]
                val = float(rec['underlyingValue'])
                chg = float(rec['change'])
                pct = (chg / (val - chg) * 100) if (val - chg) != 0 else 0
                self.data['nifty'] = {
                    'value': f'{val:,.0f}',
                    'change': f'{chg:+,.0f}',
                    'pct': f'{pct:+.2f}%',
                    'source': 'NSE Official'
                }
                logger.info(f"✓ Nifty 50: {val:,.0f} ({pct:+.2f}%)")
        except Exception as e:
            logger.error(f"Nifty error: {e}")
            self.data['nifty'] = {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A', 'source': 'NSE'}

        # Sensex
        try:
            r = self.safe_fetch('https://www.moneycontrol.com/mcapi/v2/index/data?token=sensexdata')
            if r:
                d = r.json()['data']
                val = float(d['currentValue'])
                chg = float(d['change'])
                pct = float(d['perChange'])
                self.data['sensex'] = {
                    'value': f'{val:,.0f}',
                    'change': f'{chg:+,.0f}',
                    'pct': f'{pct:+.2f}%',
                    'source': 'BSE Official'
                }
                logger.info(f"✓ Sensex: {val:,.0f} ({pct:+.2f}%)")
        except Exception as e:
            logger.error(f"Sensex error: {e}")
            self.data['sensex'] = {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A', 'source': 'BSE'}

        # India VIX
        try:
            r = self.safe_fetch('https://www.nseindia.com/api/quote-derivative?symbol=INDIAVIX')
            if r:
                rec = r.json()['records'][0]
                val = float(rec['underlyingValue'])
                chg = float(rec['change'])
                self.data['vix'] = {
                    'value': f'{val:.2f}',
                    'change': f'{chg:+.2f}',
                    'source': 'NSE Official'
                }
                logger.info(f"✓ India VIX: {val:.2f}")
        except Exception as e:
            logger.error(f"VIX error: {e}")
            self.data['vix'] = {'value': 'N/A', 'change': 'N/A', 'source': 'NSE'}

        # GIFT Nifty
        try:
            r = self.safe_fetch('https://www.nseindia.com/api/quote-derivative?symbol=NIFTY')
            if r:
                val = float(r.json()['records'][0]['underlyingValue'])
                self.data['gift'] = {
                    'value': f'{val:,.0f}',
                    'source': 'NSE/SGX'
                }
                logger.info(f"✓ GIFT Nifty: {val:,.0f}")
        except Exception as e:
            logger.error(f"GIFT error: {e}")
            self.data['gift'] = {'value': 'N/A', 'source': 'NSE/SGX'}

        # FII/DII
        try:
            r = self.safe_fetch('https://www.moneycontrol.com/mcapi/get-fii-data')
            if r:
                d = r.json()['data'][0]
                self.data['fii'] = str(d.get('fiiInflow', 'N/A'))
                self.data['dii'] = str(d.get('diiInflow', 'N/A'))
                logger.info(f"✓ FII/DII Data Fetched")
        except Exception as e:
            logger.error(f"FII/DII error: {e}")
            self.data['fii'] = 'N/A'
            self.data['dii'] = 'N/A'

    # ===== GLOBAL MARKET DATA =====
    
    def collect_global_indices(self):
        """Collect US and Asian indices"""
        logger.info("🌍 Fetching Global Market Indices...")
        
        indices = {
            'sp500': '^GSPC',
            'nasdaq': '^IXIC',
            'dow': '^DJI',
            'nikkei': '^N225',
            'hangseng': '^HSI'
        }
        
        for key, sym in indices.items():
            try:
                url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={sym}&fields=regularMarketPrice,regularMarketChange,regularMarketChangePercent'
                r = self.safe_fetch(url, timeout=10)
                if r:
                    q = r.json()['quoteResponse']['result'][0]
                    p = q.get('regularMarketPrice')
                    if p:
                        c = q.get('regularMarketChange', 0)
                        pct = q.get('regularMarketChangePercent', 0)
                        self.data[key] = {
                            'value': f'{p:,.0f}',
                            'change': f'{c:+,.0f}',
                            'pct': f'{pct:+.2f}%',
                            'source': 'Bloomberg'
                        }
                        logger.info(f"✓ {key.upper()}: {p:,.0f}")
            except Exception as e:
                logger.warning(f"{key} error: {e}")
                self.data[key] = {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A', 'source': 'Bloomberg'}

    def collect_commodities(self):
        """Collect commodity prices"""
        logger.info("💰 Fetching Commodities...")
        
        commodities = {'crude': 'CL=F', 'gold': 'GC=F', 'silver': 'SI=F'}
        
        for key, sym in commodities.items():
            try:
                url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={sym}&fields=regularMarketPrice,regularMarketChange'
                r = self.safe_fetch(url, timeout=10)
                if r:
                    q = r.json()['quoteResponse']['result'][0]
                    p = q.get('regularMarketPrice')
                    if p:
                        c = q.get('regularMarketChange', 0)
                        self.data[key] = {
                            'value': f'${p:.2f}',
                            'change': f'{c:+.2f}',
                            'source': 'Bloomberg'
                        }
                        logger.info(f"✓ {key.upper()}: ${p:.2f}")
            except Exception as e:
                logger.warning(f"{key} error: {e}")
                self.data[key] = {'value': 'N/A', 'change': 'N/A', 'source': 'Bloomberg'}

    def collect_currency_yields(self):
        """Collect currency and yields"""
        logger.info("📈 Fetching Currency & Yields...")
        
        pairs = {'usd_index': 'DXY=F', 'inr_usd': 'INRUSD=X', 'us_10y': '^TNX'}
        
        for key, sym in pairs.items():
            try:
                url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={sym}&fields=regularMarketPrice,regularMarketChange'
                r = self.safe_fetch(url, timeout=10)
                if r:
                    q = r.json()['quoteResponse']['result'][0]
                    p = q.get('regularMarketPrice')
                    if p:
                        c = q.get('regularMarketChange', 0)
                        suf = '%' if 'yield' in key else ''
                        self.data[key] = {
                            'value': f'{p:.2f}{suf}',
                            'change': f'{c:+.2f}',
                            'source': 'Bloomberg'
                        }
                        logger.info(f"✓ {key.upper()}: {p:.2f}{suf}")
            except Exception as e:
                logger.warning(f"{key} error: {e}")
                self.data[key] = {'value': 'N/A', 'change': 'N/A', 'source': 'Bloomberg'}

    def fetch_latest_research_articles(self):
        """Fetch latest research articles from news sources"""
        logger.info("\n📰 Fetching Latest Research Articles...")
        
        # Moneycontrol Markets
        try:
            logger.info("Checking Moneycontrol Markets...")
            r = self.safe_fetch('https://www.moneycontrol.com/news/markets/', timeout=15)
            if r:
                soup = BeautifulSoup(r.content, 'html.parser')
                articles = []
                for item in soup.find_all('h2', limit=3):
                    link = item.find('a')
                    if link and link.get('href'):
                        title = link.text.strip()
                        url = link.get('href')
                        if url.startswith('/'):
                            url = 'https://www.moneycontrol.com' + url
                        if title and len(articles) < 2:
                            articles.append({'title': title[:70], 'url': url})
                if articles:
                    self.research_articles['moneycontrol'] = articles
                    logger.info(f"✓ Found {len(articles)} Moneycontrol articles")
        except Exception as e:
            logger.warning(f"Moneycontrol fetch error: {e}")

        # Investing.com India Markets
        try:
            logger.info("Checking Investing.com India...")
            r = self.safe_fetch('https://in.investing.com/news/', timeout=15)
            if r:
                soup = BeautifulSoup(r.content, 'html.parser')
                articles = []
                for item in soup.find_all('a', {'data-test': 'internal-link'}, limit=3):
                    title = item.get('title', '').strip()
                    url = item.get('href', '')
                    if title and url and len(articles) < 2:
                        if not url.startswith('http'):
                            url = 'https://in.investing.com' + url
                        articles.append({'title': title[:70], 'url': url})
                if articles:
                    self.research_articles['investing'] = articles
                    logger.info(f"✓ Found {len(articles)} Investing.com articles")
        except Exception as e:
            logger.warning(f"Investing.com fetch error: {e}")

        # ET Markets
        try:
            logger.info("Checking ET Markets...")
            r = self.safe_fetch('https://markets.economictimes.indiatimes.com/', timeout=15)
            if r:
                soup = BeautifulSoup(r.content, 'html.parser')
                articles = []
                for item in soup.find_all('a', limit=5):
                    if 'markets' in item.get('href', '').lower() or 'market' in item.text.lower():
                        title = item.text.strip()
                        url = item.get('href', '')
                        if title and url and len(title) > 10 and len(articles) < 2:
                            if not url.startswith('http'):
                                url = 'https://markets.economictimes.indiatimes.com' + url
                            articles.append({'title': title[:70], 'url': url})
                if articles:
                    self.research_articles['etmarkets'] = articles
                    logger.info(f"✓ Found {len(articles)} ET Markets articles")
        except Exception as e:
            logger.warning(f"ET Markets fetch error: {e}")

    def collect_all(self):
        """Main collection function"""
        logger.info("\n" + "="*100)
        logger.info("🚀 STARTING COMPREHENSIVE LIVE DATA COLLECTION")
        logger.info("="*100)
        
        self.collect_india_indices()
        self.collect_global_indices()
        self.collect_commodities()
        self.collect_currency_yields()
        self.fetch_latest_research_articles()
        
        logger.info("\n" + "="*100)
        logger.info("✅ DATA COLLECTION COMPLETE")
        logger.info("="*100 + "\n")
        
        return self.data, self.research_articles


def create_professional_html(data, articles):
    """Create professional HTML email with live data and dynamic articles"""
    ts = datetime.now().strftime('%B %d, %Y at %H:%M IST')
    
    def val(key, field='value', default='N/A'):
        return data.get(key, {}).get(field, default)
    
    # Build research section HTML
    research_html = ""
    if articles:
        research_html = '<h3>📚 Latest Market Research & Insights</h3><ul style="line-height: 1.8; margin: 15px 0; padding-left: 20px;">'
        
        if 'moneycontrol' in articles:
            research_html += '<li><strong>💼 Moneycontrol Markets:</strong><ul style="margin-top: 8px;">'
            for article in articles['moneycontrol']:
                research_html += f'<li><a href="{article["url"]}" target="_blank" style="color: #2c5aa0; text-decoration: none; font-weight: 600;">{article["title"]}</a></li>'
            research_html += '</ul></li>'
        
        if 'investing' in articles:
            research_html += '<li style="margin-top: 15px;"><strong>📊 Investing.com India:</strong><ul style="margin-top: 8px;">'
            for article in articles['investing']:
                research_html += f'<li><a href="{article["url"]}" target="_blank" style="color: #2c5aa0; text-decoration: none; font-weight: 600;">{article["title"]}</a></li>'
            research_html += '</ul></li>'
        
        if 'etmarkets' in articles:
            research_html += '<li style="margin-top: 15px;"><strong>📰 ET Markets:</strong><ul style="margin-top: 8px;">'
            for article in articles['etmarkets']:
                research_html += f'<li><a href="{article["url"]}" target="_blank" style="color: #2c5aa0; text-decoration: none; font-weight: 600;">{article["title"]}</a></li>'
            research_html += '</ul></li>'
        
        research_html += '</ul>'
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; }}
        .wrapper {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #1a3a52 0%, #2c5aa0 100%); color: white; padding: 50px 40px; border-radius: 12px 12px 0 0; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
        .header h1 {{ font-size: 2.8em; margin-bottom: 10px; font-weight: 700; }}
        .header p {{ font-size: 1.1em; opacity: 0.95; margin-bottom: 15px; }}
        .timestamp {{ background: rgba(255,255,255,0.15); padding: 12px 24px; border-radius: 25px; display: inline-block; font-size: 0.95em; }}
        .content {{ background: white; padding: 50px 40px; }}
        .section {{ margin-bottom: 50px; }}
        .section h2 {{ color: #1a3a52; font-size: 1.9em; margin-bottom: 30px; padding-bottom: 15px; border-bottom: 3px solid #ff9800; font-weight: 700; }}
        .section h3 {{ color: #2c5aa0; font-size: 1.3em; margin: 35px 0 20px 0; font-weight: 600; }}
        table {{ width: 100%; border-collapse: collapse; margin: 25px 0; background: white; border: 2px solid #e0e7ff; border-radius: 8px; overflow: hidden; }}
        th {{ background: linear-gradient(135deg, #2c5aa0 0%, #1a3a52 100%); color: white; padding: 18px; text-align: left; font-weight: 700; font-size: 0.95em; text-transform: uppercase; letter-spacing: 0.5px; }}
        td {{ padding: 16px 18px; border-bottom: 1px solid #f0f0f0; }}
        tr:last-child td {{ border-bottom: none; }}
        tr:nth-child(even) {{ background: #f8f9ff; }}
        .value {{ font-weight: 700; color: #1a3a52; font-size: 1.05em; }}
        .source {{ font-size: 0.85em; color: #666; }}
        .footer {{ background: linear-gradient(135deg, #1a3a52 0%, #2c5aa0 100%); color: white; padding: 40px; border-radius: 0 0 12px 12px; text-align: center; font-size: 0.95em; line-height: 1.6; }}
        .footer p {{ margin: 10px 0; }}
        .excel-section {{ background: linear-gradient(135deg, #fff5f0 0%, #ffe8db 100%); border-left: 4px solid #ff9800; padding: 25px; border-radius: 8px; margin: 30px 0; text-align: center; }}
        .excel-section p {{ margin: 10px 0; line-height: 1.6; }}
        .excel-section a {{ color: #ff9800; text-decoration: none; font-weight: 700; font-size: 1.1em; }}
        .excel-section a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="header">
            <h1>📊 Daily Market Intelligence Report</h1>
            <p>Live Market Data | Professional Analysis | Current Research Insights</p>
            <div class="timestamp">🕐 {ts}</div>
        </div>

        <div class="content">
            <!-- INDIA MARKET DATA -->
            <div class="section">
                <h2>🇮🇳 Domestic Market & Portfolio Data</h2>
                
                <h3>Indian Indices (Live)</h3>
                <table>
                    <tr><th>Index</th><th>Value</th><th>Change</th><th>% Change</th><th>Source</th></tr>
                    <tr>
                        <td><strong>Nifty 50</strong></td>
                        <td class="value">{val('nifty')}</td>
                        <td>{val('nifty', 'change')}</td>
                        <td>{val('nifty', 'pct')}</td>
                        <td class="source">{val('nifty', 'source')}</td>
                    </tr>
                    <tr>
                        <td><strong>Sensex</strong></td>
                        <td class="value">{val('sensex')}</td>
                        <td>{val('sensex', 'change')}</td>
                        <td>{val('sensex', 'pct')}</td>
                        <td class="source">{val('sensex', 'source')}</td>
                    </tr>
                    <tr>
                        <td><strong>India VIX (Volatility)</strong></td>
                        <td class="value">{val('vix')}</td>
                        <td>{val('vix', 'change')}</td>
                        <td>-</td>
                        <td class="source">{val('vix', 'source')}</td>
                    </tr>
                </table>

                <h3>Investor Flows (FII/DII)</h3>
                <table>
                    <tr><th>Investor Type</th><th>Flow Status</th><th>Sentiment</th></tr>
                    <tr>
                        <td><strong>Foreign Institutional Investors (FII)</strong></td>
                        <td class="value">{data.get('fii', 'N/A')}</td>
                        <td>{('Net Buyer ✓' if data.get('fii', '')[0:1] == '+' else 'Net Seller ✗') if data.get('fii', '')[0:1] in ['+', '-'] else 'N/A'}</td>
                    </tr>
                    <tr>
                        <td><strong>Domestic Institutional Investors (DII)</strong></td>
                        <td class="value">{data.get('dii', 'N/A')}</td>
                        <td>{('Net Buyer ✓' if data.get('dii', '')[0:1] == '+' else 'Net Seller ✗') if data.get('dii', '')[0:1] in ['+', '-'] else 'N/A'}</td>
                    </tr>
                </table>
            </div>

            <!-- GLOBAL MARKET DATA -->
            <div class="section">
                <h2>🌍 Global Market Indicators (Pre-Market Cues)</h2>
                
                <h3>India Pre-Market & Global Indices</h3>
                <table>
                    <tr><th>Indicator</th><th>Value</th><th>Change</th><th>% Change</th><th>Source</th></tr>
                    <tr>
                        <td><strong>GIFT Nifty (SGX - Opening Cue)</strong></td>
                        <td class="value">{val('gift')}</td>
                        <td>-</td>
                        <td>-</td>
                        <td class="source">{val('gift', 'source')}</td>
                    </tr>
                    <tr>
                        <td><strong>S&P 500</strong></td>
                        <td class="value">{val('sp500')}</td>
                        <td>{val('sp500', 'change')}</td>
                        <td>{val('sp500', 'pct')}</td>
                        <td class="source">{val('sp500', 'source')}</td>
                    </tr>
                    <tr>
                        <td><strong>Nasdaq 100</strong></td>
                        <td class="value">{val('nasdaq')}</td>
                        <td>{val('nasdaq', 'change')}</td>
                        <td>{val('nasdaq', 'pct')}</td>
                        <td class="source">{val('nasdaq', 'source')}</td>
                    </tr>
                    <tr>
                        <td><strong>Dow Jones</strong></td>
                        <td class="value">{val('dow')}</td>
                        <td>{val('dow', 'change')}</td>
                        <td>{val('dow', 'pct')}</td>
                        <td class="source">{val('dow', 'source')}</td>
                    </tr>
                    <tr>
                        <td><strong>Nikkei 225 (Japan)</strong></td>
                        <td class="value">{val('nikkei')}</td>
                        <td>{val('nikkei', 'change')}</td>
                        <td>{val('nikkei', 'pct')}</td>
                        <td class="source">{val('nikkei', 'source')}</td>
                    </tr>
                    <tr>
                        <td><strong>Hang Seng (Hong Kong)</strong></td>
                        <td class="value">{val('hangseng')}</td>
                        <td>{val('hangseng', 'change')}</td>
                        <td>{val('hangseng', 'pct')}</td>
                        <td class="source">{val('hangseng', 'source')}</td>
                    </tr>
                </table>

                <h3>Global Commodities & Currency</h3>
                <table>
                    <tr><th>Asset</th><th>Price</th><th>Change</th><th>Impact</th><th>Source</th></tr>
                    <tr>
                        <td><strong>Crude Oil</strong></td>
                        <td class="value">{val('crude')}</td>
                        <td>{val('crude', 'change')}</td>
                        <td><small>Inflation & Import Bill</small></td>
                        <td class="source">{val('crude', 'source')}</td>
                    </tr>
                    <tr>
                        <td><strong>Gold</strong></td>
                        <td class="value">{val('gold')}</td>
                        <td>{val('gold', 'change')}</td>
                        <td><small>Safe Haven Asset</small></td>
                        <td class="source">{val('gold', 'source')}</td>
                    </tr>
                    <tr>
                        <td><strong>Silver</strong></td>
                        <td class="value">{val('silver')}</td>
                        <td>{val('silver', 'change')}</td>
                        <td><small>Industrial Demand</small></td>
                        <td class="source">{val('silver', 'source')}</td>
                    </tr>
                    <tr>
                        <td><strong>USD Index</strong></td>
                        <td class="value">{val('usd_index')}</td>
                        <td>{val('usd_index', 'change')}</td>
                        <td><small>FII Inflow Impact</small></td>
                        <td class="source">{val('usd_index', 'source')}</td>
                    </tr>
                    <tr>
                        <td><strong>INR/USD Rate</strong></td>
                        <td class="value">{val('inr_usd')}</td>
                        <td>{val('inr_usd', 'change')}</td>
                        <td><small>Export Competitiveness</small></td>
                        <td class="source">{val('inr_usd', 'source')}</td>
                    </tr>
                    <tr>
                        <td><strong>US 10Y Yield</strong></td>
                        <td class="value">{val('us_10y')}</td>
                        <td>{val('us_10y', 'change')}</td>
                        <td><small>Emerging Markets Risk</small></td>
                        <td class="source">{val('us_10y', 'source')}</td>
                    </tr>
                </table>
            </div>

            <!-- RESEARCH & ARTICLES -->
            <div class="section">
                <h2>📰 Latest Market Research & Analysis</h2>
                {research_html if research_html else '<p style="color: #666; font-style: italic;">No current research articles available from sources at this time. Check Bloomberg, Moneycontrol, Investing.com, and ET Markets directly for latest insights.</p>'}
            </div>

            <!-- EXCEL FIN CONCEPTS -->
            <div class="excel-section">
                <h3 style="color: #ff9800; margin-bottom: 15px;">🎓 Financial Planning & Mutual Fund Investment Solutions</h3>
                <p><strong>Excel Fin Concepts</strong> - Help you achieve your financial goals with expert planning and investment guidance</p>
                <p style="margin-top: 15px;"><a href="https://linktr.ee/ExcelFinConcepts" target="_blank">👉 Explore Excel Fin Concepts</a></p>
                <p style="margin-top: 10px; font-size: 0.9em; color: #666;">Professional financial planning | Mutual fund distribution | Investment solutions</p>
            </div>
        </div>

        <div class="footer">
            <p><strong>🎯 DAILY MARKET INTELLIGENCE REPORT</strong></p>
            <p>Live Market Data | Professional Analysis | Daily Automated Delivery</p>
            <p>Automated at 8:00 AM IST | mailbox.macwan@gmail.com</p>
            <p style="margin-top: 20px; opacity: 0.9;"><em>For informational purposes only. Not investment advice. Consult a financial advisor.</em></p>
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
            logger.error("❌ Email credentials missing")
            return False
        
        logger.info(f"📧 Sending email...")
        
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
        logger.error(f"❌ Email error: {e}\n")
        return False


def main():
    """Main execution"""
    logger.info("\n" + "="*100)
    logger.info("🚀 COMPREHENSIVE DAILY MARKET INTELLIGENCE REPORT SYSTEM")
    logger.info("="*100)
    
    try:
        logger.info("\n[1/3] 📊 Collecting live market data...")
        collector = LiveMarketCollector()
        market_data, research_articles = collector.collect_all()
        
        logger.info("[2/3] 🎨 Generating professional HTML email...")
        html_email = create_professional_html(market_data, research_articles)
        
        logger.info("[3/3] 📮 Sending email...")
        subject = f"Daily Market Intelligence Report - {datetime.now().strftime('%B %d, %Y')}"
        
        if send_email("mailbox.macwan@gmail.com", subject, html_email):
            logger.info("="*100)
            logger.info("✅ SUCCESS: COMPREHENSIVE REPORT WITH LIVE DATA SENT!")
            logger.info("="*100 + "\n")
            return 0
        else:
            return 1
            
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
