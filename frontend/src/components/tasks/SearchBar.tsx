"use client";

import { useState, useEffect, useCallback } from "react";
import { MagnifyingGlassIcon, XMarkIcon } from "@heroicons/react/24/outline";

interface SearchBarProps {
  /**
   * Callback when search query changes (debounced)
   * @param query - The search query string
   */
  onSearch: (query: string) => void;

  /**
   * Debounce delay in milliseconds (default: 300ms)
   */
  debounceDelay?: number;

  /**
   * Placeholder text for the search input
   */
  placeholder?: string;

  /**
   * Initial search query value
   */
  initialValue?: string;
}

/**
 * SearchBar Component
 *
 * Provides a debounced search input for task search.
 * Automatically debounces input to reduce API calls.
 *
 * Features:
 * - Debounced search (default: 300ms delay)
 * - Clear button when text is present
 * - Search icon indicator
 * - Responsive design
 *
 * @example
 * ```tsx
 * <SearchBar
 *   onSearch={(query) => fetchTasks({ search: query })}
 *   placeholder="Search tasks..."
 *   debounceDelay={500}
 * />
 * ```
 */
export default function SearchBar({
  onSearch,
  debounceDelay = 300,
  placeholder = "Search tasks by title or description...",
  initialValue = "",
}: SearchBarProps) {
  const [searchTerm, setSearchTerm] = useState(initialValue);
  const [isSearching, setIsSearching] = useState(false);

  // Debounced search handler
  useEffect(() => {
    // Don't search if the search term is empty or just whitespace
    if (!searchTerm.trim()) {
      onSearch("");
      setIsSearching(false);
      return;
    }

    setIsSearching(true);

    // Debounce the search
    const timerId = setTimeout(() => {
      onSearch(searchTerm.trim());
      setIsSearching(false);
    }, debounceDelay);

    // Cleanup: cancel the previous timeout when searchTerm changes
    return () => {
      clearTimeout(timerId);
      setIsSearching(false);
    };
  }, [searchTerm, debounceDelay, onSearch]);

  /**
   * Handle input change
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  /**
   * Handle clear button click
   */
  const handleClear = useCallback(() => {
    setSearchTerm("");
    onSearch("");
    setIsSearching(false);
  }, [onSearch]);

  /**
   * Handle Enter key press (trigger immediate search without waiting for debounce)
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      const value = searchTerm.trim();
      if (value) {
        onSearch(value);
        setIsSearching(false);
      }
    }
  };

  return (
    <div className="relative w-full">
      {/* Search icon */}
      <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
        <MagnifyingGlassIcon
          className={`h-5 w-5 transition-colors ${
            isSearching ? "text-blue-500" : "text-gray-400"
          }`}
          aria-hidden="true"
        />
      </div>

      {/* Search input */}
      <input
        type="text"
        className={`
          block w-full rounded-lg border border-gray-300
          bg-white py-2 pl-10 pr-10 text-sm
          placeholder:text-gray-400
          focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-0
          disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500
          transition-all duration-200
          ${isSearching ? "ring-2 ring-blue-200" : ""}
        `}
        placeholder={placeholder}
        value={searchTerm}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        aria-label="Search tasks"
      />

      {/* Clear button (only visible when there's text) */}
      {searchTerm && (
        <div className="absolute inset-y-0 right-0 flex items-center pr-3">
          <button
            type="button"
            onClick={handleClear}
            className="rounded-full p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Clear search"
          >
            <XMarkIcon className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>
      )}

      {/* Loading indicator (optional, shows when debouncing) */}
      {isSearching && (
        <div className="absolute inset-y-0 right-10 flex items-center pr-3">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-blue-500"></div>
        </div>
      )}
    </div>
  );
}
