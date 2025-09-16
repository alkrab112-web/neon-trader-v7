import requests
import sys
import json
from datetime import datetime

class NeonTraderAPITester:
    def __init__(self, base_url="https://marhaba-71.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.user_id = "user_12345"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_trade_id = None
        self.created_platform_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2, ensure_ascii=False)[:200]}...")
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

    def test_api_status(self):
        """Test API root endpoint"""
        return self.run_test("API Status", "GET", "/", 200)

    def test_get_portfolio(self):
        """Test getting user portfolio"""
        return self.run_test("Get Portfolio", "GET", f"/portfolio/{self.user_id}", 200)

    def test_get_trades(self):
        """Test getting user trades"""
        return self.run_test("Get Trades", "GET", f"/trades/{self.user_id}", 200)

    def test_create_trade(self):
        """Test creating a new trade"""
        trade_data = {
            "symbol": "BTCUSDT",
            "trade_type": "buy",
            "order_type": "market",
            "quantity": 0.01,
            "price": None,
            "stop_loss": 42000,
            "take_profit": 45000
        }
        success, response = self.run_test("Create Trade", "POST", f"/trades/{self.user_id}", 200, trade_data)
        if success and 'trade' in response:
            self.created_trade_id = response['trade'].get('id')
            print(f"   Created trade ID: {self.created_trade_id}")
        return success, response

    def test_close_trade(self):
        """Test closing a trade"""
        if not self.created_trade_id:
            print("❌ No trade ID available for closing test")
            return False, {}
        
        return self.run_test("Close Trade", "PUT", f"/trades/{self.created_trade_id}/close", 200)

    def test_add_platform(self):
        """Test adding a trading platform"""
        platform_data = {
            "name": "Test Binance",
            "platform_type": "binance",
            "api_key": "test_api_key",
            "secret_key": "test_secret_key",
            "is_testnet": True
        }
        success, response = self.run_test("Add Platform", "POST", f"/platforms/{self.user_id}", 200, platform_data)
        if success and 'platform' in response:
            self.created_platform_id = response['platform'].get('id')
            print(f"   Created platform ID: {self.created_platform_id}")
        return success, response

    def test_get_platforms(self):
        """Test getting user platforms"""
        return self.run_test("Get Platforms", "GET", f"/platforms/{self.user_id}", 200)

    def test_platform_connection(self):
        """Test platform connection"""
        if not self.created_platform_id:
            print("❌ No platform ID available for connection test")
            return False, {}
        
        return self.run_test("Test Platform Connection", "PUT", f"/platforms/{self.created_platform_id}/test", 200)

    def test_daily_plan(self):
        """Test getting AI daily plan"""
        return self.run_test("Get Daily Plan", "GET", f"/ai/daily-plan/{self.user_id}", 200, timeout=60)

    def test_ai_analysis(self):
        """Test AI market analysis"""
        analysis_data = {
            "symbol": "BTCUSDT",
            "timeframe": "1h"
        }
        return self.run_test("AI Market Analysis", "POST", "/ai/analyze", 200, analysis_data, timeout=60)

    def test_market_data(self):
        """Test market data endpoint"""
        return self.run_test("Get Market Data", "GET", "/market/BTCUSDT", 200)

    def test_multiple_prices(self):
        """Test multiple prices endpoint"""
        return self.run_test("Get Multiple Prices", "GET", "/market/prices/multiple?symbols=BTCUSDT,ETHUSDT", 200)

def main():
    print("🚀 Starting Neon Trader V7 API Tests")
    print("=" * 50)
    
    tester = NeonTraderAPITester()
    
    # Test sequence
    tests = [
        ("API Status", tester.test_api_status),
        ("Portfolio", tester.test_get_portfolio),
        ("Get Trades", tester.test_get_trades),
        ("Create Trade", tester.test_create_trade),
        ("Close Trade", tester.test_close_trade),
        ("Add Platform", tester.test_add_platform),
        ("Get Platforms", tester.test_get_platforms),
        ("Test Platform Connection", tester.test_platform_connection),
        ("Market Data", tester.test_market_data),
        ("Multiple Prices", tester.test_multiple_prices),
        ("Daily Plan (AI)", tester.test_daily_plan),
        ("AI Analysis", tester.test_ai_analysis),
    ]
    
    print(f"\n📋 Running {len(tests)} API tests...")
    
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        failed = tester.tests_run - tester.tests_passed
        print(f"⚠️  {failed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())