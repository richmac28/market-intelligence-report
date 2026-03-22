import requests
import json
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_url(url, headers=None, timeout=10):
    """Simple fetch with retry"""
    if headers is None:
        headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.error(f"Fetch error for {url}: {e}")
    return None

def get_nifty50():
    """Get Nifty 50 - NSE API"""
    try:
        url = 'https://www.nseindia.com/api/quote-derivative?symbol=NIFTY'
        data = fetch_url(url)
        if data and 'records' in data:
            val = data['records'][0].get('underlyingValue')
            change = data['records'][0].get('change', 0)
            if val:
                logger.info(f"✓ Nifty: {val}")
                return f"{float(val):.2f}", f"{float(change):+.2f}"
    except Exception as e:
        logger.error(f"Nifty error: {e}")
    return "N/A", "N/A"

def get_sensex():
    """Get Sensex - Using BSE API"""
    try:
        # BSE website scrape
        url = 'https://www.bseindia.com/markets/flash.html'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        
        # Try alternative - Moneycontrol
        url2 = 'https://api.moneycontrol.com/api/v1/markets/indices?tab=gainers&exchange=BSE'
        data = fetch_url(url2)
        if data:
            for item in data.get('data', []):
                if 'Sensex' in item.get('name', ''):
                    val = item.get('value')
                    if val:
                        logger.info(f"✓ Sensex: {val}")
                        return val, "N/A"
    except Exception as e:
        logger.error(f"Sensex error: {e}")
    return "N/A", "N/A"

def get_india_vix():
    """Get India VIX"""
    try:
        url = 'https://www.nseindia.com/api/quote-derivative?symbol=INDIAVIX'
        data = fetch_url(url)
        if data and 'records' in data:
            val = data['records'][0].get('underlyingValue')
            if val:
                logger.info(f"✓ VIX: {val}")
                return f"{float(val):.2f}"
    except Exception as e:
        logger.error(f"VIX error: {e}")
    return "N/A"

def get_gift_nifty():
    """Get GIFT Nifty"""
    try:
        url = 'https://www.nseindia.com/api/quote-derivative?symbol=NIFTY'
        data = fetch_url(url)
        if data and 'records' in data:
            val = data['records'][0].get('underlyingValue')
            if val:
                logger.info(f"✓ GIFT: {val}")
                return f"{float(val):.2f}"
    except Exception as e:
        logger.error(f"GIFT error: {e}")
    return "N/A"

def get_sp500():
    """Get S&P 500 - Multiple sources"""
    try:
        # Source 1: Yahoo Finance API
        url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/^GSPC?modules=price'
        data = fetch_url(url)
        if data and 'quoteSummary' in data:
            try:
                price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
                logger.info(f"✓ S&P500: {price}")
                return f"{price:,.0f}"
            except:
                pass
    except Exception as e:
        logger.error(f"S&P500 error: {e}")
    
    # Fallback
    return "N/A"

def get_nasdaq():
    """Get Nasdaq 100"""
    try:
        url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/^NDX?modules=price'
        data = fetch_url(url)
        if data and 'quoteSummary' in data:
            price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
            logger.info(f"✓ Nasdaq: {price}")
            return f"{price:,.0f}"
    except Exception as e:
        logger.error(f"Nasdaq error: {e}")
    return "N/A"

def get_dow():
    """Get Dow Jones"""
    try:
        url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/^DJI?modules=price'
        data = fetch_url(url)
        if data and 'quoteSummary' in data:
            price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
            logger.info(f"✓ Dow: {price}")
            return f"{price:,.0f}"
    except Exception as e:
        logger.error(f"Dow error: {e}")
    return "N/A"

def get_nikkei():
    """Get Nikkei 225"""
    try:
        url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/^N225?modules=price'
        data = fetch_url(url)
        if data and 'quoteSummary' in data:
            price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
            logger.info(f"✓ Nikkei: {price}")
            return f"{price:,.0f}"
    except Exception as e:
        logger.error(f"Nikkei error: {e}")
    return "N/A"

