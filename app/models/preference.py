from dataclasses import dataclass
from typing import Optional


@dataclass
class UserPreferences:
    top_cuisines: list[str]
    has_enough_data: bool
    price_tier: Optional[int] = None
