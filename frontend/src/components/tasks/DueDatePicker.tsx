/**
 * DueDatePicker Component
 *
 * Interactive date and time picker for task due dates.
 * Provides a clean, user-friendly interface for selecting deadlines.
 *
 * Features:
 * - Native datetime-local input with good browser support
 * - Timezone-aware (local timezone)
 * - Optional clear button
 * - Visual feedback for past/future dates
 * - Accessible keyboard navigation
 */

"use client";

interface DueDatePickerProps {
  /** Current due date value (ISO 8601 string or datetime-local format) */
  value: string;
  /** Callback when due date changes */
  onChange: (value: string) => void;
  /** Optional label text */
  label?: string;
  /** Show clear button to remove due date */
  showClear?: boolean;
  /** Minimum allowed date (ISO 8601 string) */
  minDate?: string;
  /** Optional className for custom styling */
  className?: string;
}

/**
 * Format ISO date string to datetime-local input format (YYYY-MM-DDTHH:MM).
 */
function formatForInput(isoString: string): string {
  if (!isoString) return "";
  const date = new Date(isoString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  return `${year}-${month}-${day}T${hours}:${minutes}`;
}

/**
 * Check if a date is in the past.
 */
function isPast(dateString: string): boolean {
  if (!dateString) return false;
  const date = new Date(dateString);
  const now = new Date();
  return date < now;
}

/**
 * DueDatePicker component for selecting task deadlines.
 *
 * Usage:
 * ```tsx
 * const [dueDate, setDueDate] = useState<string>("");
 *
 * <DueDatePicker
 *   value={dueDate}
 *   onChange={setDueDate}
 *   label="Due Date"
 *   showClear
 * />
 * ```
 */
export default function DueDatePicker({
  value,
  onChange,
  label = "Due Date",
  showClear = true,
  minDate,
  className = "",
}: DueDatePickerProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  const handleClear = () => {
    onChange("");
  };

  const inputValue = formatForInput(value);
  const minValue = minDate ? formatForInput(minDate) : undefined;
  const isOverdue = isPast(value);

  return (
    <div className={`space-y-2 ${className}`}>
      {/* Label */}
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {label}
      </label>

      {/* Input container */}
      <div className="relative">
        <input
          type="datetime-local"
          value={inputValue}
          onChange={handleChange}
          min={minValue}
          className={`
            w-full px-3 py-2 pr-10 border rounded-md
            bg-white dark:bg-gray-800
            text-gray-900 dark:text-gray-100
            border-gray-300 dark:border-gray-600
            focus:outline-none focus:ring-2
            ${
              isOverdue
                ? "border-red-300 focus:ring-red-500"
                : "focus:ring-teal-500"
            }
            transition-colors
          `}
        />

        {/* Calendar icon */}
        <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
          <svg
            className={`w-5 h-5 ${isOverdue ? "text-red-400" : "text-gray-400"}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        </div>

        {/* Clear button */}
        {showClear && value && (
          <button
            type="button"
            onClick={handleClear}
            className="
              absolute right-10 top-1/2 -translate-y-1/2
              p-1 rounded-full
              text-gray-400 hover:text-gray-600
              hover:bg-gray-100 dark:hover:bg-gray-700
              transition-colors
              focus:outline-none focus:ring-2 focus:ring-teal-500
            "
            aria-label="Clear due date"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </div>

      {/* Helper text */}
      {isOverdue && value && (
        <p className="text-sm text-red-600 dark:text-red-400 flex items-center gap-1">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          This date is in the past
        </p>
      )}

      {!value && (
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Optional - set a deadline for this task
        </p>
      )}
    </div>
  );
}
