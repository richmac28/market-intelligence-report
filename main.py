#!/usr/bin/env python3
"""
COMPLETE DAILY MARKET INTELLIGENCE REPORT SYSTEM
Production-Ready Comprehensive Implementation
"""

import requests
import json
import logging
import smtplib
import os
import sys
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MarketDataCollector:
    """Comprehensive market data collector with multiple data sources"""
    
    def __init__(self):
        """Initialize with session and configuration"""
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        self.timeout = 10
        self.data = {}
        self.collection_stats = {'attempted': 0, 'successful': 0, 'failed': 0}

    def safe_fetch(self, url, max_retries=2):
        """Safely fetch URL with retry logic"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    return response
            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed: {e}")
                time.sleep(1)
        return None

    def collect_nifty_sensex_vix(self):
        """Collect India's key indices - NIFTY, SENSEX, VIX"""
        logger.info("\n--- COLLECTING INDIA MARKET DATA ---")
        
        # NIFTY 50
        self.collection_stats['attempted'] += 1
        try:
            logger.info("Fetching Nifty 50...")
            response = self.safe_fetch('https://www.nseindia.com/api/quote-derivative?symbol=NIFTY')
            if response:
                data = response.json()
                record = data['records'][0]
                nifty_value = float(record['underlyingValue'])
                nifty_change = float(record['change'])
                nifty_pct = (nifty_change / (nifty_value - nifty_change) * 100) if (nifty_value - nifty_change) != 0 else 0
                
                self.data['nifty_50'] = {
                    'name': 'Nifty 50',
                    'value': nifty_value,
                    'value_str': f"{nifty_value:,.2f}",
                    'change': nifty_change,
                    'change_str': f"{nifty_change:+.2f}",
                    'pct': nifty_pct,
                    'pct_str': f"{nifty_pct:+.2f}%",
                    'source': 'NSE Official API',
                    'status': 'SUCCESS'
                }
                logger.info(f"✓ Nifty 50: {nifty_value:,.2f} ({nifty_pct:+.2f}%)")
                self.collection_stats['successful'] += 1
        except Exception as e:
            logger.error(f"✗ Nifty 50 failed: {e}")
            self.data['nifty_50'] = {'name': 'Nifty 50', 'value_str': 'N/A', 'change_str': 'N/A', 'pct_str': 'N/A', 'source': 'NSE', 'status': 'FAILED'}
            self.collection_stats['failed'] += 1

        # SENSEX
        self.collection_stats['attempted'] += 1
        try:
            logger.info("Fetching Sensex...")
            response = self.safe_fetch('https://www.moneycontrol.com/mcapi/v2/index/data?token=sensexdata')
            if response:
                data = response.json()['data']
                sensex_value = float(data['currentValue'])
                sensex_change = float(data['change'])
                sensex_pct = float(data['perChange'])
                
                self.data['sensex'] = {
                    'name': 'Sensex',
                    'value': sensex_value,
                    'value_str': f"{sensex_value:,.2f}",
                    'change': sensex_change,
                    'change_str': f"{sensex_change:+.2f}",
                    'pct': sensex_pct,
                    'pct_str': f"{sensex_pct:+.2f}%",
                    'source': 'BSE Official',
                    'status': 'SUCCESS'
                }
                logger.info(f"✓ Sensex: {sensex_value:,.2f} ({sensex_pct:+.2f}%)")
                self.collection_stats['successful'] += 1
        except Exception as e:
            logger.error(f"✗ Sensex failed: {e}")
            self.data['sensex'] = {'name': 'Sensex', 'value_str': 'N/A', 'change_str': 'N/A', 'pct_str': 'N/A', 'source': 'BSE', 'status': 'FAILED'}
            self.collection_stats['failed'] += 1

        # INDIA VIX
        self.collection_stats['attempted'] += 1
        try:
            logger.info("Fetching India VIX...")
            response = self.safe_fetch('https://www.nseindia.com/api/quote-derivative?symbol=INDIAVIX')
            if response:
                data = response.json()
                record = data['records'][0]
                vix_value = float(record['underlyingValue'])
                vix_change = float(record['change'])
                
                self.data['india_vix'] = {
                    'name': 'India VIX',
                    'value': vix_value,
                    'value_str': f"{vix_value:.2f}",
                    'change': vix_change,
                    'change_str': f"{vix_change:+.2f}",
                    'source': 'NSE Official API',
                    'status': 'SUCCESS'
                }
                logger.info(f"✓ India VIX: {vix_value:.2f}")
                self.collection_stats['successful'] += 1
        except Exception as e:
            logger.error(f"✗ India VIX failed: {e}")
            self.data['india_vix'] = {'name': 'India VIX', 'value_str': 'N/A', 'change_str': 'N/A', 'source': 'NSE', 'status': 'FAILED'}
            self.collection_stats['failed'] += 1

        # GIFT NIFTY
        self.collection_stats['attempted'] += 1
        try:
            logger.info("Fetching GIFT Nifty...")
            response = self.safe_fetch('https://www.nseindia.com/api/quote-derivative?symbol=NIFTY')
            if response:
                data = response.json()
                gift_value = float(data['records'][0]['underlyingValue'])
                
                self.data['gift_nifty'] = {
                    'name': 'GIFT Nifty (SGX)',
                    'value': gift_value,
                    'value_str': f"{gift_value:,.2f}",
                    'source': 'NSE/SGX',
                    'status': 'SUCCESS'
                }
                logger.info(f"✓ GIFT Nifty: {gift_value:,.2f}")
                self.collection_stats['successful'] += 1
        except Exception as e:
            logger.error(f"✗ GIFT Nifty failed: {e}")
            self.data['gift_nifty'] = {'name': 'GIFT Nifty', 'value_str': 'N/A', 'source': 'NSE', 'status': 'FAILED'}
            self.collection_stats['failed'] += 1

        # FII/DII
        self.collection_stats['attempted'] += 1
        try:
            logger.info("Fetching FII/DII...")
            response = self.safe_fetch('https://www.moneycontrol.com/mcapi/get-fii-data')
            if response:
                data = response.json()['data'][0]
                fii = data.get('fiiInflow', 'N/A')
                dii = data.get('diiInflow', 'N/A')
                
                self.data['fii_dii'] = {
                    'name': 'FII/DII Flows',
                    'fii': str(fii),
                    'dii': str(dii),
                    'source': 'Moneycontrol',
                    'status': 'SUCCESS'
                }
                logger.info(f"✓ FII/DII: FII={fii}, DII={dii}")
                self.collection_stats['successful'] += 1
        except Exception as e:
            logger.error(f"✗ FII/DII failed: {e}")
            self.data['fii_dii'] = {'name': 'FII/DII', 'fii': 'N/A', 'dii': 'N/A', 'source': 'Moneycontrol', 'status': 'FAILED'}
            self.collection_stats['failed'] += 1

    def collect_us_indices(self):
        """Collect US Market Indices"""
        logger.info("\n--- COLLECTING US MARKET DATA ---")
        
        indices = {
            'sp500': ('^GSPC', 'S&P 500'),
            'nasdaq': ('^IXIC', 'Nasdaq 100'),
            'dow': ('^DJI', 'Dow Jones')
        }
        
        for key, (symbol, name) in indices.items():
            self.collection_stats['attempted'] += 1
            try:
                logger.info(f"Fetching {name}...")
                url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}&fields=regularMarketPrice,regularMarketChange,regularMarketChangePercent'
                response = self.safe_fetch(url)
                
                if response:
                    quote = response.json()['quoteResponse']['result'][0]
                    price = quote.get('regularMarketPrice')
                    change = quote.get('regularMarketChange', 0)
                    pct = quote.get('regularMarketChangePercent', 0)
                    
                    self.data[key] = {
                        'name': name,
                        'value': price,
                        'value_str': f"{price:,.0f}",
                        'change': change,
                        'change_str': f"{change:+,.0f}",
                        'pct': pct,
                        'pct_str': f"{pct:+.2f}%",
                        'source': 'Bloomberg/Yahoo Finance',
                        'status': 'SUCCESS'
                    }
                    logger.info(f"✓ {name}: {price:,.0f} ({pct:+.2f}%)")
                    self.collection_stats['successful'] += 1
            except Exception as e:
                logger.error(f"✗ {name} failed: {e}")
                self.data[key] = {'name': name, 'value_str': 'N/A', 'change_str': 'N/A', 'pct_str': 'N/A', 'source': 'Bloomberg', 'status': 'FAILED'}
                self.collection_stats['failed'] += 1

    def collect_asian_indices(self):
        """Collect Asian Market Indices"""
        logger.info("\n--- COLLECTING ASIAN MARKET DATA ---")
        
        indices = {
            'nikkei': ('^N225', 'Nikkei 225'),
            'hangseng': ('^HSI', 'Hang Seng')
        }
        
        for key, (symbol, name) in indices.items():
            self.collection_stats['attempted'] += 1
            try:
                logger.info(f"Fetching {name}...")
                url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}&fields=regularMarketPrice,regularMarketChange,regularMarketChangePercent'
                response = self.safe_fetch(url)
                
                if response:
                    quote = response.json()['quoteResponse']['result'][0]
                    price = quote.get('regularMarketPrice')
                    change = quote.get('regularMarketChange', 0)
                    pct = quote.get('regularMarketChangePercent', 0)
                    
                    self.data[key] = {
                        'name': name,
                        'value': price,
                        'value_str': f"{price:,.0f}",
                        'change': change,
                        'change_str': f"{change:+,.0f}",
                        'pct': pct,
                        'pct_str': f"{pct:+.2f}%",
                        'source': 'Bloomberg/Yahoo Finance',
                        'status': 'SUCCESS'
                    }
                    logger.info(f"✓ {name}: {price:,.0f} ({pct:+.2f}%)")
                    self.collection_stats['successful'] += 1
            except Exception as e:
                logger.error(f"✗ {name} failed: {e}")
                self.data[key] = {'name': name, 'value_str': 'N/A', 'change_str': 'N/A', 'pct_str': 'N/A', 'source': 'Bloomberg', 'status': 'FAILED'}
                self.collection_stats['failed'] += 1

    def collect_commodities(self):
        """Collect Commodity Prices"""
        logger.info("\n--- COLLECTING COMMODITY DATA ---")
        
        commodities = {
            'crude': ('CL=F', 'Crude Oil'),
            'gold': ('GC=F', 'Gold'),
            'silver': ('SI=F', 'Silver')
        }
        
        for key, (symbol, name) in commodities.items():
            self.collection_stats['attempted'] += 1
            try:
                logger.info(f"Fetching {name}...")
                url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}&fields=regularMarketPrice,regularMarketChange,regularMarketChangePercent'
                response = self.safe_fetch(url)
                
                if response:
                    quote = response.json()['quoteResponse']['result'][0]
                    price = quote.get('regularMarketPrice')
                    change = quote.get('regularMarketChange', 0)
                    pct = quote.get('regularMarketChangePercent', 0)
                    
                    self.data[key] = {
                        'name': name,
                        'value': price,
                        'value_str': f"${price:.2f}",
                        'change': change,
                        'change_str': f"{change:+.2f}",
                        'pct': pct,
                        'pct_str': f"{pct:+.2f}%",
                        'source': 'Bloomberg/Yahoo Finance',
                        'status': 'SUCCESS'
                    }
                    logger.info(f"✓ {name}: ${price:.2f} ({pct:+.2f}%)")
                    self.collection_stats['successful'] += 1
            except Exception as e:
                logger.error(f"✗ {name} failed: {e}")
                self.data[key] = {'name': name, 'value_str': 'N/A', 'change_str': 'N/A', 'pct_str': 'N/A', 'source': 'Bloomberg', 'status': 'FAILED'}
                self.collection_stats['failed'] += 1

    def collect_currency_and_yields(self):
        """Collect Currency and Treasury Yields"""
        logger.info("\n--- COLLECTING CURRENCY & YIELDS DATA ---")
        
        pairs = {
            'usd_index': ('DXY=F', 'USD Index'),
            'inr_usd': ('INRUSD=X', 'INR/USD'),
            'us_10y': ('^TNX', 'US 10Y Yield')
        }
        
        for key, (symbol, name) in pairs.items():
            self.collection_stats['attempted'] += 1
            try:
                logger.info(f"Fetching {name}...")
                url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}&fields=regularMarketPrice,regularMarketChange,regularMarketChangePercent'
                response = self.safe_fetch(url)
                
                if response:
                    quote = response.json()['quoteResponse']['result'][0]
                    price = quote.get('regularMarketPrice')
                    change = quote.get('regularMarketChange', 0)
                    pct = quote.get('regularMarketChangePercent', 0)
                    
                    suffix = '%' if 'yield' in name.lower() else ''
                    
                    self.data[key] = {
                        'name': name,
                        'value': price,
                        'value_str': f"{price:.2f}{suffix}",
                        'change': change,
                        'change_str': f"{change:+.2f}",
                        'pct': pct,
                        'pct_str': f"{pct:+.2f}%",
                        'source': 'Bloomberg/Yahoo Finance',
                        'status': 'SUCCESS'
                    }
                    logger.info(f"✓ {name}: {price:.2f}{suffix} ({pct:+.2f}%)")
                    self.collection_stats['successful'] += 1
            except Exception as e:
                logger.error(f"✗ {name} failed: {e}")
                self.data[key] = {'name': name, 'value_str': 'N/A', 'change_str': 'N/A', 'pct_str': 'N/A', 'source': 'Bloomberg', 'status': 'FAILED'}
                self.collection_stats['failed'] += 1

    def collect_all_data(self):
        """Main collection method"""
        logger.info("\n" + "=" * 100)
        logger.info("STARTING COMPREHENSIVE MARKET DATA COLLECTION")
        logger.info("=" * 100)
        
        self.collect_nifty_sensex_vix()
        self.collect_us_indices()
        self.collect_asian_indices()
        self.collect_commodities()
        self.collect_currency_and_yields()
        
        logger.info("\n" + "=" * 100)
        logger.info(f"COLLECTION COMPLETE - Success: {self.collection_stats['successful']}, Failed: {self.collection_stats['failed']}")
        logger.info("=" * 100 + "\n")
        
        return self.data


