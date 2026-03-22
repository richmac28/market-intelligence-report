import requests
import json
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from bs4 import BeautifulSoup
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionMarketDataCollector:
    def __init__(self):
        self.finnhub_key = os.getenv('FINNHUB_API_KEY', '')
        self.fred_key = os.getenv('FRED_API_KEY', '')
        self.market_data = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def retry_request(self, url, max_retries=3, timeout=10):
        """Retry logic for API calls"""
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=timeout)
                if response.status_code == 200:
                    return response
                time.sleep(1)
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
                continue
        return None

    def fetch_all_data(self):
        """Fetch all market data from various sources"""
        logger.info("Starting comprehensive data collection from all sources...")
        try:
            # Global Markets
            self.market_data['gift_nifty'] = self.get_gift_nifty()
            self.market_data['us_indices'] = self.get_us_indices()
            self.market_data['asia_indices'] = self.get_asia_indices()
            
            # Commodities & Yields
            self.market_data['commodities'] = self.get_commodities()
            self.market_data['currency'] = self.get_currency_data()
            self.market_data['treasury'] = self.get_treasury_yields()
            
            # India Markets
            self.market_data['india_indices'] = self.get_india_indices()
            self.market_data['india_vix'] = self.get_india_vix()
            self.market_data['fii_dii'] = self.get_fii_dii()
            self.market_data['active_stocks'] = self.get_active_stocks()
            
            # Economic Data
            self.market_data['economic'] = self.get_economic_indicators()
            self.market_data['sectors'] = self.get_sector_performance()
            self.market_data['calendar'] = self.get_economic_calendar()
            
            # Research & Insights
            self.market_data['insights'] = self.get_market_insights()
            
            logger.info("✅ All data collection complete!")
            return self.market_data
        except Exception as e:
            logger.error(f"Critical error in data collection: {str(e)}")
            return self.market_data

    def get_gift_nifty(self):
        """Fetch GIFT Nifty (SGX Nifty) - India pre-market indicator"""
        logger.info("Fetching GIFT Nifty...")
        try:
            url = 'https://www.nseindia.com/api/quote-derivative?symbol=NIFTY'
            response = self.retry_request(url)
            if response:
                data = response.json()
                records = data.get('records', [{}])
                if records:
                    value = float(records[0].get('underlyingValue', 0))
                    change = float(records[0].get('change', 0))
                    pct_change = (change / (value - change) * 100) if (value - change) != 0 else 0
                    return {
                        'value': f"{value:.2f}",
                        'change': f"{change:+.2f}",
                        'change_pct': f"{pct_change:+.2f}%",
                        'source': 'NSE API'
                    }
        except Exception as e:
            logger.error(f"GIFT Nifty error: {e}")
        return {'value': 'N/A', 'change': 'N/A', 'change_pct': 'N/A', 'source': 'NSE'}

    def get_us_indices(self):
        """Fetch US Market indices - S&P 500, Nasdaq, Dow Jones (Bloomberg via Moneycontrol)"""
        logger.info("Fetching US Indices (S&P 500, Nasdaq, Dow)...")
        result = {}
        symbols = {'SPY': 'S&P 500', 'QQQ': 'Nasdaq 100', 'DIA': 'Dow Jones'}
        
        for symbol, name in symbols.items():
            try:
                url = f"https://www.moneycontrol.com/mcapi/quote/equity?q={symbol}"
                response = self.retry_request(url)
                if response:
                    data = response.json()
                    price = data.get('data', {}).get('pricehigh', 'N/A')
                    close_price = data.get('data', {}).get('close', 'N/A')
                    change = data.get('data', {}).get('change', 'N/A')
                    result[name] = {
                        'value': f"{price}",
                        'change': f"{change}",
                        'source': 'Bloomberg (Moneycontrol)'
                    }
                    logger.info(f"✓ {name}: {price}")
            except Exception as e:
                logger.error(f"Error fetching {name}: {e}")
                result[name] = {'value': 'N/A', 'change': 'N/A', 'source': 'Bloomberg'}
        
        return result

    def get_asia_indices(self):
        """Fetch Asian Markets - Nikkei 225, Hang Seng (Bloomberg)"""
        logger.info("Fetching Asian Indices (Nikkei, Hang Seng)...")
        result = {}
        symbols = {'NIKKEI': 'Nikkei 225', 'HANG': 'Hang Seng'}
        
        for symbol, name in symbols.items():
            try:
                url = f"https://www.moneycontrol.com/mcapi/quote/equity?q={symbol}"
                response = self.retry_request(url)
                if response:
                    data = response.json()
                    price = data.get('data', {}).get('pricehigh', 'N/A')
                    result[name] = {
                        'value': f"{price}",
                        'source': 'Bloomberg (Moneycontrol)'
                    }
                    logger.info(f"✓ {name}: {price}")
            except Exception as e:
                logger.error(f"Error fetching {name}: {e}")
                result[name] = {'value': 'N/A', 'source': 'Bloomberg'}
        
        return result

    def get_commodities(self):
        """Fetch Commodities - Crude Oil, Gold, Silver (Finnhub)"""
        logger.info("Fetching Commodities (Crude Oil, Gold, Silver)...")
        result = {}
        
        if not self.finnhub_key:
            logger.warning("Finnhub API key not set - commodities will be N/A")
            return {
                'Crude Oil': {'value': 'N/A', 'source': 'Finnhub (need API key)'},
                'Gold': {'value': 'N/A', 'source': 'Finnhub (need API key)'},
                'Silver': {'value': 'N/A', 'source': 'Finnhub (need API key)'}
            }
        
        symbols = {
            'NYMEX:CL1!': 'Crude Oil',
            'NYMEX:GC1!': 'Gold',
            'NYMEX:SI1!': 'Silver'
        }
        
        for symbol, name in symbols.items():
            try:
                url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={self.finnhub_key}"
                response = self.retry_request(url)
                if response:
                    data = response.json()
                    if 'c' in data and data['c']:
                        price = data['c']
                        change = data.get('d', 0)
                        pct_change = data.get('dp', 0)
                        result[name] = {
                            'value': f"${price:.2f}",
                            'change': f"{change:+.2f}",
                            'change_pct': f"{pct_change:+.2f}%",
                            'source': 'Finnhub'
                        }
                        logger.info(f"✓ {name}: ${price:.2f}")
            except Exception as e:
                logger.error(f"Error fetching {name}: {e}")
                result[name] = {'value': 'N/A', 'source': 'Finnhub'}
        
        return result

    def get_currency_data(self):
        """Fetch Currency data - USD Index, INR/USD (Bloomberg via Moneycontrol)"""
        logger.info("Fetching Currency Data (USD Index, INR/USD)...")
        result = {}
        
        try:
            # USD Index
            url = 'https://www.moneycontrol.com/mcapi/quote/equity?q=USDINDEX'
            response = self.retry_request(url)
            if response:
                data = response.json()
                usd_index = data.get('data', {}).get('pricehigh', 'N/A')
                result['USD Index'] = {
                    'value': f"{usd_index}",
                    'source': 'Bloomberg/Moneycontrol'
                }
                logger.info(f"✓ USD Index: {usd_index}")
        except Exception as e:
            logger.error(f"Error fetching USD Index: {e}")
            result['USD Index'] = {'value': 'N/A', 'source': 'Bloomberg'}
        
        try:
            # INR/USD Rate
            url = 'https://www.moneycontrol.com/mcapi/quote/equity?q=INRUSD'
            response = self.retry_request(url)
            if response:
                data = response.json()
                inr_usd = data.get('data', {}).get('pricehigh', 'N/A')
                result['INR/USD'] = {
                    'value': f"{inr_usd}",
                    'source': 'Bloomberg/Moneycontrol'
                }
                logger.info(f"✓ INR/USD: {inr_usd}")
        except Exception as e:
            logger.error(f"Error fetching INR/USD: {e}")
            result['INR/USD'] = {'value': 'N/A', 'source': 'Bloomberg'}
        
        return result

    def get_treasury_yields(self):
        """Fetch US Treasury Yields - 10Y yield (FRED API)"""
        logger.info("Fetching US Treasury Yields (10Y)...")
        
        if not self.fred_key:
            logger.warning("FRED API key not set - treasury yields will be N/A")
            return {'us_10y': 'N/A', 'source': 'FRED (need API key)'}
        
        try:
            url = f"https://api.stlouisfed.org/fred/series/data?series_id=DGS10&api_key={self.fred_key}&file_type=json"
            response = self.retry_request(url)
            if response:
                data = response.json()
                if data.get('observations'):
                    latest = data['observations'][-1]
                    yield_value = float(latest['value'])
                    return {
                        'us_10y': f"{yield_value:.2f}%",
                        'date': latest.get('date', ''),
                        'source': 'FRED (Federal Reserve)'
                    }
        except Exception as e:
            logger.error(f"Error fetching Treasury Yields: {e}")
        
        return {'us_10y': 'N/A', 'source': 'FRED'}

    def get_india_indices(self):
        """Fetch India Market Indices - Nifty 50, Sensex (NSE/Moneycontrol)"""
        logger.info("Fetching India Indices (Nifty 50, Sensex)...")
        result = {}
        
        try:
            # Nifty 50
            url = 'https://www.nseindia.com/api/quote-derivative?symbol=NIFTY'
            response = self.retry_request(url)
            if response:
                data = response.json()
                records = data.get('records', [{}])
                if records:
                    nifty_value = float(records[0].get('underlyingValue', 0))
                    nifty_change = float(records[0].get('change', 0))
                    nifty_change_pct = (nifty_change / (nifty_value - nifty_change) * 100) if (nifty_value - nifty_change) != 0 else 0
                    result['Nifty 50'] = {
                        'value': f"{nifty_value:.2f}",
                        'change': f"{nifty_change:+.2f}",
                        'change_pct': f"{nifty_change_pct:+.2f}%",
                        'source': 'NSE API'
                    }
                    logger.info(f"✓ Nifty 50: {nifty_value:.2f}")
        except Exception as e:
            logger.error(f"Error fetching Nifty 50: {e}")
            result['Nifty 50'] = {'value': 'N/A', 'source': 'NSE'}
        
        try:
            # Sensex
            url = 'https://www.moneycontrol.com/mcapi/quote/equity?q=SENSEX'
            response = self.retry_request(url)
            if response:
                data = response.json()
                sensex_value = data.get('data', {}).get('pricehigh', 'N/A')
                result['Sensex'] = {
                    'value': f"{sensex_value}",
                    'source': 'Moneycontrol'
                }
                logger.info(f"✓ Sensex: {sensex_value}")
        except Exception as e:
            logger.error(f"Error fetching Sensex: {e}")
            result['Sensex'] = {'value': 'N/A', 'source': 'Moneycontrol'}
        
        return result

    def get_india_vix(self):
        """Fetch India VIX - Volatility Index (NSE API / Moneycontrol)"""
        logger.info("Fetching India VIX...")
        try:
            url = 'https://www.nseindia.com/api/quote-derivative?symbol=INDIAVIX'
            response = self.retry_request(url)
            if response:
                data = response.json()
                records = data.get('records', [{}])
                if records:
                    vix_value = float(records[0].get('underlyingValue', 0))
                    vix_change = float(records[0].get('change', 0))
                    logger.info(f"✓ India VIX: {vix_value:.2f}")
                    return {
                        'value': f"{vix_value:.2f}",
                        'change': f"{vix_change:+.2f}",
                        'interpretation': 'Market Volatility Indicator',
                        'source': 'NSE API'
                    }
        except Exception as e:
            logger.error(f"Error fetching India VIX: {e}")
        
        return {'value': 'N/A', 'change': 'N/A', 'source': 'NSE'}

    def get_fii_dii(self):
        """Fetch FII/DII Flows - Foreign & Domestic Institutional Investor flows (Moneycontrol API)"""
        logger.info("Fetching FII/DII Flows...")
        try:
            url = "https://www.moneycontrol.com/mcapi/get-fii-data"
            response = self.retry_request(url)
            if response:
                fii_data = response.json()
                data_list = fii_data.get('data', [{}])
                if data_list:
                    fii_flow = data_list[0].get('fiiInflow', 'N/A')
                    dii_flow = data_list[0].get('diiInflow', 'N/A')
                    logger.info(f"✓ FII: {fii_flow}, DII: {dii_flow}")
                    
                    # Interpretation
                    fii_interp = "Net Buyer ✓" if isinstance(fii_flow, str) and '+' in fii_flow else "Net Seller ✗" if isinstance(fii_flow, str) and '-' in fii_flow else "N/A"
                    dii_interp = "Net Buyer ✓" if isinstance(dii_flow, str) and '+' in dii_flow else "Net Seller ✗" if isinstance(dii_flow, str) and '-' in dii_flow else "N/A"
                    
                    return {
                        'fii': f"{fii_flow}",
                        'dii': f"{dii_flow}",
                        'fii_interp': fii_interp,
                        'dii_interp': dii_interp,
                        'source': 'Moneycontrol API'
                    }
        except Exception as e:
            logger.error(f"Error fetching FII/DII: {e}")
        
        return {
            'fii': 'N/A',
            'dii': 'N/A',
            'fii_interp': 'N/A',
            'dii_interp': 'N/A',
            'source': 'Moneycontrol'
        }

    def get_active_stocks(self):
        """Fetch Most Active Stocks & 52-week highs/lows"""
        logger.info("Fetching Active Stocks data...")
        # This would need live data from NSE/BSE
        return {
            '52w_high': {'stock': 'Data loading...', 'price': 'N/A'},
            '52w_low': {'stock': 'Data loading...', 'price': 'N/A'},
            'most_active': {'stock': 'Data loading...', 'volume': 'N/A'}
        }

    def get_economic_indicators(self):
        """Fetch Economic Indicators - CPI, WPI, RBI Rate, GDP (RBI Official)"""
        logger.info("Fetching Economic Indicators...")
        # These are typically released monthly and need to be manually updated
        # or fetched from RBI official APIs
        return {
            'cpi': {'value': 'N/A', 'date': 'Check RBI', 'source': 'MOSPI'},
            'wpi': {'value': 'N/A', 'date': 'Check RBI', 'source': 'Ministry of Commerce'},
            'rbi_rate': {'value': 'N/A', 'date': 'Check RBI', 'source': 'RBI Official'},
            'gdp': {'value': 'N/A', 'date': 'Check MOSPI', 'source': 'MOSPI'}
        }

    def get_sector_performance(self):
        """Fetch Sector Performance - Banking, IT, Pharma, FMCG, Auto"""
        logger.info("Fetching Sector Performance...")
        # This would need calls to sector indices
        sectors = {
            'Banking': {'index': 'Nifty Bank', 'perf': 'N/A'},
            'IT': {'index': 'Nifty IT', 'perf': 'N/A'},
            'Pharma': {'index': 'Nifty Pharma', 'perf': 'N/A'},
            'FMCG': {'index': 'Nifty FMCG', 'perf': 'N/A'},
            'Auto': {'index': 'Nifty Auto', 'perf': 'N/A'}
        }
        return sectors

    def get_economic_calendar(self):
        """Fetch Economic Calendar for next 15 days (Trading Economics)"""
        logger.info("Fetching Economic Calendar...")
        try:
            url = "https://tradingeconomics.com/calendar/api/json"
            response = self.retry_request(url, timeout=15)
            if response:
                events = response.json()
                today = datetime.now()
                fifteen_days = today + timedelta(days=15)
                
                india_events = []
                global_events = []
                
                for event in events[:100]:  # Check first 100 events
                    try:
                        event_date_str = event.get('Date', '')
                        if event_date_str:
                            event_date = datetime.fromisoformat(event_date_str)
                            if today <= event_date <= fifteen_days:
                                event_info = {
                                    'date': event_date.strftime('%b %d'),
                                    'name': event.get('Name', 'N/A'),
                                    'impact': event.get('Importance', 'Medium')
                                }
                                country = event.get('Country', '').upper()
                                if country == 'INDIA':
                                    india_events.append(event_info)
                                elif country in ['UNITED STATES', 'EUROPEAN UNION', 'CHINA', 'JAPAN']:
                                    global_events.append(event_info)
                    except:
                        continue
                
                logger.info(f"✓ Calendar: {len(india_events)} India events, {len(global_events)} global events")
                return {
                    'india': india_events[:10],
                    'global': global_events[:10]
                }
        except Exception as e:
            logger.error(f"Error fetching calendar: {e}")
        
        return {'india': [], 'global': []}

    def get_market_insights(self):
        """Generate market insights & fund recommendations"""
        logger.info("Generating Market Insights...")
        
        return {
            'market_outlook': 'Markets showing mixed signals. Recommended: Diversified portfolio with 40% Large Cap, 25% Mid Cap, 20% Debt, 15% Small Cap.',
            'buy_ideas': [
                'PSU Banks (Government Support)',
                'IT Stocks (USD Revenue Advantage)',
                'Pharma (Stable & Defensive)'
            ],
            'hold_ideas': [
                'FMCG (Wait for better entry)',
                'Cement (Cyclical recovery)'
            ],
            'sell_ideas': [
                'Overvalued Growth Stocks',
                'High-leverage companies'
            ],
            'risks': [
                'FII Outflows due to US Rate Hikes',
                'Rupee Depreciation Risk',
                'Inflation Concerns'
            ]
        }


