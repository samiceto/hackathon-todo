"""Recurrence service for parsing RRULE and calculating next occurrences."""

import logging
from datetime import datetime, timezone
from typing import Optional

from dateutil.rrule import rrulestr, rrule
from dateutil.parser import parse as parse_datetime

logger = logging.getLogger(__name__)


class RecurrenceService:
    """Service for handling recurring task logic.

    Uses python-dateutil to parse iCal RRULE format strings and calculate
    next occurrence times for recurring tasks.

    Supported RRULE features:
    - FREQ: DAILY, WEEKLY, MONTHLY, YEARLY
    - INTERVAL: How often to repeat (e.g., every 2 weeks)
    - COUNT: Maximum number of occurrences
    - UNTIL: End date for recurrence
    - BYDAY: Day of week for weekly recurrence (MO, TU, WE, TH, FR, SA, SU)
    - BYMONTHDAY: Day of month for monthly recurrence (1-31)
    - BYHOUR, BYMINUTE: Time of day for occurrence

    Examples:
    - "FREQ=DAILY": Every day
    - "FREQ=WEEKLY;BYDAY=MO": Every Monday
    - "FREQ=MONTHLY;BYMONTHDAY=1": First day of every month
    - "FREQ=DAILY;COUNT=5": Daily for 5 occurrences
    - "FREQ=WEEKLY;INTERVAL=2": Every 2 weeks
    """

    @staticmethod
    def validate_rrule(rrule_str: str) -> bool:
        """Validate an RRULE string format.

        Args:
            rrule_str: iCal RRULE format string (e.g., "FREQ=DAILY")

        Returns:
            True if valid, False otherwise
        """
        if not rrule_str or not isinstance(rrule_str, str):
            return False

        try:
            # Try to parse the RRULE
            rrulestr(rrule_str, dtstart=datetime.now(timezone.utc))
            return True
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid RRULE: {rrule_str}, error: {str(e)}")
            return False

    @staticmethod
    def calculate_next_occurrence(
        rrule_str: str,
        after: Optional[datetime] = None
    ) -> Optional[datetime]:
        """Calculate the next occurrence time for a recurring task.

        Args:
            rrule_str: iCal RRULE format string
            after: Calculate next occurrence after this time (default: now)

        Returns:
            Next occurrence datetime (UTC), or None if no more occurrences

        Raises:
            ValueError: If RRULE string is invalid
        """
        if not rrule_str:
            return None

        # Default to current time if not specified
        if after is None:
            after = datetime.now(timezone.utc)

        # Ensure after is timezone-aware (UTC)
        if after.tzinfo is None:
            after = after.replace(tzinfo=timezone.utc)

        try:
            # Parse RRULE with start time
            rule = rrulestr(rrule_str, dtstart=after)

            # Get next occurrence after the given time
            next_occurrence = rule.after(after, inc=False)

            # Convert to UTC if needed
            if next_occurrence and next_occurrence.tzinfo is None:
                next_occurrence = next_occurrence.replace(tzinfo=timezone.utc)

            return next_occurrence

        except (ValueError, TypeError) as e:
            logger.error(f"Failed to calculate next occurrence for RRULE: {rrule_str}, error: {str(e)}")
            raise ValueError(f"Invalid RRULE format: {str(e)}")

    @staticmethod
    def rrule_to_human_readable(rrule_str: str) -> str:
        """Convert RRULE string to human-readable format.

        Args:
            rrule_str: iCal RRULE format string

        Returns:
            Human-readable description (e.g., "Repeats daily", "Repeats every Monday")
        """
        if not rrule_str:
            return "Does not repeat"

        try:
            # Parse RRULE
            rule = rrulestr(rrule_str, dtstart=datetime.now(timezone.utc))

            # Extract frequency
            freq_map = {
                0: "year",     # YEARLY
                1: "month",    # MONTHLY
                2: "week",     # WEEKLY
                3: "day",      # DAILY
                4: "hour",     # HOURLY
                5: "minute",   # MINUTELY
                6: "second"    # SECONDLY
            }

            freq = freq_map.get(rule._freq, "period")
            interval = getattr(rule, '_interval', 1)

            # Build description
            if interval == 1:
                description = f"Repeats {freq}ly"
            else:
                description = f"Repeats every {interval} {freq}s"

            # Add day of week for weekly recurrence
            if rule._freq == 2 and rule._byweekday:  # WEEKLY
                days_map = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
                           4: "Friday", 5: "Saturday", 6: "Sunday"}
                days = [days_map.get(d, "") for d in rule._byweekday if d in days_map]
                if days:
                    description += f" on {', '.join(days)}"

            # Add count limit if present
            if rule._count:
                description += f" ({rule._count} times)"

            # Add until date if present
            if rule._until:
                until_str = rule._until.strftime("%Y-%m-%d")
                description += f" (until {until_str})"

            return description

        except Exception as e:
            logger.warning(f"Failed to convert RRULE to human-readable: {rrule_str}, error: {str(e)}")
            return "Custom recurrence pattern"

    @staticmethod
    def get_occurrences_count(
        rrule_str: str,
        start: Optional[datetime] = None,
        limit: int = 100
    ) -> int:
        """Get the count of occurrences for a recurrence rule.

        Args:
            rrule_str: iCal RRULE format string
            start: Start time (default: now)
            limit: Maximum occurrences to check (default: 100)

        Returns:
            Number of occurrences (capped at limit for infinite recurrence)
        """
        if not rrule_str:
            return 0

        if start is None:
            start = datetime.now(timezone.utc)

        # Ensure start is timezone-aware
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)

        try:
            rule = rrulestr(rrule_str, dtstart=start)

            # If COUNT is specified in RRULE, return it
            if rule._count:
                return min(rule._count, limit)

            # If UNTIL is specified, count occurrences up to that date
            if rule._until:
                occurrences = list(rule.between(start, rule._until, inc=True))
                return min(len(occurrences), limit)

            # For infinite recurrence, return limit
            return limit

        except Exception as e:
            logger.warning(f"Failed to get occurrences count: {rrule_str}, error: {str(e)}")
            return 0
