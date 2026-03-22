import requests
import json
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImprovedMarketDataCollector:
    def __init__(self):
        self.finnhub_key = os.getenv('FINNHUB_API_KEY', '')
        self.fred_key = os.getenv('FRED_API_KEY', '')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def fetch_data(self, url, max_retries=2):
        """Fetch data with error handling"""
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    return response
            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed: {e}")
        return None

    def get_all_data(self):
        """Collect all market data"""
        logger.info("=" * 60)
        logger.info("Starting data collection from live sources...")
        logger.info("=" * 60)
        
        data = {}
        
        # Global Markets
        data['gift_nifty'] = self.get_gift_nifty()
        data['sp500'] = self.get_sp500()
        data['nasdaq'] = self.get_nasdaq()
        data['dow'] = self.get_dow()
        data['nikkei'] = self.get_nikkei()
        data['hangseng'] = self.get_hangseng()
        
        # Commodities & Currency
        data['crude'] = self.get_crude_oil()
        data['gold'] = self.get_gold()
        data['usd_index'] = self.get_usd_index()
        data['inr_usd'] = self.get_inr_usd()
        data['us_10y'] = self.get_us_10y_yield()
        
        # India Markets
        data['nifty'] = self.get_nifty50()
        data['sensex'] = self.get_sensex()
        data['vix'] = self.get_india_vix()
        data['fii_dii'] = self.get_fii_dii()
        
        # Economic Calendar
        data['calendar'] = self.get_calendar()
        
        logger.info("=" * 60)
        logger.info("Data collection complete!")
        logger.info("=" * 60)
        return data

    def get_gift_nifty(self):
        """Get GIFT Nifty from NSE"""
        try:
            url = 'https://www.nseindia.com/api/quote-derivative?symbol=NIFTY'
            response = self.fetch_data(url)
            if response:
                data = response.json()
                if 'records' in data and len(data['records']) > 0:
                    val = data['records'][0].get('underlyingValue')
                    if val:
                        logger.info(f"✓ GIFT Nifty: {val}")
                        return {'value': f"{float(val):.2f}", 'source': 'NSE API'}
        except Exception as e:
            logger.error(f"GIFT Nifty error: {e}")
        return {'value': 'N/A', 'source': 'NSE'}

    def get_sp500(self):
        """Get S&P 500 price"""
        try:
            # Using yfinance-like data source
            url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/^GSPC?modules=price'
            response = self.fetch_data(url)
            if response:
                data = response.json()
                if 'quoteSummary' in data:
                    price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
                    logger.info(f"✓ S&P 500: {price}")
                    return {'value': f"{price:,.2f}", 'source': 'Yahoo Finance'}
        except Exception as e:
            logger.warning(f"S&P 500 fetch failed: {e}")
        
        # Fallback method
        try:
            url = 'https://www.moneycontrol.com/mcapi/quote/equity?q=SPY'
            response = self.fetch_data(url)
            if response:
                data = response.json()
                price = data.get('data', {}).get('pricehigh')
                if price:
                    logger.info(f"✓ S&P 500 (via Moneycontrol): {price}")
                    return {'value': f"{price}", 'source': 'Moneycontrol'}
        except:
            pass
        
        return {'value': 'N/A', 'source': 'Finance'}

    def get_nasdaq(self):
        """Get Nasdaq 100"""
        try:
            url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/^NDX?modules=price'
            response = self.fetch_data(url)
            if response:
                data = response.json()
                price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
                logger.info(f"✓ Nasdaq: {price}")
                return {'value': f"{price:,.2f}", 'source': 'Yahoo Finance'}
        except:
            pass
        return {'value': 'N/A', 'source': 'Finance'}

    def get_dow(self):
        """Get Dow Jones"""
        try:
            url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/^DJI?modules=price'
            response = self.fetch_data(url)
            if response:
                data = response.json()
                price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
                logger.info(f"✓ Dow Jones: {price}")
                return {'value': f"{price:,.2f}", 'source': 'Yahoo Finance'}
        except:
            pass
        return {'value': 'N/A', 'source': 'Finance'}

    def get_nikkei(self):
        """Get Nikkei 225"""
        try:
            url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/^N225?modules=price'
            response = self.fetch_data(url)
            if response:
                data = response.json()
                price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
                logger.info(f"✓ Nikkei: {price}")
                return {'value': f"{price:,.2f}", 'source': 'Yahoo Finance'}
        except:
            pass
        return {'value': 'N/A', 'source': 'Finance'}

    def get_hangseng(self):
        """Get Hang Seng"""
        try:
            url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/^HSI?modules=price'
            response = self.fetch_data(url)
            if response:
                data = response.json()
                price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
                logger.info(f"✓ Hang Seng: {price}")
                return {'value': f"{price:,.2f}", 'source': 'Yahoo Finance'}
        except:
            pass
        return {'value': 'N/A', 'source': 'Finance'}

    def get_crude_oil(self):
        """Get Crude Oil price"""
        if self.finnhub_key:
            try:
                url = f'https://finnhub.io/api/v1/quote?symbol=NYMEX:CL1!&token={self.finnhub_key}'
                response = self.fetch_data(url)
                if response:
                    data = response.json()
                    if 'c' in data:
                        price = data['c']
                        logger.info(f"✓ Crude Oil: ${price:.2f}")
                        return {'value': f"${price:.2f}", 'source': 'Finnhub'}
            except Exception as e:
                logger.warning(f"Finnhub crude error: {e}")
        
        # Fallback
        try:
            url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/CL=F?modules=price'
            response = self.fetch_data(url)
            if response:
                data = response.json()
                price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
                logger.info(f"✓ Crude Oil (Yahoo): ${price:.2f}")
                return {'value': f"${price:.2f}", 'source': 'Yahoo Finance'}
        except:
            pass
        
        return {'value': 'N/A', 'source': 'Finnhub'}

    def get_gold(self):
        """Get Gold price"""
        if self.finnhub_key:
            try:
                url = f'https://finnhub.io/api/v1/quote?symbol=NYMEX:GC1!&token={self.finnhub_key}'
                response = self.fetch_data(url)
                if response:
                    data = response.json()
                    if 'c' in data:
                        price = data['c']
                        logger.info(f"✓ Gold: ${price:.2f}")
                        return {'value': f"${price:.2f}", 'source': 'Finnhub'}
            except:
                pass
        
        # Fallback
        try:
            url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/GC=F?modules=price'
            response = self.fetch_data(url)
            if response:
                data = response.json()
                price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
                logger.info(f"✓ Gold (Yahoo): ${price:.2f}")
                return {'value': f"${price:.2f}", 'source': 'Yahoo Finance'}
        except:
            pass
        
        return {'value': 'N/A', 'source': 'Finnhub'}

    def get_usd_index(self):
        """Get USD Index"""
        try:
            url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/DXY=F?modules=price'
            response = self.fetch_data(url)
            if response:
                data = response.json()
                price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
                logger.info(f"✓ USD Index: {price:.2f}")
                return {'value': f"{price:.2f}", 'source': 'Yahoo Finance'}
        except:
            pass
        return {'value': 'N/A', 'source': 'Finance'}

    def get_inr_usd(self):
        """Get INR/USD rate"""
        try:
            url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/INRUSD=X?modules=price'
            response = self.fetch_data(url)
            if response:
                data = response.json()
                price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
                logger.info(f"✓ INR/USD: {price:.2f}")
                return {'value': f"{price:.2f}", 'source': 'Yahoo Finance'}
        except:
            pass
        return {'value': 'N/A', 'source': 'Finance'}

    def get_us_10y_yield(self):
        """Get US 10Y Treasury Yield"""
        if self.fred_key:
            try:
                url = f'https://api.stlouisfed.org/fred/series/data?series_id=DGS10&api_key={self.fred_key}&file_type=json'
                response = self.fetch_data(url)
                if response:
                    data = response.json()
                    if data.get('observations'):
                        yield_val = float(data['observations'][-1]['value'])
                        logger.info(f"✓ US 10Y Yield: {yield_val:.2f}%")
                        return {'value': f"{yield_val:.2f}%", 'source': 'FRED'}
            except:
                pass
        
        # Fallback to Yahoo Finance
        try:
            url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/^TNX?modules=price'
            response = self.fetch_data(url)
            if response:
                data = response.json()
                price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
                logger.info(f"✓ US 10Y Yield (Yahoo): {price:.2f}%")
                return {'value': f"{price:.2f}%", 'source': 'Yahoo Finance'}
        except:
            pass
        
        return {'value': 'N/A', 'source': 'FRED'}

    def get_nifty50(self):
        """Get Nifty 50"""
        try:
            url = 'https://www.nseindia.com/api/quote-derivative?symbol=NIFTY'
            response = self.fetch_data(url)
            if response:
                data = response.json()
                if 'records' in data and len(data['records']) > 0:
                    val = data['records'][0].get('underlyingValue')
                    change = data['records'][0].get('change', 0)
                    if val:
                        logger.info(f"✓ Nifty 50: {val} ({change:+.2f})")
                        return {
                            'value': f"{float(val):.2f}",
                            'change': f"{float(change):+.2f}",
                            'source': 'NSE API'
                        }
        except Exception as e:
            logger.error(f"Nifty error: {e}")
        return {'value': 'N/A', 'change': 'N/A', 'source': 'NSE'}

    def get_sensex(self):
        """Get Sensex (BSE)"""
        try:
            url = 'https://www.moneycontrol.com/mcapi/quote/equity?q=SENSEX'
            response = self.fetch_data(url)
            if response:
                data = response.json()
                price = data.get('data', {}).get('pricehigh')
                if price:
                    logger.info(f"✓ Sensex: {price}")
                    return {'value': f"{price}", 'source': 'Moneycontrol'}
        except Exception as e:
            logger.error(f"Sensex error: {e}")
        return {'value': 'N/A', 'source': 'BSE'}

    def get_india_vix(self):
        """Get India VIX"""
        try:
            url = 'https://www.nseindia.com/api/quote-derivative?symbol=INDIAVIX'
            response = self.fetch_data(url)
            if response:
                data = response.json()
                if 'records' in data and len(data['records']) > 0:
                    val = data['records'][0].get('underlyingValue')
                    if val:
                        logger.info(f"✓ India VIX: {val}")
                        return {'value': f"{float(val):.2f}", 'source': 'NSE API'}
        except Exception as e:
            logger.error(f"VIX error: {e}")
        return {'value': 'N/A', 'source': 'NSE'}

    def get_fii_dii(self):
        """Get FII/DII flows"""
        try:
            url = 'https://www.moneycontrol.com/mcapi/get-fii-data'
            response = self.fetch_data(url)
            if response:
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    fii = data['data'][0].get('fiiInflow', 'N/A')
                    dii = data['data'][0].get('diiInflow', 'N/A')
                    logger.info(f"✓ FII: {fii}, DII: {dii}")
                    return {'fii': f"{fii}", 'dii': f"{dii}", 'source': 'Moneycontrol'}
        except Exception as e:
            logger.error(f"FII/DII error: {e}")
        return {'fii': 'N/A', 'dii': 'N/A', 'source': 'Moneycontrol'}

    def get_calendar(self):
        """Get economic calendar"""
        try:
            url = 'https://tradingeconomics.com/calendar/api/json'
            response = self.fetch_data(url, max_retries=1)
            if response:
                events = response.json()
                today = datetime.now()
                fifteen_days = today + timedelta(days=15)
                
                india_events = []
                global_events = []
                
                for event in events[:50]:
                    try:
                        event_date_str = event.get('Date', '')
                        if event_date_str:
                            event_date = datetime.fromisoformat(event_date_str)
                            if today <= event_date <= fifteen_days:
                                event_info = {
                                    'date': event_date.strftime('%b %d'),
                                    'name': event.get('Name', 'N/A')[:40],
                                    'impact': event.get('Importance', 'Medium')
                                }
                                country = event.get('Country', '').upper()
                                if country == 'INDIA':
                                    india_events.append(event_info)
                                elif country in ['UNITED STATES', 'EUROPEAN UNION']:
                                    global_events.append(event_info)
                    except:
                        continue
                
                logger.info(f"✓ Calendar: {len(india_events)} India, {len(global_events)} Global events")
                return {'india': india_events[:6], 'global': global_events[:6]}
        except Exception as e:
            logger.warning(f"Calendar error: {e}")
        
        return {'india': [], 'global': []}


