import os
from dataclasses import dataclass

@dataclass
class TestUser:
    email: str
    password: str
    name: str
    is_admin: bool = False

# Test users - replace with actual test user credentials from your system
def load_test_users():
    # Load test users from environment variables
    # Example: TEST_USER_1_EMAIL, TEST_USER_1_PASSWORD, TEST_USER_1_NAME
    test_users = []
    
    # Load up to 3 test users
    for i in range(1, 4):
        email = os.getenv(f'TEST_USER_{i}_EMAIL')
        password = os.getenv(f'TEST_USER_{i}_PASSWORD')
        name = os.getenv(f'TEST_USER_{i}_NAME', f'Test User {i}')
        
        if email and password:
            test_users.append(TestUser(
                email=email,
                password=password,
                name=name
            ))
    
    # Load admin user
    admin_email = os.getenv('TEST_ADMIN_EMAIL')
    admin_password = os.getenv('TEST_ADMIN_PASSWORD')
    admin_name = os.getenv('TEST_ADMIN_NAME', 'Admin User')
    
    if admin_email and admin_password:
        test_users.append(TestUser(
            email=admin_email,
            password=admin_password,
            name=admin_name,
            is_admin=True
        ))
    
    if not test_users:
        raise ValueError(
            "No test users configured. Please set TEST_USER_1_EMAIL, TEST_USER_1_PASSWORD, "
            "TEST_ADMIN_EMAIL, and TEST_ADMIN_PASSWORD environment variables."
        )
    
    return test_users

TEST_USERS = load_test_users()
