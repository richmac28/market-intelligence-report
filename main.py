#!/usr/bin/env python3
"""
📊 ROBUST VERSION - Better error handling and multiple fallback methods
"""

import requests
import logging
import smtplib
import os
import sys
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/market_report.log')
    ]
)
logger = logging.getLogger(__name__)

class RobustMarketCollector:
    """Robust collector with better error handling"""
    
    def __init__(self):
        self.data = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def fetch_nse_nifty(self):
        """Fetch Nifty 50 from NSE with detailed error logging"""
        logger.info("\n" + "="*100)
        logger.info("FETCHING: Nifty 50 (NSE)")
        logger.info("="*100)
        
        try:
            url = 'https://www.nseindia.com/api/quote-derivative?symbol=NIFTY'
            logger.info(f"URL: {url}")
            logger.info("Sending request (timeout: 30 seconds)...")
            
            r = self.session.get(url, timeout=30)
            
            logger.info(f"Response Status: {r.status_code}")
            logger.info(f"Response Headers: {dict(r.headers)}")
            
            if r.status_code == 200:
                try:
                    data = r.json()
                    logger.info(f"Response JSON received: {len(json.dumps(data))} characters")
                    logger.info(f"Response keys: {list(data.keys())}")
                    
                    if 'records' in data and len(data['records']) > 0:
                        record = data['records'][0]
                        logger.info(f"Record keys: {list(record.keys())}")
                        
                        # Log all values
                        for key in record.keys():
                            logger.info(f"  {key}: {record[key]}")
                        
                        # Try to extract
                        val = float(record.get('underlyingValue', 0))
                        chg = float(record.get('change', 0))
                        pct = float(record.get('percentChange', 0))
                        
                        self.data['nifty50'] = {
                            'value': f'{val:,.2f}',
                            'change': f'{chg:+.2f}',
                            'pct': f'{pct:+.2f}%',
                            'source': 'NSE'
                        }
                        logger.info(f"✓ SUCCESS: Nifty 50 = {val}")
                        return True
                    else:
                        logger.warning("No records found in response")
                        return False
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    logger.error(f"Response text: {r.text[:500]}")
                    return False
            else:
                logger.error(f"HTTP Error {r.status_code}")
                logger.error(f"Response: {r.text[:500]}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("REQUEST TIMEOUT - Server took too long to respond")
            return False
        except requests.exceptions.ConnectionError as e:
            logger.error(f"CONNECTION ERROR: {e}")
            return False
        except Exception as e:
            logger.error(f"EXCEPTION: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def fetch_yahoo_sp500(self):
        """Fetch S&P 500 from Yahoo Finance with detailed error logging"""
        logger.info("\n" + "="*100)
        logger.info("FETCHING: S&P 500 (Yahoo Finance)")
        logger.info("="*100)
        
        try:
            url = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols=^GSPC&fields=regularMarketPrice,regularMarketChange,regularMarketChangePercent'
            logger.info(f"URL: {url}")
            logger.info("Sending request (timeout: 30 seconds)...")
            
            r = self.session.get(url, timeout=30)
            
            logger.info(f"Response Status: {r.status_code}")
            logger.info(f"Response Headers: {dict(r.headers)}")
            
            if r.status_code == 200:
                try:
                    data = r.json()
                    logger.info(f"Response JSON received: {len(json.dumps(data))} characters")
                    logger.info(f"Response keys: {list(data.keys())}")
                    
                    if 'quoteResponse' in data:
                        logger.info(f"quoteResponse keys: {list(data['quoteResponse'].keys())}")
                        
                        results = data['quoteResponse'].get('result', [])
                        logger.info(f"Number of results: {len(results)}")
                        
                        if len(results) > 0:
                            quote = results[0]
                            logger.info(f"Quote keys: {list(quote.keys())}")
                            
                            # Log all values
                            for key in quote.keys():
                                logger.info(f"  {key}: {quote[key]}")
                            
                            # Try to extract
                            price = quote.get('regularMarketPrice')
                            change = quote.get('regularMarketChange')
                            pct = quote.get('regularMarketChangePercent')
                            
                            if price is not None:
                                self.data['sp500'] = {
                                    'value': f'{float(price):,.2f}',
                                    'change': f'{float(change):+.2f}',
                                    'pct': f'{float(pct):+.2f}%',
                                    'source': 'Yahoo Finance'
                                }
                                logger.info(f"✓ SUCCESS: S&P 500 = {price}")
                                return True
                            else:
                                logger.warning("regularMarketPrice is None")
                                return False
                        else:
                            logger.warning("No results in quoteResponse")
                            return False
                    else:
                        logger.warning("No quoteResponse in data")
                        logger.info(f"Data keys: {list(data.keys())}")
                        return False
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    logger.error(f"Response text: {r.text[:500]}")
                    return False
            else:
                logger.error(f"HTTP Error {r.status_code}")
                logger.error(f"Response: {r.text[:500]}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("REQUEST TIMEOUT - Server took too long to respond")
            return False
        except requests.exceptions.ConnectionError as e:
            logger.error(f"CONNECTION ERROR: {e}")
            return False
        except Exception as e:
            logger.error(f"EXCEPTION: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def fetch_yahoo_nasdaq(self):
        """Fetch Nasdaq from Yahoo Finance"""
        logger.info("\n" + "="*100)
        logger.info("FETCHING: Nasdaq 100 (Yahoo Finance)")
        logger.info("="*100)
        
        try:
            url = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols=^IXIC&fields=regularMarketPrice,regularMarketChange,regularMarketChangePercent'
            logger.info(f"URL: {url}")
            logger.info("Sending request (timeout: 30 seconds)...")
            
            r = self.session.get(url, timeout=30)
            logger.info(f"Response Status: {r.status_code}")
            
            if r.status_code == 200:
                data = r.json()
                logger.info(f"Response received successfully")
                
                results = data.get('quoteResponse', {}).get('result', [])
                if len(results) > 0:
                    quote = results[0]
                    price = quote.get('regularMarketPrice')
                    change = quote.get('regularMarketChange')
                    pct = quote.get('regularMarketChangePercent')
                    
                    if price is not None:
                        self.data['nasdaq'] = {
                            'value': f'{float(price):,.2f}',
                            'change': f'{float(change):+.2f}',
                            'pct': f'{float(pct):+.2f}%',
                            'source': 'Yahoo Finance'
                        }
                        logger.info(f"✓ SUCCESS: Nasdaq = {price}")
                        return True
            
            logger.warning("Failed to fetch Nasdaq")
            return False
            
        except Exception as e:
            logger.error(f"Error fetching Nasdaq: {e}")
            return False

    def fetch_yahoo_dow(self):
        """Fetch Dow Jones from Yahoo Finance"""
        logger.info("\n" + "="*100)
        logger.info("FETCHING: Dow Jones (Yahoo Finance)")
        logger.info("="*100)
        
        try:
            url = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols=^DJI&fields=regularMarketPrice,regularMarketChange,regularMarketChangePercent'
            logger.info(f"URL: {url}")
            
            r = self.session.get(url, timeout=30)
            logger.info(f"Response Status: {r.status_code}")
            
            if r.status_code == 200:
                data = r.json()
                results = data.get('quoteResponse', {}).get('result', [])
                
                if len(results) > 0:
                    quote = results[0]
                    price = quote.get('regularMarketPrice')
                    change = quote.get('regularMarketChange')
                    pct = quote.get('regularMarketChangePercent')
                    
                    if price is not None:
                        self.data['dow'] = {
                            'value': f'{float(price):,.2f}',
                            'change': f'{float(change):+.2f}',
                            'pct': f'{float(pct):+.2f}%',
                            'source': 'Yahoo Finance'
                        }
                        logger.info(f"✓ SUCCESS: Dow = {price}")
                        return True
            
            logger.warning("Failed to fetch Dow")
            return False
            
        except Exception as e:
            logger.error(f"Error fetching Dow: {e}")
            return False

    def collect_all(self):
        """Collect all data"""
        logger.info("\n" + "="*100)
        logger.info("STARTING DATA COLLECTION")
        logger.info("="*100)
        
        self.fetch_nse_nifty()
        time.sleep(2)
        self.fetch_yahoo_sp500()
        time.sleep(2)
        self.fetch_yahoo_nasdaq()
        time.sleep(2)
        self.fetch_yahoo_dow()
        
        logger.info("\n" + "="*100)
        logger.info(f"DATA COLLECTION COMPLETE - Collected {len(self.data)} data points")
        logger.info("="*100)
        
        return self.data


def create_html(data):
    """Create HTML email"""
    ts = datetime.now().strftime('%B %d, %Y at %H:%M IST')
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        .header {{ background: linear-gradient(135deg, #1a3a52, #2c5aa0); color: white; padding: 30px; border-radius: 5px; margin-bottom: 30px; }}
        h1 {{ margin: 0; font-size: 2em; }}
        .subtitle {{ font-size: 0.9em; margin-top: 10px; opacity: 0.9; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #2c5aa0; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 12px; border-bottom: 1px solid #ddd; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .value {{ font-weight: bold; color: #1a3a52; }}
        .footer {{ background: #2c5aa0; color: white; padding: 20px; text-align: center; border-radius: 5px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Daily Market Intelligence Report</h1>
            <div class="subtitle">{ts}</div>
        </div>
        
        <h2>Market Data</h2>
        <table>
            <tr><th>Index</th><th>Value</th><th>Change</th><th>% Change</th><th>Source</th></tr>
"""
    
    # Add data rows
    for key, values in data.items():
        if isinstance(values, dict) and 'value' in values:
            html += f"""
            <tr>
                <td><strong>{key.upper()}</strong></td>
                <td class="value">{values.get('value', 'N/A')}</td>
                <td>{values.get('change', 'N/A')}</td>
                <td>{values.get('pct', 'N/A')}</td>
                <td>{values.get('source', 'N/A')}</td>
            </tr>
"""
    
    html += """
        </table>
        
        <div class="footer">
            <p><strong>Daily Market Intelligence Report</strong></p>
            <p>8:00 AM IST | mailbox.macwan@gmail.com</p>
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
        
        logger.info("Preparing to send email...")
        
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = recipient
        message.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        logger.info(f"Connecting to SMTP server...")
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, message.as_string())
        
        logger.info("✅ Email sent successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Email error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    logger.info("\n" + "="*100)
    logger.info("ROBUST MARKET INTELLIGENCE REPORT SYSTEM")
    logger.info("="*100)
    
    try:
        logger.info("\n[1/2] Collecting market data...")
        collector = RobustMarketCollector()
        market_data = collector.collect_all()
        
        logger.info("\n[2/2] Generating and sending email...")
        logger.info(f"Collected {len(market_data)} data points: {list(market_data.keys())}")
        
        html_email = create_html(market_data)
        subject = f"Daily Market Intelligence Report - {datetime.now().strftime('%B %d, %Y')}"
        
        if send_email("mailbox.macwan@gmail.com", subject, html_email):
            logger.info("="*100)
            logger.info("✅ COMPLETE SUCCESS!")
            logger.info("="*100 + "\n")
            return 0
        
        logger.error("Failed to send email")
        return 1
            
    except Exception as e:
        logger.error(f"\n❌ CRITICAL ERROR: {e}\n")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == '__main__':
    sys.exit(main())
