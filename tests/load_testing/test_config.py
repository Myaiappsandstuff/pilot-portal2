from dataclasses import dataclass

@dataclass
class TestUser:
    email: str
    password: str
    name: str

# Test users - replace with actual test user credentials from your system
TEST_USERS = [
    TestUser(
        email="pilot1@example.com",
        password="pilot1pass",
        name="Pilot One"
    ),
    TestUser(
        email="pilot2@example.com",
        password="pilot2pass",
        name="Pilot Two"
    ),
    TestUser(
        email="pilot3@example.com",
        password="pilot3pass",
        name="Pilot Three"
    ),
    TestUser(
        email="test_admin@example.com",
        password="adminpass123",
        name="Test Admin"
    )
]
