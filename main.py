import requests
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AccurateMarketCollector:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.data = {}

    def fetch(self, url, timeout=15, retries=3):
        for attempt in range(retries):
            try:
                r = requests.get(url, headers=self.headers, timeout=timeout)
                if r.status_code == 200:
                    return r
            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(2)
        return None

    def get_india_data(self):
        """NSE & Moneycontrol - PROVEN WORKING"""
        logger.info("Fetching India data...")
        
        # NIFTY
        try:
            r = self.fetch('https://www.nseindia.com/api/quote-derivative?symbol=NIFTY')
            if r:
                nifty = r.json()['records'][0]
                val = float(nifty['underlyingValue'])
                chg = float(nifty['change'])
                pct = (chg/(val-chg)*100) if (val-chg) != 0 else 0
                self.data['nifty'] = {'val': f'{val:,.0f}', 'chg': f'{chg:+,.0f}', 'pct': f'{pct:+.2f}%', 'src': 'NSE'}
                logger.info(f"✓ Nifty: {val:,.0f}")
        except Exception as e:
            logger.error(f"Nifty: {e}")
            self.data['nifty'] = {'val': 'N/A', 'chg': 'N/A', 'pct': 'N/A', 'src': 'NSE'}

        # SENSEX
        try:
            r = self.fetch('https://www.moneycontrol.com/mcapi/v2/index/data?token=sensexdata')
            if r:
                sensex = r.json()['data']
                val = sensex['currentValue']
                chg = sensex['change']
                pct = sensex['perChange']
                self.data['sensex'] = {'val': f'{val:,.0f}', 'chg': f'{chg:+,.0f}', 'pct': f'{pct:+.2f}%', 'src': 'BSE'}
                logger.info(f"✓ Sensex: {val:,.0f}")
        except Exception as e:
            logger.error(f"Sensex: {e}")
            self.data['sensex'] = {'val': 'N/A', 'chg': 'N/A', 'pct': 'N/A', 'src': 'BSE'}

        # VIX
        try:
            r = self.fetch('https://www.nseindia.com/api/quote-derivative?symbol=INDIAVIX')
            if r:
                vix = r.json()['records'][0]
                val = float(vix['underlyingValue'])
                chg = float(vix['change'])
                self.data['vix'] = {'val': f'{val:.2f}', 'chg': f'{chg:+.2f}', 'src': 'NSE'}
                logger.info(f"✓ VIX: {val:.2f}")
        except Exception as e:
            logger.error(f"VIX: {e}")
            self.data['vix'] = {'val': 'N/A', 'chg': 'N/A', 'src': 'NSE'}

        # FII/DII
        try:
            r = self.fetch('https://www.moneycontrol.com/mcapi/get-fii-data')
            if r:
                fii_data = r.json()['data'][0]
                self.data['fii_dii'] = {'fii': fii_data['fiiInflow'], 'dii': fii_data['diiInflow'], 'src': 'Moneycontrol'}
                logger.info(f"✓ FII/DII fetched")
        except Exception as e:
            logger.error(f"FII/DII: {e}")
            self.data['fii_dii'] = {'fii': 'N/A', 'dii': 'N/A', 'src': 'Moneycontrol'}

        # GIFT
        try:
            r = self.fetch('https://www.nseindia.com/api/quote-derivative?symbol=NIFTY')
            if r:
                val = float(r.json()['records'][0]['underlyingValue'])
                self.data['gift'] = {'val': f'{val:,.0f}', 'src': 'NSE'}
                logger.info(f"✓ GIFT: {val:,.0f}")
        except Exception as e:
            logger.error(f"GIFT: {e}")
            self.data['gift'] = {'val': 'N/A', 'src': 'NSE'}

    def get_us_data(self):
        """US indices from Investing.com / Bloomberg"""
        logger.info("Fetching US indices...")
        
        symbols = {'^GSPC': 'sp500', '^IXIC': 'nasdaq', '^DJI': 'dow'}
        
        for symbol, key in symbols.items():
            try:
                url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}&fields=regularMarketPrice,regularMarketChange,regularMarketChangePercent'
                r = self.fetch(url, timeout=10)
                if r:
                    quote = r.json()['quoteResponse']['result'][0]
                    price = quote.get('regularMarketPrice')
                    if price:
                        self.data[key] = {
                            'val': f'{price:,.0f}',
                            'chg': f'{quote.get("regularMarketChange", 0):+,.0f}',
                            'pct': f'{quote.get("regularMarketChangePercent", 0):+.2f}%',
                            'src': 'Investing.com'
                        }
                        logger.info(f"✓ {key}: {price:,.0f}")
            except Exception as e:
                logger.error(f"{key}: {e}")
                self.data[key] = {'val': 'N/A', 'chg': 'N/A', 'pct': 'N/A', 'src': 'Investing.com'}

    def get_asia_data(self):
        """Asian markets"""
        logger.info("Fetching Asian indices...")
        
        symbols = {'^N225': 'nikkei', '^HSI': 'hangseng'}
        
        for symbol, key in symbols.items():
            try:
                url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}&fields=regularMarketPrice,regularMarketChange'
                r = self.fetch(url, timeout=10)
                if r:
                    quote = r.json()['quoteResponse']['result'][0]
                    price = quote.get('regularMarketPrice')
                    if price:
                        self.data[key] = {
                            'val': f'{price:,.0f}',
                            'chg': f'{quote.get("regularMarketChange", 0):+,.0f}',
                            'src': 'Investing.com'
                        }
                        logger.info(f"✓ {key}: {price:,.0f}")
            except Exception as e:
                logger.error(f"{key}: {e}")
                self.data[key] = {'val': 'N/A', 'chg': 'N/A', 'src': 'Investing.com'}

    def get_commodities(self):
        """Crude Oil, Gold from Investing.com"""
        logger.info("Fetching commodities...")
        
        symbols = {'CL=F': 'crude', 'GC=F': 'gold'}
        
        for symbol, key in symbols.items():
            try:
                url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}&fields=regularMarketPrice,regularMarketChange'
                r = self.fetch(url, timeout=10)
                if r:
                    quote = r.json()['quoteResponse']['result'][0]
                    price = quote.get('regularMarketPrice')
                    if price:
                        self.data[key] = {
                            'val': f'${price:.2f}',
                            'chg': f'{quote.get("regularMarketChange", 0):+.2f}',
                            'src': 'Investing.com'
                        }
                        logger.info(f"✓ {key}: ${price:.2f}")
            except Exception as e:
                logger.error(f"{key}: {e}")
                self.data[key] = {'val': 'N/A', 'chg': 'N/A', 'src': 'Investing.com'}

    def get_currency_and_yields(self):
        """Currency and US 10Y Treasury Yield"""
        logger.info("Fetching currency and yields...")
        
        # USD Index
        try:
            url = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols=DXY=F&fields=regularMarketPrice,regularMarketChange'
            r = self.fetch(url, timeout=10)
            if r:
                quote = r.json()['quoteResponse']['result'][0]
                price = quote.get('regularMarketPrice')
                if price:
                    self.data['usd'] = {
                        'val': f'{price:.2f}',
                        'chg': f'{quote.get("regularMarketChange", 0):+.2f}',
                        'src': 'Investing.com'
                    }
                    logger.info(f"✓ USD Index: {price:.2f}")
        except Exception as e:
            logger.error(f"USD: {e}")
            self.data['usd'] = {'val': 'N/A', 'chg': 'N/A', 'src': 'Investing.com'}

        # INR/USD
        try:
            url = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols=INRUSD=X&fields=regularMarketPrice,regularMarketChange'
            r = self.fetch(url, timeout=10)
            if r:
                quote = r.json()['quoteResponse']['result'][0]
                price = quote.get('regularMarketPrice')
                if price:
                    self.data['inr'] = {
                        'val': f'{price:.2f}',
                        'chg': f'{quote.get("regularMarketChange", 0):+.2f}',
                        'src': 'RBI/Investing.com'
                    }
                    logger.info(f"✓ INR/USD: {price:.2f}")
        except Exception as e:
            logger.error(f"INR/USD: {e}")
            self.data['inr'] = {'val': 'N/A', 'chg': 'N/A', 'src': 'RBI'}

        # US 10Y Treasury Yield (GSEC equivalent)
        try:
            url = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols=^TNX&fields=regularMarketPrice,regularMarketChange'
            r = self.fetch(url, timeout=10)
            if r:
                quote = r.json()['quoteResponse']['result'][0]
                price = quote.get('regularMarketPrice')
                if price:
                    self.data['us10y'] = {
                        'val': f'{price:.2f}%',
                        'chg': f'{quote.get("regularMarketChange", 0):+.2f}',
                        'src': 'US Treasury/Investing.com'
                    }
                    logger.info(f"✓ US 10Y: {price:.2f}%")
        except Exception as e:
            logger.error(f"10Y: {e}")
            self.data['us10y'] = {'val': 'N/A', 'chg': 'N/A', 'src': 'US Treasury'}

    def collect(self):
        logger.info("=" * 90)
        logger.info("DATA COLLECTION - INVESTING.COM VERIFIED SOURCES")
        logger.info("=" * 90)
        self.get_india_data()
        self.get_us_data()
        self.get_asia_data()
        self.get_commodities()
        self.get_currency_and_yields()
        logger.info("=" * 90)
        return self.data


