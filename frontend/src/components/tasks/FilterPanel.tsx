"use client";

import { useState, useEffect } from "react";
import { FunnelIcon, XMarkIcon } from "@heroicons/react/24/outline";

export interface FilterOptions {
  status?: "completed" | "incomplete" | null;
  priority?: "low" | "medium" | "high" | "urgent" | null;
  tags?: string[];
  dueDateStart?: string | null;
  dueDateEnd?: string | null;
}

interface FilterPanelProps {
  /**
   * Callback when filters change
   */
  onFilterChange: (filters: FilterOptions) => void;

  /**
   * Initial filter values
   */
  initialFilters?: FilterOptions;

  /**
   * Whether to show the panel (for mobile toggle)
   */
  isOpen?: boolean;
}

/**
 * FilterPanel Component
 *
 * Multi-criteria filtering panel for tasks.
 * Supports filtering by status, priority, tags, and due date ranges.
 *
 * Features:
 * - Status filter (completed/incomplete)
 * - Priority filter (low/medium/high/urgent)
 * - Tag filter (comma-separated tags)
 * - Due date range filter (start and end dates)
 * - Clear all filters button
 * - Active filter indicators
 *
 * @example
 * ```tsx
 * <FilterPanel
 *   onFilterChange={(filters) => fetchTasks(filters)}
 *   initialFilters={{ status: "incomplete", priority: "high" }}
 * />
 * ```
 */
export default function FilterPanel({
  onFilterChange,
  initialFilters = {},
  isOpen = true,
}: FilterPanelProps) {
  const [filters, setFilters] = useState<FilterOptions>(initialFilters);
  const [tagInput, setTagInput] = useState("");

  // Notify parent when filters change
  useEffect(() => {
    onFilterChange(filters);
  }, [filters, onFilterChange]);

  /**
   * Handle status filter change
   */
  const handleStatusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setFilters((prev) => ({
      ...prev,
      status: value === "" ? null : (value as "completed" | "incomplete"),
    }));
  };

  /**
   * Handle priority filter change
   */
  const handlePriorityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setFilters((prev) => ({
      ...prev,
      priority: value === "" ? null : (value as "low" | "medium" | "high" | "urgent"),
    }));
  };

  /**
   * Handle tag input change (comma-separated)
   */
  const handleTagInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setTagInput(value);

    // Parse comma-separated tags
    const tags = value
      .split(",")
      .map((tag) => tag.trim())
      .filter((tag) => tag.length > 0);

    setFilters((prev) => ({
      ...prev,
      tags: tags.length > 0 ? tags : undefined,
    }));
  };

  /**
   * Handle due date start change
   */
  const handleDueDateStartChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setFilters((prev) => ({
      ...prev,
      dueDateStart: value === "" ? null : value,
    }));
  };

  /**
   * Handle due date end change
   */
  const handleDueDateEndChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setFilters((prev) => ({
      ...prev,
      dueDateEnd: value === "" ? null : value,
    }));
  };

  /**
   * Clear all filters
   */
  const handleClearAll = () => {
    setFilters({});
    setTagInput("");
  };

  /**
   * Count active filters
   */
  const activeFilterCount = Object.values(filters).filter(
    (value) => value !== null && value !== undefined && (Array.isArray(value) ? value.length > 0 : true)
  ).length;

  if (!isOpen) {
    return null;
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FunnelIcon className="h-5 w-5 text-gray-600" />
          <h3 className="text-sm font-semibold text-gray-700">Filters</h3>
          {activeFilterCount > 0 && (
            <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800">
              {activeFilterCount} active
            </span>
          )}
        </div>

        {activeFilterCount > 0 && (
          <button
            type="button"
            onClick={handleClearAll}
            className="flex items-center gap-1 rounded px-2 py-1 text-xs font-medium text-gray-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Clear all filters"
          >
            <XMarkIcon className="h-4 w-4" />
            Clear all
          </button>
        )}
      </div>

      {/* Filter controls */}
      <div className="space-y-4">
        {/* Status filter */}
        <div>
          <label htmlFor="filter-status" className="block text-xs font-medium text-gray-700">
            Status
          </label>
          <select
            id="filter-status"
            value={filters.status || ""}
            onChange={handleStatusChange}
            className="mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All tasks</option>
            <option value="incomplete">Incomplete</option>
            <option value="completed">Completed</option>
          </select>
        </div>

        {/* Priority filter */}
        <div>
          <label htmlFor="filter-priority" className="block text-xs font-medium text-gray-700">
            Priority
          </label>
          <select
            id="filter-priority"
            value={filters.priority || ""}
            onChange={handlePriorityChange}
            className="mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All priorities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>

        {/* Tag filter */}
        <div>
          <label htmlFor="filter-tags" className="block text-xs font-medium text-gray-700">
            Tags
          </label>
          <input
            id="filter-tags"
            type="text"
            value={tagInput}
            onChange={handleTagInputChange}
            placeholder="Enter tags separated by commas"
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm placeholder:text-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p className="mt-1 text-xs text-gray-500">
            Tasks must have ALL specified tags
          </p>
        </div>

        {/* Due date range filter */}
        <div>
          <label className="block text-xs font-medium text-gray-700">
            Due Date Range
          </label>
          <div className="mt-1 grid grid-cols-2 gap-2">
            <div>
              <label htmlFor="filter-due-start" className="sr-only">
                Start date
              </label>
              <input
                id="filter-due-start"
                type="datetime-local"
                value={filters.dueDateStart || ""}
                onChange={handleDueDateStartChange}
                className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label htmlFor="filter-due-end" className="sr-only">
                End date
              </label>
              <input
                id="filter-due-end"
                type="datetime-local"
                value={filters.dueDateEnd || ""}
                onChange={handleDueDateEndChange}
                className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <p className="mt-1 text-xs text-gray-500">
            From → To
          </p>
        </div>
      </div>
    </div>
  );
}
