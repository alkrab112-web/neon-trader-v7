import requests
import json
import uuid

def test_enhanced_trading():
    base_url = "https://neon-trader.preview.emergentagent.com/api"
    
    # Setup authentication
    test_user_email = f"trader_{uuid.uuid4().hex[:8]}@neontrader.com"
    test_user_username = f"trader_{uuid.uuid4().hex[:8]}"
    test_password = "NeonTrader2024!"
    
    print("🔐 Setting up authentication...")
    
    # Register user
    registration_data = {
        "email": test_user_email,
        "username": test_user_username,
        "password": test_password,
        "confirm_password": test_password
    }
    
    response = requests.post(f"{base_url}/auth/register", json=registration_data)
    if response.status_code != 200:
        print(f"❌ Registration failed: {response.status_code}")
        return False
        
    auth_data = response.json()
    access_token = auth_data.get('access_token')
    
    if not access_token:
        print("❌ No access token received")
        return False
        
    print(f"✅ Authentication successful")
    
    # Test enhanced trading
    print("\n💼 Testing Enhanced Trading System...")
    
    trade_data = {
        "symbol": "BTCUSDT",
        "trade_type": "buy",
        "order_type": "market",
        "quantity": 0.01,
        "stop_loss": 42000,
        "take_profit": 50000
    }
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(f"{base_url}/trades", json=trade_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Trade created successfully")
        
        if 'trade' in result:
            trade = result['trade']
            print(f"📋 Trade Details:")
            print(f"   ID: {trade.get('id')}")
            print(f"   Platform: {trade.get('platform')}")
            
            # Check for enhanced fields
            execution_type = trade.get('execution_type')
            current_market_price = trade.get('current_market_price')
            
            if execution_type:
                print(f"   ✅ Execution Type: {execution_type}")
            else:
                print(f"   ❌ Missing execution_type")
                
            if current_market_price:
                print(f"   ✅ Current Market Price: ${current_market_price}")
            else:
                print(f"   ❌ Missing current_market_price")
                
            if execution_type and current_market_price:
                print(f"🎉 Enhanced trading system is working!")
                return True
            else:
                print(f"⚠️  Enhanced trading fields are missing")
                return False
        else:
            print(f"❌ No trade data in response")
            return False
    else:
        print(f"❌ Trade creation failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

if __name__ == "__main__":
    test_enhanced_trading()