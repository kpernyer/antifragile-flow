"""
Simple user management for demo - no authentication required
"""

from dataclasses import dataclass


@dataclass
class User:
    id: str
    email: str
    name: str
    role: str
    department: str


# Demo users for Globex Industrial Group
DEMO_USERS = {
    "mary": User(
        id="mary.okeefe",
        email="mary.okeefe@globex-industrial-group.com",
        name="Mary O'Keefe",
        role="CEO",
        department="Executive",
    ),
    "john": User(
        id="john.appelkvist",
        email="john.appelkvist@globex-industrial-group.com",
        name="John Appelkvist",
        role="VP of Sales",
        department="Sales",
    ),
    "isac": User(
        id="isac.ironsmith",
        email="isac.ironsmith@globex-industrial-group.com",
        name='Isac "Happy" Ironsmith',
        role="VP of Engineering",
        department="Engineering",
    ),
    "priya": User(
        id="priya.sharma",
        email="priya.sharma@globex-industrial-group.com",
        name="Priya Sharma",
        role="VP of Legal",
        department="Legal",
    ),
    "bob": User(
        id="bob.greenland",
        email="bob.greenland@globex-industrial-group.com",
        name="Bob Greenland",
        role="IT Admin",
        department="IT",
    ),
}


def get_user(user_id: str) -> User:
    """Get user by ID"""
    return DEMO_USERS.get(user_id)


def get_users_by_role(role: str) -> list[User]:
    """Get all users with a specific role"""
    return [user for user in DEMO_USERS.values() if role.lower() in user.role.lower()]


def get_all_users() -> dict[str, User]:
    """Get all demo users"""
    return DEMO_USERS
