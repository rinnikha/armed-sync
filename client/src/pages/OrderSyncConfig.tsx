import React, { useState, useCallback, useMemo, useRef, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../api/axios';
import styles from './OrderSyncConfig.module.css';
import {
  Search as SearchIcon,
  Add as AddIcon,
  Close as CloseIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
} from '@mui/icons-material';

interface MoyskladEntity {
  id: string;
  name: string;
  meta: {
    href: string;
    type: string;
  };
  type: string;
}

interface OrderSyncConfig {
  id: string;
  name: string;
  is_active: boolean;
  description: string;
  ms1_cp_id: string;
  ms2_organization_id: string;
  ms2_store_id: string;
  ms2_group_id: string;
  start_sync_datetime: string;
}

// Internal form state uses IDs and stores selected entities
interface NewConfigForm {
  name: string;
  description: string;
  is_active: boolean;
  ms1_cp_id: string | null;
  ms2_organization_id: string | null;
  ms2_store_id: string | null;
  ms2_group_id: string | null;
  start_sync_datetime: string;
}

interface SearchableSelectProps {
  label: string;
  value: string | null;
  onChange: (id: string | null) => void;
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
  const selectRef = useRef<HTMLDivElement>(null);

  // Initial data load for remote search
  const { data: initialData = [] } = useQuery({
    queryKey: ['initial', searchEndpoint],
    queryFn: async () => {
      if (!searchEndpoint) return [];
      const response = await api.get(`${searchEndpoint}?limit=20`);
      return response.data;
    },
    enabled: isRemoteSearch,
  });

  // Search data when query is entered
  const { data: searchData = [], isLoading } = useQuery({
    queryKey: ['search', searchEndpoint, searchQuery],
    queryFn: async () => {
      if (!searchEndpoint || searchQuery.length < minSearchLength) return [];
      const response = await api.get(`${searchEndpoint}?search=${searchQuery}`);
      return response.data;
    },
    enabled: isRemoteSearch && searchQuery.length >= minSearchLength,
  });

  // Add event listeners for clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    onSearchChange(e.target.value);
  }, [onSearchChange]);

  const handleClear = useCallback((e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    onChange(null);
    onSearchChange('');
  }, [onChange, onSearchChange]);

  const handleOptionSelect = useCallback((option: MoyskladEntity) => {
    onChange(option.id);
    onSearchChange(option.name); // Set the search query to the selected option's name
    setIsOpen(false);
  }, [onChange, onSearchChange]);

  const toggleDropdown = useCallback(() => {
    setIsOpen(prev => !prev);
  }, []);

  // Get filtered options based on search query
  const filteredOptions = useMemo(() => {
    if (isRemoteSearch) {
      // For remote search, use the data from API
      return searchQuery.length >= minSearchLength ? searchData : initialData;
    }
    // For local search, filter the options
    return options.filter(opt => 
      opt.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [isRemoteSearch, searchData, initialData, options, searchQuery, minSearchLength]);

  // Get display text for selected value
  const displayText = useMemo(() => {
    if (!value) return placeholder;
    
    // For remote search, check both searchData and initialData
    if (isRemoteSearch) {
      const selectedEntity = searchData.find((opt: MoyskladEntity) => opt.id === value) || 
                           initialData.find((opt: MoyskladEntity) => opt.id === value);
      return selectedEntity ? selectedEntity.name : searchQuery || placeholder;
    }
    
    // For local search, check options
    const selectedEntity = options.find(opt => opt.id === value);
    return selectedEntity ? selectedEntity.name : placeholder;
  }, [value, options, searchData, initialData, isRemoteSearch, placeholder, searchQuery]);

  return (
    <div className={styles.formGroup}>
      <label>{label}</label>
      <div 
        className={styles.searchableSelect}
        ref={selectRef}
      >
        <div
          className={styles.selectInput}
          onClick={toggleDropdown}
        >
          <span>{displayText}</span>
          {value && (
            <button
              className={styles.clearSelectionButton}
              onClick={handleClear}
              title="Clear selection"
              type="button"
            >
              <CloseIcon fontSize="small" />
            </button>
          )}
        </div>
        {isOpen && (
          <div className={styles.selectDropdown}>
            <div className={styles.searchInputWrapper}>
              <input
                type="text"
                value={searchQuery}
                onChange={handleSearchChange}
                placeholder={`Search... ${isRemoteSearch ? `(min ${minSearchLength} chars)` : ''}`}
                className={styles.searchInput}
                onClick={(e) => e.stopPropagation()}
                autoComplete="off"
                autoFocus
              />
              <SearchIcon className={styles.searchIcon} />
            </div>
            <div className={styles.optionsList}>
              {isLoading ? (
                <div className={styles.loading}>Loading...</div>
              ) : filteredOptions.length > 0 ? (
                filteredOptions.map((option: MoyskladEntity) => (
                  <div
                    key={option.id}
                    className={`${styles.option} ${value === option.id ? styles.selected : ''}`}
                    onClick={() => handleOptionSelect(option)}
                  >
                    {option.name}
                  </div>
                ))
              ) : (
                <div className={styles.noResults}>
                  {searchQuery.length < minSearchLength && isRemoteSearch
                    ? `Type at least ${minSearchLength} characters to search`
                    : 'No results found'}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const OrderSyncConfigPage: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchQueries, setSearchQueries] = useState({
    ms1_cp: '',
    ms2_organization: '',
    ms2_store: '',
    ms2_group: '',
  });

  const [newConfig, setNewConfig] = useState<NewConfigForm>({
    name: '',
    description: '',
    is_active: true,
    ms1_cp_id: null,
    ms2_organization_id: null,
    ms2_store_id: null,
    ms2_group_id: null,
    start_sync_datetime: new Date().toISOString().slice(0, 16),
  });

  const queryClient = useQueryClient();

  const { data: configs = [] } = useQuery<OrderSyncConfig[]>({
    queryKey: ['orderSyncConfigs'],
    queryFn: async () => {
      const response = await api.get('/order-sync-configs');
      return response.data;
    },
  });

  const { data: ms2_organizations = [] } = useQuery<MoyskladEntity[]>({
    queryKey: ['ms2_organizations'],
    queryFn: async () => {
      const response = await api.get('/moysklad/ms2/organizations');
      return response.data;
    },
  });

  const { data: ms2_stores = [] } = useQuery<MoyskladEntity[]>({
    queryKey: ['ms2_stores'],
    queryFn: async () => {
      const response = await api.get('/moysklad/ms2/stores');
      return response.data;
    },
  });

  const { data: ms2_groups = [] } = useQuery<MoyskladEntity[]>({
    queryKey: ['ms2_groups'],
    queryFn: async () => {
      const response = await api.get('/moysklad/ms2/groups');
      return response.data;
    },
  });

  const handleSearchChange = useCallback((field: keyof typeof searchQueries, value: string) => {
    console.log(`Updating search query for ${field}:`, value);
    setSearchQueries(prev => ({ ...prev, [field]: value }));
  }, []);

  const createConfigMutation = useMutation({
    mutationFn: async (config: NewConfigForm) => {
      const apiConfig = {
        name: config.name,
        description: config.description,
        is_active: config.is_active,
        ms1_cp_id: config.ms1_cp_id,
        ms2_organization_id: config.ms2_organization_id,
        ms2_store_id: config.ms2_store_id,
        ms2_group_id: config.ms2_group_id,
        start_sync_datetime: config.start_sync_datetime,
      };
      const response = await api.post('/order-sync-configs', apiConfig);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orderSyncConfigs'] });
      setIsModalOpen(false);
      setNewConfig({
        name: '',
        description: '',
        is_active: true,
        ms1_cp_id: null,
        ms2_organization_id: null,
        ms2_store_id: null,
        ms2_group_id: null,
        start_sync_datetime: new Date().toISOString().slice(0, 16),
      });
      setSearchQueries({
        ms1_cp: '',
        ms2_organization: '',
        ms2_store: '',
        ms2_group: '',
      });
    },
  });

  const deleteConfigMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/order-sync-configs/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orderSyncConfigs'] });
    },
  });

  const handleSaveConfig = () => {
    console.log("Form state before save:", JSON.stringify(newConfig, null, 2));
    createConfigMutation.mutate(newConfig);
  };

  const handleDeleteConfig = (id: string) => {
    if (window.confirm('Are you sure you want to delete this configuration?')) {
      deleteConfigMutation.mutate(id);
    }
  };

  const handleEditConfig = (config: OrderSyncConfig) => {
    setNewConfig({
      name: config.name,
      description: config.description,
      is_active: config.is_active,
      ms1_cp_id: config.ms1_cp_id,
      ms2_organization_id: config.ms2_organization_id,
      ms2_store_id: config.ms2_store_id,
      ms2_group_id: config.ms2_group_id,
      start_sync_datetime: config.start_sync_datetime,
    });
    setIsModalOpen(true);
  };

  function getLabelByHref(href: string | { href: string; type: string }, entities: MoyskladEntity[] = []): string {
    if (!href) return 'N/A';
    
    // Handle the case where href is an object
    const hrefString = typeof href === 'string' ? href : href.href;
    
    const entity = entities.find(e => e.meta.href === hrefString);
    if (entity) return entity.name;
    
    // If the href is actually an entity name (backward compatibility)
    if (hrefString.length > 0 && !hrefString.includes('http')) {
      return hrefString;
    }
    
    // Just show a shortened version of the href
    return hrefString.split('/').pop() || hrefString;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Order Sync Configuration</h1>
        <button
          className={styles.newConfigButton}
          onClick={() => setIsModalOpen(true)}
        >
          <AddIcon /> New Configuration
        </button>
      </div>

      {isModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <div className={styles.modalHeader}>
              <h2>New Configuration</h2>
              <button
                className={styles.closeButton}
                onClick={() => setIsModalOpen(false)}
              >
                <CloseIcon />
              </button>
            </div>
            <div className={styles.modalContent}>
              <div className={styles.formGroup}>
                <label>Configuration Name</label>
                <input
                  type="text"
                  value={newConfig.name}
                  onChange={(e) => setNewConfig({ ...newConfig, name: e.target.value })}
                  className={styles.input}
                  placeholder="Enter configuration name"
                />
              </div>

              <div className={styles.formGroup}>
                <label>Description</label>
                <textarea
                  value={newConfig.description}
                  onChange={(e) => setNewConfig({ ...newConfig, description: e.target.value })}
                  className={styles.input}
                  placeholder="Enter configuration description"
                  rows={3}
                />
              </div>

              <div className={styles.formGroup}>
                <label className={styles.checkboxLabel}>
                  <input
                    type="checkbox"
                    checked={newConfig.is_active}
                    onChange={(e) => setNewConfig({ ...newConfig, is_active: e.target.checked })}
                    className={styles.checkbox}
                  />
                  Active
                </label>
              </div>

              <SearchableSelect
                label="MS1 Counterparty"
                value={newConfig.ms1_cp_id}
                onChange={(id: string | null) => setNewConfig(prev => ({ ...prev, ms1_cp_id: id }))}
                searchQuery={searchQueries.ms1_cp}
                onSearchChange={value => handleSearchChange('ms1_cp', value)}
                options={[]}
                placeholder="Select MS1 Counterparty"
                isRemoteSearch={true}
                searchEndpoint="/moysklad/ms1/counterparties"
                minSearchLength={2}
              />

              <SearchableSelect
                label="MS2 Organization"
                value={newConfig.ms2_organization_id}
                onChange={(id: string | null) => setNewConfig(prev => ({ ...prev, ms2_organization_id: id }))}
                searchQuery={searchQueries.ms2_organization}
                onSearchChange={value => handleSearchChange('ms2_organization', value)}
                options={ms2_organizations}
                placeholder="Select MS2 Organization"
                isRemoteSearch={false}
              />

              <SearchableSelect
                label="MS2 Store"
                value={newConfig.ms2_store_id}
                onChange={(id: string | null) => setNewConfig(prev => ({ ...prev, ms2_store_id: id }))}
                searchQuery={searchQueries.ms2_store}
                onSearchChange={value => handleSearchChange('ms2_store', value)}
                options={ms2_stores}
                placeholder="Select MS2 Store"
                isRemoteSearch={false}
              />

              <SearchableSelect
                label="MS2 Group"
                value={newConfig.ms2_group_id}
                onChange={(id: string | null) => setNewConfig(prev => ({ ...prev, ms2_group_id: id }))}
                searchQuery={searchQueries.ms2_group}
                onSearchChange={value => handleSearchChange('ms2_group', value)}
                options={ms2_groups}
                placeholder="Select MS2 Group"
                isRemoteSearch={false}
              />

              <div className={styles.formGroup}>
                <label>Start Sync DateTime</label>
                <input
                  type="datetime-local"
                  value={newConfig.start_sync_datetime}
                  onChange={(e) => setNewConfig({ ...newConfig, start_sync_datetime: e.target.value })}
                  className={styles.input}
                />
              </div>
            </div>
            <div className={styles.modalFooter}>
              <button
                className={styles.cancelButton}
                onClick={() => setIsModalOpen(false)}
              >
                Cancel
              </button>
              <button
                className={styles.saveButton}
                onClick={handleSaveConfig}
                disabled={
                  !newConfig.name ||
                  !newConfig.ms1_cp_id ||
                  !newConfig.ms2_organization_id ||
                  !newConfig.ms2_store_id ||
                  !newConfig.ms2_group_id ||
                  !newConfig.start_sync_datetime
                }
              >
                Save Configuration
              </button>
            </div>
          </div>
        </div>
      )}

      <div className={styles.configsList}>
        {configs.map((config) => (
          <div key={config.id} className={styles.configCard}>
            <div className={styles.configHeader}>
              <div className={styles.configTitle}>
                <h3>{config.name}</h3>
                <span className={`${styles.statusBadge} ${config.is_active ? styles.active : styles.inactive}`}>
                  {config.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <div className={styles.configActions}>
                <button
                  className={`${styles.actionButton} ${styles.editButton}`}
                  onClick={() => handleEditConfig(config)}
                  title="Edit configuration"
                >
                  <EditIcon fontSize="small" />
                </button>
                <button
                  className={`${styles.actionButton} ${styles.deleteButton}`}
                  onClick={() => handleDeleteConfig(config.id)}
                  title="Delete configuration"
                >
                  <DeleteIcon fontSize="small" />
                </button>
              </div>
            </div>
            <div className={styles.configDetails}>
              <div className={styles.detailRow}>
                <span className={styles.detailLabel}>MS1 CP:</span>
                <span className={styles.detailValue}>{getLabelByHref(config.ms1_cp_id, ms2_organizations)}</span>
              </div>
              <div className={styles.detailRow}>
                <span className={styles.detailLabel}>MS2 Organization:</span>
                <span className={styles.detailValue}>{getLabelByHref(config.ms2_organization_id, ms2_organizations)}</span>
              </div>
              <div className={styles.detailRow}>
                <span className={styles.detailLabel}>MS2 Store:</span>
                <span className={styles.detailValue}>{getLabelByHref(config.ms2_store_id, ms2_stores)}</span>
              </div>
              <div className={styles.detailRow}>
                <span className={styles.detailLabel}>MS2 Group:</span>
                <span className={styles.detailValue}>{getLabelByHref(config.ms2_group_id, ms2_groups)}</span>
              </div>
              <div className={styles.detailRow}>
                <span className={styles.detailLabel}>Start Sync:</span>
                <span className={styles.detailValue}>{new Date(config.start_sync_datetime).toLocaleString()}</span>
              </div>
              {config.description && (
                <div className={styles.detailRow}>
                  <span className={styles.detailLabel}>Description:</span>
                  <span className={styles.detailValue}>{config.description}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default OrderSyncConfigPage; 