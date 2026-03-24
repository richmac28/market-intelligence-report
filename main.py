#!/usr/bin/env python3
"""
📊 SIMPLE HYBRID SOLUTION
Reads real market data from market_data.json file
User updates the file daily with actual values from NSE/Yahoo Finance
Script automates the email sending
"""

import json
import logging
import smtplib
import os
import sys
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_market_data():
    """Load market data from JSON file"""
    logger.info("\n" + "="*100)
    logger.info("LOADING MARKET DATA FROM FILE")
    logger.info("="*100)
    
    try:
        # Try to load from market_data.json in repo
        with open('market_data.json', 'r') as f:
            data = json.load(f)
            logger.info("✓ market_data.json loaded successfully")
            logger.info(f"  Data date: {data.get('date')}")
            logger.info(f"  Timestamp: {data.get('timestamp')}")
            logger.info(f"  Number of data points: {len(data.get('data', {}))}")
            return data
    except FileNotFoundError:
        logger.error("market_data.json not found!")
        logger.error("Make sure market_data.json exists in the repository root")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return None


def create_html(market_data):
    """Create professional HTML email from market data"""
    if not market_data:
        logger.error("No market data to create HTML")
        return None
    
    ts = datetime.now().strftime('%B %d, %Y at %H:%M IST')
    data = market_data.get('data', {})
    
    def val(key, field='value', default='N/A'):
        return data.get(key, {}).get(field, default)
    
    def source(key):
        return data.get(key, {}).get('source', 'N/A')
    
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
        .section h3 {{ color: #2c5aa0; font-size: 1.3em; margin: 30px 0 20px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 25px 0; border: 2px solid #e0e7ff; border-radius: 8px; overflow: hidden; }}
        th {{ background: linear-gradient(135deg, #2c5aa0, #1a3a52); color: white; padding: 18px; text-align: left; font-weight: 700; text-transform: uppercase; font-size: 0.95em; }}
        td {{ padding: 16px 18px; border-bottom: 1px solid #f0f0f0; }}
        tr:nth-child(even) {{ background: #f8f9ff; }}
        .value {{ font-weight: 700; color: #1a3a52; font-size: 1.05em; }}
        .change {{ font-weight: 600; }}
        .positive {{ color: #27ae60; }}
        .negative {{ color: #e74c3c; }}
        .footer {{ background: linear-gradient(135deg, #1a3a52, #2c5aa0); color: white; padding: 40px; border-radius: 0 0 12px 12px; text-align: center; font-size: 0.95em; }}
        .footer p {{ margin: 10px 0; }}
        .data-info {{ background: #f0f9ff; border-left: 4px solid #2c5aa0; padding: 15px; border-radius: 5px; margin: 20px 0; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="header">
            <h1>📊 Daily Market Intelligence Report</h1>
            <p>Live Market Data from Real Sources</p>
            <div class="timestamp">{ts}</div>
        </div>

        <div class="content">
            <!-- DATA SOURCE INFO -->
            <div class="data-info">
                <strong>📅 Data Date:</strong> {market_data.get('date', 'N/A')} | <strong>⏰ Time:</strong> {market_data.get('timestamp', 'N/A')}
            </div>

            <!-- INDIAN MARKET -->
            <div class="section">
                <h2>🇮🇳 Indian Market</h2>
                <h3>Core Indices</h3>
                <table>
                    <tr><th>Index</th><th>Value</th><th>Change</th><th>% Change</th><th>Source</th></tr>
                    <tr>
                        <td><strong>Nifty 50</strong></td>
                        <td class="value">{val('nifty50')}</td>
                        <td class="change {'positive' if float(val('nifty50', 'change', '0')) >= 0 else 'negative'}">{val('nifty50', 'change')}</td>
                        <td>{val('nifty50', 'pct')}</td>
                        <td>{source('nifty50')}</td>
                    </tr>
                    <tr>
                        <td><strong>Sensex</strong></td>
                        <td class="value">{val('sensex')}</td>
                        <td class="change {'positive' if float(val('sensex', 'change', '0')) >= 0 else 'negative'}">{val('sensex', 'change')}</td>
                        <td>{val('sensex', 'pct')}</td>
                        <td>{source('sensex')}</td>
                    </tr>
                    <tr>
                        <td><strong>India VIX</strong></td>
                        <td class="value">{val('vix')}</td>
                        <td>-</td>
                        <td>-</td>
                        <td>{source('vix')}</td>
                    </tr>
                </table>

                <h3>Sectoral Indices</h3>
                <table>
                    <tr><th>Index</th><th>Value</th><th>Change</th><th>% Change</th><th>Source</th></tr>
                    <tr>
                        <td><strong>Nifty Bank</strong></td>
                        <td class="value">{val('nifty_bank')}</td>
                        <td class="change {'positive' if float(val('nifty_bank', 'change', '0')) >= 0 else 'negative'}">{val('nifty_bank', 'change')}</td>
                        <td>{val('nifty_bank', 'pct')}</td>
                        <td>{source('nifty_bank')}</td>
                    </tr>
                    <tr>
                        <td><strong>Nifty Midcap 100</strong></td>
                        <td class="value">{val('nifty_midcap100')}</td>
                        <td class="change {'positive' if float(val('nifty_midcap100', 'change', '0')) >= 0 else 'negative'}">{val('nifty_midcap100', 'change')}</td>
                        <td>{val('nifty_midcap100', 'pct')}</td>
                        <td>{source('nifty_midcap100')}</td>
                    </tr>
                    <tr>
                        <td><strong>Nifty Smallcap 250</strong></td>
                        <td class="value">{val('nifty_smallcap250')}</td>
                        <td class="change {'positive' if float(val('nifty_smallcap250', 'change', '0')) >= 0 else 'negative'}">{val('nifty_smallcap250', 'change')}</td>
                        <td>{val('nifty_smallcap250', 'pct')}</td>
                        <td>{source('nifty_smallcap250')}</td>
                    </tr>
                </table>
            </div>

            <!-- US MARKET -->
            <div class="section">
                <h2>🇺🇸 US Market Indices</h2>
                <table>
                    <tr><th>Index</th><th>Value</th><th>Change</th><th>% Change</th><th>Source</th></tr>
                    <tr>
                        <td><strong>S&P 500</strong></td>
                        <td class="value">{val('sp500')}</td>
                        <td class="change {'positive' if float(val('sp500', 'change', '0')) >= 0 else 'negative'}">{val('sp500', 'change')}</td>
                        <td>{val('sp500', 'pct')}</td>
                        <td>{source('sp500')}</td>
                    </tr>
                    <tr>
                        <td><strong>Nasdaq 100</strong></td>
                        <td class="value">{val('nasdaq')}</td>
                        <td class="change {'positive' if float(val('nasdaq', 'change', '0')) >= 0 else 'negative'}">{val('nasdaq', 'change')}</td>
                        <td>{val('nasdaq', 'pct')}</td>
                        <td>{source('nasdaq')}</td>
                    </tr>
                    <tr>
                        <td><strong>Dow Jones</strong></td>
                        <td class="value">{val('dow')}</td>
                        <td class="change {'positive' if float(val('dow', 'change', '0')) >= 0 else 'negative'}">{val('dow', 'change')}</td>
                        <td>{val('dow', 'pct')}</td>
                        <td>{source('dow')}</td>
                    </tr>
                </table>
            </div>

            <!-- EUROPE MARKET -->
            <div class="section">
                <h2>🇪🇺 Europe Market Indices</h2>
                <table>
                    <tr><th>Market</th><th>Country</th><th>Value</th><th>Change</th><th>% Change</th><th>Source</th></tr>
                    <tr>
                        <td><strong>FTSE 100</strong></td>
                        <td>UK</td>
                        <td class="value">{val('ftse')}</td>
                        <td class="change {'positive' if float(val('ftse', 'change', '0')) >= 0 else 'negative'}">{val('ftse', 'change')}</td>
                        <td>{val('ftse', 'pct')}</td>
                        <td>{source('ftse')}</td>
                    </tr>
                    <tr>
                        <td><strong>DAX</strong></td>
                        <td>Germany</td>
                        <td class="value">{val('dax')}</td>
                        <td class="change {'positive' if float(val('dax', 'change', '0')) >= 0 else 'negative'}">{val('dax', 'change')}</td>
                        <td>{val('dax', 'pct')}</td>
                        <td>{source('dax')}</td>
                    </tr>
                    <tr>
                        <td><strong>CAC 40</strong></td>
                        <td>France</td>
                        <td class="value">{val('cac')}</td>
                        <td class="change {'positive' if float(val('cac', 'change', '0')) >= 0 else 'negative'}">{val('cac', 'change')}</td>
                        <td>{val('cac', 'pct')}</td>
                        <td>{source('cac')}</td>
                    </tr>
                </table>
            </div>

            <!-- CRYPTOCURRENCY -->
            <div class="section">
                <h2>₿ Major Cryptocurrencies</h2>
                <table>
                    <tr><th>Asset</th><th>Price</th><th>Change</th><th>% Change</th><th>Source</th></tr>
                    <tr>
                        <td><strong>Bitcoin</strong></td>
                        <td class="value">${val('btc')}</td>
                        <td class="change {'positive' if float(val('btc', 'change', '0')) >= 0 else 'negative'}">{val('btc', 'change')}</td>
                        <td>{val('btc', 'pct')}</td>
                        <td>{source('btc')}</td>
                    </tr>
                    <tr>
                        <td><strong>Ethereum</strong></td>
                        <td class="value">${val('eth')}</td>
                        <td class="change {'positive' if float(val('eth', 'change', '0')) >= 0 else 'negative'}">{val('eth', 'change')}</td>
                        <td>{val('eth', 'pct')}</td>
                        <td>{source('eth')}</td>
                    </tr>
                </table>
            </div>

            <!-- COMMODITIES & CURRENCY -->
            <div class="section">
                <h2>💎 Commodities & Currency</h2>
                <table>
                    <tr><th>Asset</th><th>Price</th><th>Change</th><th>% Change</th><th>Source</th></tr>
                    <tr>
                        <td><strong>Gold (per oz)</strong></td>
                        <td class="value">${val('gold')}</td>
                        <td class="change {'positive' if float(val('gold', 'change', '0')) >= 0 else 'negative'}">{val('gold', 'change')}</td>
                        <td>{val('gold', 'pct')}</td>
                        <td>{source('gold')}</td>
                    </tr>
                    <tr>
                        <td><strong>Silver (per oz)</strong></td>
                        <td class="value">${val('silver')}</td>
                        <td class="change {'positive' if float(val('silver', 'change', '0')) >= 0 else 'negative'}">{val('silver', 'change')}</td>
                        <td>{val('silver', 'pct')}</td>
                        <td>{source('silver')}</td>
                    </tr>
                    <tr>
                        <td><strong>Crude Oil (Brent)</strong></td>
                        <td class="value">${val('crude')}</td>
                        <td class="change {'positive' if float(val('crude', 'change', '0')) >= 0 else 'negative'}">{val('crude', 'change')}</td>
                        <td>{val('crude', 'pct')}</td>
                        <td>{source('crude')}</td>
                    </tr>
                    <tr>
                        <td><strong>USD Index</strong></td>
                        <td class="value">{val('usd')}</td>
                        <td class="change {'positive' if float(val('usd', 'change', '0')) >= 0 else 'negative'}">{val('usd', 'change')}</td>
                        <td>{val('usd', 'pct')}</td>
                        <td>{source('usd')}</td>
                    </tr>
                    <tr>
                        <td><strong>INR/USD</strong></td>
                        <td class="value">{val('inr_usd')}</td>
                        <td class="change {'positive' if float(val('inr_usd', 'change', '0')) >= 0 else 'negative'}">{val('inr_usd', 'change')}</td>
                        <td>{val('inr_usd', 'pct')}</td>
                        <td>{source('inr_usd')}</td>
                    </tr>
                    <tr>
                        <td><strong>US 10Y Treasury Yield</strong></td>
                        <td class="value">{val('us_10y')}%</td>
                        <td class="change {'positive' if float(val('us_10y', 'change', '0')) >= 0 else 'negative'}">{val('us_10y', 'change')}</td>
                        <td>{val('us_10y', 'pct')}</td>
                        <td>{source('us_10y')}</td>
                    </tr>
                </table>
            </div>
        </div>

        <div class="footer">
            <p><strong>Daily Market Intelligence Report</strong></p>
            <p>Comprehensive Global Market Analysis</p>
            <p>8:00 AM IST Daily | mailbox.macwan@gmail.com</p>
            <p style="margin-top: 20px; opacity: 0.9;"><em>Data sourced from NSE, Yahoo Finance, and official market sources</em></p>
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
    logger.info("DAILY MARKET INTELLIGENCE REPORT")
    logger.info("JSON-BASED SOLUTION")
    logger.info("="*100)
    
    try:
        logger.info("\n[1/2] Loading market data from file...")
        market_data = load_market_data()
        
        if not market_data:
            logger.error("Failed to load market data!")
            return 1
        
        logger.info("\n[2/2] Generating and sending email...")
        html_email = create_html(market_data)
        
        if not html_email:
            logger.error("Failed to create HTML!")
            return 1
        
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
