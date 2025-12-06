/**
 * ItemFlags - UI komponensek a tétel jelzők kezeléséhez
 *
 * Komponensek:
 * - UrgentToggle: Sürgős jelző kapcsoló
 * - SyncDropdown: Szinkronizálás beállító legördülő
 */

import { useState } from 'react';
import './ItemFlags.css';

// =====================================================
// URGENT TOGGLE - Sürgős tétel jelző
// =====================================================

interface UrgentToggleProps {
  isUrgent: boolean;
  onChange: (value: boolean) => void;
  disabled?: boolean;
}

export const UrgentToggle = ({ isUrgent, onChange, disabled = false }: UrgentToggleProps) => {
  return (
    <button
      className={`urgent-toggle ${isUrgent ? 'active' : ''}`}
      onClick={() => onChange(!isUrgent)}
      disabled={disabled}
      title={
        isUrgent
          ? 'Sürgős tétel – Kattints a jelző eltávolításához'
          : 'Sürgős tétel jelölése – A konyha/piackészítő látja, hogy ez elsőbbséget élvez'
      }
      type="button"
    >
      {isUrgent ? '⚡' : '⚪'}
    </button>
  );
};

// =====================================================
// SYNC DROPDOWN - Szinkronizálás beállító
// =====================================================

interface SyncDropdownProps {
  syncWith: string | undefined;
  onChange: (value: string | undefined) => void;
  disabled?: boolean;
}

export const SyncDropdown = ({ syncWith, onChange, disabled = false }: SyncDropdownProps) => {
  const [isOpen, setIsOpen] = useState(false);

  const options = [
    { value: undefined, label: 'Nincs szinkronizálás', icon: '⚪' },
    { value: 'starter', label: 'Előételhez igazítva', icon: '🥗' },
    { value: 'main', label: 'Főételhez igazítva', icon: '🍽️' },
    { value: 'dessert', label: 'Desszerthez igazítva', icon: '🍰' },
  ];

  const currentOption = options.find((opt) => opt.value === syncWith) || options[0];

  const handleSelect = (value: string | undefined) => {
    onChange(value);
    setIsOpen(false);
  };

  return (
    <div className="sync-dropdown">
      <button
        className={`sync-toggle ${syncWith ? 'active' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        disabled={disabled}
        title="Előbb kérjük – A tétel szinkronizálva lesz más fogásokkal"
        type="button"
      >
        <span className="sync-icon">{currentOption.icon}</span>
      </button>

      {isOpen && (
        <>
          <div className="sync-overlay" onClick={() => setIsOpen(false)} />
          <div className="sync-menu">
            {options.map((option) => (
              <button
                key={option.value || 'none'}
                className={`sync-option ${syncWith === option.value ? 'selected' : ''}`}
                onClick={() => handleSelect(option.value)}
                type="button"
              >
                <span className="option-icon">{option.icon}</span>
                <span className="option-label">{option.label}</span>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

// =====================================================
// ITEM FLAGS CONTAINER - Mindkét jelző együtt
// =====================================================

interface ItemFlagsProps {
  isUrgent: boolean;
  syncWith: string | undefined;
  onUrgentChange: (value: boolean) => void;
  onSyncChange: (value: string | undefined) => void;
  disabled?: boolean;
}

export const ItemFlags = ({
  isUrgent,
  syncWith,
  onUrgentChange,
  onSyncChange,
  disabled = false,
}: ItemFlagsProps) => {
  return (
    <div className="item-flags">
      <UrgentToggle isUrgent={isUrgent} onChange={onUrgentChange} disabled={disabled} />
      <SyncDropdown syncWith={syncWith} onChange={onSyncChange} disabled={disabled} />
    </div>
  );
};
