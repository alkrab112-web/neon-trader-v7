import requests
import sys
import json
import uuid
from datetime import datetime

class NeonTraderV7ImprovementsTester:
    def __init__(self, base_url="https://neon-trader.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.access_token = None
        self.user_id = None
        self.test_user_email = f"trader_{uuid.uuid4().hex[:8]}@neontrader.com"
        self.test_user_username = f"trader_{uuid.uuid4().hex[:8]}"
        self.test_password = "NeonTrader2024!"
        self.created_platform_id = None
        self.improvements_tested = {
            'market_data_enhanced': False,
            'realistic_prices': False,
            'smart_notifications_fixed': False,
            'trading_system_enhanced': False,
            'platform_testing_enhanced': False,
            'ai_system_working': False
        }

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, timeout=30):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {'Content-Type': 'application/json'}
        
        if headers:
            default_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2, ensure_ascii=False)[:500]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout after {timeout}s")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def get_auth_headers(self):
        """Get authorization headers with JWT token"""
        if not self.access_token:
            return {}
        return {'Authorization': f'Bearer {self.access_token}'}

    def setup_authentication(self):
        """Setup authentication for protected route tests"""
        print("\n🔐 Setting up authentication...")
        
        # Register user
        registration_data = {
            "email": self.test_user_email,
            "username": self.test_user_username,
            "password": self.test_password,
            "confirm_password": self.test_password
        }
        
        success, response = self.run_test("User Registration", "POST", "/auth/register", 200, registration_data)
        
        if success and response:
            self.access_token = response.get('access_token')
            self.user_id = response.get('user_id')
            print(f"   ✅ Authentication setup complete - User ID: {self.user_id}")
            return True
        else:
            print("   ❌ Authentication setup failed")
            return False

    # ========== IMPROVEMENT 1: Enhanced Market Data with CoinGecko API ==========
    
    def test_btc_real_price_coingecko(self):
        """Test BTC price from CoinGecko API - should be realistic, not $100"""
        success, response = self.run_test("BTC Real Price (CoinGecko)", "GET", "/market/BTCUSDT", 200)
        
        if success and response:
            price = response.get('price', 0)
            data_source = response.get('data_source', 'unknown')
            
            print(f"   💰 BTC Price: ${price}")
            print(f"   📊 Data Source: {data_source}")
            
            # Check if price is realistic (BTC should be > $20,000 in 2024)
            if price > 20000:
                print(f"   ✅ Price is realistic: ${price}")
                self.improvements_tested['market_data_enhanced'] = True
                self.improvements_tested['realistic_prices'] = True
                
                # Check if using real CoinGecko data
                if 'CoinGecko' in data_source:
                    print(f"   ✅ Using real CoinGecko API data")
                else:
                    print(f"   ⚠️  Using fallback data, not real CoinGecko API")
                    
            else:
                print(f"   ❌ Price still unrealistic: ${price} (should be > $20,000)")
                
        return success, response

    def test_eth_real_price_coingecko(self):
        """Test ETH price from CoinGecko API"""
        success, response = self.run_test("ETH Real Price (CoinGecko)", "GET", "/market/ETHUSDT", 200)
        
        if success and response:
            price = response.get('price', 0)
            data_source = response.get('data_source', 'unknown')
            
            print(f"   💰 ETH Price: ${price}")
            print(f"   📊 Data Source: {data_source}")
            
            # Check if price is realistic (ETH should be > $1,000 in 2024)
            if price > 1000:
                print(f"   ✅ ETH price is realistic: ${price}")
                
                # Check if using real CoinGecko data
                if 'CoinGecko' in data_source:
                    print(f"   ✅ Using real CoinGecko API data")
                else:
                    print(f"   ⚠️  Using fallback data, not real CoinGecko API")
                    
            else:
                print(f"   ❌ ETH price still unrealistic: ${price} (should be > $1,000)")
                
        return success, response

    def test_aapl_realistic_price(self):
        """Test AAPL stock price - should be realistic"""
        success, response = self.run_test("AAPL Realistic Price", "GET", "/market/AAPL", 200)
        
        if success and response:
            price = response.get('price', 0)
            asset_type = response.get('asset_type', 'unknown')
            
            print(f"   💰 AAPL Price: ${price}")
            print(f"   📊 Asset Type: {asset_type}")
            
            # Check if price is realistic (AAPL should be > $100 in 2024)
            if price > 100 and asset_type == 'stocks':
                print(f"   ✅ AAPL price is realistic: ${price}")
                self.improvements_tested['realistic_prices'] = True
            else:
                print(f"   ❌ AAPL price unrealistic: ${price} or wrong asset type: {asset_type}")
                
        return success, response

    # ========== IMPROVEMENT 2: Fixed Smart Notifications ==========
    
    def test_smart_notifications_fixed(self):
        """Test smart notifications - should work without 500 error"""
        if not self.access_token:
            print("❌ No access token available for smart notifications test")
            return False, {}
            
        auth_headers = self.get_auth_headers()
        success, response = self.run_test("Smart Notifications Fixed", "POST", "/notifications/smart-alert", 200, headers=auth_headers, timeout=60)
        
        if success and response:
            print(f"   ✅ Smart notifications working - no 500 error!")
            
            # Check if response contains expected fields
            if 'notification' in response:
                notification = response['notification']
                if notification and 'id' in notification:
                    print(f"   ✅ Notification created with ID: {notification['id']}")
                    self.improvements_tested['smart_notifications_fixed'] = True
                else:
                    print(f"   ⚠️  Notification created but missing ID")
            
            if 'analysis' in response:
                analysis = response['analysis']
                if analysis and len(analysis) > 10:
                    print(f"   ✅ AI analysis generated: {analysis[:100]}...")
                else:
                    print(f"   ⚠️  AI analysis too short or missing")
                    
        return success, response

    def test_get_notifications(self):
        """Test getting notifications list"""
        if not self.access_token:
            print("❌ No access token available for get notifications test")
            return False, {}
            
        auth_headers = self.get_auth_headers()
        success, response = self.run_test("Get Notifications", "GET", "/notifications", 200, headers=auth_headers)
        
        if success:
            print(f"   ✅ Notifications endpoint working")
            if isinstance(response, list):
                print(f"   📋 Found {len(response)} notifications")
            else:
                print(f"   ⚠️  Response is not a list: {type(response)}")
                
        return success, response

    # ========== IMPROVEMENT 3: Enhanced Trading System ==========
    
    def test_enhanced_trading_system(self):
        """Test enhanced trading system with execution details"""
        if not self.access_token:
            print("❌ No access token available for enhanced trading test")
            return False, {}
            
        trade_data = {
            "symbol": "BTCUSDT",
            "trade_type": "buy",
            "order_type": "market",
            "quantity": 0.01,
            "stop_loss": 42000,
            "take_profit": 50000
        }
        
        auth_headers = self.get_auth_headers()
        success, response = self.run_test("Enhanced Trading System", "POST", "/trades", 200, trade_data, auth_headers)
        
        if success and response and 'trade' in response:
            trade = response['trade']
            
            # Check for enhanced execution details
            execution_type = trade.get('execution_type')
            current_market_price = trade.get('current_market_price')
            
            print(f"   💼 Trade created with ID: {trade.get('id')}")
            
            if execution_type:
                print(f"   ✅ Execution type included: {execution_type}")
                self.improvements_tested['trading_system_enhanced'] = True
            else:
                print(f"   ❌ Missing execution_type in trade response")
                
            if current_market_price:
                print(f"   ✅ Current market price included: ${current_market_price}")
            else:
                print(f"   ❌ Missing current_market_price in trade response")
                
            # Check platform information
            platform = trade.get('platform', '')
            print(f"   🏢 Platform: {platform}")
            
        return success, response

    # ========== IMPROVEMENT 4: Enhanced Platform Testing ==========
    
    def test_enhanced_platform_connection(self):
        """Test enhanced platform connection with detailed feedback"""
        if not self.access_token:
            print("❌ No access token available for platform test")
            return False, {}
            
        # First add a platform
        platform_data = {
            "name": "Enhanced Test Platform",
            "platform_type": "binance",
            "api_key": "test_enhanced_api_key",
            "secret_key": "test_enhanced_secret",
            "is_testnet": True
        }
        
        auth_headers = self.get_auth_headers()
        success, response = self.run_test("Add Enhanced Platform", "POST", "/platforms", 200, platform_data, auth_headers)
        
        if success and response and 'platform' in response:
            self.created_platform_id = response['platform'].get('id')
            print(f"   🏢 Platform created with ID: {self.created_platform_id}")
            
            # Test enhanced connection
            if self.created_platform_id:
                success2, response2 = self.run_test("Enhanced Platform Connection Test", "PUT", f"/platforms/{self.created_platform_id}/test", 200, headers=auth_headers)
                
                if success2 and response2:
                    # Check for enhanced connection details
                    connection_details = response2.get('connection_details', {})
                    message = response2.get('message', '')
                    
                    print(f"   📋 Connection message: {message}")
                    
                    if connection_details:
                        print(f"   ✅ Enhanced connection details provided:")
                        for key, value in connection_details.items():
                            print(f"      - {key}: {value}")
                        self.improvements_tested['platform_testing_enhanced'] = True
                    else:
                        print(f"   ❌ Missing enhanced connection_details")
                        
                return success2, response2
                
        return success, response

    # ========== IMPROVEMENT 5: AI System Testing ==========
    
    def test_ai_daily_plan_working(self):
        """Test AI daily plan generation"""
        if not self.access_token:
            print("❌ No access token available for AI daily plan test")
            return False, {}
            
        auth_headers = self.get_auth_headers()
        success, response = self.run_test("AI Daily Plan Working", "GET", "/ai/daily-plan", 200, headers=auth_headers, timeout=60)
        
        if success and response:
            # Check for Arabic content and AI analysis
            market_analysis = response.get('market_analysis', '')
            trading_strategy = response.get('trading_strategy', '')
            opportunities = response.get('opportunities', [])
            
            print(f"   🤖 Market Analysis: {market_analysis[:100]}...")
            print(f"   📈 Trading Strategy: {trading_strategy}")
            print(f"   🎯 Opportunities: {len(opportunities)} found")
            
            # Check for Arabic content (indicates real AI)
            if any(ord(char) > 127 for char in market_analysis):
                print(f"   ✅ Arabic content detected - AI working")
                self.improvements_tested['ai_system_working'] = True
            else:
                print(f"   ⚠️  No Arabic content - may be fallback")
                
        return success, response

    def test_ai_analysis_arabic(self):
        """Test AI market analysis with Arabic output"""
        analysis_data = {
            "symbol": "BTCUSDT",
            "timeframe": "1h"
        }
        
        success, response = self.run_test("AI Analysis Arabic", "POST", "/ai/analyze", 200, analysis_data, timeout=60)
        
        if success and response:
            analysis = response.get('analysis', '')
            market_data = response.get('market_data', {})
            
            print(f"   🤖 AI Analysis: {analysis[:150]}...")
            
            # Check for Arabic content
            if any(ord(char) > 127 for char in analysis):
                print(f"   ✅ Arabic AI analysis working")
                self.improvements_tested['ai_system_working'] = True
            else:
                print(f"   ⚠️  No Arabic content in analysis")
                
            # Check market data
            if market_data and 'price' in market_data:
                print(f"   📊 Market data included: ${market_data['price']}")
                
        return success, response

    def run_all_improvement_tests(self):
        """Run all improvement tests"""
        print("🚀 Starting Neon Trader V7 Improvements Testing")
        print("=" * 70)
        
        # Setup authentication first
        if not self.setup_authentication():
            print("❌ Authentication setup failed - cannot run protected route tests")
            return False
        
        print("\n" + "=" * 70)
        print("📊 TESTING IMPROVEMENT 1: Enhanced Market Data with CoinGecko API")
        print("=" * 70)
        
        self.test_btc_real_price_coingecko()
        self.test_eth_real_price_coingecko()
        self.test_aapl_realistic_price()
        
        print("\n" + "=" * 70)
        print("🔔 TESTING IMPROVEMENT 2: Fixed Smart Notifications")
        print("=" * 70)
        
        self.test_smart_notifications_fixed()
        self.test_get_notifications()
        
        print("\n" + "=" * 70)
        print("💼 TESTING IMPROVEMENT 3: Enhanced Trading System")
        print("=" * 70)
        
        self.test_enhanced_trading_system()
        
        print("\n" + "=" * 70)
        print("🏢 TESTING IMPROVEMENT 4: Enhanced Platform Testing")
        print("=" * 70)
        
        self.test_enhanced_platform_connection()
        
        print("\n" + "=" * 70)
        print("🤖 TESTING IMPROVEMENT 5: AI System Working")
        print("=" * 70)
        
        self.test_ai_daily_plan_working()
        self.test_ai_analysis_arabic()
        
        return True

    def print_improvement_summary(self):
        """Print summary of improvements tested"""
        print("\n" + "=" * 70)
        print("📋 IMPROVEMENTS TESTING SUMMARY")
        print("=" * 70)
        
        improvements = [
            ("Enhanced Market Data (CoinGecko API)", self.improvements_tested['market_data_enhanced']),
            ("Realistic Prices", self.improvements_tested['realistic_prices']),
            ("Smart Notifications Fixed", self.improvements_tested['smart_notifications_fixed']),
            ("Trading System Enhanced", self.improvements_tested['trading_system_enhanced']),
            ("Platform Testing Enhanced", self.improvements_tested['platform_testing_enhanced']),
            ("AI System Working", self.improvements_tested['ai_system_working'])
        ]
        
        working_count = 0
        for name, status in improvements:
            if status:
                print(f"✅ {name}")
                working_count += 1
            else:
                print(f"❌ {name}")
        
        print(f"\n📊 Overall Results: {self.tests_passed}/{self.tests_run} tests passed")
        print(f"🔧 Improvements Working: {working_count}/{len(improvements)}")
        
        if working_count == len(improvements):
            print("🎉 All improvements are working correctly!")
        else:
            failed_improvements = len(improvements) - working_count
            print(f"⚠️  {failed_improvements} improvements still need attention")

def main():
    tester = NeonTraderV7ImprovementsTester()
    
    # Run all improvement tests
    tester.run_all_improvement_tests()
    
    # Print summary
    tester.print_improvement_summary()
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())