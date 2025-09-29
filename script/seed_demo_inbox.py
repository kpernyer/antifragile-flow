#!/usr/bin/env python3
"""
Seed demo inbox data for testing the rich inbox system
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.inbox_service import seed_demo_inbox_data

if __name__ == "__main__":
    print("🌱 Seeding demo inbox data...")
    service = seed_demo_inbox_data()
    print("📬 Demo inbox data created successfully!")

    # Show summary for each user
    users = ["mary", "john", "isac", "priya", "bob"]
    for user_id in users:
        summary = service.get_dashboard_summary(user_id)
        print(
            f"📊 {user_id}: {summary['total_messages']} messages, {summary['unread_count']} unread"
        )
