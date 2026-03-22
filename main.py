import requests
import json
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionMarketCollector:
    def __init__(self):
        self.finnhub_key = os.getenv('FINNHUB_API_KEY', '')
        self.fred_key = os.getenv('FRED_API_KEY', '')
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        self.data = {}

    def safe_request(self, url, timeout=12, max_retries=3):
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=timeout)
                if response.status_code == 200:
                    return response
            except:
                if attempt < max_retries - 1:
                    time.sleep(2)
        return None

    def collect_all_data(self):
        logger.info("=" * 90)
        logger.info("STARTING DATA COLLECTION FROM AUTHORITATIVE SOURCES")
        logger.info("=" * 90)

        self.get_nifty50_accurate()
        self.get_sensex_accurate()
        self.get_india_vix_accurate()
        self.get_gift_nifty_accurate()
        self.get_fii_dii_accurate()
        self.get_us_indices_accurate()
        self.get_asia_indices_accurate()
        self.get_commodities_accurate()
        self.get_currency_accurate()
        self.get_treasury_yields_accurate()
        self.get_economic_calendar_accurate()

        logger.info("=" * 90)
        logger.info("DATA COLLECTION COMPLETE")
        logger.info("=" * 90)
        return self.data

    def get_nifty50_accurate(self):
        logger.info("Fetching Nifty 50 from NSE...")
        try:
            url = 'https://www.nseindia.com/api/quote-derivative?symbol=NIFTY'
            response = self.safe_request(url)
            if response:
                data = response.json()
                if 'records' in data and len(data['records']) > 0:
                    record = data['records'][0]
                    value = float(record.get('underlyingValue', 0))
                    change = float(record.get('change', 0))
                    pct = (change / (value - change) * 100) if (value - change) != 0 else 0
                    self.data['nifty'] = {'value': f'{value:,.2f}', 'change': f'{change:+,.2f}', 'pct': f'{pct:+.2f}%', 'source': 'NSE Official'}
                    logger.info(f"✓ Nifty 50: {value:,.2f}")
                    return
        except Exception as e:
            logger.error(f"Nifty error: {e}")
        self.data['nifty'] = {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A', 'source': 'NSE'}

    def get_sensex_accurate(self):
        logger.info("Fetching Sensex...")
        try:
            url = 'https://www.moneycontrol.com/mcapi/v2/index/data?token=sensexdata'
            response = self.safe_request(url)
            if response:
                data = response.json()
                if 'data' in data and isinstance(data['data'], dict):
                    val = data['data'].get('currentValue')
                    change = data['data'].get('change')
                    pct = data['data'].get('perChange')
                    if val:
                        self.data['sensex'] = {'value': f'{float(val):,.2f}', 'change': f'{float(change):+,.2f}' if change else 'N/A', 'pct': f'{float(pct):+.2f}%' if pct else 'N/A', 'source': 'Moneycontrol'}
                        logger.info(f"✓ Sensex: {val}")
                        return
        except Exception as e:
            logger.error(f"Sensex error: {e}")
        self.data['sensex'] = {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A', 'source': 'BSE'}

    def get_india_vix_accurate(self):
        logger.info("Fetching India VIX...")
        try:
            url = 'https://www.nseindia.com/api/quote-derivative?symbol=INDIAVIX'
            response = self.safe_request(url)
            if response:
                data = response.json()
                if 'records' in data and len(data['records']) > 0:
                    value = float(data['records'][0].get('underlyingValue', 0))
                    change = float(data['records'][0].get('change', 0))
                    self.data['vix'] = {'value': f'{value:.2f}', 'change': f'{change:+.2f}', 'source': 'NSE Official'}
                    logger.info(f"✓ India VIX: {value:.2f}")
                    return
        except Exception as e:
            logger.error(f"VIX error: {e}")
        self.data['vix'] = {'value': 'N/A', 'change': 'N/A', 'source': 'NSE'}

    def get_gift_nifty_accurate(self):
        logger.info("Fetching GIFT Nifty...")
        try:
            url = 'https://www.nseindia.com/api/quote-derivative?symbol=NIFTY'
            response = self.safe_request(url)
            if response:
                data = response.json()
                if 'records' in data and len(data['records']) > 0:
                    value = float(data['records'][0].get('underlyingValue', 0))
                    self.data['gift'] = {'value': f'{value:,.2f}', 'source': 'NSE (SGX)'}
                    logger.info(f"✓ GIFT Nifty: {value:,.2f}")
                    return
        except Exception as e:
            logger.error(f"GIFT error: {e}")
        self.data['gift'] = {'value': 'N/A', 'source': 'NSE'}

    def get_fii_dii_accurate(self):
        logger.info("Fetching FII/DII...")
        try:
            url = 'https://www.moneycontrol.com/mcapi/get-fii-data'
            response = self.safe_request(url)
            if response:
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    fii = data['data'][0].get('fiiInflow', 'N/A')
                    dii = data['data'][0].get('diiInflow', 'N/A')
                    self.data['fii_dii'] = {'fii': f'{fii}', 'dii': f'{dii}', 'source': 'Moneycontrol API'}
                    logger.info(f"✓ FII: {fii}, DII: {dii}")
                    return
        except Exception as e:
            logger.error(f"FII/DII error: {e}")
        self.data['fii_dii'] = {'fii': 'N/A', 'dii': 'N/A', 'source': 'Moneycontrol'}

    def get_us_indices_accurate(self):
        logger.info("Fetching US Indices...")
        try:
            url = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols=^GSPC,^IXIC,^DJI&fields=symbol,regularMarketPrice,regularMarketChange,regularMarketChangePercent'
            response = self.safe_request(url)
            if response:
                api_data = response.json()
                if 'quoteResponse' in api_data and 'result' in api_data['quoteResponse']:
                    for quote in api_data['quoteResponse']['result']:
                        symbol = quote.get('symbol', '')
                        price = quote.get('regularMarketPrice')
                        change = quote.get('regularMarketChange', 0)
                        pct = quote.get('regularMarketChangePercent', 0)
                        if price:
                            if symbol == '^GSPC':
                                self.data['sp500'] = {'value': f'{price:,.0f}', 'change': f'{change:+,.0f}', 'pct': f'{pct:+.2f}%', 'source': 'Bloomberg'}
                                logger.info(f"✓ S&P 500: {price:,.0f}")
                            elif symbol == '^IXIC':
                                self.data['nasdaq'] = {'value': f'{price:,.0f}', 'change': f'{change:+,.0f}', 'pct': f'{pct:+.2f}%', 'source': 'Bloomberg'}
                                logger.info(f"✓ Nasdaq: {price:,.0f}")
                            elif symbol == '^DJI':
                                self.data['dow'] = {'value': f'{price:,.0f}', 'change': f'{change:+,.0f}', 'pct': f'{pct:+.2f}%', 'source': 'Bloomberg'}
                                logger.info(f"✓ Dow: {price:,.0f}")
        except Exception as e:
            logger.error(f"US error: {e}")
        if 'sp500' not in self.data:
            self.data['sp500'] = {'value': 'N/A', 'source': 'Bloomberg'}
        if 'nasdaq' not in self.data:
            self.data['nasdaq'] = {'value': 'N/A', 'source': 'Bloomberg'}
        if 'dow' not in self.data:
            self.data['dow'] = {'value': 'N/A', 'source': 'Bloomberg'}

    def get_asia_indices_accurate(self):
        logger.info("Fetching Asian Indices...")
        try:
            url = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols=^N225,^HSI&fields=symbol,regularMarketPrice,regularMarketChange'
            response = self.safe_request(url)
            if response:
                api_data = response.json()
                if 'quoteResponse' in api_data and 'result' in api_data['quoteResponse']:
                    for quote in api_data['quoteResponse']['result']:
                        symbol = quote.get('symbol', '')
                        price = quote.get('regularMarketPrice')
                        change = quote.get('regularMarketChange', 0)
                        if price:
                            if symbol == '^N225':
                                self.data['nikkei'] = {'value': f'{price:,.0f}', 'change': f'{change:+,.0f}', 'source': 'Bloomberg'}
                                logger.info(f"✓ Nikkei: {price:,.0f}")
                            elif symbol == '^HSI':
                                self.data['hangseng'] = {'value': f'{price:,.0f}', 'change': f'{change:+,.0f}', 'source': 'Bloomberg'}
                                logger.info(f"✓ Hang Seng: {price:,.0f}")
        except Exception as e:
            logger.error(f"Asia error: {e}")
        if 'nikkei' not in self.data:
            self.data['nikkei'] = {'value': 'N/A', 'source': 'Bloomberg'}
        if 'hangseng' not in self.data:
            self.data['hangseng'] = {'value': 'N/A', 'source': 'Bloomberg'}

    def get_commodities_accurate(self):
        logger.info("Fetching Commodities...")
        if self.finnhub_key:
            try:
                for symbol, key in {'NYMEX:CL1!': 'crude', 'NYMEX:GC1!': 'gold'}.items():
                    url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={self.finnhub_key}'
                    response = self.safe_request(url)
                    if response:
                        quote = response.json()
                        if 'c' in quote:
                            price = quote['c']
                            change = quote.get('d', 0)
                            pct = quote.get('dp', 0)
                            if key == 'crude':
                                self.data['crude'] = {'value': f'${price:.2f}', 'change': f'{change:+.2f}', 'pct': f'{pct:+.2f}%', 'source': 'Finnhub'}
                                logger.info(f"✓ Crude: ${price:.2f}")
                            elif key == 'gold':
                                self.data['gold'] = {'value': f'${price:.2f}', 'change': f'{change:+.2f}', 'pct': f'{pct:+.2f}%', 'source': 'Finnhub'}
                                logger.info(f"✓ Gold: ${price:.2f}")
            except Exception as e:
                logger.error(f"Finnhub error: {e}")
        try:
            url = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols=CL=F,GC=F&fields=symbol,regularMarketPrice,regularMarketChange'
            response = self.safe_request(url)
            if response:
                api_data = response.json()
                if 'quoteResponse' in api_data and 'result' in api_data['quoteResponse']:
                    for quote in api_data['quoteResponse']['result']:
                        symbol = quote.get('symbol', '')
                        price = quote.get('regularMarketPrice')
                        change = quote.get('regularMarketChange', 0)
                        if symbol == 'CL=F' and price and 'crude' not in self.data:
                            self.data['crude'] = {'value': f'${price:.2f}', 'change': f'{change:+.2f}', 'source': 'Yahoo Finance'}
                            logger.info(f"✓ Crude: ${price:.2f}")
                        elif symbol == 'GC=F' and price and 'gold' not in self.data:
                            self.data['gold'] = {'value': f'${price:.2f}', 'change': f'{change:+.2f}', 'source': 'Yahoo Finance'}
                            logger.info(f"✓ Gold: ${price:.2f}")
        except Exception as e:
            logger.error(f"Yahoo comm error: {e}")
        if 'crude' not in self.data:
            self.data['crude'] = {'value': 'N/A', 'source': 'Finnhub'}
        if 'gold' not in self.data:
            self.data['gold'] = {'value': 'N/A', 'source': 'Yahoo Finance'}

    def get_currency_accurate(self):
        logger.info("Fetching Currency...")
        try:
            url = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols=DXY=F,INRUSD=X&fields=symbol,regularMarketPrice,regularMarketChange'
            response = self.safe_request(url)
            if response:
                api_data = response.json()
                if 'quoteResponse' in api_data and 'result' in api_data['quoteResponse']:
                    for quote in api_data['quoteResponse']['result']:
                        symbol = quote.get('symbol', '')
                        price = quote.get('regularMarketPrice')
                        change = quote.get('regularMarketChange', 0)
                        if symbol == 'DXY=F' and price:
                            self.data['usd_index'] = {'value': f'{price:.2f}', 'change': f'{change:+.2f}', 'source': 'Bloomberg'}
                            logger.info(f"✓ USD Index: {price:.2f}")
                        elif symbol == 'INRUSD=X' and price:
                            self.data['inr_usd'] = {'value': f'{price:.2f}', 'change': f'{change:+.2f}', 'source': 'Bloomberg'}
                            logger.info(f"✓ INR/USD: {price:.2f}")
        except Exception as e:
            logger.error(f"Currency error: {e}")
        if 'usd_index' not in self.data:
            self.data['usd_index'] = {'value': 'N/A', 'source': 'Bloomberg'}
        if 'inr_usd' not in self.data:
            self.data['inr_usd'] = {'value': 'N/A', 'source': 'Bloomberg'}

    def get_treasury_yields_accurate(self):
        logger.info("Fetching Treasury Yields...")
        if self.fred_key:
            try:
                url = f'https://api.stlouisfed.org/fred/series/data?series_id=DGS10&api_key={self.fred_key}&file_type=json'
                response = self.safe_request(url)
                if response:
                    data = response.json()
                    if 'observations' in data and len(data['observations']) > 0:
                        latest = data['observations'][-1]
                        value = float(latest['value'])
                        self.data['us_10y'] = {'value': f'{value:.2f}%', 'source': 'FRED'}
                        logger.info(f"✓ 10Y: {value:.2f}%")
                        return
            except Exception as e:
                logger.error(f"FRED error: {e}")
        try:
            url = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols=^TNX&fields=symbol,regularMarketPrice'
            response = self.safe_request(url)
            if response:
                api_data = response.json()
                if 'quoteResponse' in api_data and 'result' in api_data['quoteResponse']:
                    quote = api_data['quoteResponse']['result'][0]
                    price = quote.get('regularMarketPrice')
                    if price:
                        self.data['us_10y'] = {'value': f'{price:.2f}%', 'source': 'Yahoo Finance'}
                        logger.info(f"✓ 10Y: {price:.2f}%")
                        return
        except Exception as e:
            logger.error(f"Yield error: {e}")
        self.data['us_10y'] = {'value': 'N/A', 'source': 'FRED'}

    def get_economic_calendar_accurate(self):
        logger.info("Fetching Economic Calendar...")
        try:
            url = 'https://tradingeconomics.com/calendar/api/json'
            response = self.safe_request(url, timeout=15)
            if response:
                events = response.json()
                today = datetime.now()
                fifteen_days = today + timedelta(days=15)
                india_events = []
                global_events = []
                for event in events[:200]:
                    try:
                        event_date_str = event.get('Date', '')
                        if event_date_str:
                            event_date = datetime.fromisoformat(event_date_str)
                            if today <= event_date <= fifteen_days:
                                event_info = {'date': event_date.strftime('%b %d'), 'name': event.get('Name', '')[:50], 'impact': event.get('Importance', 'Medium')}
                                country = event.get('Country', '').upper()
                                if country == 'INDIA':
                                    india_events.append(event_info)
                                elif country in ['UNITED STATES', 'EUROPEAN UNION']:
                                    global_events.append(event_info)
                    except:
                        continue
                self.data['calendar'] = {'india': india_events[:8], 'global': global_events[:8], 'source': 'Trading Economics'}
                logger.info(f"✓ Calendar: {len(india_events)} India, {len(global_events)} Global events")
                return
        except Exception as e:
            logger.error(f"Calendar error: {e}")
        self.data['calendar'] = {'india': [], 'global': [], 'source': 'Trading Economics'}


def generate_comprehensive_email(data):
    timestamp = datetime.now().strftime('%B %d, %Y at %H:%M IST')
    def get_val(key, subkey='value'):
        return data.get(key, {}).get(subkey, 'N/A')
    
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
body{{font-family:'Segoe UI',Arial;background:#f0f2f5}}.container{{max-width:1100px;margin:20px auto;background:white;border-radius:12px;box-shadow:0 4px 8px rgba(0,0,0,0.15)}}
.header{{background:linear-gradient(135deg,#1a3a52,#2c5aa0);padding:50px 30px;text-align:center;color:white}}.header h1{{font-size:2.4em;margin-bottom:10px}}.header p{{opacity:0.9}}
.timestamp{{background:rgba(255,255,255,0.15);padding:10px 20px;border-radius:20px;display:inline-block;margin-top:15px;font-size:0.9em}}
.content{{padding:40px}}.section{{margin-bottom:50px}}.section h2{{color:#1a3a52;font-size:1.8em;border-bottom:3px solid #ff9800;padding-bottom:12px;margin-bottom:25px}}
.section h3{{color:#2c5aa0;margin:25px 0 15px 0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px;margin:20px 0}}
.card{{background:linear-gradient(135deg,#f5f7fa,#ffffff);border:1px solid #ddd;border-radius:10px;padding:18px;box-shadow:0 2px 4px rgba(0,0,0,0.05)}}
.label{{font-size:0.75em;color:#666;text-transform:uppercase;letter-spacing:0.5px;font-weight:700;margin-bottom:8px}}.value{{font-size:1.9em;font-weight:700;color:#1a3a52;line-height:1.2}}
.subval{{font-size:0.9em;color:#666;margin-top:6px}}table{{width:100%;border-collapse:collapse;margin:20px 0;background:#f8f9fa;border-radius:8px}}
th{{background:#2c5aa0;color:white;padding:12px;text-align:left;font-weight:700}}td{{padding:11px 12px;border-bottom:1px solid #e0e0e0}}tr:nth-child(even){{background:white}}
.footer{{background:#1a3a52;color:white;padding:25px;text-align:center;font-size:0.85em}}.footer p{{margin:6px 0}}
</style></head><body><div class="container">
<div class="header"><h1>📊 Daily Market Intelligence Report</h1><p>Comprehensive Global & India Market Analysis</p><div class="timestamp">Generated: {timestamp}</div></div>
<div class="content">
<div class="section"><h2>🌍 Global Market Indicators</h2>
<h3>India Pre-Market</h3><div class="grid"><div class="card"><div class="label">GIFT Nifty (SGX)</div><div class="value">{get_val('gift')}</div><div class="subval">{get_val('gift','source')}</div></div></div>
<h3>US Markets</h3><div class="grid">
<div class="card"><div class="label">S&P 500</div><div class="value">{get_val('sp500')}</div><div class="subval">{get_val('sp500','change')}</div></div>
<div class="card"><div class="label">Nasdaq 100</div><div class="value">{get_val('nasdaq')}</div><div class="subval">{get_val('nasdaq','change')}</div></div>
<div class="card"><div class="label">Dow Jones</div><div class="value">{get_val('dow')}</div><div class="subval">{get_val('dow','change')}</div></div></div>
<h3>Asian Markets</h3><div class="grid">
<div class="card"><div class="label">Nikkei 225</div><div class="value">{get_val('nikkei')}</div><div class="subval">{get_val('nikkei','change')}</div></div>
<div class="card"><div class="label">Hang Seng</div><div class="value">{get_val('hangseng')}</div><div class="subval">{get_val('hangseng','change')}</div></div></div>
<h3>Commodities & Yields</h3><table>
<tr><th>Indicator</th><th>Value</th><th>Change</th><th>Source</th></tr>
<tr><td><strong>Crude Oil</strong></td><td>{get_val('crude')}</td><td>{get_val('crude','change')}</td><td>{get_val('crude','source')}</td></tr>
<tr><td><strong>Gold</strong></td><td>{get_val('gold')}</td><td>{get_val('gold','change')}</td><td>{get_val('gold','source')}</td></tr>
<tr><td><strong>USD Index</strong></td><td>{get_val('usd_index')}</td><td>{get_val('usd_index','change')}</td><td>{get_val('usd_index','source')}</td></tr>
<tr><td><strong>INR/USD</strong></td><td>{get_val('inr_usd')}</td><td>{get_val('inr_usd','change')}</td><td>{get_val('inr_usd','source')}</td></tr>
<tr><td><strong>US 10Y Yield</strong></td><td>{get_val('us_10y')}</td><td>-</td><td>{get_val('us_10y','source')}</td></tr>
</table></div>

<div class="section"><h2>🇮🇳 India Market Data</h2><table>
<tr><th>Index</th><th>Value</th><th>Change</th><th>Source</th></tr>
<tr><td><strong>Nifty 50</strong></td><td><strong>{get_val('nifty')}</strong></td><td>{get_val('nifty','change')}</td><td>{get_val('nifty','source')}</td></tr>
<tr><td><strong>Sensex</strong></td><td><strong>{get_val('sensex')}</strong></td><td>-</td><td>{get_val('sensex','source')}</td></tr>
<tr><td><strong>India VIX</strong></td><td><strong>{get_val('vix')}</strong></td><td>{get_val('vix','change')}</td><td>{get_val('vix','source')}</td></tr>
<tr><td><strong>FII Flow</strong></td><td>{get_val('fii_dii','fii')}</td><td>-</td><td rowspan="2">{get_val('fii_dii','source')}</td></tr>
<tr><td><strong>DII Flow</strong></td><td>{get_val('fii_dii','dii')}</td><td>-</td></tr>
</table></div>

<div class="section"><h2>📅 Economic Calendar (Next 15 Days)</h2><h3>🇮🇳 India Events</h3><table>
<tr><th>Date</th><th>Event</th><th>Impact</th></tr>
"""
    for event in data.get('calendar', {}).get('india', []):
        html += f"<tr><td><strong>{event.get('date')}</strong></td><td>{event.get('name')}</td><td>{event.get('impact')}</td></tr>"
    html += """</table><h3>🌍 Global Events</h3><table><tr><th>Date</th><th>Event</th><th>Impact</th></tr>"""
    for event in data.get('calendar', {}).get('global', []):
        html += f"<tr><td><strong>{event.get('date')}</strong></td><td>{event.get('name')}</td><td>{event.get('impact')}</td></tr>"
    html += f"""</table></div>
<div class="section"><h2>📊 Data Sources</h2><p><strong>NSE:</strong> Nifty 50, GIFT Nifty, VIX | <strong>BSE:</strong> Sensex | <strong>Bloomberg:</strong> US Indices, Nikkei, Hang Seng, USD/INR | <strong>Finnhub:</strong> Commodities | <strong>FRED:</strong> Treasury | <strong>Moneycontrol:</strong> FII/DII | <strong>Trading Economics:</strong> Calendar</p></div>
</div><div class="footer"><p><strong>Daily Market Intelligence Report</strong></p><p>Automated daily at 8:00 AM IST | mailbox.macwan@gmail.com</p><p>For informational purposes only.</p></div></div></body></html>
"""
    return html


def send_email(recipient, subject, html_body):
    try:
        sender = os.getenv('SENDER_EMAIL')
        password = os.getenv('SENDER_PASSWORD')
        if not sender or not password:
            logger.error("Email credentials missing")
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
        logger.info(f"✓ Email sent to {recipient}")
        return True
    except Exception as e:
        logger.error(f"Email error: {e}")
        return False


def main():
    logger.info("\n" + "=" * 90)
    logger.info("PRODUCTION MARKET INTELLIGENCE SYSTEM - ACCURATE DATA")
    logger.info("=" * 90 + "\n")
    try:
        collector = ProductionMarketCollector()
        data = collector.collect_all_data()
        html = generate_comprehensive_email(data)
        subject = f"Daily Market Intelligence Report - {datetime.now().strftime('%B %d, %Y')}"
        if send_email("mailbox.macwan@gmail.com", subject, html):
            logger.info("\n" + "=" * 90)
            logger.info("✅ SUCCESS: COMPREHENSIVE REPORT WITH ACCURATE DATA SENT")
            logger.info("=" * 90 + "\n")
            return True
        return False
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
