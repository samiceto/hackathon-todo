"""Models for Reminder Service.

The Reminder model is shared with the main backend API to ensure consistency.
We import it from the backend/api models directory.
"""

# Import Reminder model from backend/api
import sys
from pathlib import Path

# Add backend/api to Python path to import shared models
api_path = Path(__file__).parent.parent.parent.parent / "api" / "src"
sys.path.insert(0, str(api_path))

from models.reminder import Reminder
from models.event import ReminderDueEvent

__all__ = ["Reminder", "ReminderDueEvent"]
