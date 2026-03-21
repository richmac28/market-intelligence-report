import requests
import json
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketDataCollector:
    def __init__(self):
        self.finnhub_key = os.getenv('FINNHUB_API_KEY', '')
        self.fred_key = os.getenv('FRED_API_KEY', '')
        self.market_data = {}

    def get_us_indices_bloomberg(self):
        logger.info("📊 Fetching US Indices from Bloomberg...")
        result = {}
        symbols = {'SPY': 'S&P 500', 'QQQ': 'Nasdaq 100', 'DIA': 'Dow Jones'}
        for symbol, name in symbols.items():
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                url = f"https://www.moneycontrol.com/mcapi/quote/equity?q={symbol}"
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    price = data.get('data', {}).get('pricehigh', 'N/A')
                    result[name] = {'value': price, 'source': 'Bloomberg (Moneycontrol)'}
                    logger.info(f"✓ {name}: {price}")
            except Exception as e:
                logger.error(f"✗ {name}: {str(e)}")
                result[name] = {'value': 'N/A', 'source': 'Error'}
        return result

    def get_nifty_sensex(self):
        logger.info("🇮🇳 Fetching India Indices...")
        result = {}
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            url = 'https://www.nseindia.com/api/quote-derivative?symbol=NIFTY'
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                records = data.get('records', [{}])
                if records:
                    nifty_value = float(records[0].get('underlyingValue', 0))
                    nifty_change = float(records[0].get('change', 0))
                    nifty_change_pct = (nifty_change / (nifty_value - nifty_change) * 100) if (nifty_value - nifty_change) != 0 else 0
                    result['Nifty 50'] = {'value': round(nifty_value, 2), 'change_pct': f"{nifty_change_pct:+.2f}%", 'source': 'NSE API'}
                    logger.info(f"✓ Nifty 50: {nifty_value:.2f}")
        except Exception as e:
            logger.error(f"✗ Nifty: {str(e)}")
            result['Nifty 50'] = {'value': 'N/A', 'source': 'Error'}
        try:
            url = 'https://www.moneycontrol.com/mcapi/quote/equity?q=SENSEX'
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                sensex_value = data.get('data', {}).get('pricehigh', 'N/A')
                result['Sensex'] = {'value': sensex_value, 'source': 'Moneycontrol'}
                logger.info(f"✓ Sensex: {sensex_value}")
        except Exception as e:
            logger.error(f"✗ Sensex: {str(e)}")
            result['Sensex'] = {'value': 'N/A', 'source': 'Error'}
        return result

    def get_india_vix(self):
        logger.info("📉 Fetching India VIX...")
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            url = 'https://www.nseindia.com/api/quote-derivative?symbol=INDIAVIX'
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                records = data.get('records', [{}])
                if records:
                    vix_value = float(records[0].get('underlyingValue', 0))
                    vix_change = float(records[0].get('change', 0))
                    self.market_data['india_vix'] = {'value': round(vix_value, 2), 'change': f"{vix_change:+.2f}", 'source': 'NSE API'}
                    logger.info(f"✓ India VIX: {vix_value:.2f}")
        except Exception as e:
            logger.error(f"✗ India VIX: {str(e)}")
            self.market_data['india_vix'] = {'value': 'N/A', 'source': 'Error'}

    def get_currency(self):
        logger.info("💱 Fetching Currency...")
        result = {}
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            url = 'https://www.moneycontrol.com/mcapi/quote/equity?q=USDINDEX'
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                usd_value = data.get('data', {}).get('pricehigh', 'N/A')
                result['USD Index'] = {'value': usd_value, 'source': 'Bloomberg'}
        except:
            result['USD Index'] = {'value': 'N/A', 'source': 'Error'}
        try:
            url = 'https://www.moneycontrol.com/mcapi/quote/equity?q=INRUSD'
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                inr_usd = data.get('data', {}).get('pricehigh', 'N/A')
                result['INR/USD'] = {'value': inr_usd, 'source': 'Bloomberg'}
        except:
            result['INR/USD'] = {'value': 'N/A', 'source': 'Error'}
        return result

    def get_commodities(self):
        logger.info("🛢️ Fetching Commodities...")
        result = {}
        if not self.finnhub_key:
            return result
        symbols = {'NYMEX:CL1!': 'Crude Oil', 'NYMEX:GC1!': 'Gold', 'NYMEX:SI1!': 'Silver'}
        for symbol, name in symbols.items():
            try:
                url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={self.finnhub_key}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'c' in data:
                        price = data['c']
                        result[name] = {'value': round(price, 2), 'change_pct': f"{data.get('dp', 0):+.2f}%", 'source': 'Finnhub'}
                        logger.info(f"✓ {name}: {price:.2f}")
            except Exception as e:
                logger.error(f"✗ {name}: {str(e)}")
                result[name] = {'value': 'N/A', 'source': 'Error'}
        return result

    def get_treasury_yields(self):
        logger.info("📈 Fetching Treasury Yields...")
        result = {}
        if not self.fred_key:
            return result
        try:
            url = f"https://api.stlouisfed.org/fred/series/data?series_id=DGS10&api_key={self.fred_key}&file_type=json"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('observations'):
                    latest = data['observations'][-1]
                    yield_value = float(latest['value'])
                    result['us_10y_yield'] = {'value': f"{yield_value:.2f}%", 'source': 'FRED'}
                    logger.info(f"✓ US 10Y Yield: {yield_value:.2f}%")
        except Exception as e:
            logger.error(f"✗ Treasury Yields: {str(e)}")
            result['us_10y_yield'] = {'value': 'N/A', 'source': 'Error'}
        return result

    def get_fii_dii(self):
        logger.info("💰 Fetching FII/DII...")
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get("https://www.moneycontrol.com/mcapi/get-fii-data", headers=headers, timeout=10)
            if response.status_code == 200:
                fii_data = response.json()
                data_list = fii_data.get('data', [{}])
                if data_list:
                    fii_flow = data_list[0].get('fiiInflow', 'N/A')
                    dii_flow = data_list[0].get('diiInflow', 'N/A')
                    self.market_data['fii_dii'] = {'fii': fii_flow, 'dii': dii_flow, 'source': 'Moneycontrol'}
                    logger.info(f"✓ FII: {fii_flow}, DII: {dii_flow}")
        except Exception as e:
            logger.error(f"✗ FII/DII: {str(e)}")
            self.market_data['fii_dii'] = {'fii': 'N/A', 'dii': 'N/A', 'source': 'Error'}

    def get_economic_calendar(self):
        logger.info("📅 Fetching Economic Calendar...")
        try:
            response = requests.get("https://tradingeconomics.com/calendar/api/json", timeout=15)
            if response.status_code == 200:
                events = response.json()
                today = datetime.now()
                fifteen_days = today + timedelta(days=15)
                india_events = []
                global_events = []
                for event in events:
                    try:
                        event_date = datetime.fromisoformat(event.get('Date', ''))
                        if today <= event_date <= fifteen_days:
                            event_info = {'date': event_date.strftime('%b %d'), 'name': event.get('Name', 'Unknown'), 'impact': event.get('Importance', 'Medium')}
                            country = event.get('Country', '').upper()
                            if country == 'INDIA':
                                india_events.append(event_info)
                            elif country in ['UNITED STATES', 'EUROPEAN UNION', 'CHINA', 'JAPAN']:
                                global_events.append(event_info)
                    except:
                        continue
                self.market_data['economic_calendar'] = {'india_events': india_events[:6], 'global_events': global_events[:6], 'source': 'Trading Economics'}
                logger.info(f"✓ Calendar fetched")
        except Exception as e:
            logger.error(f"✗ Calendar: {str(e)}")
            self.market_data['economic_calendar'] = {'india_events': [], 'global_events': [], 'source': 'Error'}

    def collect_all_data(self):
        logger.info("🚀 STARTING MARKET DATA COLLECTION")
        try:
            self.market_data['us_indices'] = self.get_us_indices_bloomberg()
            india_data = self.get_nifty_sensex()
            self.market_data.update(india_data)
            self.get_india_vix()
            self.market_data['currency'] = self.get_currency()
            self.market_data['commodities'] = self.get_commodities()
            self.market_data['yields'] = self.get_treasury_yields()
            self.get_fii_dii()
            self.get_economic_calendar()
            logger.info("✅ DATA COLLECTION COMPLETE")
            return self.market_data
        except Exception as e:
            logger.error(f"Error during collection: {str(e)}")
            return None

