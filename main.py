#!/usr/bin/env python3
import os, sys, requests, logging, smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class MarketFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
        self.timeout = 10
        self.data = {}

    def get_nifty_sensex_vix(self):
        try:
            r = self.session.get('https://www.nseindia.com/api/quote-derivative?symbol=NIFTY', timeout=self.timeout)
            if r.status_code == 200:
                d = r.json()['records'][0]
                v = float(d['underlyingValue'])
                c = float(d['change'])
                p = (c/(v-c)*100) if (v-c) != 0 else 0
                self.data['nifty'] = {'value': f"{v:,.0f}", 'change': f"{c:+.0f}", 'pct': f"{p:+.2f}%"}
                logger.info(f"✓ Nifty: {v:,.0f}")
        except Exception as e:
            logger.error(f"Nifty: {e}")
            self.data['nifty'] = {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A'}

        try:
            r = self.session.get('https://www.moneycontrol.com/mcapi/v2/index/data?token=sensexdata', timeout=self.timeout)
            if r.status_code == 200:
                d = r.json()['data']
                v = d['currentValue']
                c = d['change']
                p = d['perChange']
                self.data['sensex'] = {'value': f"{v:,.0f}", 'change': f"{c:+.0f}", 'pct': f"{p:+.2f}%"}
                logger.info(f"✓ Sensex: {v:,.0f}")
        except Exception as e:
            logger.error(f"Sensex: {e}")
            self.data['sensex'] = {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A'}

        try:
            r = self.session.get('https://www.nseindia.com/api/quote-derivative?symbol=INDIAVIX', timeout=self.timeout)
            if r.status_code == 200:
                d = r.json()['records'][0]
                v = float(d['underlyingValue'])
                c = float(d['change'])
                self.data['vix'] = {'value': f"{v:.2f}", 'change': f"{c:+.2f}"}
                logger.info(f"✓ VIX: {v:.2f}")
        except Exception as e:
            logger.error(f"VIX: {e}")
            self.data['vix'] = {'value': 'N/A', 'change': 'N/A'}

    def get_global_indices(self):
        indices = {'sp500': '^GSPC', 'nasdaq': '^IXIC', 'dow': '^DJI', 'nikkei': '^N225', 'hangseng': '^HSI'}
        for key, sym in indices.items():
            try:
                r = self.session.get(f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={sym}&fields=regularMarketPrice,regularMarketChange,regularMarketChangePercent", timeout=self.timeout)
                if r.status_code == 200:
                    q = r.json()['quoteResponse']['result'][0]
                    p = q.get('regularMarketPrice')
                    if p:
                        self.data[key] = {'value': f"{p:,.0f}", 'change': f"{q.get('regularMarketChange',0):+,.0f}", 'pct': f"{q.get('regularMarketChangePercent',0):+.2f}%"}
                        logger.info(f"✓ {key}: {p:,.0f}")
            except Exception as e:
                logger.error(f"{key}: {e}")
                self.data[key] = {'value': 'N/A', 'change': 'N/A', 'pct': 'N/A'}

    def get_commodities(self):
        commodities = {'crude': 'CL=F', 'gold': 'GC=F'}
        for key, sym in commodities.items():
            try:
                r = self.session.get(f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={sym}&fields=regularMarketPrice,regularMarketChange", timeout=self.timeout)
                if r.status_code == 200:
                    q = r.json()['quoteResponse']['result'][0]
                    p = q.get('regularMarketPrice')
                    if p:
                        self.data[key] = {'value': f"${p:.2f}", 'change': f"{q.get('regularMarketChange',0):+.2f}"}
                        logger.info(f"✓ {key}: ${p:.2f}")
            except Exception as e:
                logger.error(f"{key}: {e}")
                self.data[key] = {'value': 'N/A', 'change': 'N/A'}

    def get_currency_yields(self):
        pairs = {'usd_index': 'DXY=F', 'inr_usd': 'INRUSD=X', 'us_10y': '^TNX'}
        for key, sym in pairs.items():
            try:
                r = self.session.get(f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={sym}&fields=regularMarketPrice,regularMarketChange", timeout=self.timeout)
                if r.status_code == 200:
                    q = r.json()['quoteResponse']['result'][0]
                    p = q.get('regularMarketPrice')
                    if p:
                        suf = '%' if key == 'us_10y' else ''
                        self.data[key] = {'value': f"{p:.2f}{suf}", 'change': f"{q.get('regularMarketChange',0):+.2f}"}
                        logger.info(f"✓ {key}: {p:.2f}")
            except Exception as e:
                logger.error(f"{key}: {e}")
                self.data[key] = {'value': 'N/A', 'change': 'N/A'}

    def get_fii_dii(self):
        try:
            r = self.session.get('https://www.moneycontrol.com/mcapi/get-fii-data', timeout=self.timeout)
            if r.status_code == 200:
                d = r.json()['data'][0]
                self.data['fii'] = d.get('fiiInflow', 'N/A')
                self.data['dii'] = d.get('diiInflow', 'N/A')
                logger.info(f"✓ FII/DII")
        except Exception as e:
            logger.error(f"FII/DII: {e}")
            self.data['fii'] = 'N/A'
            self.data['dii'] = 'N/A'

    def fetch_all(self):
        logger.info("=" * 80)
        logger.info("FETCHING MARKET DATA")
        logger.info("=" * 80)
        self.get_nifty_sensex_vix()
        self.get_global_indices()
        self.get_commodities()
        self.get_currency_yields()
        self.get_fii_dii()
        logger.info("=" * 80)
        return self.data

def create_html(data):
    ts = datetime.now().strftime('%B %d, %Y at %H:%M IST')
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
body{{font-family:Arial,sans-serif;background:#f5f5f5;margin:0;padding:20px}}
.container{{max-width:1000px;margin:0 auto;background:white;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}}
.header{{background:linear-gradient(135deg,#1a3a52,#2c5aa0);color:white;padding:40px;text-align:center}}
.header h1{{margin:0;font-size:2.2em}}.header p{{margin:10px 0 0 0;opacity:0.9}}
.content{{padding:40px}}.section{{margin-bottom:40px}}.section h2{{color:#1a3a52;border-bottom:2px solid #2c5aa0;padding-bottom:10px;margin-bottom:20px}}
table{{width:100%;border-collapse:collapse;margin:20px 0}}th{{background:#2c5aa0;color:white;padding:12px;text-align:left;font-weight:bold}}
td{{padding:10px 12px;border-bottom:1px solid #e0e0e0}}.value{{font-weight:bold;color:#1a3a52}}tr:nth-child(even){{background:#f9f9f9}}
.footer{{background:#1a3a52;color:white;padding:30px;text-align:center;font-size:0.9em}}
</style></head><body><div class="container">
<div class="header"><h1>📊 Daily Market Intelligence Report</h1><p>Global & India Market Analysis</p><p>{ts}</p></div>
<div class="content">
<div class="section"><h2>🌍 Global Indices</h2><table>
<tr><th>Index</th><th>Value</th><th>Change</th><th>%</th></tr>
<tr><td><b>S&P 500</b></td><td class="value">{data.get('sp500',{}).get('value','N/A')}</td><td>{data.get('sp500',{}).get('change','N/A')}</td><td>{data.get('sp500',{}).get('pct','N/A')}</td></tr>
<tr><td><b>Nasdaq</b></td><td class="value">{data.get('nasdaq',{}).get('value','N/A')}</td><td>{data.get('nasdaq',{}).get('change','N/A')}</td><td>{data.get('nasdaq',{}).get('pct','N/A')}</td></tr>
<tr><td><b>Dow</b></td><td class="value">{data.get('dow',{}).get('value','N/A')}</td><td>{data.get('dow',{}).get('change','N/A')}</td><td>{data.get('dow',{}).get('pct','N/A')}</td></tr>
<tr><td><b>Nikkei</b></td><td class="value">{data.get('nikkei',{}).get('value','N/A')}</td><td>{data.get('nikkei',{}).get('change','N/A')}</td><td>{data.get('nikkei',{}).get('pct','N/A')}</td></tr>
<tr><td><b>Hang Seng</b></td><td class="value">{data.get('hangseng',{}).get('value','N/A')}</td><td>{data.get('hangseng',{}).get('change','N/A')}</td><td>{data.get('hangseng',{}).get('pct','N/A')}</td></tr>
</table></div>
<div class="section"><h2>🇮🇳 India Indices</h2><table>
<tr><th>Index</th><th>Value</th><th>Change</th><th>%</th></tr>
<tr><td><b>Nifty 50</b></td><td class="value">{data.get('nifty',{}).get('value','N/A')}</td><td>{data.get('nifty',{}).get('change','N/A')}</td><td>{data.get('nifty',{}).get('pct','N/A')}</td></tr>
<tr><td><b>Sensex</b></td><td class="value">{data.get('sensex',{}).get('value','N/A')}</td><td>{data.get('sensex',{}).get('change','N/A')}</td><td>{data.get('sensex',{}).get('pct','N/A')}</td></tr>
<tr><td><b>VIX</b></td><td class="value">{data.get('vix',{}).get('value','N/A')}</td><td>{data.get('vix',{}).get('change','N/A')}</td><td>-</td></tr>
<tr><td><b>FII</b></td><td class="value">{data.get('fii','N/A')}</td><td colspan="2">Investor Flow</td></tr>
<tr><td><b>DII</b></td><td class="value">{data.get('dii','N/A')}</td><td colspan="2">Domestic Flow</td></tr>
</table></div>
<div class="section"><h2>💰 Commodities & Currency</h2><table>
<tr><th>Indicator</th><th>Value</th><th>Change</th></tr>
<tr><td><b>Crude Oil</b></td><td class="value">{data.get('crude',{}).get('value','N/A')}</td><td>{data.get('crude',{}).get('change','N/A')}</td></tr>
<tr><td><b>Gold</b></td><td class="value">{data.get('gold',{}).get('value','N/A')}</td><td>{data.get('gold',{}).get('change','N/A')}</td></tr>
<tr><td><b>USD Index</b></td><td class="value">{data.get('usd_index',{}).get('value','N/A')}</td><td>{data.get('usd_index',{}).get('change','N/A')}</td></tr>
<tr><td><b>INR/USD</b></td><td class="value">{data.get('inr_usd',{}).get('value','N/A')}</td><td>{data.get('inr_usd',{}).get('change','N/A')}</td></tr>
<tr><td><b>US 10Y Yield</b></td><td class="value">{data.get('us_10y',{}).get('value','N/A')}</td><td>{data.get('us_10y',{}).get('change','N/A')}</td></tr>
</table></div>
<div class="section"><h2>📊 Sources</h2><p>NSE | BSE | Moneycontrol | Yahoo Finance</p></div>
</div><div class="footer"><p><b>Daily Market Intelligence Report</b></p><p>Automated 8:00 AM IST Daily | mailbox.macwan@gmail.com</p></div></div></body></html>"""
    return html

def send_email(recipient, subject, html_content):
    try:
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        if not sender_email or not sender_password:
            logger.error("Credentials missing")
            return False
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient
        msg.attach(MIMEText(html_content, 'html'))
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, msg.as_string())
        logger.info(f"✓ Email sent to {recipient}")
        return True
    except Exception as e:
        logger.error(f"Email failed: {e}")
        return False

def main():
    logger.info("\n" + "=" * 80)
    logger.info("DAILY MARKET INTELLIGENCE REPORT")
    logger.info("=" * 80)
    fetcher = MarketFetcher()
    data = fetcher.fetch_all()
    html = create_html(data)
    subject = f"Daily Market Intelligence Report - {datetime.now().strftime('%B %d, %Y')}"
    if send_email("mailbox.macwan@gmail.com", subject, html):
        logger.info("\n" + "=" * 80)
        logger.info("✅ SUCCESS: REPORT SENT")
        logger.info("=" * 80)
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