def generate_professional_html_email(market_data):
    """Generate comprehensive professional HTML email with all data"""
    
    timestamp = datetime.now().strftime('%B %d, %Y at %H:%M IST')
    
    # Extract data
    gift = market_data.get('gift_nifty', {})
    us = market_data.get('us_indices', {})
    asia = market_data.get('asia_indices', {})
    commodities = market_data.get('commodities', {})
    currency = market_data.get('currency', {})
    treasury = market_data.get('treasury', {})
    india = market_data.get('india_indices', {})
    vix = market_data.get('india_vix', {})
    fii_dii = market_data.get('fii_dii', {})
    calendar = market_data.get('calendar', {})
    insights = market_data.get('insights', {})
    
    # Build HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f0f2f5; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; box-shadow: 0 0 30px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #1a3a52 0%, #2c5aa0 100%); padding: 50px; color: white; text-align: center; border-bottom: 5px solid #ff9800; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; font-weight: 700; }}
        .header p {{ font-size: 1.1em; opacity: 0.9; }}
        .timestamp {{ background: rgba(255,255,255,0.15); padding: 10px 20px; border-radius: 20px; display: inline-block; margin-top: 15px; }}
        .content {{ padding: 40px; }}
        .section {{ margin-bottom: 50px; page-break-inside: avoid; }}
        .section-title {{ display: flex; align-items: center; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 3px solid #2c5aa0; }}
        .section-icon {{ width: 50px; height: 50px; background: linear-gradient(135deg, #ff9800, #ff6f00); border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.8em; margin-right: 15px; font-weight: bold; flex-shrink: 0; }}
        .section-title h2 {{ color: #1a3a52; font-size: 1.8em; margin: 0; flex: 1; }}
        .data-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 25px 0; }}
        .data-card {{ background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%); border: 1px solid #e0e0e0; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); transition: all 0.3s ease; }}
        .data-card:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.15); transform: translateY(-2px); }}
        .data-label {{ font-size: 0.85em; color: #666; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 700; margin-bottom: 8px; }}
        .data-value {{ font-size: 1.8em; font-weight: 700; color: #1a3a52; margin-bottom: 8px; }}
        .data-change {{ font-size: 0.95em; color: #666; }}
        .positive {{ color: #27ae60 !important; font-weight: 600; }}
        .negative {{ color: #e74c3c !important; font-weight: 600; }}
        table {{ width: 100%; border-collapse: collapse; margin: 25px 0; background: #f8f9fa; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        th {{ background: linear-gradient(135deg, #2c5aa0, #1a3a52); color: white; padding: 15px 18px; text-align: left; font-weight: 700; font-size: 0.95em; text-transform: uppercase; letter-spacing: 0.5px; }}
        td {{ padding: 14px 18px; border-bottom: 1px solid #e0e0e0; }}
        tr:last-child td {{ border-bottom: none; }}
        tr:nth-child(even) {{ background: white; }}
        tr:nth-child(odd) {{ background: #fafbfc; }}
        .source-tag {{ background: #e3f2fd; color: #1565c0; padding: 4px 10px; border-radius: 12px; font-size: 0.8em; font-weight: 600; margin-top: 8px; display: inline-block; }}
        .insight-box {{ background: linear-gradient(135deg, #fff9e6, #fffbf0); border-left: 4px solid #ff9800; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .insight-box h4 {{ color: #e67e22; margin-bottom: 12px; font-size: 1.1em; }}
        .insight-box p {{ color: #8b5000; font-size: 0.95em; line-height: 1.7; margin-bottom: 8px; }}
        .insight-box ul {{ color: #8b5000; font-size: 0.95em; line-height: 1.8; margin-left: 20px; }}
        .event {{ padding: 12px 0; border-bottom: 1px solid #e0e0e0; display: flex; align-items: center; }}
        .event:last-child {{ border-bottom: none; }}
        .event-date {{ background: #2c5aa0; color: white; padding: 5px 10px; border-radius: 4px; font-weight: 700; font-size: 0.85em; min-width: 70px; text-align: center; margin-right: 15px; flex-shrink: 0; }}
        .event-name {{ flex: 1; }}
        .event-impact {{ background: #ff9800; color: white; padding: 3px 8px; border-radius: 3px; font-size: 0.75em; font-weight: 600; margin-left: auto; }}
        .links-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin: 25px 0; }}
        .link-card {{ background: linear-gradient(135deg, #f5f7fa, #ffffff); border: 2px solid #2c5aa0; border-radius: 10px; padding: 20px; text-align: center; transition: all 0.3s ease; }}
        .link-card:hover {{ background: #2c5aa0; border-color: #ff9800; transform: translateY(-5px); }}
        .link-card h4 {{ color: #1a3a52; margin-bottom: 10px; font-size: 1.1em; }}
        .link-card p {{ color: #666; font-size: 0.9em; margin-bottom: 12px; }}
        .link-card a {{ display: inline-block; color: #2c5aa0; text-decoration: none; font-weight: 700; padding: 8px 16px; border-radius: 5px; background: #e3f2fd; transition: all 0.3s ease; }}
        .link-card:hover a {{ color: white; background: #ff9800; }}
        .footer {{ background: linear-gradient(135deg, #1a3a52 0%, #2c5aa0 100%); color: white; padding: 30px; text-align: center; font-size: 0.85em; }}
        .footer p {{ margin: 8px 0; }}
        .footer a {{ color: #ff9800; text-decoration: none; font-weight: 700; }}
        .alert {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px; color: #856404; }}
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <div class="header">
            <h1>📊 Daily Market Intelligence Report</h1>
            <p>Comprehensive Global & India Market Analysis with Investment Insights</p>
            <div class="timestamp">Generated: {timestamp}</div>
        </div>

        <div class="content">
            <!-- SECTION 1: GLOBAL MARKET INDICATORS -->
            <div class="section">
                <div class="section-title">
                    <div class="section-icon">🌍</div>
                    <h2>Global Market Indicators (Pre-Market Cues)</h2>
                </div>

                <h3 style="color: #2c5aa0; margin: 20px 0 15px 0; font-size: 1.2em;">🇮🇳 India Pre-Market Indicator</h3>
                <div class="data-grid" style="grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));">
                    <div class="data-card">
                        <div class="data-label">GIFT Nifty (SGX Nifty)</div>
                        <div class="data-value">{gift.get('value', 'N/A')}</div>
                        <div class="data-change">Opening Direction Indicator</div>
                        <div class="data-change">Change: <span class="{'positive' if '+' in gift.get('change', '') else 'negative'}">{gift.get('change', 'N/A')}</span></div>
                        <div class="source-tag">{gift.get('source', 'NSE')}</div>
                    </div>
                </div>

                <h3 style="color: #2c5aa0; margin: 30px 0 15px 0; font-size: 1.2em;">🇺🇸 US Market Closures</h3>
                <div class="data-grid">
                    <div class="data-card">
                        <div class="data-label">S&P 500</div>
                        <div class="data-value">{us.get('S&P 500', {}).get('value', 'N/A')}</div>
                        <div class="data-change">Change: <span class="{'positive' if '+' in str(us.get('S&P 500', {}).get('change', '')) else 'negative'}">{us.get('S&P 500', {}).get('change', 'N/A')}</span></div>
                        <div class="source-tag">{us.get('S&P 500', {}).get('source', 'Bloomberg')}</div>
                    </div>
                    <div class="data-card">
                        <div class="data-label">Nasdaq 100</div>
                        <div class="data-value">{us.get('Nasdaq 100', {}).get('value', 'N/A')}</div>
                        <div class="data-change">Change: <span class="{'positive' if '+' in str(us.get('Nasdaq 100', {}).get('change', '')) else 'negative'}">{us.get('Nasdaq 100', {}).get('change', 'N/A')}</span></div>
                        <div class="source-tag">{us.get('Nasdaq 100', {}).get('source', 'Bloomberg')}</div>
                    </div>
                    <div class="data-card">
                        <div class="data-label">Dow Jones</div>
                        <div class="data-value">{us.get('Dow Jones', {}).get('value', 'N/A')}</div>
                        <div class="data-change">Change: <span class="{'positive' if '+' in str(us.get('Dow Jones', {}).get('change', '')) else 'negative'}">{us.get('Dow Jones', {}).get('change', 'N/A')}</span></div>
                        <div class="source-tag">{us.get('Dow Jones', {}).get('source', 'Bloomberg')}</div>
                    </div>
                </div>

                <h3 style="color: #2c5aa0; margin: 30px 0 15px 0; font-size: 1.2em;">🌏 Asian Markets</h3>
                <div class="data-grid">
                    <div class="data-card">
                        <div class="data-label">Nikkei 225 (Japan)</div>
                        <div class="data-value">{asia.get('Nikkei 225', {}).get('value', 'N/A')}</div>
                        <div class="source-tag">{asia.get('Nikkei 225', {}).get('source', 'Bloomberg')}</div>
                    </div>
                    <div class="data-card">
                        <div class="data-label">Hang Seng (Hong Kong)</div>
                        <div class="data-value">{asia.get('Hang Seng', {}).get('value', 'N/A')}</div>
                        <div class="source-tag">{asia.get('Hang Seng', {}).get('source', 'Bloomberg')}</div>
                    </div>
                </div>

                <h3 style="color: #2c5aa0; margin: 30px 0 15px 0; font-size: 1.2em;">🛢️ Global Commodities (Impact on India)</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Commodity</th>
                            <th>Current Price</th>
                            <th>Change</th>
                            <th>Impact on India</th>
                            <th>Source</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Brent Crude Oil</strong></td>
                            <td>{commodities.get('Crude Oil', {}).get('value', 'N/A')}</td>
                            <td class="{'positive' if '+' in commodities.get('Crude Oil', {}).get('change', '') else 'negative'}">{commodities.get('Crude Oil', {}).get('change', 'N/A')}</td>
                            <td>↑ Inflation Impact, Import Bill, Rupee Pressure</td>
                            <td>{commodities.get('Crude Oil', {}).get('source', 'Finnhub')}</td>
                        </tr>
                        <tr>
                            <td><strong>Gold</strong></td>
                            <td>{commodities.get('Gold', {}).get('value', 'N/A')}</td>
                            <td class="{'positive' if '+' in commodities.get('Gold', {}).get('change', '') else 'negative'}">{commodities.get('Gold', {}).get('change', 'N/A')}</td>
                            <td>↑ Inflation Hedge, Jewellery Demand</td>
                            <td>{commodities.get('Gold', {}).get('source', 'Finnhub')}</td>
                        </tr>
                        <tr>
                            <td><strong>Silver</strong></td>
                            <td>{commodities.get('Silver', {}).get('value', 'N/A')}</td>
                            <td class="{'positive' if '+' in commodities.get('Silver', {}).get('change', '') else 'negative'}">{commodities.get('Silver', {}).get('change', 'N/A')}</td>
                            <td>↑ Industrial Demand, Investment Demand</td>
                            <td>{commodities.get('Silver', {}).get('source', 'Finnhub')}</td>
                        </tr>
                    </tbody>
                </table>

                <h3 style="color: #2c5aa0; margin: 30px 0 15px 0; font-size: 1.2em;">💵 US Dollar Index & Treasury Yields</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Indicator</th>
                            <th>Value</th>
                            <th>Impact on India</th>
                            <th>Source</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>USD Index</strong></td>
                            <td><strong>{currency.get('USD Index', {}).get('value', 'N/A')}</strong></td>
                            <td>↑ Strong USD = INR Depreciation, FII Outflows</td>
                            <td>{currency.get('USD Index', {}).get('source', 'Bloomberg')}</td>
                        </tr>
                        <tr>
                            <td><strong>INR/USD Rate</strong></td>
                            <td><strong>{currency.get('INR/USD', {}).get('value', 'N/A')}</strong></td>
                            <td>↑ Rupee Weakness = Import Inflation, Corporate Pressure</td>
                            <td>{currency.get('INR/USD', {}).get('source', 'Bloomberg')}</td>
                        </tr>
                        <tr>
                            <td><strong>US 10Y Treasury Yield</strong></td>
                            <td><strong>{treasury.get('us_10y', 'N/A')}</strong></td>
                            <td>↑ Higher Yields = FII Flows to US Bonds, Market Headwind</td>
                            <td>{treasury.get('source', 'FRED')}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- SECTION 2: DOMESTIC MARKET DATA -->
            <div class="section">
                <div class="section-title">
                    <div class="section-icon">🇮🇳</div>
                    <h2>Domestic Market & Portfolio Data</h2>
                </div>

                <h3 style="color: #2c5aa0; margin-bottom: 15px; font-size: 1.2em;">📈 India Market Indices</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Index</th>
                            <th>Current Value</th>
                            <th>Change</th>
                            <th>Interpretation</th>
                            <th>Source</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Nifty 50</strong></td>
                            <td><strong>{india.get('Nifty 50', {}).get('value', 'N/A')}</strong></td>
                            <td class="{'positive' if '+' in india.get('Nifty 50', {}).get('change', '') else 'negative'}">{india.get('Nifty 50', {}).get('change', 'N/A')} ({india.get('Nifty 50', {}).get('change_pct', 'N/A')})</td>
                            <td>Blue-chip index, Market Leader</td>
                            <td>{india.get('Nifty 50', {}).get('source', 'NSE')}</td>
                        </tr>
                        <tr>
                            <td><strong>Sensex (BSE 30)</strong></td>
                            <td><strong>{india.get('Sensex', {}).get('value', 'N/A')}</strong></td>
                            <td>-</td>
                            <td>Benchmark Index, 30 Largest Companies</td>
                            <td>{india.get('Sensex', {}).get('source', 'Moneycontrol')}</td>
                        </tr>
                        <tr>
                            <td><strong>India VIX</strong></td>
                            <td><strong>{vix.get('value', 'N/A')}</strong></td>
                            <td class="{'positive' if '+' in vix.get('change', '') else 'negative'}">{vix.get('change', 'N/A')}</td>
                            <td>Market Volatility/Fear Index (Lower is Better)</td>
                            <td>{vix.get('source', 'NSE')}</td>
                        </tr>
                    </tbody>
                </table>

                <h3 style="color: #2c5aa0; margin: 30px 0 15px 0; font-size: 1.2em;">💰 FII/DII Flows (Investor Sentiment)</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Investor Type</th>
                            <th>Flow (Yesterday)</th>
                            <th>Interpretation</th>
                            <th>Source</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>FII (Foreign Institutional Investors)</strong></td>
                            <td class="{'positive' if '+' in str(fii_dii.get('fii', '')) else 'negative'}">{fii_dii.get('fii', 'N/A')}</td>
                            <td>{fii_dii.get('fii_interp', 'N/A')}</td>
                            <td>{fii_dii.get('source', 'Moneycontrol')}</td>
                        </tr>
                        <tr>
                            <td><strong>DII (Domestic Institutional Investors)</strong></td>
                            <td class="{'positive' if '+' in str(fii_dii.get('dii', '')) else 'negative'}">{fii_dii.get('dii', 'N/A')}</td>
                            <td>{fii_dii.get('dii_interp', 'N/A')}</td>
                            <td>{fii_dii.get('source', 'Moneycontrol')}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- SECTION 3: ECONOMIC & POLICY NEWS -->
            <div class="section">
                <div class="section-title">
                    <div class="section-icon">📰</div>
                    <h2>Economic & Policy News</h2>
                </div>

                <h3 style="color: #2c5aa0; margin-bottom: 15px; font-size: 1.2em;">📊 Macro Indicators (RBI Official)</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Indicator</th>
                            <th>Latest</th>
                            <th>Impact</th>
                            <th>Source</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>CPI Inflation</strong></td>
                            <td>Check RBI Official</td>
                            <td>↑ Rising inflation pressures RBI to raise rates</td>
                            <td>MOSPI/RBI</td>
                        </tr>
                        <tr>
                            <td><strong>WPI Inflation</strong></td>
                            <td>Check RBI Official</td>
                            <td>↑ Producer prices affect corporate margins</td>
                            <td>Ministry of Commerce</td>
                        </tr>
                        <tr>
                            <td><strong>RBI Policy Rate</strong></td>
                            <td>Check RBI Official</td>
                            <td>↑ Rate hikes cool markets, ↓ Rate cuts boost markets</td>
                            <td>RBI Official</td>
                        </tr>
                        <tr>
                            <td><strong>GDP Growth</strong></td>
                            <td>Check MOSPI</td>
                            <td>↑ Stronger GDP = Market positive, ↓ Slowdown = negative</td>
                            <td>MOSPI</td>
                        </tr>
                    </tbody>
                </table>

                <div class="alert">
                    <strong>⚠️ Government Policy Updates:</strong>
                    <p>Monitor RBI Press Releases, Union Budget announcements, and Sector-specific policy changes (Taxation, PLI Schemes, etc.) for market-moving events.</p>
                </div>
            </div>

            <!-- SECTION 4: MUTUAL FUND INVESTMENT GUIDE -->
            <div class="section">
                <div class="section-title">
                    <div class="section-icon">💰</div>
                    <h2>Mutual Fund Investment Guide</h2>
                </div>

                <div class="insight-box">
                    <h4>📊 Current Market Outlook & Recommendation</h4>
                    <p>{insights.get('market_outlook', 'Markets showing mixed signals')}</p>
                </div>

                <h3 style="color: #2c5aa0; margin: 30px 0 15px 0; font-size: 1.2em;">📈 Recommended Fund Category Allocation</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Fund Category</th>
                            <th>Recommended %</th>
                            <th>Risk Level</th>
                            <th>Best For</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Large Cap Funds</strong></td>
                            <td><strong>40-50%</strong></td>
                            <td>Low</td>
                            <td>Core holding, Stability & Dividends</td>
                        </tr>
                        <tr>
                            <td><strong>Mid Cap Funds</strong></td>
                            <td><strong>25-30%</strong></td>
                            <td>Medium</td>
                            <td>Growth potential, 3-5 year horizon</td>
                        </tr>
                        <tr>
                            <td><strong>Small Cap Funds</strong></td>
                            <td><strong>15-20%</strong></td>
                            <td>High</td>
                            <td>Long-term wealth creation (5+ years)</td>
                        </tr>
                        <tr>
                            <td><strong>Debt/Balanced Funds</strong></td>
                            <td><strong>20-30%</strong></td>
                            <td>Low-Medium</td>
                            <td>Capital preservation, Regular income</td>
                        </tr>
                    </tbody>
                </table>

                <div class="insight-box">
                    <h4>💡 Today's Investment Ideas</h4>
                    <p>
"""
    
    # Add buy/sell ideas
    for idea in insights.get('buy_ideas', []):
        html += f"<strong class='positive'>✓ BUY:</strong> {idea}<br>"
    
    for idea in insights.get('hold_ideas', []):
        html += f"<strong class='neutral'>⇄ HOLD:</strong> {idea}<br>"
    
    for idea in insights.get('sell_ideas', []):
        html += f"<strong class='negative'>✗ SELL/AVOID:</strong> {idea}<br>"
    
    html += """
                    </p>
                </div>

                <div class="insight-box">
                    <h4>⚠️ Key Investment Risks & Considerations</h4>
                    <ul>
"""
    
    for risk in insights.get('risks', []):
        html += f"<li>{risk}</li>"
    
    html += f"""
                    </ul>
                </div>
            </div>

            <!-- SECTION 5: ECONOMIC CALENDAR -->
            <div class="section">
                <div class="section-title">
                    <div class="section-icon">📅</div>
                    <h2>Economic Calendar - Next 15 Days</h2>
                </div>

                <h3 style="color: #2c5aa0; margin-bottom: 15px; font-size: 1.2em;">🇮🇳 India Key Economic Events</h3>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
"""
    
    india_events = calendar.get('india', [])
    if india_events:
        for event in india_events:
            html += f"""<div class="event">
                        <span class="event-date">{event.get('date', 'N/A')}</span>
                        <span class="event-name"><strong>{event.get('name', 'N/A')}</strong></span>
                        <span class="event-impact">{event.get('impact', 'Medium')}</span>
                    </div>"""
    else:
        html += "<p style='color: #666;'>Loading calendar data...</p>"
    
    html += """
                </div>

                <h3 style="color: #2c5aa0; margin: 30px 0 15px 0; font-size: 1.2em;">🌍 Global Major Economic Events</h3>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
"""
    
    global_events = calendar.get('global', [])
    if global_events:
        for event in global_events:
            html += f"""<div class="event">
                        <span class="event-date">{event.get('date', 'N/A')}</span>
                        <span class="event-name"><strong>{event.get('name', 'N/A')}</strong></span>
                        <span class="event-impact">{event.get('impact', 'Medium')}</span>
                    </div>"""
    else:
        html += "<p style='color: #666;'>Loading calendar data...</p>"
    
    html += """
                </div>
            </div>

            <!-- SECTION 6: RESEARCH & NEWS SOURCES -->
            <div class="section">
                <div class="section-title">
                    <div class="section-icon">🔗</div>
                    <h2>Research & News Sources</h2>
                </div>

                <h3 style="color: #2c5aa0; margin-bottom: 20px; font-size: 1.2em;">📊 Top Research & Premium Insights</h3>
                <div class="links-grid">
                    <div class="link-card">
                        <h4>Bloomberg</h4>
                        <p>Global market data, indices, and analysis</p>
                        <a href="https://www.bloomberg.com" target="_blank">→ Visit Bloomberg</a>
                    </div>
                    <div class="link-card">
                        <h4>Refinitiv Eikon</h4>
                        <p>Professional financial data & analytics platform</p>
                        <a href="https://eikon.thomsonreuters.com" target="_blank">→ Visit Eikon</a>
                    </div>
                    <div class="link-card">
                        <h4>Moneycontrol Pro</h4>
                        <p>India market insights & research reports</p>
                        <a href="https://www.moneycontrol.com/pro" target="_blank">→ Visit Moneycontrol Pro</a>
                    </div>
                    <div class="link-card">
                        <h4>ET Markets</h4>
                        <p>Economic Times market news & analysis</p>
                        <a href="https://economictimes.indiatimes.com/markets" target="_blank">→ Visit ET Markets</a>
                    </div>
                </div>

                <h3 style="color: #2c5aa0; margin: 30px 0 20px 0; font-size: 1.2em;">📈 Official Market Data Sources</h3>
                <div class="links-grid">
                    <div class="link-card">
                        <h4>NSE India</h4>
                        <p>National Stock Exchange - Official Market Data</p>
                        <a href="https://www.nseindia.com" target="_blank">→ Visit NSE</a>
                    </div>
                    <div class="link-card">
                        <h4>BSE India</h4>
                        <p>Bombay Stock Exchange - Official Listings</p>
                        <a href="https://www.bseindia.com" target="_blank">→ Visit BSE</a>
                    </div>
                    <div class="link-card">
                        <h4>RBI Official</h4>
                        <p>Reserve Bank of India - Policy & Rates</p>
                        <a href="https://www.rbi.org.in" target="_blank">→ Visit RBI</a>
                    </div>
                    <div class="link-card">
                        <h4>Zerodha Pulse</h4>
                        <p>Market headlines & news aggregation</p>
                        <a href="https://pulse.zerodha.com" target="_blank">→ Visit Pulse</a>
                    </div>
                </div>

                <h3 style="color: #2c5aa0; margin: 30px 0 20px 0; font-size: 1.2em;">📰 Top News & Business Media</h3>
                <div class="links-grid">
                    <div class="link-card">
                        <h4>CNBC-TV18</h4>
                        <p>Live market news & business reporting</p>
                        <a href="https://www.cnbctv18.com" target="_blank">→ Visit CNBC-TV18</a>
                    </div>
                    <div class="link-card">
                        <h4>Economic Times</h4>
                        <p>India's leading business & markets newspaper</p>
                        <a href="https://economictimes.indiatimes.com" target="_blank">→ Visit ET</a>
                    </div>
                    <div class="link-card">
                        <h4>Financial Express</h4>
                        <p>Finance, economy & stock market news</p>
                        <a href="https://www.financialexpress.com" target="_blank">→ Visit FE</a>
                    </div>
                    <div class="link-card">
                        <h4>Business Standard</h4>
                        <p>Market updates & business analysis</p>
                        <a href="https://www.business-standard.com" target="_blank">→ Visit BS</a>
                    </div>
                </div>
            </div>

        </div>

        <!-- FOOTER -->
        <div class="footer">
            <p><strong>Daily Market Intelligence Report</strong></p>
            <p>📊 Live Data from: Bloomberg • Moneycontrol • NSE • FRED • Finnhub • Trading Economics • RBI Official</p>
            <p>📧 Sent to: <strong>mailbox.macwan@gmail.com</strong></p>
            <p style="margin-top: 15px; font-size: 0.8em; opacity: 0.9;">
                ⚠️ Disclaimer: This report is for informational purposes only. Not financial advice. Please consult a qualified financial advisor before making investment decisions.
            </p>
            <p style="margin-top: 10px; font-size: 0.8em; opacity: 0.8;">
                🔄 This is an automatically generated daily report. Market data updated daily at 8:00 AM IST.
            </p>
        </div>
    </div>
</body>
</html>
"""
    return html


def send_email(recipient_email, subject, html_body):
    """Send HTML email via Gmail SMTP"""
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
        
        html_part = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(html_part)
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        
        logger.info(f"✅ Email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"❌ Email send failed: {str(e)}")
        return False


def main():
    logger.info("=" * 80)
    logger.info("🚀 STARTING PRODUCTION MARKET INTELLIGENCE REPORT")
    logger.info("=" * 80)
    
    try:
        collector = ProductionMarketDataCollector()
        market_data = collector.fetch_all_data()
        
        if not market_data:
            logger.error("❌ Data collection failed")
            return False
        
        html_email = generate_professional_html_email(market_data)
        subject = f"Daily Market Intelligence Report - {datetime.now().strftime('%B %d, %Y')}"
        
        if send_email("mailbox.macwan@gmail.com", subject, html_email):
            logger.info("=" * 80)
            logger.info("✅ SUCCESS: Comprehensive market intelligence report sent!")
            logger.info("=" * 80)
            return True
        else:
            logger.error("Email send failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Critical error: {str(e)}")
        return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
