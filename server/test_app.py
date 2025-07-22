import requests
import json

# Test configuration
BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api/auth"

def test_signup_success():
    """Test successful signup"""
    print("Testing successful signup...")
    
    data = {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "1234567890"
    }
    
    response = requests.post(f"{API_URL}/signup", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_signup_duplicate_email():
    """Test signup with duplicate email"""
    print("Testing signup with duplicate email...")
    
    data = {
        "email": "test@example.com",  # Same email as above
        "password": "AnotherPass123!",
        "confirm_password": "AnotherPass123!",
        "first_name": "Jane",
        "last_name": "Smith"
    }
    
    response = requests.post(f"{API_URL}/signup", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_signup_validation_errors():
    """Test signup with validation errors"""
    print("Testing signup with validation errors...")
    
    # Missing required fields
    data = {
        "email": "invalid-email",
        "password": "weak",
        "first_name": "",
        "last_name": "Doe"
    }
    
    response = requests.post(f"{API_URL}/signup", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_check_email():
    """Test email availability check"""
    print("Testing email availability check...")
    
    # Check existing email
    data = {"email": "test@example.com"}
    response = requests.post(f"{API_URL}/check-email", json=data)
    print(f"Existing email - Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Check new email
    data = {"email": "newemail@example.com"}
    response = requests.post(f"{API_URL}/check-email", json=data)
    print(f"New email - Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_password_validation():
    """Test password validation"""
    print("Testing password validation...")
    
    passwords = [
        "weak",
        "StrongPass123!",
        "NoSpecialChar123",
        "nouppercasechar123!",
        "NOLOWERCASECHAR123!"
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
        test_signup_validation_errors()
        
        # Test utility endpoints
        test_check_email()
        test_password_validation()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        print("Make sure your Flask app is running on http://localhost:5000")
    except Exception as e:
        print(f"Error running tests: {str(e)}")