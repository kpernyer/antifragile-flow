import firebase_admin
from firebase_admin import auth, credentials

# Initialize the Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

users = [
    {
        "uid": "bob.greenland@globex-industrial-group.com",
        "email": "bob.greenland@globex-industrial-group.com",
        "password": "password123",
        "display_name": "Bob Greenland (IT Admin)",
    },
    {
        "uid": "mary.okeefe@globex-industrial-group.com",
        "email": "mary.okeefe@globex-industrial-group.com",
        "password": "password123",
        "display_name": "Mary O'Keefe (CEO)",
    },
    {
        "uid": "john.appelkvist@globex-industrial-group.com",
        "email": "john.appelkvist@globex-industrial-group.com",
        "password": "password123",
        "display_name": "John Appelkvist (VP of Sales)",
    },
    {
        "uid": "isac.ironsmith@globex-industrial-group.com",
        "email": "isac.ironsmith@globex-industrial-group.com",
        "password": "password123",
        "display_name": 'Isac "Happy" Ironsmith (VP of Engineering)',
    },
    {
        "uid": "priya.sharma@globex-industrial-group.com",
        "email": "priya.sharma@globex-industrial-group.com",
        "password": "password123",
        "display_name": "Priya Sharma (VP of Legal)",
    },
]

for user_data in users:
    try:
        user = auth.create_user(**user_data)
        print(f"Successfully created user: {user.uid}")
    except Exception as e:
        print(f"Error creating user {user_data['email']}: {e}")
