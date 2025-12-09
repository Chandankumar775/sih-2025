"""
Check if demo passwords work
"""
import sys
sys.path.insert(0, '.')

from modules.auth_manager import AuthManager

auth = AuthManager(db_path="./auth/users.db")

print("Testing login credentials...")
print("=" * 60)

# Test admin login
result1 = auth.login("admin@rakshanetra.mil", "demo123")
print(f"Admin login (demo123): {result1['success']}")
if not result1['success']:
    print(f"  Error: {result1['message']}")

# Also try with admin123 (the default password)
result2 = auth.login("admin@rakshanetra.mil", "admin123")
print(f"Admin login (admin123): {result2['success']}")
if not result2['success']:
    print(f"  Error: {result2['message']}")

# Test reporter
result3 = auth.login("reporter@army.mil", "demo123")
print(f"Reporter login (demo123): {result3['success']}")
if not result3['success']:
    print(f"  Error: {result3['message']}")

print("=" * 60)
