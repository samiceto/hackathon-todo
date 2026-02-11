/**
 * PrioritySelector Component
 *
 * Interactive priority selector for tasks with visual color coding.
 * Provides a clear, intuitive interface for setting task priority levels.
 *
 * Features:
 * - 4 priority levels (low, medium, high, urgent)
 * - Color-coded badges for visual distinction
 * - Button grid layout for easy selection
 * - Active state highlighting
 * - Accessible keyboard navigation
 */

"use client";

interface PrioritySelectorProps {
  /** Current priority value */
  value: string;
  /** Callback when priority changes */
  onChange: (priority: string) => void;
  /** Optional label text */
  label?: string;
  /** Optional className for custom styling */
  className?: string;
}

/**
 * Priority level configuration with colors and descriptions.
 */
const PRIORITY_LEVELS = [
  {
    value: "low",
    label: "Low",
    description: "Not urgent, can wait",
    color: "text-gray-700",
    bgColor: "bg-gray-100",
    hoverBg: "hover:bg-gray-200",
    activeBg: "bg-gray-600",
    activeText: "text-white",
    borderColor: "border-gray-300",
    activeBorder: "border-gray-600",
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M19 9l-7 7-7-7"
        />
      </svg>
    ),
  },
  {
    value: "medium",
    label: "Medium",
    description: "Normal priority",
    color: "text-blue-700",
    bgColor: "bg-blue-100",
    hoverBg: "hover:bg-blue-200",
    activeBg: "bg-blue-600",
    activeText: "text-white",
    borderColor: "border-blue-300",
    activeBorder: "border-blue-600",
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M4 6h16M4 12h16M4 18h16"
        />
      </svg>
    ),
  },
  {
    value: "high",
    label: "High",
    description: "Important, prioritize",
    color: "text-orange-700",
    bgColor: "bg-orange-100",
    hoverBg: "hover:bg-orange-200",
    activeBg: "bg-orange-600",
    activeText: "text-white",
    borderColor: "border-orange-300",
    activeBorder: "border-orange-600",
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M5 15l7-7 7 7"
        />
      </svg>
    ),
  },
  {
    value: "urgent",
    label: "Urgent",
    description: "Critical, do immediately",
    color: "text-red-700",
    bgColor: "bg-red-100",
    hoverBg: "hover:bg-red-200",
    activeBg: "bg-red-600",
    activeText: "text-white",
    borderColor: "border-red-300",
    activeBorder: "border-red-600",
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
        />
      </svg>
    ),
  },
];

/**
 * PrioritySelector component for setting task priority.
 *
 * Usage:
 * ```tsx
 * const [priority, setPriority] = useState<string>("medium");
 *
 * <PrioritySelector
 *   value={priority}
 *   onChange={setPriority}
 *   label="Task Priority"
 * />
 * ```
 */
export default function PrioritySelector({
  value,
  onChange,
  label = "Priority",
  className = "",
}: PrioritySelectorProps) {
  const handleSelect = (priorityValue: string) => {
    onChange(priorityValue);
  };

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Label */}
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {label}
      </label>

      {/* Priority buttons grid */}
      <div className="grid grid-cols-2 gap-2">
        {PRIORITY_LEVELS.map((priority) => {
          const isActive = value === priority.value;

          return (
            <button
              key={priority.value}
              type="button"
              onClick={() => handleSelect(priority.value)}
              className={`
                flex items-center gap-2 px-3 py-2.5 rounded-lg border-2
                transition-all duration-200
                focus:outline-none focus:ring-4 focus:ring-offset-1
                ${
                  isActive
                    ? `${priority.activeBg} ${priority.activeText} ${priority.activeBorder} shadow-md focus:ring-${priority.value}-500/30`
                    : `${priority.bgColor} ${priority.color} ${priority.borderColor} ${priority.hoverBg} focus:ring-${priority.value}-500/20`
                }
              `}
              title={priority.description}
            >
              {/* Icon */}
              <div className="flex-shrink-0">{priority.icon}</div>

              {/* Label */}
              <span className="font-semibold text-sm">{priority.label}</span>

              {/* Active checkmark */}
              {isActive && (
                <svg
                  className="w-4 h-4 ml-auto"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
            </button>
          );
        })}
      </div>

      {/* Current selection preview */}
      <div className="text-xs text-gray-600 dark:text-gray-400">
        {PRIORITY_LEVELS.find((p) => p.value === value)?.description || "Select a priority level"}
      </div>
    </div>
  );
}
