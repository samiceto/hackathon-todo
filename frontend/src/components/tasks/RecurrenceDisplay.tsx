/**
 * RecurrenceDisplay Component
 *
 * Displays a human-readable recurrence pattern from an iCal RRULE string.
 * Converts technical RRULE format (e.g., "FREQ=DAILY") to user-friendly text
 * (e.g., "Repeats daily").
 *
 * Features:
 * - Parses RRULE and displays frequency (daily, weekly, monthly, yearly)
 * - Shows interval (e.g., "every 2 weeks")
 * - Displays day of week for weekly recurrence (e.g., "on Monday")
 * - Shows COUNT limit (e.g., "5 times")
 * - Shows UNTIL date (e.g., "until 2026-12-31")
 * - Handles invalid RRULEs gracefully
 */

import React from "react";

interface RecurrenceDisplayProps {
  /** iCal RRULE format recurrence rule (e.g., "FREQ=DAILY") */
  recurrenceRule: string | null | undefined;
  /** Optional className for custom styling */
  className?: string;
}

/**
 * Parse RRULE string and convert to human-readable format.
 *
 * Supports:
 * - FREQ: DAILY, WEEKLY, MONTHLY, YEARLY
 * - INTERVAL: How often to repeat
 * - BYDAY: Day of week for weekly recurrence
 * - COUNT: Maximum number of occurrences
 * - UNTIL: End date for recurrence
 *
 * Examples:
 * - "FREQ=DAILY" → "Repeats daily"
 * - "FREQ=WEEKLY;BYDAY=MO" → "Repeats weekly on Monday"
 * - "FREQ=MONTHLY;BYMONTHDAY=1" → "Repeats monthly"
 * - "FREQ=DAILY;COUNT=5" → "Repeats daily (5 times)"
 * - "FREQ=WEEKLY;INTERVAL=2" → "Repeats every 2 weeks"
 */
function parseRRuleToHumanReadable(rrule: string): string {
  if (!rrule || rrule.trim() === "") {
    return "Does not repeat";
  }

  try {
    // Parse RRULE into key-value pairs
    const parts = rrule.split(";").reduce((acc, part) => {
      const [key, value] = part.split("=");
      if (key && value) {
        acc[key.toUpperCase()] = value.toUpperCase();
      }
      return acc;
    }, {} as Record<string, string>);

    // Extract frequency
    const freq = parts["FREQ"];
    if (!freq) {
      return "Custom recurrence pattern";
    }

    // Map frequency to human-readable terms
    const freqMap: Record<string, string> = {
      DAILY: "day",
      WEEKLY: "week",
      MONTHLY: "month",
      YEARLY: "year",
      HOURLY: "hour",
      MINUTELY: "minute",
      SECONDLY: "second",
    };

    const freqTerm = freqMap[freq] || "period";

    // Extract interval (default: 1)
    const interval = parseInt(parts["INTERVAL"] || "1", 10);

    // Build description
    let description = "";

    if (interval === 1) {
      description = `Repeats ${freqTerm}ly`;
    } else {
      description = `Repeats every ${interval} ${freqTerm}s`;
    }

    // Add day of week for weekly recurrence
    if (freq === "WEEKLY" && parts["BYDAY"]) {
      const daysMap: Record<string, string> = {
        MO: "Monday",
        TU: "Tuesday",
        WE: "Wednesday",
        TH: "Thursday",
        FR: "Friday",
        SA: "Saturday",
        SU: "Sunday",
      };

      const days = parts["BYDAY"]
        .split(",")
        .map((d) => daysMap[d.trim()] || d)
        .filter(Boolean);

      if (days.length > 0) {
        description += ` on ${days.join(", ")}`;
      }
    }

    // Add month day for monthly recurrence
    if (freq === "MONTHLY" && parts["BYMONTHDAY"]) {
      const day = parts["BYMONTHDAY"];
      description += ` on day ${day}`;
    }

    // Add count limit if present
    if (parts["COUNT"]) {
      description += ` (${parts["COUNT"]} times)`;
    }

    // Add until date if present
    if (parts["UNTIL"]) {
      // UNTIL format: YYYYMMDD or YYYYMMDDTHHMMSSZ
      const until = parts["UNTIL"];
      const year = until.substring(0, 4);
      const month = until.substring(4, 6);
      const day = until.substring(6, 8);
      description += ` (until ${year}-${month}-${day})`;
    }

    return description;
  } catch (error) {
    console.error("Failed to parse RRULE:", error);
    return "Custom recurrence pattern";
  }
}

/**
 * RecurrenceDisplay component for showing human-readable recurrence patterns.
 *
 * Usage:
 * ```tsx
 * <RecurrenceDisplay recurrenceRule="FREQ=DAILY" />
 * // Output: "Repeats daily"
 *
 * <RecurrenceDisplay recurrenceRule="FREQ=WEEKLY;BYDAY=MO,WE,FR" />
 * // Output: "Repeats weekly on Monday, Wednesday, Friday"
 *
 * <RecurrenceDisplay recurrenceRule={null} />
 * // Output: "Does not repeat"
 * ```
 */
export default function RecurrenceDisplay({
  recurrenceRule,
  className = "",
}: RecurrenceDisplayProps) {
  const displayText = parseRRuleToHumanReadable(recurrenceRule || "");

  return (
    <span
      className={`text-sm text-gray-600 dark:text-gray-400 ${className}`}
      title={recurrenceRule || "No recurrence"}
    >
      🔁 {displayText}
    </span>
  );
}