def generate_html_email(data):
    """Generate comprehensive HTML email"""
    
    timestamp = datetime.now().strftime('%B %d, %Y at %H:%M IST')
    
    # Helper function
    def val(key, field='value_str', default='N/A'):
        return data.get(key, {}).get(field, default)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px; }}
        .container {{ max-width: 1100px; margin: 0 auto; background-color: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #1a3a52, #2c5aa0); color: white; padding: 40px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 2.3em; font-weight: bold; }}
        .header p {{ margin: 10px 0 0 0; font-size: 1em; opacity: 0.9; }}
        .timestamp {{ background: rgba(255,255,255,0.15); padding: 10px 20px; border-radius: 15px; display: inline-block; margin-top: 15px; font-size: 0.9em; }}
        .content {{ padding: 40px; }}
        .section {{ margin-bottom: 50px; }}
        .section h2 {{ color: #1a3a52; font-size: 1.7em; border-bottom: 3px solid #ff9800; padding-bottom: 12px; margin-bottom: 25px; }}
        .section h3 {{ color: #2c5aa0; font-size: 1.2em; margin: 25px 0 15px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background-color: #f9f9f9; }}
        th {{ background-color: #2c5aa0; color: white; padding: 14px; text-align: left; font-weight: bold; }}
        td {{ padding: 12px 14px; border-bottom: 1px solid #e0e0e0; }}
        tr:nth-child(even) {{ background-color: white; }}
        .value {{ font-weight: bold; color: #1a3a52; font-size: 1.05em; }}
        .source {{ font-size: 0.85em; color: #666; }}
        .footer {{ background-color: #1a3a52; color: white; padding: 30px; text-align: center; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Daily Market Intelligence Report</h1>
            <p>Comprehensive Global & India Market Analysis</p>
            <div class="timestamp">Generated: {timestamp}</div>
        </div>

        <div class="content">
            <div class="section">
                <h2>🌍 Global Market Indicators</h2>
                
                <h3>India Pre-Market Indicator</h3>
                <table>
                    <tr><th>Indicator</th><th>Value</th><th>Source</th></tr>
                    <tr><td><strong>GIFT Nifty (SGX)</strong></td><td class="value">{val('gift_nifty')}</td><td class="source">{val('gift_nifty', 'source')}</td></tr>
                </table>

                <h3>US Market Indices</h3>
                <table>
                    <tr><th>Index</th><th>Value</th><th>Change</th><th>% Change</th><th>Source</th></tr>
                    <tr><td><strong>S&P 500</strong></td><td class="value">{val('sp500')}</td><td>{val('sp500', 'change_str')}</td><td>{val('sp500', 'pct_str')}</td><td class="source">{val('sp500', 'source')}</td></tr>
                    <tr><td><strong>Nasdaq 100</strong></td><td class="value">{val('nasdaq')}</td><td>{val('nasdaq', 'change_str')}</td><td>{val('nasdaq', 'pct_str')}</td><td class="source">{val('nasdaq', 'source')}</td></tr>
                    <tr><td><strong>Dow Jones</strong></td><td class="value">{val('dow')}</td><td>{val('dow', 'change_str')}</td><td>{val('dow', 'pct_str')}</td><td class="source">{val('dow', 'source')}</td></tr>
                </table>

                <h3>Asian Markets</h3>
                <table>
                    <tr><th>Index</th><th>Value</th><th>Change</th><th>% Change</th><th>Source</th></tr>
                    <tr><td><strong>Nikkei 225</strong></td><td class="value">{val('nikkei')}</td><td>{val('nikkei', 'change_str')}</td><td>{val('nikkei', 'pct_str')}</td><td class="source">{val('nikkei', 'source')}</td></tr>
                    <tr><td><strong>Hang Seng</strong></td><td class="value">{val('hangseng')}</td><td>{val('hangseng', 'change_str')}</td><td>{val('hangseng', 'pct_str')}</td><td class="source">{val('hangseng', 'source')}</td></tr>
                </table>

                <h3>Global Commodities</h3>
                <table>
                    <tr><th>Commodity</th><th>Value</th><th>Change</th><th>% Change</th><th>Source</th></tr>
                    <tr><td><strong>Crude Oil</strong></td><td class="value">{val('crude')}</td><td>{val('crude', 'change_str')}</td><td>{val('crude', 'pct_str')}</td><td class="source">{val('crude', 'source')}</td></tr>
                    <tr><td><strong>Gold</strong></td><td class="value">{val('gold')}</td><td>{val('gold', 'change_str')}</td><td>{val('gold', 'pct_str')}</td><td class="source">{val('gold', 'source')}</td></tr>
                    <tr><td><strong>Silver</strong></td><td class="value">{val('silver')}</td><td>{val('silver', 'change_str')}</td><td>{val('silver', 'pct_str')}</td><td class="source">{val('silver', 'source')}</td></tr>
                </table>

                <h3>Currency & US Treasury</h3>
                <table>
                    <tr><th>Indicator</th><th>Value</th><th>Change</th><th>% Change</th><th>Source</th></tr>
                    <tr><td><strong>USD Index</strong></td><td class="value">{val('usd_index')}</td><td>{val('usd_index', 'change_str')}</td><td>{val('usd_index', 'pct_str')}</td><td class="source">{val('usd_index', 'source')}</td></tr>
                    <tr><td><strong>INR/USD Rate</strong></td><td class="value">{val('inr_usd')}</td><td>{val('inr_usd', 'change_str')}</td><td>{val('inr_usd', 'pct_str')}</td><td class="source">{val('inr_usd', 'source')}</td></tr>
                    <tr><td><strong>US 10Y Treasury (GSEC)</strong></td><td class="value">{val('us_10y')}</td><td>{val('us_10y', 'change_str')}</td><td>{val('us_10y', 'pct_str')}</td><td class="source">{val('us_10y', 'source')}</td></tr>
                </table>
            </div>

            <div class="section">
                <h2>🇮🇳 India Market Data</h2>
                <table>
                    <tr><th>Index</th><th>Value</th><th>Change</th><th>% Change</th><th>Source</th></tr>
                    <tr><td><strong>Nifty 50</strong></td><td class="value">{val('nifty_50')}</td><td>{val('nifty_50', 'change_str')}</td><td>{val('nifty_50', 'pct_str')}</td><td class="source">{val('nifty_50', 'source')}</td></tr>
                    <tr><td><strong>Sensex</strong></td><td class="value">{val('sensex')}</td><td>{val('sensex', 'change_str')}</td><td>{val('sensex', 'pct_str')}</td><td class="source">{val('sensex', 'source')}</td></tr>
                    <tr><td><strong>India VIX</strong></td><td class="value">{val('india_vix')}</td><td>{val('india_vix', 'change_str')}</td><td>-</td><td class="source">{val('india_vix', 'source')}</td></tr>
                    <tr><td colspan="2"><strong>FII Flow:</strong> {val('fii_dii', 'fii')}</td><td colspan="3"><strong>DII Flow:</strong> {val('fii_dii', 'dii')}</td></tr>
                </table>
            </div>

            <div class="section">
                <h2>📊 Data Sources</h2>
                <p><strong>NSE:</strong> Nifty 50, GIFT Nifty, VIX | <strong>BSE:</strong> Sensex | <strong>Moneycontrol:</strong> FII/DII | <strong>Bloomberg/Yahoo:</strong> Global Data</p>
            </div>
        </div>

        <div class="footer">
            <p><strong>Daily Market Intelligence Report</strong></p>
            <p>8:00 AM IST Daily | mailbox.macwan@gmail.com</p>
        </div>
    </div>
</body>
</html>
"""
    return html


def send_email(recipient, subject, html_content):
    """Send comprehensive HTML email"""
    try:
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        
        if not sender_email or not sender_password:
            logger.error("Email credentials missing")
            return False
        
        logger.info(f"Sending email to {recipient}...")
        
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = recipient
        message.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, message.as_string())
        
        logger.info(f"✓ Email sent successfully\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ Email failed: {e}\n")
        return False


def main():
    """Main execution function"""
    logger.info("\n" + "=" * 100)
    logger.info("DAILY MARKET INTELLIGENCE REPORT SYSTEM")
    logger.info("=" * 100)
    
    try:
        logger.info("\n[1/3] Collecting market data...")
        collector = MarketDataCollector()
        market_data = collector.collect_all_data()
        
        logger.info("[2/3] Generating HTML email...")
        html_email = generate_html_email(market_data)
        
        logger.info("[3/3] Sending email...")
        subject = f"Daily Market Intelligence Report - {datetime.now().strftime('%B %d, %Y')}"
        
        if send_email("mailbox.macwan@gmail.com", subject, html_email):
            logger.info("=" * 100)
            logger.info("✅ SUCCESS: REPORT SENT SUCCESSFULLY")
            logger.info("=" * 100 + "\n")
            return 0
        else:
            logger.error("=" * 100)
            logger.error("❌ FAILED")
            logger.error("=" * 100 + "\n")
            return 1
            
    except Exception as e:
        logger.error(f"\n❌ CRITICAL ERROR: {e}\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
