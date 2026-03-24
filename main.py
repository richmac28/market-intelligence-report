#!/usr/bin/env python3
"""
📊 YFINANCE-BASED MARKET INTELLIGENCE REPORT
Most reliable approach - using yfinance library
"""

import yfinance as yf
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

class YfinanceMarketCollector:
    """Using yfinance library - most reliable"""
    
    def __init__(self):
        self.data = {}

    def fetch_index(self, symbol, display_name):
        """Fetch any index using yfinance"""
        try:
            logger.info(f"Fetching {display_name} ({symbol})...")
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # yfinance returns currentPrice or regularMarketPrice
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            
            if price:
                logger.info(f"✓ {display_name}: {price}")
                return price
            else:
                logger.warning(f"Could not get price for {display_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching {display_name}: {e}")
            return None

    def collect_all(self):
        """Collect all data using yfinance"""
        logger.info("\n" + "="*100)
        logger.info("COLLECTING DATA WITH YFINANCE")
        logger.info("="*100)
        
        # Indian Indices
        logger.info("\n--- INDIAN INDICES ---")
        nifty50 = self.fetch_index('^NSEI', 'Nifty 50')
        if nifty50:
            self.data['nifty50'] = {'value': f'{nifty50:,.2f}', 'source': 'Yfinance'}
        
        time.sleep(1)
        
        sensex = self.fetch_index('^BSESN', 'Sensex')
        if sensex:
            self.data['sensex'] = {'value': f'{sensex:,.2f}', 'source': 'Yfinance'}
        
        time.sleep(1)
        
        nifty_bank = self.fetch_index('^NSEBANK', 'Nifty Bank')
        if nifty_bank:
            self.data['nifty_bank'] = {'value': f'{nifty_bank:,.2f}', 'source': 'Yfinance'}
        
        time.sleep(1)
        
        vix = self.fetch_index('^VIX', 'India VIX')
        if vix:
            self.data['vix'] = {'value': f'{vix:.2f}', 'source': 'Yfinance'}
        
        # US Indices
        logger.info("\n--- US INDICES ---")
        sp500 = self.fetch_index('^GSPC', 'S&P 500')
        if sp500:
            self.data['sp500'] = {'value': f'{sp500:,.2f}', 'source': 'Yfinance'}
        
        time.sleep(1)
        
        nasdaq = self.fetch_index('^IXIC', 'Nasdaq 100')
        if nasdaq:
            self.data['nasdaq'] = {'value': f'{nasdaq:,.2f}', 'source': 'Yfinance'}
        
        time.sleep(1)
        
        dow = self.fetch_index('^DJI', 'Dow Jones')
        if dow:
            self.data['dow'] = {'value': f'{dow:,.2f}', 'source': 'Yfinance'}
        
        # Europe Indices
        logger.info("\n--- EUROPE INDICES ---")
        ftse = self.fetch_index('^FTSE', 'FTSE 100')
        if ftse:
            self.data['ftse'] = {'value': f'{ftse:,.2f}', 'source': 'Yfinance'}
        
        time.sleep(1)
        
        dax = self.fetch_index('^GDAXI', 'DAX')
        if dax:
            self.data['dax'] = {'value': f'{dax:,.2f}', 'source': 'Yfinance'}
        
        time.sleep(1)
        
        cac = self.fetch_index('^FCHI', 'CAC 40')
        if cac:
            self.data['cac'] = {'value': f'{cac:,.2f}', 'source': 'Yfinance'}
        
        # Cryptocurrency
        logger.info("\n--- CRYPTOCURRENCY ---")
        btc = self.fetch_index('BTC-USD', 'Bitcoin')
        if btc:
            self.data['btc'] = {'value': f'${btc:,.2f}', 'source': 'Yfinance'}
        
        time.sleep(1)
        
        eth = self.fetch_index('ETH-USD', 'Ethereum')
        if eth:
            self.data['eth'] = {'value': f'${eth:,.2f}', 'source': 'Yfinance'}
        
        # Commodities
        logger.info("\n--- COMMODITIES ---")
        gold = self.fetch_index('GC=F', 'Gold')
        if gold:
            self.data['gold'] = {'value': f'${gold:,.2f}', 'source': 'Yfinance'}
        
        time.sleep(1)
        
        silver = self.fetch_index('SI=F', 'Silver')
        if silver:
            self.data['silver'] = {'value': f'${silver:,.2f}', 'source': 'Yfinance'}
        
        time.sleep(1)
        
        crude = self.fetch_index('CL=F', 'Crude Oil')
        if crude:
            self.data['crude'] = {'value': f'${crude:,.2f}', 'source': 'Yfinance'}
        
        # Currency
        logger.info("\n--- CURRENCY ---")
        usd = self.fetch_index('DXY=F', 'USD Index')
        if usd:
            self.data['usd'] = {'value': f'{usd:,.2f}', 'source': 'Yfinance'}
        
        time.sleep(1)
        
        inr_usd = self.fetch_index('INRUSD=X', 'INR/USD')
        if inr_usd:
            self.data['inr_usd'] = {'value': f'{inr_usd:,.2f}', 'source': 'Yfinance'}
        
        logger.info("\n" + "="*100)
        logger.info(f"Collected {len(self.data)} data points")
        logger.info("="*100 + "\n")
        
        return self.data