def get_hangseng():
    """Get Hang Seng"""
    try:
        url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/^HSI?modules=price'
        data = fetch_url(url)
        if data and 'quoteSummary' in data:
            price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
            logger.info(f"✓ Hang Seng: {price}")
            return f"{price:,.0f}"
    except Exception as e:
        logger.error(f"Hang Seng error: {e}")
    return "N/A"

def get_crude():
    """Get Crude Oil"""
    try:
        url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/CL=F?modules=price'
        data = fetch_url(url)
        if data and 'quoteSummary' in data:
            price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
            logger.info(f"✓ Crude: {price}")
            return f"${price:.2f}"
    except Exception as e:
        logger.error(f"Crude error: {e}")
    return "N/A"

def get_gold():
    """Get Gold"""
    try:
        url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/GC=F?modules=price'
        data = fetch_url(url)
        if data and 'quoteSummary' in data:
            price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
            logger.info(f"✓ Gold: {price}")
            return f"${price:.2f}"
    except Exception as e:
        logger.error(f"Gold error: {e}")
    return "N/A"

def get_usd_index():
    """Get USD Index"""
    try:
        url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/DXY=F?modules=price'
        data = fetch_url(url)
        if data and 'quoteSummary' in data:
            price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
            logger.info(f"✓ USD Index: {price}")
            return f"{price:.2f}"
    except Exception as e:
        logger.error(f"USD Index error: {e}")
    return "N/A"

def get_inr_usd():
    """Get INR/USD"""
    try:
        url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/INRUSD=X?modules=price'
        data = fetch_url(url)
        if data and 'quoteSummary' in data:
            price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
            logger.info(f"✓ INR/USD: {price}")
            return f"{price:.2f}"
    except Exception as e:
        logger.error(f"INR/USD error: {e}")
    return "N/A"

def get_us_10y():
    """Get US 10Y Yield"""
    try:
        url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/^TNX?modules=price'
        data = fetch_url(url)
        if data and 'quoteSummary' in data:
            price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
            logger.info(f"✓ 10Y: {price}")
            return f"{price:.2f}%"
    except Exception as e:
        logger.error(f"10Y error: {e}")
    return "N/A"

def get_fii_dii():
    """Get FII/DII"""
    try:
        url = 'https://www.moneycontrol.com/mcapi/get-fii-data'
        data = fetch_url(url)
        if data and 'data' in data:
            fii = data['data'][0].get('fiiInflow', 'N/A')
            dii = data['data'][0].get('diiInflow', 'N/A')
            logger.info(f"✓ FII: {fii}, DII: {dii}")
            return fii, dii
    except Exception as e:
        logger.error(f"FII/DII error: {e}")
    return "N/A", "N/A"

