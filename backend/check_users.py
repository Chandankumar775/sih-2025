import sqlite3

conn = sqlite3.connect('./auth/users.db')
conn.row_factory = sqlite3.Row
users = conn.execute('SELECT username, email, role FROM users').fetchall()

print('Current users in database:')
print('=' * 60)
for user in users:
    print(f"Username: {user['username']}")
    print(f"Email: {user['email']}")
    print(f"Role: {user['role']}")
    print('-' * 60)
conn.close()
