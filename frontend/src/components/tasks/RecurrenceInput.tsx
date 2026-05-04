/**
 * RecurrenceInput Component
 *
 * Interactive UI for creating and editing recurrence rules in iCal RRULE format.
 * Provides both preset options (daily, weekly, monthly) and custom RRULE input.
 *
 * Features:
 * - Preset buttons for common recurrence patterns
 * - Custom RRULE input for advanced users
 * - "No recurrence" option to clear recurrence
 * - Real-time preview of human-readable pattern
 * - Validation feedback for invalid RRULEs
 */

"use client";

import React, { useState, useEffect } from "react";
import RecurrenceDisplay from "./RecurrenceDisplay";

interface RecurrenceInputProps {
  /** Current recurrence rule value */
  value: string | null | undefined;
  /** Callback when recurrence rule changes */
  onChange: (recurrenceRule: string | null) => void;
  /** Optional className for custom styling */
  className?: string;
}

/**
 * Preset recurrence patterns for common use cases.
 */
const RECURRENCE_PRESETS = [
  { label: "No recurrence", value: null, description: "One-time task" },
  { label: "Daily", value: "FREQ=DAILY", description: "Repeats every day" },
  {
    label: "Weekly",
    value: "FREQ=WEEKLY",
    description: "Repeats every week",
  },
  {
    label: "Monthly",
    value: "FREQ=MONTHLY",
    description: "Repeats every month",
  },
  {
    label: "Weekdays",
    value: "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR",
    description: "Repeats Monday-Friday",
  },
  {
    label: "Bi-weekly",
    value: "FREQ=WEEKLY;INTERVAL=2",
    description: "Repeats every 2 weeks",
  },
];

/**
 * Basic RRULE validation.
 * Returns true if the RRULE has valid syntax (at minimum, contains FREQ=).
 */
function validateRRule(rrule: string): boolean {
  if (!rrule || rrule.trim() === "") {
    return true; // Empty is valid (no recurrence)
  }

  // Must contain FREQ= at minimum
  if (!rrule.includes("FREQ=")) {
    return false;
  }

  // Check for valid frequency values
  const freqMatch = rrule.match(/FREQ=(DAILY|WEEKLY|MONTHLY|YEARLY|HOURLY|MINUTELY|SECONDLY)/);
  if (!freqMatch) {
    return false;
  }

  return true;
}

/**
 * RecurrenceInput component for creating/editing recurrence rules.
 *
 * Usage:
 * ```tsx
 * const [recurrence, setRecurrence] = useState<string | null>(null);
 *
 * <RecurrenceInput
 *   value={recurrence}
 *   onChange={setRecurrence}
 * />
 * ```
 */
export default function RecurrenceInput({
  value,
  onChange,
  className = "",
}: RecurrenceInputProps) {
  const [customMode, setCustomMode] = useState(false);
  const [customValue, setCustomValue] = useState(value || "");
  const [validationError, setValidationError] = useState<string | null>(null);

  // Update customValue when value prop changes
  useEffect(() => {
    setCustomValue(value || "");
  }, [value]);

  /**
   * Handle preset button click.
   */
  const handlePresetClick = (presetValue: string | null) => {
    setCustomMode(false);
    setValidationError(null);
    onChange(presetValue);
  };

  /**
   * Handle custom RRULE input change.
   */
  const handleCustomChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setCustomValue(newValue);

    // Validate
    if (newValue.trim() === "") {
      setValidationError(null);
      onChange(null);
    } else if (validateRRule(newValue)) {
      setValidationError(null);
      onChange(newValue);
    } else {
      setValidationError(
        "Invalid RRULE format. Must start with FREQ= (e.g., FREQ=DAILY)"
      );
    }
  };

  /**
   * Check if a preset is currently selected.
   */
  const isPresetSelected = (presetValue: string | null) => {
    if (customMode) return false;
    if (presetValue === null && value === null) return true;
    return presetValue === value;
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Preset buttons */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Recurrence Pattern
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {RECURRENCE_PRESETS.map((preset) => (
            <button
              key={preset.label}
              type="button"
              onClick={() => handlePresetClick(preset.value)}
              className={`
                px-4 py-2 text-sm font-medium rounded-md border transition-colors
                ${
                  isPresetSelected(preset.value)
                    ? "bg-teal-600 text-white border-teal-600"
                    : "bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
                }
              `}
              title={preset.description}
            >
              {preset.label}
            </button>
          ))}
        </div>
      </div>

      {/* Custom RRULE input */}
      <div>
        <button
          type="button"
          onClick={() => setCustomMode(!customMode)}
          className="text-sm text-teal-600 dark:text-teal-400 hover:underline"
        >
          {customMode ? "Hide" : "Show"} custom recurrence rule
        </button>

        {customMode && (
          <div className="mt-2 space-y-2">
            <input
              type="text"
              value={customValue}
              onChange={handleCustomChange}
              placeholder="e.g., FREQ=DAILY;INTERVAL=2"
              className={`
                w-full px-3 py-2 border rounded-md
                bg-white dark:bg-gray-800
                text-gray-900 dark:text-gray-100
                placeholder-gray-400 dark:placeholder-gray-500
                ${
                  validationError
                    ? "border-red-500 focus:ring-red-500"
                    : "border-gray-300 dark:border-gray-600 focus:ring-teal-500"
                }
                focus:outline-none focus:ring-2
              `}
            />
            {validationError && (
              <p className="text-sm text-red-600 dark:text-red-400">
                {validationError}
              </p>
            )}
            <p className="text-xs text-gray-500 dark:text-gray-400">
              iCal RRULE format. Examples: FREQ=DAILY, FREQ=WEEKLY;BYDAY=MO,
              FREQ=MONTHLY;BYMONTHDAY=1
            </p>
          </div>
        )}
      </div>

      {/* Preview */}
      {value && !validationError && (
        <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-md border border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
            Preview:
          </p>
          <RecurrenceDisplay recurrenceRule={value} />
        </div>
      )}
    </div>
  );
}
