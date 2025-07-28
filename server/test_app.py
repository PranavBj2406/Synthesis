import requests
import json

# Test configuration
BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api/auth"

def test_signup_success():
    """Test successful signup"""
    print("Testing successful signup...")
    
    data = {
        "email": "eshwar@example.com",
        "username": "eshwar_roy",
        "password": "SecurePass123!",
        "phone": "1234567890"  # Optional field
    }
    
    response = requests.post(f"{API_URL}/signup", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_signup_duplicate_email():
    """Test signup with duplicate email"""
    print("Testing signup with duplicate email...")
    
    data = {
        "email": "eshwar@example.com",  # Same email as above
        "username": "different_user",
        "password": "AnotherPass123!"
    }
    
    response = requests.post(f"{API_URL}/signup", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_signup_duplicate_username():
    """Test signup with duplicate username"""
    print("Testing signup with duplicate username...")
    
    data = {
        "email": "different@example.com",
        "username": "eshwar_roy",  # Same username as first test
        "password": "AnotherPass123!"
    }
    
    response = requests.post(f"{API_URL}/signup", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_signup_validation_errors():
    """Test signup with validation errors"""
    print("Testing signup with validation errors...")
    
    # Missing required fields and invalid data
    data = {
        "email": "invalid-email",
        "username": "ab",  # Too short
        "password": "weak",  # Doesn't meet strength requirements
    }
    
    response = requests.post(f"{API_URL}/signup", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_check_email():
    """Test email availability check"""
    print("Testing email availability check...")
    
    # Check existing email
    data = {"email": "eshwar@example.com"}
    response = requests.post(f"{API_URL}/check-email", json=data)
    print(f"Existing email - Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Check new email
    data = {"email": "newemail@example.com"}
    response = requests.post(f"{API_URL}/check-email", json=data)
    print(f"New email - Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_check_username():
    """Test username availability check"""
    print("Testing username availability check...")
    
    # Check existing username
    data = {"username": "eshwar_roy"}
    response = requests.post(f"{API_URL}/check-username", json=data)
    print(f"Existing username - Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Check new username
    data = {"username": "new_user_123"}
    response = requests.post(f"{API_URL}/check-username", json=data)
    print(f"New username - Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_password_validation():
    """Test password validation"""
    print("Testing password validation...")
    
    passwords = [
        "weak",                    # Too weak
        "StrongPass123!",         # Valid
        "NoSpecialChar123",       # Missing special char
        "nouppercasechar123!",    # Missing uppercase
        "NOLOWERCASECHAR123!",    # Missing lowercase
        "NoNumbers!"              # Missing numbers
    ]
    
    for password in passwords:
        data = {"password": password}
        response = requests.post(f"{API_URL}/validate-password", json=data)
        print(f"Password '{password}' - Response: {response.json()}")
    
    print("-" * 50)

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    
    response = requests.get(f"{API_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

if __name__ == "__main__":
    print("Starting API Tests...\n")
    
    try:
        # Test health check first
        test_health_check()
        
        # Test signup functionality
        test_signup_success()
        test_signup_duplicate_email()
        test_signup_duplicate_username()
        test_signup_validation_errors()
        
        # Test utility endpoints
        test_check_email()
        test_check_username()
        test_password_validation()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        print("Make sure your Flask app is running on http://localhost:5000")
    except Exception as e:
        print(f"Error running tests: {str(e)}")