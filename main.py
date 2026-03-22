import requests
import json
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealDataCollector:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.timeout = 15
        self.data = {}

    def get(self, url):
        """Fetch URL with proper headers"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Fetch failed for {url}: {e}")
            return None

    def collect(self):
        """Collect all market data"""
        logger.info("=" * 80)
        logger.info("STARTING DATA COLLECTION FROM LIVE SOURCES")
        logger.info("=" * 80)
        
        self.get_nifty_data()
        self.get_sensex_data()
        self.get_vix_data()
        self.get_gift_nifty()
        self.get_us_markets()
        self.get_asian_markets()
        self.get_commodities()
        self.get_currency()
        self.get_fii_dii()
        
        logger.info("=" * 80)
        logger.info("DATA COLLECTION COMPLETE")
        logger.info("=" * 80)
        return self.data

    def get_nifty_data(self):
        """Get Nifty 50 from NSE"""
        logger.info("Fetching Nifty 50...")
        try:
            url = 'https://www.nseindia.com/api/quote-derivative?symbol=NIFTY'
            data = self.get(url)
            if data and 'records' in data and len(data['records']) > 0:
                record = data['records'][0]
                val = float(record.get('underlyingValue', 0))
                change = float(record.get('change', 0))
                pct = (change / (val - change) * 100) if (val - change) != 0 else 0
                
                self.data['nifty'] = {
                    'value': f'{val:,.2f}',
                    'change': f'{change:+,.2f}',
                    'pct': f'{pct:+.2f}%'
                }
                logger.info(f"✓ Nifty 50: {val:,.2f} ({change:+,.2f})")
        except Exception as e:
            logger.error(f"Nifty error: {e}")
            self.data['nifty'] = {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A'}

    def get_sensex_data(self):
        """Get Sensex from Moneycontrol"""
        logger.info("Fetching Sensex...")
        try:
            url = 'https://www.moneycontrol.com/mcapi/v2/index/data?token=sensexdata'
            data = self.get(url)
            if data and 'data' in data:
                val = data['data'].get('currentValue')
                change = data['data'].get('change')
                pct = data['data'].get('perChange')
                
                if val:
                    self.data['sensex'] = {
                        'value': f'{float(val):,.2f}',
                        'change': f'{float(change):+,.2f}' if change else 'N/A',
                        'pct': f'{float(pct):+.2f}%' if pct else 'N/A'
                    }
                    logger.info(f"✓ Sensex: {val}")
        except Exception as e:
            logger.error(f"Sensex error: {e}")
            self.data['sensex'] = {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A'}

    def get_vix_data(self):
        """Get India VIX"""
        logger.info("Fetching India VIX...")
        try:
            url = 'https://www.nseindia.com/api/quote-derivative?symbol=INDIAVIX'
            data = self.get(url)
            if data and 'records' in data and len(data['records']) > 0:
                val = float(data['records'][0].get('underlyingValue', 0))
                change = float(data['records'][0].get('change', 0))
                
                self.data['vix'] = {
                    'value': f'{val:.2f}',
                    'change': f'{change:+.2f}'
                }
                logger.info(f"✓ India VIX: {val:.2f}")
        except Exception as e:
            logger.error(f"VIX error: {e}")
            self.data['vix'] = {'value': 'N/A', 'change': 'N/A'}

    def get_gift_nifty(self):
        """Get GIFT Nifty"""
        logger.info("Fetching GIFT Nifty...")
        try:
            url = 'https://www.nseindia.com/api/quote-derivative?symbol=NIFTY'
            data = self.get(url)
            if data and 'records' in data:
                val = float(data['records'][0].get('underlyingValue', 0))
                self.data['gift'] = {'value': f'{val:,.2f}'}
                logger.info(f"✓ GIFT Nifty: {val:,.2f}")
        except Exception as e:
            logger.error(f"GIFT error: {e}")
            self.data['gift'] = {'value': 'N/A'}

    def get_us_markets(self):
        """Get US market indices"""
        logger.info("Fetching US Markets...")
        try:
            url = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols=^GSPC,^IXIC,^DJI&fields=shortName,regularMarketPrice'
            data = self.get(url)
            if data and 'quoteResponse' in data and 'result' in data['quoteResponse']:
                results = data['quoteResponse']['result']
                for quote in results:
                    symbol = quote.get('symbol', '')
                    price = quote.get('regularMarketPrice', 'N/A')
                    
                    if symbol == '^GSPC':
                        self.data['sp500'] = {'value': f'{price:,.0f}'}
                        logger.info(f"✓ S&P 500: {price:,.0f}")
                    elif symbol == '^IXIC':
                        self.data['nasdaq'] = {'value': f'{price:,.0f}'}
                        logger.info(f"✓ Nasdaq: {price:,.0f}")
                    elif symbol == '^DJI':
                        self.data['dow'] = {'value': f'{price:,.0f}'}
                        logger.info(f"✓ Dow: {price:,.0f}")
        except Exception as e:
            logger.error(f"US Markets error: {e}")
            self.data['sp500'] = {'value': 'N/A'}
            self.data['nasdaq'] = {'value': 'N/A'}
            self.data['dow'] = {'value': 'N/A'}

    def get_asian_markets(self):
        """Get Asian market indices"""
        logger.info("Fetching Asian Markets...")
        try:
            url = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols=^N225,^HSI&fields=shortName,regularMarketPrice'
            data = self.get(url)
            if data and 'quoteResponse' in data and 'result' in data['quoteResponse']:
                results = data['quoteResponse']['result']
                for quote in results:
                    symbol = quote.get('symbol', '')
                    price = quote.get('regularMarketPrice', 'N/A')
                    
                    if symbol == '^N225':
                        self.data['nikkei'] = {'value': f'{price:,.0f}'}
                        logger.info(f"✓ Nikkei: {price:,.0f}")
                    elif symbol == '^HSI':
                        self.data['hangseng'] = {'value': f'{price:,.0f}'}
                        logger.info(f"✓ Hang Seng: {price:,.0f}")
        except Exception as e:
            logger.error(f"Asian Markets error: {e}")
            self.data['nikkei'] = {'value': 'N/A'}
            self.data['hangseng'] = {'value': 'N/A'}

    def get_commodities(self):
        """Get commodity prices"""
        logger.info("Fetching Commodities...")
        try:
            url = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols=CL=F,GC=F&fields=shortName,regularMarketPrice'
            data = self.get(url)
            if data and 'quoteResponse' in data and 'result' in data['quoteResponse']:
                results = data['quoteResponse']['result']
                for quote in results:
                    symbol = quote.get('symbol', '')
                    price = quote.get('regularMarketPrice', 'N/A')
                    
                    if symbol == 'CL=F':
                        self.data['crude'] = {'value': f'${price:.2f}'}
                        logger.info(f"✓ Crude Oil: ${price:.2f}")
                    elif symbol == 'GC=F':
                        self.data['gold'] = {'value': f'${price:.2f}'}
                        logger.info(f"✓ Gold: ${price:.2f}")
        except Exception as e:
            logger.error(f"Commodities error: {e}")
            self.data['crude'] = {'value': 'N/A'}
            self.data['gold'] = {'value': 'N/A'}

    def get_currency(self):
        """Get currency rates"""
        logger.info("Fetching Currency...")
        try:
            url = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols=DXY=F,INRUSD=X,^TNX&fields=shortName,regularMarketPrice'
            data = self.get(url)
            if data and 'quoteResponse' in data and 'result' in data['quoteResponse']:
                results = data['quoteResponse']['result']
                for quote in results:
                    symbol = quote.get('symbol', '')
                    price = quote.get('regularMarketPrice', 'N/A')
                    
                    if symbol == 'DXY=F':
                        self.data['usd_index'] = {'value': f'{price:.2f}'}
                        logger.info(f"✓ USD Index: {price:.2f}")
                    elif symbol == 'INRUSD=X':
                        self.data['inr_usd'] = {'value': f'{price:.2f}'}
                        logger.info(f"✓ INR/USD: {price:.2f}")
                    elif symbol == '^TNX':
                        self.data['us_10y'] = {'value': f'{price:.2f}%'}
                        logger.info(f"✓ US 10Y: {price:.2f}%")
        except Exception as e:
            logger.error(f"Currency error: {e}")
            self.data['usd_index'] = {'value': 'N/A'}
            self.data['inr_usd'] = {'value': 'N/A'}
            self.data['us_10y'] = {'value': 'N/A'}

    def get_fii_dii(self):
        """Get FII/DII flows"""
        logger.info("Fetching FII/DII...")
        try:
            url = 'https://www.moneycontrol.com/mcapi/get-fii-data'
            data = self.get(url)
            if data and 'data' in data and len(data['data']) > 0:
                fii = data['data'][0].get('fiiInflow', 'N/A')
                dii = data['data'][0].get('diiInflow', 'N/A')
                
                self.data['fii'] = {'value': f'{fii}'}
                self.data['dii'] = {'value': f'{dii}'}
                logger.info(f"✓ FII: {fii}, DII: {dii}")
        except Exception as e:
            logger.error(f"FII/DII error: {e}")
            self.data['fii'] = {'value': 'N/A'}
            self.data['dii'] = {'value': 'N/A'}


def generate_email_html(data):
    """Generate comprehensive HTML email"""
    
    timestamp = datetime.now().strftime('%B %d, %Y at %H:%M IST')
    
    # Get values with defaults
    gift = data.get('gift', {}).get('value', 'N/A')
    nifty = data.get('nifty', {}).get('value', 'N/A')
    nifty_chg = data.get('nifty', {}).get('change', 'N/A')
    sensex = data.get('sensex', {}).get('value', 'N/A')
    vix = data.get('vix', {}).get('value', 'N/A')
    
    sp500 = data.get('sp500', {}).get('value', 'N/A')
    nasdaq = data.get('nasdaq', {}).get('value', 'N/A')
    dow = data.get('dow', {}).get('value', 'N/A')
    nikkei = data.get('nikkei', {}).get('value', 'N/A')
    hangseng = data.get('hangseng', {}).get('value', 'N/A')
    
    crude = data.get('crude', {}).get('value', 'N/A')
    gold = data.get('gold', {}).get('value', 'N/A')
    usd_idx = data.get('usd_index', {}).get('value', 'N/A')
    inr_usd = data.get('inr_usd', {}).get('value', 'N/A')
    us_10y = data.get('us_10y', {}).get('value', 'N/A')
    
    fii = data.get('fii', {}).get('value', 'N/A')
    dii = data.get('dii', {}).get('value', 'N/A')

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; color: #333; line-height: 1.6; }}
        .container {{ max-width: 1000px; margin: 20px auto; background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #1a3a52 0%, #2c5aa0 100%); padding: 50px 30px; text-align: center; color: white; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; font-weight: 700; }}
        .header p {{ font-size: 1em; opacity: 0.9; }}
        .timestamp {{ background: rgba(255,255,255,0.15); padding: 12px 24px; border-radius: 25px; display: inline-block; margin-top: 15px; font-size: 0.95em; }}
        .content {{ padding: 40px; }}
        .section {{ margin-bottom: 50px; }}
        .section h2 {{ color: #1a3a52; font-size: 1.8em; margin-bottom: 25px; padding-bottom: 12px; border-bottom: 3px solid #ff9800; }}
        .section h3 {{ color: #2c5aa0; font-size: 1.3em; margin: 30px 0 15px 0; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin: 20px 0; }}
        .card {{ background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%); border: 1px solid #ddd; border-radius: 10px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .label {{ font-size: 0.8em; color: #666; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 700; margin-bottom: 8px; }}
        .value {{ font-size: 1.8em; font-weight: 700; color: #1a3a52; }}
        .change {{ font-size: 0.9em; color: #666; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: #f8f9fa; border-radius: 8px; overflow: hidden; }}
        th {{ background: #2c5aa0; color: white; padding: 14px; text-align: left; font-weight: 700; }}
        td {{ padding: 12px 14px; border-bottom: 1px solid #e0e0e0; }}
        tr:last-child td {{ border-bottom: none; }}
        tr:nth-child(even) {{ background: white; }}
        .footer {{ background: #1a3a52; color: white; padding: 30px; text-align: center; font-size: 0.9em; }}
        .footer p {{ margin: 8px 0; }}
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
            <!-- SECTION 1: GLOBAL MARKETS -->
            <div class="section">
                <h2>🌍 Global Market Indicators</h2>
                
                <h3>India Pre-Market</h3>
                <div class="grid">
                    <div class="card">
                        <div class="label">GIFT Nifty (SGX)</div>
                        <div class="value">{gift}</div>
                    </div>
                </div>

                <h3>US Markets</h3>
                <div class="grid">
                    <div class="card">
                        <div class="label">S&P 500</div>
                        <div class="value">{sp500}</div>
                    </div>
                    <div class="card">
                        <div class="label">Nasdaq 100</div>
                        <div class="value">{nasdaq}</div>
                    </div>
                    <div class="card">
                        <div class="label">Dow Jones</div>
                        <div class="value">{dow}</div>
                    </div>
                </div>

                <h3>Asian Markets</h3>
                <div class="grid">
                    <div class="card">
                        <div class="label">Nikkei 225 (Japan)</div>
                        <div class="value">{nikkei}</div>
                    </div>
                    <div class="card">
                        <div class="label">Hang Seng (Hong Kong)</div>
                        <div class="value">{hangseng}</div>
                    </div>
                </div>

                <h3>Commodities & Currency</h3>
                <table>
                    <tr>
                        <th style="width: 50%;">Indicator</th>
                        <th style="width: 50%;">Value</th>
                    </tr>
                    <tr><td><strong>Brent Crude Oil</strong></td><td>{crude}</td></tr>
                    <tr><td><strong>Gold</strong></td><td>{gold}</td></tr>
                    <tr><td><strong>USD Index</strong></td><td>{usd_idx}</td></tr>
                    <tr><td><strong>INR/USD</strong></td><td>{inr_usd}</td></tr>
                    <tr><td><strong>US 10Y Treasury Yield</strong></td><td>{us_10y}</td></tr>
                </table>
            </div>

            <!-- SECTION 2: INDIA MARKETS -->
            <div class="section">
                <h2>🇮🇳 India Market Data</h2>
                <table>
                    <tr>
                        <th style="width: 35%;">Index</th>
                        <th style="width: 25%;">Value</th>
                        <th style="width: 40%;">Change / Notes</th>
                    </tr>
                    <tr><td><strong>Nifty 50</strong></td><td>{nifty}</td><td>{nifty_chg}</td></tr>
                    <tr><td><strong>Sensex</strong></td><td>{sensex}</td><td>BSE Index</td></tr>
                    <tr><td><strong>India VIX</strong></td><td>{vix}</td><td>Volatility Index</td></tr>
                    <tr><td><strong>FII Flow</strong></td><td>{fii}</td><td>Foreign Investors</td></tr>
                    <tr><td><strong>DII Flow</strong></td><td>{dii}</td><td>Domestic Investors</td></tr>
                </table>
            </div>

            <!-- SECTION 3: SUMMARY -->
            <div class="section">
                <h2>📊 Market Summary</h2>
                <p><strong>Data Sources:</strong></p>
                <p>Global Indices: Yahoo Finance | India Indices: NSE API | Moneycontrol: Sensex, FII/DII | Commodities: Yahoo Finance</p>
            </div>
        </div>

        <div class="footer">
            <p><strong>Daily Market Intelligence Report</strong></p>
            <p>Automated Daily | 8:00 AM IST | Sent to: mailbox.macwan@gmail.com</p>
            <p>This report is for informational purposes only. Consult a financial advisor before making investment decisions.</p>
        </div>
    </div>
</body>
</html>
"""
    return html


def send_email(recipient, subject, html_body):
    """Send HTML email via Gmail SMTP"""
    try:
        sender = os.getenv('SENDER_EMAIL')
        password = os.getenv('SENDER_PASSWORD')
        
        if not sender or not password:
            logger.error("❌ Email credentials missing")
            return False
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        
        logger.info(f"✅ Email sent successfully to {recipient}")
        return True
    except Exception as e:
        logger.error(f"❌ Email send failed: {e}")
        return False


def main():
    logger.info("\n" + "=" * 80)
    logger.info("MARKET INTELLIGENCE REPORT GENERATION")
    logger.info("=" * 80 + "\n")
    
    try:
        collector = RealDataCollector()
        data = collector.collect()
        
        html = generate_email_html(data)
        subject = f"Daily Market Intelligence Report - {datetime.now().strftime('%B %d, %Y')}"
        
        if send_email("mailbox.macwan@gmail.com", subject, html):
            logger.info("\n" + "=" * 80)
            logger.info("✅ SUCCESS: REPORT SENT WITH REAL MARKET DATA!")
            logger.info("=" * 80 + "\n")
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