def create_html(data):
    """Create professional HTML email"""
    ts = datetime.now().strftime('%B %d, %Y at %H:%M IST')
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px; }}
        .wrapper {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #1a3a52, #2c5aa0); color: white; padding: 50px 40px; border-radius: 12px 12px 0 0; text-align: center; }}
        .header h1 {{ font-size: 2.8em; margin-bottom: 10px; font-weight: 700; }}
        .timestamp {{ background: rgba(255,255,255,0.15); padding: 10px 20px; border-radius: 20px; display: inline-block; margin-top: 15px; font-size: 0.95em; }}
        .content {{ background: white; padding: 50px 40px; }}
        .section {{ margin-bottom: 50px; }}
        .section h2 {{ color: #1a3a52; font-size: 1.9em; margin-bottom: 30px; padding-bottom: 15px; border-bottom: 3px solid #ff9800; font-weight: 700; }}
        table {{ width: 100%; border-collapse: collapse; margin: 25px 0; border: 2px solid #e0e7ff; border-radius: 8px; overflow: hidden; }}
        th {{ background: linear-gradient(135deg, #2c5aa0, #1a3a52); color: white; padding: 18px; text-align: left; font-weight: 700; text-transform: uppercase; font-size: 0.95em; }}
        td {{ padding: 16px 18px; border-bottom: 1px solid #f0f0f0; }}
        tr:nth-child(even) {{ background: #f8f9ff; }}
        .value {{ font-weight: 700; color: #1a3a52; font-size: 1.1em; }}
        .footer {{ background: linear-gradient(135deg, #1a3a52, #2c5aa0); color: white; padding: 40px; border-radius: 0 0 12px 12px; text-align: center; font-size: 0.95em; }}
        .footer p {{ margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="header">
            <h1>📊 Daily Market Intelligence Report</h1>
            <p>Global Markets | Live Data</p>
            <div class="timestamp">{ts}</div>
        </div>

        <div class="content">
            <!-- INDIAN MARKET -->
            <div class="section">
                <h2>🇮🇳 Indian Market</h2>
                <table>
                    <tr><th>Index</th><th>Value</th><th>Source</th></tr>
                    <tr>
                        <td><strong>Nifty 50</strong></td>
                        <td class="value">{data.get('nifty50', {}).get('value', 'N/A')}</td>
                        <td>{data.get('nifty50', {}).get('source', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td><strong>Sensex</strong></td>
                        <td class="value">{data.get('sensex', {}).get('value', 'N/A')}</td>
                        <td>{data.get('sensex', {}).get('source', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td><strong>Nifty Bank</strong></td>
                        <td class="value">{data.get('nifty_bank', {}).get('value', 'N/A')}</td>
                        <td>{data.get('nifty_bank', {}).get('source', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td><strong>India VIX</strong></td>
                        <td class="value">{data.get('vix', {}).get('value', 'N/A')}</td>
                        <td>{data.get('vix', {}).get('source', 'N/A')}</td>
                    </tr>
                </table>
            </div>

            <!-- US MARKET -->
            <div class="section">
                <h2>🇺🇸 US Market</h2>
                <table>
                    <tr><th>Index</th><th>Value</th><th>Source</th></tr>
                    <tr>
                        <td><strong>S&P 500</strong></td>
                        <td class="value">{data.get('sp500', {}).get('value', 'N/A')}</td>
                        <td>{data.get('sp500', {}).get('source', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td><strong>Nasdaq 100</strong></td>
                        <td class="value">{data.get('nasdaq', {}).get('value', 'N/A')}</td>
                        <td>{data.get('nasdaq', {}).get('source', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td><strong>Dow Jones</strong></td>
                        <td class="value">{data.get('dow', {}).get('value', 'N/A')}</td>
                        <td>{data.get('dow', {}).get('source', 'N/A')}</td>
                    </tr>
                </table>
            </div>

            <!-- EUROPE MARKET -->
            <div class="section">
                <h2>🇪🇺 Europe Market</h2>
                <table>
                    <tr><th>Index</th><th>Country</th><th>Value</th><th>Source</th></tr>
                    <tr>
                        <td><strong>FTSE 100</strong></td>
                        <td>UK</td>
                        <td class="value">{data.get('ftse', {}).get('value', 'N/A')}</td>
                        <td>{data.get('ftse', {}).get('source', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td><strong>DAX</strong></td>
                        <td>Germany</td>
                        <td class="value">{data.get('dax', {}).get('value', 'N/A')}</td>
                        <td>{data.get('dax', {}).get('source', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td><strong>CAC 40</strong></td>
                        <td>France</td>
                        <td class="value">{data.get('cac', {}).get('value', 'N/A')}</td>
                        <td>{data.get('cac', {}).get('source', 'N/A')}</td>
                    </tr>
                </table>
            </div>

            <!-- CRYPTOCURRENCY -->
            <div class="section">
                <h2>₿ Cryptocurrency</h2>
                <table>
                    <tr><th>Asset</th><th>Price</th><th>Source</th></tr>
                    <tr>
                        <td><strong>Bitcoin</strong></td>
                        <td class="value">{data.get('btc', {}).get('value', 'N/A')}</td>
                        <td>{data.get('btc', {}).get('source', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td><strong>Ethereum</strong></td>
                        <td class="value">{data.get('eth', {}).get('value', 'N/A')}</td>
                        <td>{data.get('eth', {}).get('source', 'N/A')}</td>
                    </tr>
                </table>
            </div>

            <!-- COMMODITIES & CURRENCY -->
            <div class="section">
                <h2>💎 Commodities & Currency</h2>
                <table>
                    <tr><th>Asset</th><th>Price</th><th>Source</th></tr>
                    <tr>
                        <td><strong>Gold</strong></td>
                        <td class="value">{data.get('gold', {}).get('value', 'N/A')}</td>
                        <td>{data.get('gold', {}).get('source', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td><strong>Silver</strong></td>
                        <td class="value">{data.get('silver', {}).get('value', 'N/A')}</td>
                        <td>{data.get('silver', {}).get('source', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td><strong>Crude Oil</strong></td>
                        <td class="value">{data.get('crude', {}).get('value', 'N/A')}</td>
                        <td>{data.get('crude', {}).get('source', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td><strong>USD Index</strong></td>
                        <td class="value">{data.get('usd', {}).get('value', 'N/A')}</td>
                        <td>{data.get('usd', {}).get('source', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td><strong>INR/USD</strong></td>
                        <td class="value">{data.get('inr_usd', {}).get('value', 'N/A')}</td>
                        <td>{data.get('inr_usd', {}).get('source', 'N/A')}</td>
                    </tr>
                </table>
            </div>
        </div>

        <div class="footer">
            <p><strong>Daily Market Intelligence Report</strong></p>
            <p>Live Data from Yfinance</p>
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
    logger.info("MARKET INTELLIGENCE REPORT - YFINANCE VERSION")
    logger.info("="*100)
    
    try:
        logger.info("\n[1/2] Collecting market data...")
        collector = YfinanceMarketCollector()
        market_data = collector.collect_all()
        
        logger.info("[2/2] Sending email...")
        html_email = create_html(market_data)
        subject = f"Daily Market Intelligence Report - {datetime.now().strftime('%B %d, %Y')}"
        
        if send_email("mailbox.macwan@gmail.com", subject, html_email):
            logger.info("="*100)
            logger.info("✅ SUCCESS!")
            logger.info("="*100 + "\n")
            return 0
        return 1
            
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}\n")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == '__main__':
    sys.exit(main())