def generate_html_email(market_data):
    us_indices = market_data.get('us_indices', {})
    currency = market_data.get('currency', {})
    commodities = market_data.get('commodities', {})
    yields = market_data.get('yields', {})
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{{font-family:Arial;background:#f5f5f5;}}table{{width:100%;border-collapse:collapse;}}.header{{background:#1e3c72;color:white;padding:20px;}}</style></head><body><div style="background:#1e3c72;color:white;padding:20px;text-align:center;"><h1>📊 Daily Market Intelligence Report</h1><p>Generated: {datetime.now().strftime('%B %d, %Y at %H:%M IST')}</p></div><div style="padding:20px;"><h2>Global Market Indicators</h2><table border="1" cellpadding="10"><tr><th>Indicator</th><th>Value</th><th>Source</th></tr><tr><td>S&P 500</td><td>{us_indices.get('S&P 500', {}).get('value', 'N/A')}</td><td>{us_indices.get('S&P 500', {}).get('source', 'N/A')}</td></tr><tr><td>Nasdaq 100</td><td>{us_indices.get('Nasdaq 100', {}).get('value', 'N/A')}</td><td>{us_indices.get('Nasdaq 100', {}).get('source', 'N/A')}</td></tr><tr><td>Crude Oil</td><td>{commodities.get('Crude Oil', {}).get('value', 'N/A')}</td><td>{commodities.get('Crude Oil', {}).get('source', 'N/A')}</td></tr><tr><td>Gold</td><td>{commodities.get('Gold', {}).get('value', 'N/A')}</td><td>{commodities.get('Gold', {}).get('source', 'N/A')}</td></tr></table><h2>India Market Data</h2><table border="1" cellpadding="10"><tr><th>Index</th><th>Value</th><th>Source</th></tr><tr><td>Nifty 50</td><td>{market_data.get('Nifty 50', {}).get('value', 'N/A')}</td><td>{market_data.get('Nifty 50', {}).get('source', 'N/A')}</td></tr><tr><td>Sensex</td><td>{market_data.get('Sensex', {}).get('value', 'N/A')}</td><td>{market_data.get('Sensex', {}).get('source', 'N/A')}</td></tr></table></div><div style="background:#1a1f3a;color:white;padding:20px;text-align:center;"><p>Automated Daily Market Intelligence Report</p><p>Data from: Bloomberg • Moneycontrol • NSE • FRED • Finnhub</p></div></body></html>"""
    return html

def send_email(recipient_email, subject, html_body):
    try:
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        if not sender_email or not sender_password:
            logger.error("Email credentials not configured")
            return False
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        logger.info(f"✓ Email sent to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"✗ Email send failed: {str(e)}")
        return False

def main():
    logger.info("🚀 STARTING MARKET INTELLIGENCE REPORT GENERATION")
    try:
        collector = MarketDataCollector()
        market_data = collector.collect_all_data()
        if not market_data:
            logger.error("Failed to collect market data")
            return False
        html_email = generate_html_email(market_data)
        subject = f"Daily Market Intelligence Report - {datetime.now().strftime('%B %d, %Y')}"
        recipient = "mailbox.macwan@gmail.com"
        if send_email(recipient, subject, html_email):
            logger.info("✅ Report generated and sent successfully")
            return True
        else:
            logger.error("Failed to send email")
            return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
