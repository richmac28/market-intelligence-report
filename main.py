import requests
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_nifty():
    """Test Nifty API and show exact response"""
    logger.info("\n" + "="*80)
    logger.info("TESTING NIFTY 50 API")
    logger.info("="*80)
    
    url = 'https://www.nseindia.com/api/quote-derivative?symbol=NIFTY'
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        logger.info(f"URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        logger.info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Response Keys: {data.keys()}")
            
            if 'records' in data:
                logger.info(f"Records Count: {len(data['records'])}")
                if len(data['records']) > 0:
                    record = data['records'][0]
                    logger.info(f"Record Keys: {record.keys()}")
                    logger.info(f"Underlying Value: {record.get('underlyingValue')}")
                    logger.info(f"Change: {record.get('change')}")
                    return {
                        'value': record.get('underlyingValue'),
                        'change': record.get('change'),
                        'raw': record
                    }
        else:
            logger.error(f"Bad status code: {response.status_code}")
            logger.error(f"Response: {response.text[:500]}")
    except Exception as e:
        logger.error(f"Exception: {e}", exc_info=True)
    
    return None

def test_yahoo_sp500():
    """Test Yahoo Finance API for S&P 500"""
    logger.info("\n" + "="*80)
    logger.info("TESTING YAHOO FINANCE S&P 500")
    logger.info("="*80)
    
    url = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols=^GSPC&fields=shortName,regularMarketPrice,regularMarketChange'
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        logger.info(f"URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        logger.info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Full Response: {json.dumps(data, indent=2)}")
            
            if 'quoteResponse' in data:
                quotes = data['quoteResponse'].get('result', [])
                logger.info(f"Quotes Count: {len(quotes)}")
                if len(quotes) > 0:
                    quote = quotes[0]
                    logger.info(f"Quote Keys: {quote.keys()}")
                    logger.info(f"Price: {quote.get('regularMarketPrice')}")
                    return quote
        else:
            logger.error(f"Bad status: {response.status_code}")
            logger.error(f"Response: {response.text[:500]}")
    except Exception as e:
        logger.error(f"Exception: {e}", exc_info=True)
    
    return None

def test_sensex():
    """Test Sensex API"""
    logger.info("\n" + "="*80)
    logger.info("TESTING SENSEX API")
    logger.info("="*80)
    
    url = 'https://www.moneycontrol.com/mcapi/v2/index/data?token=sensexdata'
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        logger.info(f"URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        logger.info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Full Response: {json.dumps(data, indent=2)[:1000]}")
            return data
        else:
            logger.error(f"Bad status: {response.status_code}")
    except Exception as e:
        logger.error(f"Exception: {e}", exc_info=True)
    
    return None

