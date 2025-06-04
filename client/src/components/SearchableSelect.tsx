import React, { useState, useEffect, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../api/axios';
import styles from './SearchableSelect.module.css';

interface MoyskladEntity {
  id: string;
  name: string;
  meta: {
    href: string;
    type: string;
  };
  type: string;
}

interface SearchableSelectProps {
  label: string;
  value: string | null;
  onChange: (value: string | null) => void;
  searchQuery: string;
  onSearchChange: (value: string) => void;
  options: MoyskladEntity[];
  placeholder: string;
  isRemoteSearch?: boolean;
  searchEndpoint?: string;
  minSearchLength?: number;
}

const SearchableSelect: React.FC<SearchableSelectProps> = ({
  label,
  value,
  onChange,
  searchQuery,
  onSearchChange,
  options,
  placeholder,
  isRemoteSearch = false,
  searchEndpoint,
  minSearchLength = 2,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchData, setSearchData] = useState<MoyskladEntity[]>([]);
  const [initialData, setInitialData] = useState<MoyskladEntity[]>([]);

  // Fetch data for remote search
  const { data: remoteData } = useQuery({
    queryKey: ['remoteSearch', searchEndpoint, searchQuery],
    queryFn: async () => {
      if (!searchEndpoint || searchQuery.length < minSearchLength) return [];
      const response = await api.get(`${searchEndpoint}?search=${searchQuery}`);
      return response.data;
    },
    enabled: isRemoteSearch && !!searchEndpoint && searchQuery.length >= minSearchLength,
  });

  // Update search data when remote data changes
  useEffect(() => {
    if (isRemoteSearch && remoteData) {
      setSearchData(remoteData);
    }
  }, [isRemoteSearch, remoteData]);

  // Update initial data when options change (for non-remote search)
  useEffect(() => {
    if (!isRemoteSearch) {
      setInitialData(options);
    }
  }, [isRemoteSearch, options]);

  // Handle search input change
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onSearchChange(e.target.value);
    if (e.target.value.length >= minSearchLength) {
      setIsOpen(true);
    }
  };

  // Handle option selection
  const handleSelect = (option: MoyskladEntity) => {
    onChange(option.id);
    onSearchChange(option.name);
    setIsOpen(false);
  };

  // Get display text for selected value
  const displayText = useMemo(() => {
    if (!value) return placeholder;
    
    // For remote search, check both searchData and initialData
    if (isRemoteSearch) {
      const selectedEntity = searchData.find(opt => opt.id === value) || 
                           initialData.find(opt => opt.id === value);
      return selectedEntity ? selectedEntity.name : placeholder;
    }
    
    // For local search, check options
    const selectedEntity = options.find(opt => opt.id === value);
    return selectedEntity ? selectedEntity.name : placeholder;
  }, [value, options, searchData, initialData, isRemoteSearch, placeholder]);

  // Get current options to display
  const currentOptions = useMemo(() => {
    if (isRemoteSearch) {
      return searchData;
    }
    return options;
  }, [isRemoteSearch, searchData, options]);

  return (
    <div className={styles.container}>
      <label className={styles.label}>{label}</label>
      <div className={styles.selectContainer}>
        <div className={styles.searchContainer}>
          <input
            type="text"
            value={isOpen ? searchQuery : displayText}
            onChange={handleSearchChange}
            onFocus={() => setIsOpen(true)}
            placeholder={placeholder}
            className={styles.searchInput}
          />
          {value && (
            <button
              className={styles.clearButton}
              onClick={() => {
                onChange(null);
                onSearchChange('');
              }}
            >
              ×
            </button>
          )}
        </div>
        {isOpen && (
          <div className={styles.optionsContainer}>
            {currentOptions.length > 0 ? (
              currentOptions.map((option) => (
                <div
                  key={option.id}
                  className={`${styles.option} ${value === option.id ? styles.selected : ''}`}
                  onClick={() => handleSelect(option)}
                >
                  {option.name}
                </div>
              ))
            ) : (
              <div className={styles.noOptions}>No options found</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchableSelect; 