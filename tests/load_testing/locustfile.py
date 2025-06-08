from locust import HttpUser, task, between, TaskSet, tag
from faker import Faker
import random
import logging
from test_config import TEST_USERS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PilotBehavior(TaskSet):
    """Simulates a pilot's behavior on the portal"""
    
    def on_start(self):
        """Login when a pilot starts"""
        self.user_data = random.choice(TEST_USERS)
        self.login()
    
    def login(self):
        """Helper method to log in"""
        response = self.client.get("/pilot/login")
        if response.status_code == 200:
            csrf_token = response.text.split('name="csrf_token" value="')[1].split('"')[0]
            
            login_data = {
                "email": self.user_data.email,
                "password": self.user_data.password,
                "csrf_token": csrf_token
            }
            
            with self.client.post("/pilot/login", data=login_data, catch_response=True) as response:
                if response.status_code == 302 and "/pilot/dashboard" in response.headers.get("Location", ""):
                    logger.info(f"Successfully logged in as {self.user_data.email}")
                else:
                    logger.error(f"Login failed for {self.user_data.email}")
                    response.failure("Login failed")
    
    @task(3)
    def view_dashboard(self):
        """View the dashboard"""
        self.client.get("/pilot/dashboard")
    
    @task(2)
    def submit_logsheet(self):
        """Simulate submitting a logsheet"""
        fake = Faker()
        
        # Get the logsheet form
        response = self.client.get("/logsheet")
        if response.status_code != 200:
            return
            
        # Extract CSRF token if available
        csrf_token = ""
        if 'name="csrf_token"' in response.text:
            try:
                csrf_token = response.text.split('name="csrf_token" value="')[1].split('"')[0]
            except IndexError:
                pass
        
        # Prepare logsheet data
        logsheet_data = {
            "date": fake.date_this_year().strftime("%Y-%m-%d"),
            "aircraft": "C-GABC",
            "flight_time": f"{random.randint(1, 5)}.{random.randint(0, 59):02d}",
            "departure": "CYYZ",
            "arrival": "CYUL",
            "remarks": fake.sentence(),
            "csrf_token": csrf_token
        }
        
        # Submit the logsheet
        self.client.post("/logsheet/submit", data=logsheet_data)
    
    @task(1)
    def view_earnings(self):
        """View earnings page"""
        self.client.get("/pilot/earnings")

class AdminBehavior(TaskSet):
    """Simulates an admin's behavior on the portal"""
    
    def on_start(self):
        """Login when an admin starts"""
        admin_users = [u for u in TEST_USERS if "admin" in u.email]
        if admin_users:
            self.user_data = admin_users[0]
            self.login()
    
    def login(self):
        """Helper method to log in as admin"""
        response = self.client.get("/admin/login")
        if response.status_code == 200:
            csrf_token = response.text.split('name="csrf_token" value="')[1].split('"')[0]
            
            login_data = {
                "email": self.user_data.email,
                "password": self.user_data.password,
                "csrf_token": csrf_token
            }
            
            with self.client.post("/admin/login", data=login_data, catch_response=True) as response:
                if response.status_code == 302 and "/admin/dashboard" in response.headers.get("Location", ""):
                    logger.info(f"Admin logged in as {self.user_data.email}")
                else:
                    logger.error(f"Admin login failed for {self.user_data.email}")
                    response.failure("Admin login failed")
    
    @task(3)
    def view_admin_dashboard(self):
        """View admin dashboard"""
        self.client.get("/admin/dashboard")
    
    @task(2)
    def manage_pilots(self):
        """View and manage pilots"""
        self.client.get("/admin/pilots")
    
    @task(1)
    def generate_reports(self):
        """Generate reports"""
        self.client.get("/admin/reports")

class PilotUser(HttpUser):
    """Simulates a pilot user"""
    tasks = [PilotBehavior]
    wait_time = between(5, 15)  # Wait between 5-15 seconds between tasks
    weight = 3  # 3x more likely to be a pilot than an admin

class AdminUser(HttpUser):
    """Simulates an admin user"""
    tasks = [AdminBehavior]
    wait_time = between(10, 30)  # Wait between 10-30 seconds between tasks
    weight = 1  # Less frequent than pilots
