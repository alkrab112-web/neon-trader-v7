import requests
import sys
import json
import uuid
from datetime import datetime

class NeonTraderJWTTester:
    def __init__(self, base_url="https://neon-trader.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.access_token = None
        self.user_id = None
        self.test_user_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
        self.test_user_username = f"testuser_{uuid.uuid4().hex[:8]}"
        self.test_password = "testpass123"
        self.created_trade_id = None
        self.created_platform_id = None

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
                    print(f"   Response: {json.dumps(response_data, indent=2, ensure_ascii=False)[:300]}...")
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

    # ========== JWT Authentication Tests ==========
    
    def test_api_status(self):
        """Test API root endpoint"""
        return self.run_test("API Status", "GET", "/", 200)

    def test_user_registration(self):
        """Test user registration with JWT token generation"""
        registration_data = {
            "email": self.test_user_email,
            "username": self.test_user_username,
            "password": self.test_password,
            "confirm_password": self.test_password
        }
        
        success, response = self.run_test("User Registration", "POST", "/auth/register", 200, registration_data)
        
        if success and response:
            # Store token and user info for subsequent tests
            self.access_token = response.get('access_token')
            self.user_id = response.get('user_id')
            print(f"   Registered user ID: {self.user_id}")
            print(f"   JWT token received: {self.access_token[:20]}..." if self.access_token else "   No token received")
            
            # Verify token structure
            if self.access_token and '.' in self.access_token:
                print("   ✅ JWT token has proper structure")
            else:
                print("   ❌ JWT token structure invalid")
                return False, response
                
        return success, response

    def test_user_login(self):
        """Test user login with JWT token generation"""
        login_data = {
            "email": self.test_user_email,
            "password": self.test_password
        }
        
        success, response = self.run_test("User Login", "POST", "/auth/login", 200, login_data)
        
        if success and response:
            # Verify login response contains required fields
            required_fields = ['access_token', 'token_type', 'user_id', 'email', 'username']
            for field in required_fields:
                if field not in response:
                    print(f"   ❌ Missing required field: {field}")
                    return False, response
            
            # Update token for subsequent tests
            self.access_token = response.get('access_token')
            print(f"   Login successful for user: {response.get('username')}")
            
        return success, response

    def test_get_current_user(self):
        """Test getting current user info with JWT token"""
        if not self.access_token:
            print("❌ No access token available for authentication test")
            return False, {}
            
        auth_headers = self.get_auth_headers()
        success, response = self.run_test("Get Current User", "GET", "/auth/me", 200, headers=auth_headers)
        
        if success and response:
            # Verify user info matches registration
            if response.get('email') != self.test_user_email:
                print(f"   ❌ Email mismatch: expected {self.test_user_email}, got {response.get('email')}")
                return False, response
            if response.get('username') != self.test_user_username:
                print(f"   ❌ Username mismatch: expected {self.test_user_username}, got {response.get('username')}")
                return False, response
                
        return success, response

    # ========== Security Tests ==========
    
    def test_duplicate_email_registration(self):
        """Test duplicate email registration attempt"""
        duplicate_data = {
            "email": self.test_user_email,  # Same email as before
            "username": f"different_{uuid.uuid4().hex[:8]}",
            "password": self.test_password,
            "confirm_password": self.test_password
        }
        
        return self.run_test("Duplicate Email Registration", "POST", "/auth/register", 400, duplicate_data)

    def test_duplicate_username_registration(self):
        """Test duplicate username registration attempt"""
        duplicate_data = {
            "email": f"different_{uuid.uuid4().hex[:8]}@example.com",
            "username": self.test_user_username,  # Same username as before
            "password": self.test_password,
            "confirm_password": self.test_password
        }
        
        return self.run_test("Duplicate Username Registration", "POST", "/auth/register", 400, duplicate_data)

    def test_password_mismatch_registration(self):
        """Test registration with mismatched passwords"""
        mismatch_data = {
            "email": f"mismatch_{uuid.uuid4().hex[:8]}@example.com",
            "username": f"mismatch_{uuid.uuid4().hex[:8]}",
            "password": self.test_password,
            "confirm_password": "different_password"
        }
        
        return self.run_test("Password Mismatch Registration", "POST", "/auth/register", 400, mismatch_data)

    def test_invalid_credentials_login(self):
        """Test login with invalid credentials"""
        invalid_data = {
            "email": self.test_user_email,
            "password": "wrong_password"
        }
        
        return self.run_test("Invalid Credentials Login", "POST", "/auth/login", 401, invalid_data)

    def test_nonexistent_user_login(self):
        """Test login with non-existent user"""
        nonexistent_data = {
            "email": "nonexistent@example.com",
            "password": self.test_password
        }
        
        return self.run_test("Non-existent User Login", "POST", "/auth/login", 401, nonexistent_data)

    # ========== Protected Route Tests ==========
    
    def test_protected_route_without_token(self):
        """Test accessing protected route without JWT token"""
        # FastAPI HTTPBearer returns 403 when no Authorization header is present
        success, response = self.run_test("Portfolio Without Token", "GET", "/portfolio", 403)
        if not success:
            # Also accept 401 as valid authentication failure
            success, response = self.run_test("Portfolio Without Token (retry)", "GET", "/portfolio", 401)
        return success, response

    def test_protected_route_with_invalid_token(self):
        """Test accessing protected route with invalid JWT token"""
        invalid_headers = {'Authorization': 'Bearer invalid_token_here'}
        return self.run_test("Portfolio With Invalid Token", "GET", "/portfolio", 401, headers=invalid_headers)

    def test_get_portfolio_authenticated(self):
        """Test getting user portfolio with valid JWT token"""
        if not self.access_token:
            print("❌ No access token available for portfolio test")
            return False, {}
            
        auth_headers = self.get_auth_headers()
        success, response = self.run_test("Get Portfolio (Authenticated)", "GET", "/portfolio", 200, headers=auth_headers)
        
        if success and response:
            # Verify portfolio belongs to authenticated user
            if response.get('user_id') != self.user_id:
                print(f"   ❌ Portfolio user_id mismatch: expected {self.user_id}, got {response.get('user_id')}")
                return False, response
                
        return success, response

    def test_get_trades_authenticated(self):
        """Test getting user trades with valid JWT token"""
        if not self.access_token:
            print("❌ No access token available for trades test")
            return False, {}
            
        auth_headers = self.get_auth_headers()
        return self.run_test("Get Trades (Authenticated)", "GET", "/trades", 200, headers=auth_headers)

    def test_create_trade_authenticated(self):
        """Test creating a trade with valid JWT token"""
        if not self.access_token:
            print("❌ No access token available for create trade test")
            return False, {}
            
        trade_data = {
            "symbol": "BTCUSDT",
            "trade_type": "buy",
            "order_type": "market",
            "quantity": 0.01,
            "stop_loss": 42000,
            "take_profit": 45000
        }
        
        auth_headers = self.get_auth_headers()
        success, response = self.run_test("Create Trade (Authenticated)", "POST", "/trades", 200, trade_data, auth_headers)
        
        if success and response and 'trade' in response:
            self.created_trade_id = response['trade'].get('id')
            trade_user_id = response['trade'].get('user_id')
            
            # Verify trade belongs to authenticated user
            if trade_user_id != self.user_id:
                print(f"   ❌ Trade user_id mismatch: expected {self.user_id}, got {trade_user_id}")
                return False, response
                
            print(f"   Created trade ID: {self.created_trade_id}")
            
        return success, response

    def test_get_platforms_authenticated(self):
        """Test getting user platforms with valid JWT token"""
        if not self.access_token:
            print("❌ No access token available for platforms test")
            return False, {}
            
        auth_headers = self.get_auth_headers()
        return self.run_test("Get Platforms (Authenticated)", "GET", "/platforms", 200, headers=auth_headers)

    def test_add_platform_authenticated(self):
        """Test adding a platform with valid JWT token"""
        if not self.access_token:
            print("❌ No access token available for add platform test")
            return False, {}
            
        platform_data = {
            "name": "Test Binance Platform",
            "platform_type": "binance",
            "api_key": "test_api_key_123",
            "secret_key": "test_secret_key_456",
            "is_testnet": True
        }
        
        auth_headers = self.get_auth_headers()
        success, response = self.run_test("Add Platform (Authenticated)", "POST", "/platforms", 200, platform_data, auth_headers)
        
        if success and response and 'platform' in response:
            self.created_platform_id = response['platform'].get('id')
            platform_user_id = response['platform'].get('user_id')
            
            # Verify platform belongs to authenticated user
            if platform_user_id != self.user_id:
                print(f"   ❌ Platform user_id mismatch: expected {self.user_id}, got {platform_user_id}")
                return False, response
                
            print(f"   Created platform ID: {self.created_platform_id}")
            
        return success, response

    # ========== AI Routes Tests (Protected) ==========
    
    def test_daily_plan_authenticated(self):
        """Test getting AI daily plan with authentication"""
        if not self.access_token:
            print("❌ No access token available for daily plan test")
            return False, {}
            
        auth_headers = self.get_auth_headers()
        return self.run_test("Get Daily Plan (Authenticated)", "GET", "/ai/daily-plan", 200, headers=auth_headers, timeout=60)

    def test_ai_analysis_public(self):
        """Test AI market analysis (public endpoint)"""
        analysis_data = {
            "symbol": "BTCUSDT",
            "timeframe": "1h"
        }
        return self.run_test("AI Market Analysis (Public)", "POST", "/ai/analyze", 200, analysis_data, timeout=60)

    # ========== Public Route Tests ==========
    
    def test_market_data_public(self):
        """Test public market data endpoint (should work without authentication)"""
        return self.run_test("Get Market Data (Public)", "GET", "/market/BTCUSDT", 200)

    def test_multiple_prices_public(self):
        """Test public multiple prices endpoint"""
        return self.run_test("Get Multiple Prices (Public)", "GET", "/market/prices/multiple?symbols=BTCUSDT,ETHUSDT", 200)

    def test_asset_types_public(self):
        """Test public asset types endpoint"""
        return self.run_test("Get Asset Types (Public)", "GET", "/market/types/all", 200)

def main():
    print("🚀 Starting Neon Trader V7 JWT Authentication Tests")
    print("=" * 60)
    
    tester = NeonTraderJWTTester()
    
    # Test sequence - Authentication flow first, then protected routes
    tests = [
        # Basic API Test
        ("API Status", tester.test_api_status),
        
        # Authentication Tests
        ("User Registration", tester.test_user_registration),
        ("User Login", tester.test_user_login),
        ("Get Current User", tester.test_get_current_user),
        
        # Security Tests
        ("Duplicate Email Registration", tester.test_duplicate_email_registration),
        ("Duplicate Username Registration", tester.test_duplicate_username_registration),
        ("Password Mismatch Registration", tester.test_password_mismatch_registration),
        ("Invalid Credentials Login", tester.test_invalid_credentials_login),
        ("Non-existent User Login", tester.test_nonexistent_user_login),
        
        # Protected Route Security Tests
        ("Portfolio Without Token", tester.test_protected_route_without_token),
        ("Portfolio With Invalid Token", tester.test_protected_route_with_invalid_token),
        
        # Protected Routes with Authentication
        ("Get Portfolio (Authenticated)", tester.test_get_portfolio_authenticated),
        ("Get Trades (Authenticated)", tester.test_get_trades_authenticated),
        ("Create Trade (Authenticated)", tester.test_create_trade_authenticated),
        ("Get Platforms (Authenticated)", tester.test_get_platforms_authenticated),
        ("Add Platform (Authenticated)", tester.test_add_platform_authenticated),
        ("Get Daily Plan (Authenticated)", tester.test_daily_plan_authenticated),
        
        # Public Routes (No Authentication Required)
        ("Market Data (Public)", tester.test_market_data_public),
        ("Multiple Prices (Public)", tester.test_multiple_prices_public),
        ("Asset Types (Public)", tester.test_asset_types_public),
        ("AI Analysis (Public)", tester.test_ai_analysis_public),
    ]
    
    print(f"\n📋 Running {len(tests)} JWT Authentication tests...")
    
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All JWT authentication tests passed!")
        return 0
    else:
        failed = tester.tests_run - tester.tests_passed
        print(f"⚠️  {failed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())