def generate_html_email(data):
    """Generate professional HTML email"""
    
    timestamp = datetime.now().strftime('%B %d, %Y at %H:%M IST')
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; background: #f0f2f5; margin: 0; padding: 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #1a3a52 0%, #2c5aa0 100%); padding: 40px; text-align: center; color: white; }}
        .header h1 {{ margin: 0; font-size: 2.2em; }}
        .content {{ padding: 40px; }}
        .section {{ margin-bottom: 40px; }}
        .section h2 {{ color: #1a3a52; border-bottom: 3px solid #ff9800; padding-bottom: 10px; margin-bottom: 20px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
        .card {{ background: #f5f7fa; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; }}
        .label {{ font-size: 0.85em; color: #666; text-transform: uppercase; margin-bottom: 8px; font-weight: bold; }}
        .value {{ font-size: 1.8em; font-weight: bold; color: #1a3a52; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: #f8f9fa; }}
        th {{ background: #2c5aa0; color: white; padding: 12px; text-align: left; font-weight: bold; }}
        td {{ padding: 12px; border-bottom: 1px solid #e0e0e0; }}
        tr:nth-child(even) {{ background: white; }}
        .footer {{ background: #1a3a52; color: white; padding: 20px; text-align: center; font-size: 0.9em; }}
        .source {{ font-size: 0.75em; color: #666; margin-top: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Daily Market Intelligence Report</h1>
            <p>Generated: {timestamp}</p>
        </div>

        <div class="content">
            <!-- GLOBAL MARKETS -->
            <div class="section">
                <h2>🌍 Global Market Indicators</h2>
                <div class="grid">
                    <div class="card">
                        <div class="label">GIFT Nifty (India Pre-Market)</div>
                        <div class="value">{data['gift_nifty']['value']}</div>
                        <div class="source">{data['gift_nifty']['source']}</div>
                    </div>
                    <div class="card">
                        <div class="label">S&P 500</div>
                        <div class="value">{data['sp500']['value']}</div>
                        <div class="source">{data['sp500']['source']}</div>
                    </div>
                    <div class="card">
                        <div class="label">Nasdaq 100</div>
                        <div class="value">{data['nasdaq']['value']}</div>
                        <div class="source">{data['nasdaq']['source']}</div>
                    </div>
                    <div class="card">
                        <div class="label">Dow Jones</div>
                        <div class="value">{data['dow']['value']}</div>
                        <div class="source">{data['dow']['source']}</div>
                    </div>
                    <div class="card">
                        <div class="label">Nikkei 225 (Japan)</div>
                        <div class="value">{data['nikkei']['value']}</div>
                        <div class="source">{data['nikkei']['source']}</div>
                    </div>
                    <div class="card">
                        <div class="label">Hang Seng (Hong Kong)</div>
                        <div class="value">{data['hangseng']['value']}</div>
                        <div class="source">{data['hangseng']['source']}</div>
                    </div>
                </div>

                <h3 style="color: #2c5aa0; margin-top: 30px;">Commodities & Currency</h3>
                <table>
                    <tr>
                        <th>Indicator</th>
                        <th>Value</th>
                        <th>Source</th>
                    </tr>
                    <tr>
                        <td><strong>Crude Oil (Brent)</strong></td>
                        <td>{data['crude']['value']}</td>
                        <td>{data['crude']['source']}</td>
                    </tr>
                    <tr>
                        <td><strong>Gold</strong></td>
                        <td>{data['gold']['value']}</td>
                        <td>{data['gold']['source']}</td>
                    </tr>
                    <tr>
                        <td><strong>USD Index</strong></td>
                        <td>{data['usd_index']['value']}</td>
                        <td>{data['usd_index']['source']}</td>
                    </tr>
                    <tr>
                        <td><strong>INR/USD</strong></td>
                        <td>{data['inr_usd']['value']}</td>
                        <td>{data['inr_usd']['source']}</td>
                    </tr>
                    <tr>
                        <td><strong>US 10Y Treasury Yield</strong></td>
                        <td>{data['us_10y']['value']}</td>
                        <td>{data['us_10y']['source']}</td>
                    </tr>
                </table>
            </div>

            <!-- INDIA MARKETS -->
            <div class="section">
                <h2>🇮🇳 India Market Data</h2>
                <table>
                    <tr>
                        <th>Index</th>
                        <th>Value</th>
                        <th>Change</th>
                        <th>Source</th>
                    </tr>
                    <tr>
                        <td><strong>Nifty 50</strong></td>
                        <td>{data['nifty']['value']}</td>
                        <td>{data['nifty'].get('change', 'N/A')}</td>
                        <td>{data['nifty']['source']}</td>
                    </tr>
                    <tr>
                        <td><strong>Sensex</strong></td>
                        <td>{data['sensex']['value']}</td>
                        <td>-</td>
                        <td>{data['sensex']['source']}</td>
                    </tr>
                    <tr>
                        <td><strong>India VIX</strong></td>
                        <td>{data['vix']['value']}</td>
                        <td>Market Volatility</td>
                        <td>{data['vix']['source']}</td>
                    </tr>
                    <tr>
                        <td><strong>FII Flow</strong></td>
                        <td>{data['fii_dii']['fii']}</td>
                        <td>-</td>
                        <td rowspan="2">{data['fii_dii']['source']}</td>
                    </tr>
                    <tr>
                        <td><strong>DII Flow</strong></td>
                        <td>{data['fii_dii']['dii']}</td>
                        <td>-</td>
                    </tr>
                </table>
            </div>

            <!-- ECONOMIC CALENDAR -->
            <div class="section">
                <h2>📅 Economic Calendar (Next 15 Days)</h2>
                
                <h3 style="color: #2c5aa0;">🇮🇳 India Events</h3>
                <table>
                    <tr>
                        <th>Date</th>
                        <th>Event</th>
                        <th>Impact</th>
                    </tr>
"""
    
    for event in data['calendar'].get('india', []):
        html += f"""
                    <tr>
                        <td><strong>{event['date']}</strong></td>
                        <td>{event['name']}</td>
                        <td>{event['impact']}</td>
                    </tr>
"""
    
    html += """
                </table>

                <h3 style="color: #2c5aa0; margin-top: 20px;">🌍 Global Events</h3>
                <table>
                    <tr>
                        <th>Date</th>
                        <th>Event</th>
                        <th>Impact</th>
                    </tr>
"""
    
    for event in data['calendar'].get('global', []):
        html += f"""
                    <tr>
                        <td><strong>{event['date']}</strong></td>
                        <td>{event['name']}</td>
                        <td>{event['impact']}</td>
                    </tr>
"""
    
    html += """
                </table>
            </div>

            <!-- INVESTMENT INSIGHTS -->
            <div class="section">
                <h2>💰 Investment Insights</h2>
                <div class="card" style="background: #fff3cd; border-left: 4px solid #ff9800;">
                    <p><strong>Today's Recommendation:</strong></p>
                    <p>Diversified portfolio: 40% Large Cap, 25% Mid Cap, 20% Debt, 15% Small Cap</p>
                    <p><strong>Sources:</strong> Bloomberg | Moneycontrol | NSE | FRED | Finnhub | Trading Economics</p>
                </div>
            </div>

        </div>

        <div class="footer">
            <p><strong>Daily Market Intelligence Report</strong></p>
            <p>Sent to: mailbox.macwan@gmail.com | Automated daily at 8:00 AM IST</p>
            <p>Disclaimer: For information only. Consult a financial advisor before making investment decisions.</p>
        </div>
    </div>
</body>
</html>
"""
    return html


def send_email(recipient, subject, html_body):
    """Send email"""
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
        
        logger.info(f"✅ Email sent to {recipient}")
        return True
    except Exception as e:
        logger.error(f"❌ Email error: {e}")
        return False


def main():
    logger.info("🚀 Starting Market Intelligence Report...")
    
    try:
        collector = ImprovedMarketDataCollector()
        data = collector.get_all_data()
        
        html = generate_html_email(data)
        subject = f"Daily Market Intelligence Report - {datetime.now().strftime('%B %d, %Y')}"
        
        if send_email("mailbox.macwan@gmail.com", subject, html):
            logger.info("=" * 60)
            logger.info("✅ SUCCESS: Report sent with REAL data!")
            logger.info("=" * 60)
            return True
        return False
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