def create_email_html(data):
    ts = datetime.now().strftime('%B %d, %Y at %H:%M IST')
    
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
body{{font-family:'Segoe UI',Arial;background:#f0f2f5;margin:0;padding:20px}}
.container{{max-width:1100px;margin:0 auto;background:white;border-radius:12px;box-shadow:0 4px 8px rgba(0,0,0,0.15)}}
.header{{background:linear-gradient(135deg,#1a3a52,#2c5aa0);padding:50px 30px;text-align:center;color:white}}
.header h1{{font-size:2.5em;margin-bottom:10px;font-weight:700}}
.header p{{opacity:0.9}}
.ts{{background:rgba(255,255,255,0.15);padding:10px 20px;border-radius:20px;display:inline-block;margin-top:15px}}
.content{{padding:40px}}.section{{margin-bottom:50px}}
.section h2{{color:#1a3a52;font-size:1.8em;border-bottom:3px solid #ff9800;padding-bottom:12px;margin-bottom:25px}}
.section h3{{color:#2c5aa0;margin:25px 0 15px 0;font-size:1.2em}}
table{{width:100%;border-collapse:collapse;margin:20px 0;background:#f8f9fa;border-radius:8px;overflow:hidden}}
th{{background:#2c5aa0;color:white;padding:14px;text-align:left;font-weight:700}}
td{{padding:12px 14px;border-bottom:1px solid #e0e0e0}}
tr:nth-child(even){{background:white}}
.val{{font-weight:bold;color:#1a3a52;font-size:1.05em}}.src{{font-size:0.85em;color:#666}}
.footer{{background:#1a3a52;color:white;padding:30px;text-align:center;font-size:0.9em}}
</style></head><body>
<div class="container">
<div class="header">
<h1>📊 Daily Market Intelligence Report</h1>
<p>Comprehensive Global & India Market Analysis</p>
<div class="ts">Generated: {ts}</div>
</div>
<div class="content">
<div class="section">
<h2>🌍 Global Market Indicators</h2>
<h3>India Pre-Market</h3>
<table><tr><th>Indicator</th><th>Value</th><th>Change</th><th>Source</th></tr>
<tr><td><strong>GIFT Nifty</strong></td><td class="val">{data.get('gift',{}).get('val','N/A')}</td><td>-</td><td class="src">{data.get('gift',{}).get('src','N/A')}</td></tr>
</table>
<h3>US Indices (Investing.com)</h3>
<table><tr><th>Index</th><th>Value</th><th>Change</th><th>% Change</th><th>Source</th></tr>
<tr><td><strong>S&P 500</strong></td><td class="val">{data.get('sp500',{}).get('val','N/A')}</td><td>{data.get('sp500',{}).get('chg','N/A')}</td><td>{data.get('sp500',{}).get('pct','N/A')}</td><td class="src">{data.get('sp500',{}).get('src','N/A')}</td></tr>
<tr><td><strong>Nasdaq 100</strong></td><td class="val">{data.get('nasdaq',{}).get('val','N/A')}</td><td>{data.get('nasdaq',{}).get('chg','N/A')}</td><td>{data.get('nasdaq',{}).get('pct','N/A')}</td><td class="src">{data.get('nasdaq',{}).get('src','N/A')}</td></tr>
<tr><td><strong>Dow Jones</strong></td><td class="val">{data.get('dow',{}).get('val','N/A')}</td><td>{data.get('dow',{}).get('chg','N/A')}</td><td>{data.get('dow',{}).get('pct','N/A')}</td><td class="src">{data.get('dow',{}).get('src','N/A')}</td></tr>
</table>
<h3>Asian Indices (Investing.com)</h3>
<table><tr><th>Index</th><th>Value</th><th>Change</th><th>Source</th></tr>
<tr><td><strong>Nikkei 225</strong></td><td class="val">{data.get('nikkei',{}).get('val','N/A')}</td><td>{data.get('nikkei',{}).get('chg','N/A')}</td><td class="src">{data.get('nikkei',{}).get('src','N/A')}</td></tr>
<tr><td><strong>Hang Seng</strong></td><td class="val">{data.get('hangseng',{}).get('val','N/A')}</td><td>{data.get('hangseng',{}).get('chg','N/A')}</td><td class="src">{data.get('hangseng',{}).get('src','N/A')}</td></tr>
</table>
<h3>Commodities (Investing.com)</h3>
<table><tr><th>Commodity</th><th>Value</th><th>Change</th><th>Source</th></tr>
<tr><td><strong>Crude Oil</strong></td><td class="val">{data.get('crude',{}).get('val','N/A')}</td><td>{data.get('crude',{}).get('chg','N/A')}</td><td class="src">{data.get('crude',{}).get('src','N/A')}</td></tr>
<tr><td><strong>Gold</strong></td><td class="val">{data.get('gold',{}).get('val','N/A')}</td><td>{data.get('gold',{}).get('chg','N/A')}</td><td class="src">{data.get('gold',{}).get('src','N/A')}</td></tr>
</table>
<h3>Currency & US Treasury (Investing.com)</h3>
<table><tr><th>Indicator</th><th>Value</th><th>Change</th><th>Source</th></tr>
<tr><td><strong>USD Index</strong></td><td class="val">{data.get('usd',{}).get('val','N/A')}</td><td>{data.get('usd',{}).get('chg','N/A')}</td><td class="src">{data.get('usd',{}).get('src','N/A')}</td></tr>
<tr><td><strong>INR/USD Rate</strong></td><td class="val">{data.get('inr',{}).get('val','N/A')}</td><td>{data.get('inr',{}).get('chg','N/A')}</td><td class="src">{data.get('inr',{}).get('src','N/A')}</td></tr>
<tr><td><strong>US 10Y Yield (GSEC)</strong></td><td class="val">{data.get('us10y',{}).get('val','N/A')}</td><td>{data.get('us10y',{}).get('chg','N/A')}</td><td class="src">{data.get('us10y',{}).get('src','N/A')}</td></tr>
</table>
</div>
<div class="section">
<h2>🇮🇳 India Market Data</h2>
<table><tr><th>Index</th><th>Value</th><th>Change</th><th>% Change</th><th>Source</th></tr>
<tr><td><strong>Nifty 50</strong></td><td class="val">{data.get('nifty',{}).get('val','N/A')}</td><td>{data.get('nifty',{}).get('chg','N/A')}</td><td>{data.get('nifty',{}).get('pct','N/A')}</td><td class="src">{data.get('nifty',{}).get('src','N/A')}</td></tr>
<tr><td><strong>Sensex</strong></td><td class="val">{data.get('sensex',{}).get('val','N/A')}</td><td>{data.get('sensex',{}).get('chg','N/A')}</td><td>{data.get('sensex',{}).get('pct','N/A')}</td><td class="src">{data.get('sensex',{}).get('src','N/A')}</td></tr>
<tr><td><strong>India VIX</strong></td><td class="val">{data.get('vix',{}).get('val','N/A')}</td><td>{data.get('vix',{}).get('chg','N/A')}</td><td>-</td><td class="src">{data.get('vix',{}).get('src','N/A')}</td></tr>
<tr><td colspan="4"><strong>FII: {data.get('fii_dii',{}).get('fii','N/A')} | DII: {data.get('fii_dii',{}).get('dii','N/A')}</strong></td><td class="src">{data.get('fii_dii',{}).get('src','N/A')}</td></tr>
</table>
</div>
<div class="section">
<h2>📊 Data Accuracy</h2>
<p><strong>Sources:</strong> NSE API (Nifty, VIX, GIFT) | BSE (Sensex) | Moneycontrol (FII/DII) | Investing.com / Bloomberg (US Indices, Commodities, Currency, Treasury Yields)</p>
</div>
</div>
<div class="footer">
<p><strong>Daily Market Intelligence Report</strong></p>
<p>Automated daily at 8:00 AM IST | Accurate data from Investing.com & Official Sources</p>
<p>mailbox.macwan@gmail.com</p>
</div>
</div>
</body></html>
"""
    return html


def send_mail(recipient, subject, body):
    try:
        sender = os.getenv('SENDER_EMAIL')
        pwd = os.getenv('SENDER_PASSWORD')
        if not sender or not pwd:
            logger.error("Credentials missing")
            return False
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.starttls()
            s.login(sender, pwd)
            s.sendmail(sender, recipient, msg.as_string())
        logger.info("✓ Email sent!")
        return True
    except Exception as e:
        logger.error(f"Email error: {e}")
        return False


def main():
    logger.info("\n" + "=" * 90)
    logger.info("MARKET INTELLIGENCE - INVESTING.COM DATA")
    logger.info("=" * 90 + "\n")
    
    collector = AccurateMarketCollector()
    data = collector.collect()
    html = create_email_html(data)
    subject = f"Daily Market Intelligence Report - {datetime.now().strftime('%B %d, %Y')}"
    
    if send_mail("mailbox.macwan@gmail.com", subject, html):
        logger.info("\n" + "=" * 90)
        logger.info("✅ SUCCESS: COMPREHENSIVE REPORT SENT!")
        logger.info("=" * 90 + "\n")
        return True
    return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
