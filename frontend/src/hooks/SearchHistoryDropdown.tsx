import React from 'react';
import './SearchHistoryDropdown.css';

export function SearchHistoryDropdown({ history, onSelect, onRemove, onClear, isOpen }) {
  if (!isOpen || history.length === 0) return null;

  return (
    <div className="search-history-dropdown">
      <div className="dropdown-header">
        <span>Recent Searches</span>
        <button onClick={onClear}>Clear All</button>
      </div>
      <ul>
        {history.map((query, i) => (
          <li key={i}>
            <button onClick={() => onSelect(query)}>🔍 {query}</button>
            <button onClick={() => onRemove(query)}>✕</button>
          </li>
        ))}
      </ul>
    </div>
  );
}