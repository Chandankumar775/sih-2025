"""
Create demo users for the application
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.auth_manager import AuthManager

# Initialize auth manager
auth = AuthManager(db_path="./auth/users.db")

print("Creating demo users...")
print("=" * 60)

# Admin user (matching the login page)
result1 = auth.register_user(
    username="admin",
    email="admin@rakshanetra.mil",
    password="demo123",
    full_name="System Administrator",
    role="admin",
    unit="Cyber Defence HQ"
)
if result1["success"]:
    print("✅ Admin created: admin@rakshanetra.mil / demo123")
else:
    print(f"Admin: {result1['message']}")

# Reporter user (matching the login page)
result2 = auth.register_user(
    username="reporter",
    email="reporter@army.mil",
    password="demo123",
    full_name="Field Reporter",
    role="reporter",
    unit="Delhi Cantonment"
)
if result2["success"]:
    print("✅ Reporter created: reporter@army.mil / demo123")
else:
    print(f"Reporter: {result2['message']}")

print("=" * 60)
print("✅ Demo accounts are ready!")
