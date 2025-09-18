import requests
import sys
import json
import uuid
from datetime import datetime

class NeonTraderComprehensiveTester:
    def __init__(self, base_url="https://neon-trader.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.access_token = None
        self.user_id = None
        self.test_user_email = f"trader_{uuid.uuid4().hex[:8]}@neontrader.com"
        self.test_user_username = f"trader_{uuid.uuid4().hex[:8]}"
        self.test_password = "NeonTrader2024!"
        self.created_trade_id = None
        self.created_platform_id = None
        self.test_results = {}
        self.critical_failures = []
        self.mock_features = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, timeout=30):
        """Run a single API test with detailed analysis"""
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
                    
                    # Analyze response for mock vs real data
                    self.analyze_response_authenticity(name, response_data)
                    
                    self.test_results[name] = {
                        'status': 'passed',
                        'response': response_data,
                        'analysis': self.get_response_analysis(name, response_data)
                    }
                    return True, response_data
                except:
                    self.test_results[name] = {'status': 'passed', 'response': {}, 'analysis': 'No JSON response'}
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    self.test_results[name] = {
                        'status': 'failed',
                        'error': error_data,
                        'expected_status': expected_status,
                        'actual_status': response.status_code
                    }
                    
                    # Track critical failures
                    if response.status_code >= 500:
                        self.critical_failures.append(f"{name}: Server Error {response.status_code}")
                    
                except:
                    error_text = response.text
                    print(f"   Error: {error_text}")
                    self.test_results[name] = {
                        'status': 'failed',
                        'error': error_text,
                        'expected_status': expected_status,
                        'actual_status': response.status_code
                    }
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout after {timeout}s")
            self.test_results[name] = {'status': 'timeout', 'timeout': timeout}
            self.critical_failures.append(f"{name}: Timeout after {timeout}s")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results[name] = {'status': 'error', 'exception': str(e)}
            self.critical_failures.append(f"{name}: Exception - {str(e)}")
            return False, {}

    def analyze_response_authenticity(self, test_name, response_data):
        """Analyze if response contains real or mock data"""
        if not response_data:
            return
            
        # Check for obvious mock patterns
        mock_indicators = [
            'test_', 'mock_', 'fake_', 'dummy_',
            'paper_trading', 'testnet', 'sandbox'
        ]
        
        response_str = json.dumps(response_data).lower()
        for indicator in mock_indicators:
            if indicator in response_str:
                self.mock_features.append(f"{test_name}: Contains '{indicator}' - likely mock data")
                break

    def get_response_analysis(self, test_name, response_data):
        """Get detailed analysis of response data"""
        if not response_data:
            return "Empty response"
            
        analysis = []
        
        # Check for real vs mock data patterns
        if 'BTCUSDT' in str(response_data):
            if isinstance(response_data, dict) and 'price' in response_data:
                price = response_data.get('price', 0)
                if 40000 <= price <= 50000:  # Reasonable BTC price range
                    analysis.append("Real-looking BTC price data")
                else:
                    analysis.append("Suspicious BTC price - might be mock")
        
        # Check for AI content
        if any(key in str(response_data) for key in ['analysis', 'market_analysis', 'opportunities']):
            if any(arabic in str(response_data) for arabic in ['السوق', 'تحليل', 'شراء', 'بيع']):
                analysis.append("Contains Arabic AI analysis - likely real AI")
            else:
                analysis.append("Contains analysis but no Arabic - might be mock")
        
        # Check for user-specific data
        if 'user_id' in str(response_data) and self.user_id:
            if self.user_id in str(response_data):
                analysis.append("User-specific data correctly isolated")
            else:
                analysis.append("User data isolation issue")
        
        return "; ".join(analysis) if analysis else "Standard response"

    def get_auth_headers(self):
        """Get authorization headers with JWT token"""
        if not self.access_token:
            return {}
        return {'Authorization': f'Bearer {self.access_token}'}

    # ========== Authentication Flow Tests ==========
    
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
            self.access_token = response.get('access_token')
            self.user_id = response.get('user_id')
            print(f"   ✅ Registered user ID: {self.user_id}")
            print(f"   ✅ JWT token received: {self.access_token[:20]}..." if self.access_token else "   ❌ No token received")
                
        return success, response

    def test_user_login(self):
        """Test user login with JWT token generation"""
        login_data = {
            "email": self.test_user_email,
            "password": self.test_password
        }
        
        success, response = self.run_test("User Login", "POST", "/auth/login", 200, login_data)
        
        if success and response:
            self.access_token = response.get('access_token')
            print(f"   ✅ Login successful for user: {response.get('username')}")
            
        return success, response

    def test_get_current_user(self):
        """Test getting current user info with JWT token"""
        if not self.access_token:
            print("❌ No access token available for authentication test")
            return False, {}
            
        auth_headers = self.get_auth_headers()
        return self.run_test("Get Current User", "GET", "/auth/me", 200, headers=auth_headers)

    # ========== Core Functionality Tests ==========
    
    def test_get_portfolio_functionality(self):
        """Test portfolio functionality - check if real or mock"""
        if not self.access_token:
            print("❌ No access token available for portfolio test")
            return False, {}
            
        auth_headers = self.get_auth_headers()
        success, response = self.run_test("Portfolio Functionality", "GET", "/portfolio", 200, headers=auth_headers)
        
        if success and response:
            # Analyze portfolio data authenticity
            balance = response.get('total_balance', 0)
            if balance == 10000.0:
                print("   ⚠️  Default balance detected - likely starting with mock data")
            else:
                print("   ✅ Non-default balance - might be real trading data")
                
            # Check for realistic portfolio structure
            required_fields = ['total_balance', 'available_balance', 'invested_balance', 'daily_pnl', 'total_pnl']
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                print(f"   ❌ Missing portfolio fields: {missing_fields}")
            else:
                print("   ✅ Complete portfolio structure")
                
        return success, response

    def test_get_trades_functionality(self):
        """Test trades functionality - check if real trading or paper trading"""
        if not self.access_token:
            print("❌ No access token available for trades test")
            return False, {}
            
        auth_headers = self.get_auth_headers()
        success, response = self.run_test("Trades Functionality", "GET", "/trades", 200, headers=auth_headers)
        
        if success and isinstance(response, list):
            if len(response) == 0:
                print("   ℹ️  No existing trades - clean account")
            else:
                print(f"   ✅ Found {len(response)} existing trades")
                # Check if trades are real or paper trading
                for trade in response[:3]:  # Check first 3 trades
                    platform = trade.get('platform', '')
                    if 'paper' in platform.lower() or 'test' in platform.lower():
                        print(f"   ⚠️  Trade on {platform} - paper trading detected")
                    else:
                        print(f"   ✅ Trade on {platform} - might be real trading")
                
        return success, response

    def test_create_trade_functionality(self):
        """Test creating a trade - check if it's real or simulated"""
        if not self.access_token:
            print("❌ No access token available for create trade test")
            return False, {}
            
        trade_data = {
            "symbol": "BTCUSDT",
            "trade_type": "buy",
            "order_type": "market",
            "quantity": 0.001,  # Small amount for testing
            "stop_loss": 42000,
            "take_profit": 47000
        }
        
        auth_headers = self.get_auth_headers()
        success, response = self.run_test("Create Trade Functionality", "POST", "/trades", 200, trade_data, auth_headers)
        
        if success and response and 'trade' in response:
            trade = response['trade']
            self.created_trade_id = trade.get('id')
            platform = trade.get('platform', '')
            entry_price = trade.get('entry_price', 0)
            
            print(f"   ✅ Created trade ID: {self.created_trade_id}")
            print(f"   Platform: {platform}")
            print(f"   Entry price: ${entry_price}")
            
            # Analyze if trade is real or simulated
            if 'paper' in platform.lower():
                print("   ⚠️  Paper trading detected - not real money")
                self.mock_features.append("Trading: Paper trading mode")
            elif platform == "paper_trading":
                print("   ⚠️  Explicit paper trading - simulated trades only")
                self.mock_features.append("Trading: Simulated trades only")
            else:
                print("   ✅ Platform suggests real trading capability")
                
            # Check if price is realistic
            if 40000 <= entry_price <= 50000:
                print("   ✅ Realistic BTC entry price")
            else:
                print("   ⚠️  Unusual entry price - might be mock data")
                
        return success, response

    def test_get_platforms_functionality(self):
        """Test platforms functionality - check real exchange connections"""
        if not self.access_token:
            print("❌ No access token available for platforms test")
            return False, {}
            
        auth_headers = self.get_auth_headers()
        success, response = self.run_test("Platforms Functionality", "GET", "/platforms", 200, headers=auth_headers)
        
        if success and isinstance(response, list):
            if len(response) == 0:
                print("   ℹ️  No platforms configured - user needs to add exchanges")
            else:
                print(f"   ✅ Found {len(response)} configured platforms")
                for platform in response:
                    name = platform.get('name', 'Unknown')
                    platform_type = platform.get('platform_type', 'Unknown')
                    status = platform.get('status', 'Unknown')
                    is_testnet = platform.get('is_testnet', True)
                    
                    print(f"   Platform: {name} ({platform_type}) - Status: {status}")
                    if is_testnet:
                        print("   ⚠️  Testnet mode - not real trading")
                        self.mock_features.append(f"Platform {name}: Testnet mode")
                    else:
                        print("   ✅ Live mode - real trading capability")
                
        return success, response

    def test_add_platform_functionality(self):
        """Test adding a platform - check real exchange integration"""
        if not self.access_token:
            print("❌ No access token available for add platform test")
            return False, {}
            
        platform_data = {
            "name": "Test Binance Connection",
            "platform_type": "binance",
            "api_key": "test_api_key_for_testing",
            "secret_key": "test_secret_key_for_testing",
            "is_testnet": True
        }
        
        auth_headers = self.get_auth_headers()
        success, response = self.run_test("Add Platform Functionality", "POST", "/platforms", 200, platform_data, auth_headers)
        
        if success and response and 'platform' in response:
            platform = response['platform']
            self.created_platform_id = platform.get('id')
            print(f"   ✅ Created platform ID: {self.created_platform_id}")
            
            if platform.get('is_testnet'):
                print("   ⚠️  Platform added in testnet mode")
                self.mock_features.append("Platform: Testnet mode only")
            else:
                print("   ✅ Platform configured for live trading")
                
        return success, response

    def test_platform_connection_test(self):
        """Test platform connection testing - check if real API integration works"""
        if not self.created_platform_id:
            print("❌ No platform ID available for connection test")
            return False, {}
            
        success, response = self.run_test("Platform Connection Test", "PUT", f"/platforms/{self.created_platform_id}/test", 200)
        
        if success and response:
            connection_success = response.get('success', False)
            message = response.get('message', '')
            status = response.get('status', '')
            
            print(f"   Connection result: {connection_success}")
            print(f"   Message: {message}")
            print(f"   Status: {status}")
            
            if 'وهمي' in message or 'mock' in message.lower():
                print("   ⚠️  Mock connection detected")
                self.mock_features.append("Platform Connection: Mock/simulated")
            elif connection_success:
                print("   ✅ Real connection test passed")
            else:
                print("   ❌ Connection test failed")
                
        return success, response

    # ========== AI and Intelligence Tests ==========
    
    def test_ai_daily_plan_functionality(self):
        """Test AI daily plan - check if real AI or mock responses"""
        if not self.access_token:
            print("❌ No access token available for AI daily plan test")
            return False, {}
            
        auth_headers = self.get_auth_headers()
        success, response = self.run_test("AI Daily Plan Functionality", "GET", "/ai/daily-plan", 200, headers=auth_headers, timeout=60)
        
        if success and response:
            market_analysis = response.get('market_analysis', '')
            trading_strategy = response.get('trading_strategy', '')
            opportunities = response.get('opportunities', [])
            
            print(f"   Market Analysis: {market_analysis[:100]}...")
            print(f"   Trading Strategy: {trading_strategy}")
            print(f"   Opportunities: {len(opportunities)} found")
            
            # Check if AI content is real or mock
            if any(arabic in market_analysis for arabic in ['السوق', 'تحليل', 'البيتكوين', 'العملات']):
                print("   ✅ Arabic AI analysis detected - likely real AI")
            else:
                print("   ⚠️  No Arabic content - might be mock AI")
                self.mock_features.append("AI Daily Plan: No Arabic content - possibly mock")
                
            # Check for generic vs specific analysis
            if len(market_analysis) > 50 and 'استقرار' not in market_analysis:
                print("   ✅ Detailed analysis - likely real AI")
            else:
                print("   ⚠️  Generic analysis - might be template response")
                
        return success, response

    def test_ai_market_analysis_functionality(self):
        """Test AI market analysis - check Emergent LLM integration"""
        analysis_data = {
            "symbol": "BTCUSDT",
            "timeframe": "1h"
        }
        
        success, response = self.run_test("AI Market Analysis Functionality", "POST", "/ai/analyze", 200, analysis_data, timeout=60)
        
        if success and response:
            analysis = response.get('analysis', '')
            market_data = response.get('market_data', {})
            symbol = response.get('symbol', '')
            
            print(f"   Symbol: {symbol}")
            print(f"   Analysis: {analysis[:150]}...")
            
            # Check if analysis is real AI or fallback
            if any(arabic in analysis for arabic in ['تحليل', 'السعر', 'المقاومة', 'الدعم']):
                print("   ✅ Arabic AI analysis - Emergent LLM working")
            else:
                print("   ⚠️  No Arabic AI content - might be fallback response")
                self.mock_features.append("AI Analysis: No Arabic - possibly fallback")
                
            # Check market data authenticity
            if market_data and 'price' in market_data:
                price = market_data.get('price', 0)
                if 40000 <= price <= 50000:
                    print("   ✅ Realistic market data")
                else:
                    print("   ⚠️  Unusual market data")
                    
        return success, response

    # ========== Market Data Tests ==========
    
    def test_market_data_functionality(self):
        """Test market data - check if real or mock prices"""
        success, response = self.run_test("Market Data Functionality", "GET", "/market/BTCUSDT", 200)
        
        if success and response:
            price = response.get('price', 0)
            change_24h = response.get('change_24h', 0)
            volume_24h = response.get('volume_24h', 0)
            asset_type = response.get('asset_type', '')
            
            print(f"   Price: ${price}")
            print(f"   24h Change: ${change_24h}")
            print(f"   24h Volume: {volume_24h}")
            print(f"   Asset Type: {asset_type}")
            
            # Check if data looks real
            if 40000 <= price <= 50000:
                print("   ✅ Realistic BTC price range")
            else:
                print("   ⚠️  Price outside normal BTC range - might be mock")
                self.mock_features.append("Market Data: Unusual BTC price")
                
            if volume_24h > 1000000:
                print("   ✅ Realistic trading volume")
            else:
                print("   ⚠️  Low volume - might be mock data")
                
        return success, response

    def test_binance_api_connection(self):
        """Test if Binance API is actually working"""
        # Test multiple crypto symbols to see if real Binance data
        symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
        real_data_count = 0
        
        for symbol in symbols:
            success, response = self.run_test(f"Binance API - {symbol}", "GET", f"/market/{symbol}", 200)
            if success and response:
                price = response.get('price', 0)
                # Check if prices are in realistic ranges
                if symbol == 'BTCUSDT' and 40000 <= price <= 50000:
                    real_data_count += 1
                elif symbol == 'ETHUSDT' and 2000 <= price <= 4000:
                    real_data_count += 1
                elif symbol == 'ADAUSDT' and 0.3 <= price <= 1.0:
                    real_data_count += 1
        
        if real_data_count >= 2:
            print("   ✅ Multiple realistic prices - likely real Binance API")
        else:
            print("   ⚠️  Prices don't match expected ranges - might be mock data")
            self.mock_features.append("Binance API: Prices outside expected ranges")
            
        return real_data_count >= 2, {}

    def test_asset_types_functionality(self):
        """Test asset types - check market coverage"""
        success, response = self.run_test("Asset Types Functionality", "GET", "/market/types/all", 200)
        
        if success and response:
            asset_types = list(response.keys()) if isinstance(response, dict) else []
            print(f"   Supported asset types: {asset_types}")
            
            expected_types = ['crypto', 'forex', 'stocks', 'commodities', 'indices']
            supported_count = sum(1 for t in expected_types if t in asset_types)
            
            if supported_count >= 4:
                print("   ✅ Comprehensive asset type coverage")
            else:
                print("   ⚠️  Limited asset type coverage")
                
            # Check if each type has symbols
            for asset_type, data in response.items():
                if isinstance(data, dict) and 'symbols' in data:
                    symbols = data['symbols']
                    print(f"   {asset_type}: {len(symbols)} symbols")
                else:
                    print(f"   {asset_type}: No symbols data")
                    
        return success, response

    # ========== Notifications and Smart Features Tests ==========
    
    def test_notifications_functionality(self):
        """Test notifications system"""
        if not self.access_token:
            print("❌ No access token available for notifications test")
            return False, {}
            
        auth_headers = self.get_auth_headers()
        success, response = self.run_test("Notifications Functionality", "GET", "/notifications", 200, headers=auth_headers)
        
        if success and isinstance(response, list):
            print(f"   ✅ Found {len(response)} notifications")
            
            # Check notification quality
            for notification in response[:3]:  # Check first 3
                title = notification.get('title', '')
                message = notification.get('message', '')
                notification_type = notification.get('type', '')
                
                if any(arabic in title + message for arabic in ['تحليل', 'السوق', 'فرصة']):
                    print("   ✅ Arabic notification content - real AI")
                else:
                    print("   ⚠️  No Arabic content in notifications")
                    
        return success, response

    def test_smart_alert_functionality(self):
        """Test smart alert generation"""
        if not self.access_token:
            print("❌ No access token available for smart alert test")
            return False, {}
            
        auth_headers = self.get_auth_headers()
        success, response = self.run_test("Smart Alert Functionality", "POST", "/notifications/smart-alert", 200, headers=auth_headers, timeout=60)
        
        if success and response:
            notification = response.get('notification', {})
            analysis = response.get('analysis', '')
            opportunities = response.get('opportunities', [])
            
            print(f"   Analysis length: {len(analysis)} characters")
            print(f"   Opportunities: {len(opportunities)} found")
            
            # Check if AI analysis is real
            if any(arabic in analysis for arabic in ['السوق', 'تحليل', 'الأسواق']):
                print("   ✅ Arabic AI analysis in smart alert")
            else:
                print("   ⚠️  No Arabic AI content - might be mock")
                self.mock_features.append("Smart Alerts: No Arabic AI content")
                
        return success, response

    def test_trading_opportunities_functionality(self):
        """Test trading opportunities detection"""
        if not self.access_token:
            print("❌ No access token available for opportunities test")
            return False, {}
            
        auth_headers = self.get_auth_headers()
        success, response = self.run_test("Trading Opportunities Functionality", "GET", "/notifications/opportunities", 200, headers=auth_headers)
        
        if success and response:
            opportunities = response.get('opportunities', [])
            print(f"   ✅ Found {len(opportunities)} trading opportunities")
            
            for opp in opportunities[:2]:  # Check first 2
                symbol = opp.get('symbol', '')
                confidence = opp.get('confidence', 0)
                description = opp.get('description', '')
                
                print(f"   Opportunity: {symbol} (Confidence: {confidence}%)")
                
                if confidence > 50 and len(description) > 20:
                    print("   ✅ Detailed opportunity analysis")
                else:
                    print("   ⚠️  Basic opportunity data - might be mock")
                    
        return success, response

    # ========== Environment and Integration Tests ==========
    
    def test_emergent_llm_integration(self):
        """Test if Emergent LLM key is working"""
        # This is tested indirectly through AI endpoints
        ai_endpoints_with_arabic = 0
        
        # Check daily plan
        if self.access_token:
            auth_headers = self.get_auth_headers()
            success, response = self.run_test("Emergent LLM Test - Daily Plan", "GET", "/ai/daily-plan", 200, headers=auth_headers, timeout=60)
            if success and response:
                analysis = response.get('market_analysis', '')
                if any(arabic in analysis for arabic in ['السوق', 'تحليل']):
                    ai_endpoints_with_arabic += 1
        
        # Check market analysis
        analysis_data = {"symbol": "BTCUSDT", "timeframe": "1h"}
        success, response = self.run_test("Emergent LLM Test - Analysis", "POST", "/ai/analyze", 200, analysis_data, timeout=60)
        if success and response:
            analysis = response.get('analysis', '')
            if any(arabic in analysis for arabic in ['تحليل', 'السعر']):
                ai_endpoints_with_arabic += 1
        
        if ai_endpoints_with_arabic >= 1:
            print("   ✅ Emergent LLM integration working - Arabic AI content detected")
            return True, {"working": True, "arabic_endpoints": ai_endpoints_with_arabic}
        else:
            print("   ❌ Emergent LLM integration not working - no Arabic AI content")
            self.critical_failures.append("Emergent LLM: No Arabic AI content generated")
            return False, {"working": False, "arabic_endpoints": 0}

    def generate_comprehensive_report(self):
        """Generate comprehensive diagnostic report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE NEON TRADER V7 DIAGNOSTIC REPORT")
        print("=" * 80)
        
        # Overall statistics
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"\n📈 OVERALL STATISTICS:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Critical failures
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                print(f"   ❌ {failure}")
        else:
            print(f"\n✅ NO CRITICAL FAILURES DETECTED")
        
        # Mock vs Real functionality analysis
        if self.mock_features:
            print(f"\n⚠️  MOCK/SIMULATED FEATURES DETECTED ({len(self.mock_features)}):")
            for mock in self.mock_features:
                print(f"   🎭 {mock}")
        else:
            print(f"\n✅ NO OBVIOUS MOCK FEATURES DETECTED")
        
        # Feature-by-feature analysis
        print(f"\n🔍 FEATURE ANALYSIS:")
        
        # Authentication
        auth_tests = ['User Registration', 'User Login', 'Get Current User']
        auth_passed = sum(1 for test in auth_tests if self.test_results.get(test, {}).get('status') == 'passed')
        print(f"   🔐 Authentication: {auth_passed}/{len(auth_tests)} working")
        
        # Trading functionality
        trading_tests = ['Portfolio Functionality', 'Trades Functionality', 'Create Trade Functionality']
        trading_passed = sum(1 for test in trading_tests if self.test_results.get(test, {}).get('status') == 'passed')
        print(f"   💰 Trading: {trading_passed}/{len(trading_tests)} working")
        
        # Platform integration
        platform_tests = ['Platforms Functionality', 'Add Platform Functionality', 'Platform Connection Test']
        platform_passed = sum(1 for test in platform_tests if self.test_results.get(test, {}).get('status') == 'passed')
        print(f"   🔗 Platforms: {platform_passed}/{len(platform_tests)} working")
        
        # AI features
        ai_tests = ['AI Daily Plan Functionality', 'AI Market Analysis Functionality']
        ai_passed = sum(1 for test in ai_tests if self.test_results.get(test, {}).get('status') == 'passed')
        print(f"   🤖 AI Features: {ai_passed}/{len(ai_tests)} working")
        
        # Market data
        market_tests = ['Market Data Functionality', 'Asset Types Functionality', 'Binance API - BTCUSDT']
        market_passed = sum(1 for test in market_tests if self.test_results.get(test, {}).get('status') == 'passed')
        print(f"   📊 Market Data: {market_passed}/{len(market_tests)} working")
        
        # Smart features
        smart_tests = ['Notifications Functionality', 'Smart Alert Functionality', 'Trading Opportunities Functionality']
        smart_passed = sum(1 for test in smart_tests if self.test_results.get(test, {}).get('status') == 'passed')
        print(f"   🧠 Smart Features: {smart_passed}/{len(smart_tests)} working")
        
        # Final verdict
        print(f"\n🎯 FINAL VERDICT:")
        if success_rate >= 90:
            print("   ✅ EXCELLENT - Most functionality working properly")
        elif success_rate >= 75:
            print("   ✅ GOOD - Core functionality working with minor issues")
        elif success_rate >= 60:
            print("   ⚠️  FAIR - Some functionality working but significant issues")
        else:
            print("   ❌ POOR - Major functionality issues detected")
            
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if len(self.critical_failures) > 0:
            print("   🔧 Fix critical failures first")
        if len(self.mock_features) > 3:
            print("   🎭 Replace mock features with real implementations")
        if ai_passed < 2:
            print("   🤖 Check Emergent LLM integration and API key")
        if platform_passed < 2:
            print("   🔗 Verify exchange API integrations")
            
        return {
            'success_rate': success_rate,
            'critical_failures': len(self.critical_failures),
            'mock_features': len(self.mock_features),
            'recommendations': []
        }

def main():
    print("🚀 Starting Neon Trader V7 Comprehensive Functionality Test")
    print("🔍 Testing all features to identify real vs mock functionality")
    print("=" * 80)
    
    tester = NeonTraderComprehensiveTester()
    
    # Comprehensive test sequence
    tests = [
        # Core Authentication
        ("API Status", tester.test_api_status),
        ("User Registration", tester.test_user_registration),
        ("User Login", tester.test_user_login),
        ("Get Current User", tester.test_get_current_user),
        
        # Core Trading Functionality
        ("Portfolio Functionality", tester.test_get_portfolio_functionality),
        ("Trades Functionality", tester.test_get_trades_functionality),
        ("Create Trade Functionality", tester.test_create_trade_functionality),
        
        # Platform Integration
        ("Platforms Functionality", tester.test_get_platforms_functionality),
        ("Add Platform Functionality", tester.test_add_platform_functionality),
        ("Platform Connection Test", tester.test_platform_connection_test),
        
        # AI and Intelligence
        ("AI Daily Plan Functionality", tester.test_ai_daily_plan_functionality),
        ("AI Market Analysis Functionality", tester.test_ai_market_analysis_functionality),
        ("Emergent LLM Integration", tester.test_emergent_llm_integration),
        
        # Market Data
        ("Market Data Functionality", tester.test_market_data_functionality),
        ("Binance API Connection", tester.test_binance_api_connection),
        ("Asset Types Functionality", tester.test_asset_types_functionality),
        
        # Smart Features
        ("Notifications Functionality", tester.test_notifications_functionality),
        ("Smart Alert Functionality", tester.test_smart_alert_functionality),
        ("Trading Opportunities Functionality", tester.test_trading_opportunities_functionality),
    ]
    
    print(f"\n📋 Running {len(tests)} comprehensive functionality tests...")
    
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            tester.critical_failures.append(f"{test_name}: Exception - {str(e)}")
    
    # Generate comprehensive report
    report = tester.generate_comprehensive_report()
    
    return 0 if report['success_rate'] >= 75 else 1

if __name__ == "__main__":
    sys.exit(main())