"""
User profile loader for demo personalities and behavioral traits
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class UserProfile:
    basic_info: dict[str, Any]
    personality: dict[str, Any]
    behavioral_traits: dict[str, Any]
    communication_patterns: dict[str, Any]
    preferences: dict[str, Any]
    backstory: dict[str, Any]


def load_user_profile(user_id: str) -> UserProfile | None:
    """Load user profile from YAML file"""
    # Look for profile in demo-data directory
    profile_path = Path(__file__).parent.parent.parent / "demo-data" / f"{user_id}.yaml"

    if not profile_path.exists():
        return None

    try:
        with open(profile_path) as file:
            data = yaml.safe_load(file)
            return UserProfile(
                basic_info=data.get("basic_info", {}),
                personality=data.get("personality", {}),
                behavioral_traits=data.get("behavioral_traits", {}),
                communication_patterns=data.get("communication_patterns", {}),
                preferences=data.get("preferences", {}),
                backstory=data.get("backstory", {}),
            )
    except Exception as e:
        print(f"Error loading profile for {user_id}: {e}")
        return None


def get_user_display_info(user_id: str) -> tuple[str, str, str]:
    """Get three-line display information for a user"""
    profile = load_user_profile(user_id)

    if not profile:
        return (
            f"User: {user_id}",
            "Profile: No profile data available",
            "Style: Standard response pattern",
        )

    basic = profile.basic_info
    personality = profile.personality
    behavioral = profile.behavioral_traits
    backstory = profile.backstory

    # Line 1: Basic info with experience
    line1 = f"👤 {basic.get('name', user_id)} | {basic.get('role', 'Unknown')} | {backstory.get('experience_years', '?')} years exp"

    # Line 2: Personality and decision style
    decision_style = personality.get("decision_style", "balanced")
    response_time = personality.get("response_time", "moderate")
    agreement = personality.get("agreement_tendency", "moderate")
    line2 = f"🧠 {decision_style.title()} decision-maker | {response_time} responder | {agreement} agreement tendency"

    # Line 3: Communication and behavioral traits
    comm_style = personality.get("communication_style", "professional")
    detail_level = personality.get("detail_orientation", "balanced")
    typical_time = behavioral.get("typical_response_time_minutes", 15)
    line3 = f"💬 {comm_style.title()} communicator | {detail_level} detail focus | ~{typical_time}min response time"

    return (line1, line2, line3)


def get_behavioral_modifier(user_id: str, context: str = "general") -> dict[str, Any]:
    """Get behavioral modifiers for AI responses"""
    profile = load_user_profile(user_id)

    if not profile:
        return {}

    return {
        "response_time_minutes": profile.behavioral_traits.get("typical_response_time_minutes", 15),
        "agreement_probability": profile.behavioral_traits.get("agrees_with_majority", 0.5),
        "detail_level": profile.personality.get("detail_orientation", "balanced"),
        "communication_style": profile.personality.get("communication_style", "professional"),
        "uses_data": profile.communication_patterns.get("uses_data", 0.6),
        "decision_factors": profile.preferences.get("decision_factors", []),
        "management_philosophy": profile.backstory.get("management_philosophy", ""),
    }
