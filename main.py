#!/usr/bin/env python3
"""
📊 DEBUG VERSION - Shows what APIs are actually returning
This helps us identify the exact field names and structure
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DebugCollector:
    """Debug version that shows actual API responses"""
    
    def __init__(self):
        self.data = {}

    def test_nse_api(self):
        """Test NSE API and print full response"""
        logger.info("\n" + "="*100)
        logger.info("TEST 1: NSE NIFTY 50 API")
        logger.info("="*100)
        
        try:
            url = 'https://www.nseindia.com/api/quote-derivative?symbol=NIFTY'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            logger.info(f"Requesting: {url}")
            r = requests.get(url, headers=headers, timeout=15)
            logger.info(f"Status Code: {r.status_code}")
            
            if r.status_code == 200:
                response_json = r.json()
                logger.info(f"FULL RESPONSE:\n{json.dumps(response_json, indent=2)}")
                
                # Try to extract data
                if 'records' in response_json:
                    logger.info(f"✓ Found 'records' key")
                    logger.info(f"  Number of records: {len(response_json['records'])}")
                    
                    if len(response_json['records']) > 0:
                        record = response_json['records'][0]
                        logger.info(f"  Record keys: {list(record.keys())}")
                        logger.info(f"  First record data:\n{json.dumps(record, indent=2)}")
                        
                        # Log all available values
                        logger.info("\n  ALL AVAILABLE FIELDS:")
                        for key, value in record.items():
                            logger.info(f"    {key}: {value}")
                else:
                    logger.warning("No 'records' key found in response!")
                    logger.warning(f"Response keys: {list(response_json.keys())}")
            else:
                logger.error(f"Failed: HTTP {r.status_code}")
                logger.error(f"Response: {r.text}")
                
        except Exception as e:
            logger.error(f"Exception: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def test_yahoo_api(self):
        """Test Yahoo Finance API and print full response"""
        logger.info("\n" + "="*100)
        logger.info("TEST 2: YAHOO FINANCE S&P 500 API")
        logger.info("="*100)
        
        try:
            url = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols=^GSPC&fields=regularMarketPrice,regularMarketChange,regularMarketChangePercent'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            logger.info(f"Requesting: {url}")
            r = requests.get(url, headers=headers, timeout=15)
            logger.info(f"Status Code: {r.status_code}")
            
            if r.status_code == 200:
                response_json = r.json()
                logger.info(f"FULL RESPONSE:\n{json.dumps(response_json, indent=2)}")
                
                # Try to extract data
                if 'quoteResponse' in response_json:
                    logger.info(f"✓ Found 'quoteResponse' key")
                    
                    results = response_json['quoteResponse'].get('result', [])
                    logger.info(f"  Number of results: {len(results)}")
                    
                    if len(results) > 0:
                        quote = results[0]
                        logger.info(f"  Quote keys: {list(quote.keys())}")
                        logger.info(f"  First quote data:\n{json.dumps(quote, indent=2)}")
                        
                        # Log all available values
                        logger.info("\n  ALL AVAILABLE FIELDS:")
                        for key, value in quote.items():
                            logger.info(f"    {key}: {value}")
                else:
                    logger.warning("No 'quoteResponse' key found!")
                    logger.warning(f"Response keys: {list(response_json.keys())}")
            else:
                logger.error(f"Failed: HTTP {r.status_code}")
                logger.error(f"Response: {r.text}")
                
        except Exception as e:
            logger.error(f"Exception: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def test_nse_bank_api(self):
        """Test NSE Bank Nifty API"""
        logger.info("\n" + "="*100)
        logger.info("TEST 3: NSE BANK NIFTY API")
        logger.info("="*100)
        
        try:
            url = 'https://www.nseindia.com/api/quote-derivative?symbol=NIFTYBANK'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            logger.info(f"Requesting: {url}")
            r = requests.get(url, headers=headers, timeout=15)
            logger.info(f"Status Code: {r.status_code}")
            
            if r.status_code == 200:
                response_json = r.json()
                logger.info(f"FULL RESPONSE:\n{json.dumps(response_json, indent=2)}")
            else:
                logger.error(f"Failed: HTTP {r.status_code}")
                
        except Exception as e:
            logger.error(f"Exception: {e}")


def create_debug_html(test_results=""):
    """Create debug HTML email"""
    ts = datetime.now().strftime('%B %d, %Y at %H:%M IST')
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        h1 {{ color: #2c5aa0; margin-bottom: 20px; }}
        .debug-box {{ background: #f0f0f0; padding: 15px; border-left: 4px solid #ff9800; margin: 20px 0; }}
        pre {{ background: #222; color: #0f0; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 DEBUG: API Response Test</h1>
        <p class="timestamp">Generated: {ts}</p>
        
        <div class="debug-box">
            <h2>Debug Information</h2>
            <p>This is a DEBUG version to show what APIs are returning.</p>
            <p>Check the GitHub Actions logs for detailed API responses!</p>
            <p>The logs will show:</p>
            <ul>
                <li>Full API response JSON</li>
                <li>All available field names</li>
                <li>Actual values being returned</li>
            </ul>
        </div>
        
        <h2>Next Steps</h2>
        <ol>
            <li>Go to GitHub Actions tab</li>
            <li>Click the last workflow run</li>
            <li>Click "Run Market Report" job</li>
            <li>Look at the logs (scroll down)</li>
            <li>Find the TEST sections showing API responses</li>
            <li>Copy the field names and values</li>
            <li>Send this info so we can fix the parsing</li>
        </ol>
    </div>
</body>
</html>
"""
    return html


def send_email(recipient, subject, html_content):
    """Send debug email"""
    try:
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        
        if not sender_email or not sender_password:
            logger.error("Email credentials missing")
            return False
        
        logger.info("Sending debug email...")
        
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = recipient
        message.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, message.as_string())
        
        logger.info("✅ Debug email sent!")
        return True
        
    except Exception as e:
        logger.error(f"Email error: {e}")
        return False


def main():
    logger.info("\n" + "="*100)
    logger.info("DEBUG VERSION - TESTING API RESPONSES")
    logger.info("="*100)
    
    try:
        # Run tests
        collector = DebugCollector()
        collector.test_nse_api()
        time.sleep(2)
        collector.test_yahoo_api()
        time.sleep(2)
        collector.test_nse_bank_api()
        
        # Send debug email
        logger.info("\n[2/2] Sending debug email...")
        html_email = create_debug_html()
        subject = f"DEBUG: API Response Test - {datetime.now().strftime('%B %d, %Y')}"
        
        if send_email("mailbox.macwan@gmail.com", subject, html_email):
            logger.info("="*100)
            logger.info("✅ DEBUG TEST COMPLETE!")
            logger.info("="*100)
            logger.info("\nNOW CHECK GITHUB ACTIONS LOGS:")
            logger.info("1. Go to Actions tab")
            logger.info("2. Click latest workflow run")
            logger.info("3. Click 'Run Market Report' job")
            logger.info("4. Scroll through logs to find TEST sections")
            logger.info("5. Look for FULL RESPONSE and field names")
            logger.info("6. Send screenshot or copy of the field names")
            logger.info("\n" + "="*100 + "\n")
            return 0
        return 1
            
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}\n")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == '__main__':
    sys.exit(main())
