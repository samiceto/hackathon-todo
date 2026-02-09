/**
 * TagInput Component
 *
 * Interactive tag input with autocomplete and visual tag management.
 * Allows users to add, remove, and view tags for tasks.
 *
 * Features:
 * - Add tags via input or autocomplete suggestions
 * - Display tags as removable badges
 * - Maximum 10 tags per task enforcement
 * - Duplicate prevention (case-insensitive)
 * - Enter or comma to add tags
 * - Autocomplete from user's existing tags
 * - Visual feedback for tag limit
 */

"use client";

import React, { useState, useRef, useEffect } from "react";

interface TagInputProps {
  /** Current list of tags */
  value: string[];
  /** Callback when tags change */
  onChange: (tags: string[]) => void;
  /** Optional autocomplete suggestions */
  suggestions?: string[];
  /** Maximum tags allowed (default: 10) */
  maxTags?: number;
  /** Optional label text */
  label?: string;
  /** Optional placeholder */
  placeholder?: string;
  /** Optional error message */
  error?: string;
  /** Optional className for custom styling */
  className?: string;
}

/**
 * TagInput component for managing task tags.
 *
 * Usage:
 * ```tsx
 * const [tags, setTags] = useState<string[]>([]);
 * const [userTags, setUserTags] = useState<string[]>(["work", "urgent", "meeting"]);
 *
 * <TagInput
 *   value={tags}
 *   onChange={setTags}
 *   suggestions={userTags}
 *   maxTags={10}
 * />
 * ```
 */
export default function TagInput({
  value,
  onChange,
  suggestions = [],
  maxTags = 10,
  label = "Tags",
  placeholder = "Add tags...",
  error,
  className = "",
}: TagInputProps) {
  const [inputValue, setInputValue] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Filter suggestions based on input and exclude already selected tags
  const filteredSuggestions = suggestions.filter(
    (suggestion) =>
      suggestion.toLowerCase().includes(inputValue.toLowerCase()) &&
      !value.some((tag) => tag.toLowerCase() === suggestion.toLowerCase())
  );

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    setShowSuggestions(newValue.length > 0 && filteredSuggestions.length > 0);
  };

  const addTag = (tag: string) => {
    const trimmedTag = tag.trim().toLowerCase();

    // Validate tag
    if (!trimmedTag) return;
    if (trimmedTag.length > 50) return; // Max tag length

    // Check if tag already exists (case-insensitive)
    if (value.some((t) => t.toLowerCase() === trimmedTag)) {
      setInputValue("");
      setShowSuggestions(false);
      return;
    }

    // Check max tags limit
    if (value.length >= maxTags) {
      setInputValue("");
      setShowSuggestions(false);
      return;
    }

    // Add tag
    onChange([...value, trimmedTag]);
    setInputValue("");
    setShowSuggestions(false);
    inputRef.current?.focus();
  };

  const removeTag = (tagToRemove: string) => {
    onChange(value.filter((tag) => tag !== tagToRemove));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addTag(inputValue);
    } else if (e.key === "Backspace" && !inputValue && value.length > 0) {
      // Remove last tag on backspace if input is empty
      removeTag(value[value.length - 1]);
    } else if (e.key === "Escape") {
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    addTag(suggestion);
  };

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (inputRef.current && !inputRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const isMaxTagsReached = value.length >= maxTags;

  return (
    <div className={`space-y-2 ${className}`}>
      {/* Label */}
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {label}
        <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">
          ({value.length}/{maxTags})
        </span>
      </label>

      {/* Tags display + input */}
      <div className="relative">
        <div
          className={`
            min-h-[42px] px-3 py-2 border rounded-md
            bg-white dark:bg-gray-800
            border-gray-300 dark:border-gray-600
            focus-within:ring-2
            ${
              error
                ? "border-red-500 focus-within:ring-red-500"
                : "focus-within:ring-blue-500"
            }
            ${isMaxTagsReached ? "opacity-75" : ""}
            transition-colors
          `}
        >
          <div className="flex flex-wrap gap-2">
            {/* Tag badges */}
            {value.map((tag) => (
              <span
                key={tag}
                className="
                  inline-flex items-center gap-1 px-2 py-1
                  bg-blue-100 dark:bg-blue-900/30
                  text-blue-700 dark:text-blue-300
                  text-sm font-medium rounded-md
                  border border-blue-300 dark:border-blue-700
                "
              >
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
                  />
                </svg>
                {tag}
                <button
                  type="button"
                  onClick={() => removeTag(tag)}
                  className="
                    ml-1 text-blue-600 dark:text-blue-400
                    hover:text-blue-800 dark:hover:text-blue-200
                    transition-colors
                  "
                  aria-label={`Remove ${tag} tag`}
                >
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </span>
            ))}

            {/* Input */}
            {!isMaxTagsReached && (
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                placeholder={value.length === 0 ? placeholder : ""}
                className="
                  flex-1 min-w-[120px] px-1 py-0.5
                  bg-transparent
                  text-gray-900 dark:text-gray-100
                  placeholder-gray-400 dark:placeholder-gray-500
                  outline-none
                "
              />
            )}
          </div>
        </div>

        {/* Autocomplete suggestions */}
        {showSuggestions && filteredSuggestions.length > 0 && (
          <div className="
            absolute z-10 w-full mt-1
            bg-white dark:bg-gray-800
            border border-gray-300 dark:border-gray-600
            rounded-md shadow-lg
            max-h-48 overflow-y-auto
          ">
            {filteredSuggestions.map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() => handleSuggestionClick(suggestion)}
                className="
                  w-full px-3 py-2 text-left
                  text-sm text-gray-900 dark:text-gray-100
                  hover:bg-blue-50 dark:hover:bg-blue-900/30
                  transition-colors
                  flex items-center gap-2
                "
              >
                <svg className="w-3.5 h-3.5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
                  />
                </svg>
                {suggestion}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Error message */}
      {error && (
        <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
      )}

      {/* Helper text */}
      {isMaxTagsReached ? (
        <p className="text-sm text-orange-600 dark:text-orange-400 flex items-center gap-1">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          Maximum {maxTags} tags reached
        </p>
      ) : (
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Type and press Enter or comma to add tags. Click × to remove.
        </p>
      )}
    </div>
  );
}