def test_vix():
    """Test India VIX"""
    logger.info("\n" + "="*80)
    logger.info("TESTING INDIA VIX API")
    logger.info("="*80)
    
    url = 'https://www.nseindia.com/api/quote-derivative?symbol=INDIAVIX'
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        logger.info(f"URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        logger.info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'records' in data and len(data['records']) > 0:
                logger.info(f"VIX Value: {data['records'][0].get('underlyingValue')}")
                return data['records'][0]
        else:
            logger.error(f"Bad status: {response.status_code}")
    except Exception as e:
        logger.error(f"Exception: {e}", exc_info=True)
    
    return None

def test_fii_dii():
    """Test FII/DII API"""
    logger.info("\n" + "="*80)
    logger.info("TESTING FII/DII API")
    logger.info("="*80)
    
    url = 'https://www.moneycontrol.com/mcapi/get-fii-data'
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        logger.info(f"URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        logger.info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Full Response: {json.dumps(data, indent=2)[:1000]}")
            return data
        else:
            logger.error(f"Bad status: {response.status_code}")
    except Exception as e:
        logger.error(f"Exception: {e}", exc_info=True)
    
    return None

def generate_diagnostic_email():
    """Generate email with diagnostic information"""
    
    logger.info("\n" + "="*80)
    logger.info("COLLECTING ALL DATA")
    logger.info("="*80)
    
    nifty_data = test_nifty()
    sp500_data = test_yahoo_sp500()
    sensex_data = test_sensex()
    vix_data = test_vix()
    fii_data = test_fii_dii()
    
    logger.info("\n" + "="*80)
    logger.info("GENERATING EMAIL")
    logger.info("="*80)
    
    timestamp = datetime.now().strftime('%B %d, %Y at %H:%M IST')
    
    # Extract values safely
    nifty_val = nifty_data['value'] if nifty_data else 'API FAILED'
    sp500_val = sp500_data.get('regularMarketPrice') if sp500_data else 'API FAILED'
    sensex_val = sensex_data.get('data', {}).get('currentValue') if sensex_data else 'API FAILED'
    vix_val = vix_data.get('underlyingValue') if vix_data else 'API FAILED'
    fii_val = fii_data.get('data', [{}])[0].get('fiiInflow') if fii_data else 'API FAILED'
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial; background: #f0f2f5; }}
        .container {{ max-width: 900px; margin: 20px auto; background: white; padding: 30px; border-radius: 10px; }}
        .header {{ background: #1a3a52; color: white; padding: 20px; text-align: center; }}
        h1 {{ margin: 0; }}
        .section {{ margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; }}
        .label {{ font-weight: bold; color: #333; }}
        .value {{ font-size: 1.5em; color: #1a3a52; font-weight: bold; margin: 10px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th {{ background: #2c5aa0; color: white; padding: 10px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Daily Market Intelligence Report</h1>
            <p>Diagnostic Version - {timestamp}</p>
        </div>

        <div class="section">
            <h2>API Test Results</h2>
            <table>
                <tr>
                    <th>API</th>
                    <th>Status</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td><strong>Nifty 50 (NSE)</strong></td>
                    <td>{"✓ OK" if nifty_data else "✗ FAILED"}</td>
                    <td><strong>{nifty_val}</strong></td>
                </tr>
                <tr>
                    <td><strong>S&P 500 (Yahoo)</strong></td>
                    <td>{"✓ OK" if sp500_data else "✗ FAILED"}</td>
                    <td><strong>{sp500_val}</strong></td>
                </tr>
                <tr>
                    <td><strong>Sensex (Moneycontrol)</strong></td>
                    <td>{"✓ OK" if sensex_data else "✗ FAILED"}</td>
                    <td><strong>{sensex_val}</strong></td>
                </tr>
                <tr>
                    <td><strong>India VIX (NSE)</strong></td>
                    <td>{"✓ OK" if vix_data else "✗ FAILED"}</td>
                    <td><strong>{vix_val}</strong></td>
                </tr>
                <tr>
                    <td><strong>FII Flow (Moneycontrol)</strong></td>
                    <td>{"✓ OK" if fii_data else "✗ FAILED"}</td>
                    <td><strong>{fii_val}</strong></td>
                </tr>
            </table>
        </div>

        <div class="section">
            <h2>Summary</h2>
            <p>This diagnostic version tests all APIs and shows which ones are working.</p>
            <p>If you see "API FAILED" in the table above, that's why data isn't showing in the regular report.</p>
            <p><strong>Next Step:</strong> Share which APIs failed, and I'll fix them.</p>
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
        
        logger.info("✅ Email sent successfully!")
        return True
    except Exception as e:
        logger.error(f"Email error: {e}")
        return False

def main():
    logger.info("\n" + "="*80)
    logger.info("DIAGNOSTIC MARKET INTELLIGENCE REPORT")
    logger.info("="*80 + "\n")
    
    html = generate_diagnostic_email()
    subject = f"Diagnostic Report - Market APIs Test - {datetime.now().strftime('%B %d, %Y')}"
    
    if send_email("mailbox.macwan@gmail.com", subject, html):
        logger.info("\n" + "="*80)
        logger.info("✅ DIAGNOSTIC EMAIL SENT")
        logger.info("="*80)
        return True
    return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
