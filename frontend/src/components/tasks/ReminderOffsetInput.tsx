/**
 * ReminderOffsetInput Component
 *
 * Input for setting reminder time offset (minutes before due date).
 * Provides preset options and custom input for flexible reminder scheduling.
 *
 * Features:
 * - Preset buttons for common intervals (15min, 30min, 1hr, 1day)
 * - Custom number input for any minute value
 * - Validation (requires due date, must be positive)
 * - Human-readable time display
 * - Disabled state when no due date is set
 */

"use client";

import React, { useState } from "react";

interface ReminderOffsetInputProps {
  /** Current reminder offset value (minutes) */
  value: string;
  /** Callback when reminder offset changes */
  onChange: (value: string) => void;
  /** Whether task has a due date (required for reminders) */
  hasDueDate: boolean;
  /** Optional error message */
  error?: string;
  /** Optional className for custom styling */
  className?: string;
}

/**
 * Preset reminder intervals (in minutes).
 */
const REMINDER_PRESETS = [
  { label: "15 min", value: 15, description: "15 minutes before" },
  { label: "30 min", value: 30, description: "30 minutes before" },
  { label: "1 hour", value: 60, description: "1 hour before" },
  { label: "1 day", value: 1440, description: "1 day before" },
];

/**
 * Convert minutes to human-readable format.
 */
function formatMinutes(minutes: number): string {
  if (minutes < 60) {
    return `${minutes} minute${minutes !== 1 ? "s" : ""}`;
  } else if (minutes < 1440) {
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    if (remainingMinutes === 0) {
      return `${hours} hour${hours !== 1 ? "s" : ""}`;
    }
    return `${hours}h ${remainingMinutes}m`;
  } else {
    const days = Math.floor(minutes / 1440);
    const remainingHours = Math.floor((minutes % 1440) / 60);
    if (remainingHours === 0) {
      return `${days} day${days !== 1 ? "s" : ""}`;
    }
    return `${days}d ${remainingHours}h`;
  }
}

/**
 * ReminderOffsetInput component for setting task reminders.
 *
 * Usage:
 * ```tsx
 * const [reminderOffset, setReminderOffset] = useState<string>("");
 * const [dueDate, setDueDate] = useState<string>("");
 *
 * <ReminderOffsetInput
 *   value={reminderOffset}
 *   onChange={setReminderOffset}
 *   hasDueDate={!!dueDate}
 * />
 * ```
 */
export default function ReminderOffsetInput({
  value,
  onChange,
  hasDueDate,
  error,
  className = "",
}: ReminderOffsetInputProps) {
  const [customMode, setCustomMode] = useState(false);

  const handlePresetClick = (presetValue: number) => {
    setCustomMode(false);
    onChange(String(presetValue));
  };

  const handleCustomChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  const handleClear = () => {
    onChange("");
    setCustomMode(false);
  };

  const numericValue = value ? parseInt(value, 10) : 0;
  const isPresetSelected = (presetValue: number) => {
    return !customMode && numericValue === presetValue;
  };

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Label */}
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        Reminder
        {!hasDueDate && (
          <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">
            (requires due date)
          </span>
        )}
      </label>

      {/* Preset buttons */}
      {hasDueDate && (
        <div>
          <div className="grid grid-cols-2 gap-2">
            {REMINDER_PRESETS.map((preset) => (
              <button
                key={preset.value}
                type="button"
                onClick={() => handlePresetClick(preset.value)}
                disabled={!hasDueDate}
                className={`
                  px-3 py-2 text-sm font-medium rounded-md border transition-colors
                  ${
                    isPresetSelected(preset.value)
                      ? "bg-purple-600 text-white border-purple-600"
                      : "bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
                  }
                  disabled:opacity-50 disabled:cursor-not-allowed
                `}
                title={preset.description}
              >
                {preset.label}
              </button>
            ))}
          </div>

          {/* Custom input toggle */}
          <button
            type="button"
            onClick={() => setCustomMode(!customMode)}
            className="mt-2 text-sm text-purple-600 dark:text-purple-400 hover:underline"
          >
            {customMode ? "Hide" : "Show"} custom reminder time
          </button>

          {/* Custom input */}
          {customMode && (
            <div className="mt-2 space-y-2">
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  value={value}
                  onChange={handleCustomChange}
                  placeholder="0"
                  min="1"
                  disabled={!hasDueDate}
                  className={`
                    flex-1 px-3 py-2 border rounded-md
                    bg-white dark:bg-gray-800
                    text-gray-900 dark:text-gray-100
                    border-gray-300 dark:border-gray-600
                    focus:outline-none focus:ring-2
                    ${
                      error
                        ? "border-red-500 focus:ring-red-500"
                        : "focus:ring-purple-500"
                    }
                    disabled:opacity-50 disabled:cursor-not-allowed
                  `}
                />
                <span className="text-sm text-gray-600 dark:text-gray-400 whitespace-nowrap">
                  minutes before
                </span>
              </div>
              {error && (
                <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* No due date message */}
      {!hasDueDate && (
        <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-md border border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Set a due date to enable reminders
          </p>
        </div>
      )}

      {/* Preview */}
      {hasDueDate && value && numericValue > 0 && !error && (
        <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-md border border-purple-200 dark:border-purple-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 text-purple-600 dark:text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
              />
            </svg>
            <span className="text-sm text-purple-700 dark:text-purple-300">
              Reminder: {formatMinutes(numericValue)} before due date
            </span>
          </div>
          <button
            type="button"
            onClick={handleClear}
            className="text-purple-600 dark:text-purple-400 hover:text-purple-800 dark:hover:text-purple-200"
            aria-label="Clear reminder"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
}
