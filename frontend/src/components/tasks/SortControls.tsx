"use client";

import { useState } from "react";
import {
  ArrowsUpDownIcon,
  ArrowUpIcon,
  ArrowDownIcon,
} from "@heroicons/react/24/outline";

export type SortField = "created_at" | "updated_at" | "due_date" | "priority" | "title";
export type SortOrder = "asc" | "desc";

export interface SortOptions {
  sortBy: SortField | null;
  sortOrder: SortOrder;
}

interface SortControlsProps {
  /**
   * Callback when sort options change
   */
  onSortChange: (options: SortOptions) => void;

  /**
   * Initial sort options
   */
  initialSort?: SortOptions;

  /**
   * Compact mode (icon button instead of full dropdown)
   */
  compact?: boolean;
}

/**
 * SortControls Component
 *
 * Provides controls for sorting task lists.
 * Supports sorting by multiple fields with ascending/descending order.
 *
 * Features:
 * - Sort by created_at, updated_at, due_date, priority, or title
 * - Toggle ascending/descending order
 * - Visual sort direction indicator
 * - Compact mode for mobile/small screens
 *
 * @example
 * ```tsx
 * <SortControls
 *   onSortChange={(options) => fetchTasks(options)}
 *   initialSort={{ sortBy: "created_at", sortOrder: "desc" }}
 * />
 * ```
 */
export default function SortControls({
  onSortChange,
  initialSort = { sortBy: null, sortOrder: "desc" },
  compact = false,
}: SortControlsProps) {
  const [sortBy, setSortBy] = useState<SortField | null>(initialSort.sortBy);
  const [sortOrder, setSortOrder] = useState<SortOrder>(initialSort.sortOrder);

  /**
   * Sort field options with human-readable labels
   */
  const sortFieldOptions: { value: SortField | ""; label: string }[] = [
    { value: "", label: "Default (newest first)" },
    { value: "created_at", label: "Date Created" },
    { value: "updated_at", label: "Last Updated" },
    { value: "due_date", label: "Due Date" },
    { value: "priority", label: "Priority" },
    { value: "title", label: "Title (A-Z)" },
  ];

  /**
   * Handle sort field change
   */
  const handleSortByChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value as SortField | "";
    const newSortBy = value === "" ? null : value;
    setSortBy(newSortBy);
    onSortChange({ sortBy: newSortBy, sortOrder });
  };

  /**
   * Toggle sort order (asc <-> desc)
   */
  const toggleSortOrder = () => {
    const newSortOrder = sortOrder === "asc" ? "desc" : "asc";
    setSortOrder(newSortOrder);
    onSortChange({ sortBy, sortOrder: newSortOrder });
  };

  /**
   * Get current sort field label
   */
  const getCurrentSortLabel = () => {
    if (!sortBy) return "Default";
    const option = sortFieldOptions.find((opt) => opt.value === sortBy);
    return option?.label || "Unknown";
  };

  /**
   * Compact mode rendering (just icon button with popover)
   */
  if (compact) {
    return (
      <div className="flex items-center gap-2">
        <select
          value={sortBy || ""}
          onChange={handleSortByChange}
          className="block rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-label="Sort by"
        >
          {sortFieldOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>

        {sortBy && (
          <button
            type="button"
            onClick={toggleSortOrder}
            className="rounded-md border border-gray-300 bg-white p-2 text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label={`Sort ${sortOrder === "asc" ? "ascending" : "descending"}`}
            title={`Click to sort ${sortOrder === "asc" ? "descending" : "ascending"}`}
          >
            {sortOrder === "asc" ? (
              <ArrowUpIcon className="h-5 w-5" />
            ) : (
              <ArrowDownIcon className="h-5 w-5" />
            )}
          </button>
        )}
      </div>
    );
  }

  /**
   * Full mode rendering
   */
  return (
    <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
      {/* Sort field selector */}
      <div className="flex items-center gap-2">
        <ArrowsUpDownIcon className="h-5 w-5 text-gray-500" aria-hidden="true" />
        <label htmlFor="sort-by" className="text-sm font-medium text-gray-700">
          Sort by:
        </label>
        <select
          id="sort-by"
          value={sortBy || ""}
          onChange={handleSortByChange}
          className="block rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {sortFieldOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      {/* Sort order toggle (only visible when a sort field is selected) */}
      {sortBy && (
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">Order:</span>
          <button
            type="button"
            onClick={toggleSortOrder}
            className="inline-flex items-center gap-1 rounded-md border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label={`Sort ${sortOrder === "asc" ? "ascending" : "descending"}`}
          >
            {sortOrder === "asc" ? (
              <>
                <ArrowUpIcon className="h-4 w-4" />
                Ascending
              </>
            ) : (
              <>
                <ArrowDownIcon className="h-4 w-4" />
                Descending
              </>
            )}
          </button>
        </div>
      )}

      {/* Active sort indicator */}
      {sortBy && (
        <div className="text-xs text-gray-500">
          Sorting by <span className="font-medium">{getCurrentSortLabel()}</span> (
          {sortOrder === "asc" ? "A→Z" : "Z→A"})
        </div>
      )}
    </div>
  );
}