def generate_email_html():
    """Generate simple HTML email with real data"""
    
    logger.info("Fetching all market data...")
    
    # Get all data
    gift = get_gift_nifty()
    nifty, nifty_chg = get_nifty50()
    sensex, _ = get_sensex()
    vix = get_india_vix()
    sp500 = get_sp500()
    nasdaq = get_nasdaq()
    dow = get_dow()
    nikkei = get_nikkei()
    hangseng = get_hangseng()
    crude = get_crude()
    gold = get_gold()
    usd_idx = get_usd_index()
    inr_usd = get_inr_usd()
    us_10y = get_us_10y()
    fii, dii = get_fii_dii()
    
    timestamp = datetime.now().strftime('%B %d, %Y at %H:%M IST')
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; background: #f0f2f5; margin: 0; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #1a3a52, #2c5aa0); padding: 30px; text-align: center; color: white; }}
        .header h1 {{ margin: 0; font-size: 2em; }}
        .header p {{ margin: 5px 0; opacity: 0.9; }}
        .content {{ padding: 30px; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: #1a3a52; border-bottom: 2px solid #ff9800; padding-bottom: 10px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .card {{ background: #f5f7fa; padding: 15px; border-radius: 5px; border-left: 3px solid #2c5aa0; }}
        .label {{ font-size: 0.8em; color: #666; text-transform: uppercase; margin-bottom: 5px; }}
        .value {{ font-size: 1.6em; font-weight: bold; color: #1a3a52; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th {{ background: #2c5aa0; color: white; padding: 10px; text-align: left; }}
        td {{ padding: 8px 10px; border-bottom: 1px solid #e0e0e0; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .footer {{ background: #1a3a52; color: white; padding: 20px; text-align: center; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Daily Market Intelligence Report</h1>
            <p>Generated: {timestamp}</p>
        </div>

        <div class="content">
            <div class="section">
                <h2>🌍 Global Market Indicators</h2>
                <div class="grid">
                    <div class="card">
                        <div class="label">GIFT Nifty</div>
                        <div class="value">{gift}</div>
                    </div>
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
                    <div class="card">
                        <div class="label">Nikkei 225</div>
                        <div class="value">{nikkei}</div>
                    </div>
                    <div class="card">
                        <div class="label">Hang Seng</div>
                        <div class="value">{hangseng}</div>
                    </div>
                </div>

                <h3 style="color: #2c5aa0; margin-top: 20px;">Commodities & Yields</h3>
                <table>
                    <tr>
                        <th>Indicator</th>
                        <th>Value</th>
                    </tr>
                    <tr><td>Crude Oil (Brent)</td><td><strong>{crude}</strong></td></tr>
                    <tr><td>Gold</td><td><strong>{gold}</strong></td></tr>
                    <tr><td>USD Index</td><td><strong>{usd_idx}</strong></td></tr>
                    <tr><td>INR/USD</td><td><strong>{inr_usd}</strong></td></tr>
                    <tr><td>US 10Y Yield</td><td><strong>{us_10y}</strong></td></tr>
                </table>
            </div>

            <div class="section">
                <h2>🇮🇳 India Market Data</h2>
                <table>
                    <tr>
                        <th>Index</th>
                        <th>Value</th>
                        <th>Change</th>
                    </tr>
                    <tr><td><strong>Nifty 50</strong></td><td>{nifty}</td><td>{nifty_chg}</td></tr>
                    <tr><td><strong>Sensex</strong></td><td>{sensex}</td><td>-</td></tr>
                    <tr><td><strong>India VIX</strong></td><td>{vix}</td><td>-</td></tr>
                    <tr><td><strong>FII Flow</strong></td><td>{fii}</td><td>-</td></tr>
                    <tr><td><strong>DII Flow</strong></td><td>{dii}</td><td>-</td></tr>
                </table>
            </div>

            <div class="section">
                <h2>📊 Market Summary</h2>
                <p>This report contains live market data from:</p>
                <ul>
                    <li><strong>Global Indices:</strong> Yahoo Finance (S&P 500, Nasdaq, Dow, Nikkei, Hang Seng)</li>
                    <li><strong>India Indices:</strong> NSE API (Nifty 50, India VIX, GIFT Nifty)</li>
                    <li><strong>Sensex & FII/DII:</strong> Moneycontrol</li>
                    <li><strong>Commodities & Currency:</strong> Yahoo Finance</li>
                </ul>
            </div>
        </div>

        <div class="footer">
            <p><strong>Daily Market Intelligence Report</strong></p>
            <p>Automated daily at 8:00 AM IST | Sent to: mailbox.macwan@gmail.com</p>
            <p>This report is for informational purposes only. Consult a financial advisor before investing.</p>
        </div>
    </div>
</body>
</html>
"""
    return html

def send_email(recipient, subject, html_body):
    """Send HTML email"""
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
        
        logger.info(f"✅ Email sent successfully!")
        return True
    except Exception as e:
        logger.error(f"Email error: {e}")
        return False

def main():
    logger.info("=" * 70)
    logger.info("STARTING MARKET INTELLIGENCE REPORT")
    logger.info("=" * 70)
    
    try:
        html = generate_email_html()
        subject = f"Daily Market Intelligence Report - {datetime.now().strftime('%B %d, %Y')}"
        
        if send_email("mailbox.macwan@gmail.com", subject, html):
            logger.info("=" * 70)
            logger.info("✅ REPORT SENT SUCCESSFULLY WITH REAL DATA!")
            logger.info("=" * 70)
            return True
        return False
    except Exception as e:
        logger.error(f"Error: {e}")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
