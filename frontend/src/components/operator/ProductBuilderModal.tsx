/**
 * ProductBuilderModal - Professional POS Product Builder
 *
 * Features:
 * - Modifier group selection (single/multiple choice)
 * - Course selection (Előétel, Főétel, Desszert)
 * - Notes field for special instructions
 * - Validation for required modifiers
 * - Real-time price calculation
 *
 * Backend API: GET /api/modifier-groups/products/{product_id}/modifier-groups
 */

import { useState, useEffect } from 'react';
import type { Product } from '@/types/menu';
import type {
  ModifierGroupWithModifiers,
  Modifier,
  SelectionType,
  SelectedModifier
} from '@/types/modifier';
import { getModifierGroupsByProduct } from '@/services/menuService';
import './ProductBuilderModal.css';

interface ProductBuilderModalProps {
  product: Product;
  isOpen: boolean;
  onClose: () => void;
  onAddToCart: (item: CartItem) => void;
}

export interface CartItem {
  product: Product;
  quantity: number;
  selected_modifiers: SelectedModifier[];
  course?: string;
  notes?: string;
  unit_price: number; // Base price + modifiers
}

const COURSE_OPTIONS = [
  { value: '', label: '-- Válassz fogást --' },
  { value: 'Előétel', label: 'Előétel' },
  { value: 'Levesek', label: 'Levesek' },
  { value: 'Főétel', label: 'Főétel' },
  { value: 'Desszert', label: 'Desszert' },
  { value: 'Italok', label: 'Italok' },
];

export const ProductBuilderModal = ({
  product,
  isOpen,
  onClose,
  onAddToCart,
}: ProductBuilderModalProps) => {
  const [modifierGroups, setModifierGroups] = useState<ModifierGroupWithModifiers[]>([]);
  const [selectedModifiers, setSelectedModifiers] = useState<Map<number, Set<number>>>(new Map());
  const [course, setCourse] = useState<string>('');
  const [notes, setNotes] = useState<string>('');
  const [quantity, setQuantity] = useState<number>(1);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  // Load modifier groups when modal opens
  useEffect(() => {
    if (isOpen && product.id) {
      loadModifierGroups();
    }
  }, [isOpen, product.id]);

  const loadModifierGroups = async () => {
    try {
      setIsLoading(true);
      const groups = await getModifierGroupsByProduct(product.id, true);
      setModifierGroups(groups);

      // Initialize with default selections
      const defaultSelections = new Map<number, Set<number>>();
      groups.forEach(group => {
        const defaultModifiers = group.modifiers.filter(m => m.is_default);
        if (defaultModifiers.length > 0) {
          defaultSelections.set(
            group.id,
            new Set(defaultModifiers.map(m => m.id))
          );
        }
      });
      setSelectedModifiers(defaultSelections);
    } catch (error) {
      console.error('Error loading modifier groups:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle modifier selection
  const handleModifierToggle = (groupId: number, modifierId: number, selectionType: SelectionType) => {
    const newSelections = new Map(selectedModifiers);
    const groupSelections = newSelections.get(groupId) || new Set<number>();

    if (selectionType.includes('SINGLE_CHOICE')) {
      // Single choice: replace selection
      newSelections.set(groupId, new Set([modifierId]));
    } else {
      // Multiple choice: toggle selection
      if (groupSelections.has(modifierId)) {
        groupSelections.delete(modifierId);
      } else {
        groupSelections.add(modifierId);
      }
      newSelections.set(groupId, groupSelections);
    }

    setSelectedModifiers(newSelections);
    setValidationErrors([]); // Clear errors when user makes changes
  };

  // Validate selections
  const validateSelections = (): boolean => {
    const errors: string[] = [];

    modifierGroups.forEach(group => {
      const selections = selectedModifiers.get(group.id) || new Set();
      const count = selections.size;

      // Check minimum selection
      if (group.min_selection > 0 && count < group.min_selection) {
        errors.push(
          `"${group.name}": Legalább ${group.min_selection} elemet kell választani!`
        );
      }

      // Check maximum selection
      if (count > group.max_selection) {
        errors.push(
          `"${group.name}": Maximum ${group.max_selection} elemet választhatsz!`
        );
      }

      // Check required selection
      if (group.selection_type.includes('REQUIRED') && count === 0) {
        errors.push(`"${group.name}": Kötelező választani!`);
      }
    });

    setValidationErrors(errors);
    return errors.length === 0;
  };

  // Calculate total price
  const calculateTotalPrice = (): number => {
    let total = product.base_price;

    modifierGroups.forEach(group => {
      const selections = selectedModifiers.get(group.id) || new Set();
      group.modifiers.forEach(modifier => {
        if (selections.has(modifier.id)) {
          total += modifier.price_modifier;
        }
      });
    });

    return total;
  };

  // Handle add to cart
  const handleAddToCart = () => {
    if (!validateSelections()) {
      return;
    }

    // Build selected modifiers list
    const selectedModifiersList: SelectedModifier[] = [];
    modifierGroups.forEach(group => {
      const selections = selectedModifiers.get(group.id) || new Set();
      group.modifiers.forEach(modifier => {
        if (selections.has(modifier.id)) {
          selectedModifiersList.push({
            group_name: group.name,
            modifier_name: modifier.name,
            price: modifier.price_modifier,
          });
        }
      });
    });

    const unitPrice = calculateTotalPrice();

    const cartItem: CartItem = {
      product,
      quantity,
      selected_modifiers: selectedModifiersList,
      course: course || undefined,
      notes: notes || undefined,
      unit_price: unitPrice,
    };

    onAddToCart(cartItem);
    handleClose();
  };

  // Handle close
  const handleClose = () => {
    // Reset state
    setSelectedModifiers(new Map());
    setCourse('');
    setNotes('');
    setQuantity(1);
    setValidationErrors([]);
    onClose();
  };

  // Format price
  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('hu-HU', {
      style: 'currency',
      currency: 'HUF',
      minimumFractionDigits: 0,
    }).format(price);
  };

  if (!isOpen) return null;

  const unitPrice = calculateTotalPrice();
  const totalPrice = unitPrice * quantity;

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="product-builder-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <h2>{product.name}</h2>
          <button className="close-btn" onClick={handleClose}>
            ✕
          </button>
        </div>

        {/* Body */}
        <div className="modal-body">
          {isLoading ? (
            <div className="loading-state">
              <p>Betöltés...</p>
            </div>
          ) : (
            <>
              {/* Product Info */}
              <div className="product-info">
                {product.description && <p className="product-description">{product.description}</p>}
                <p className="base-price">Alapár: {formatPrice(product.base_price)}</p>
              </div>

              {/* Modifier Groups */}
              {modifierGroups.length > 0 && (
                <div className="modifier-groups">
                  <h3>Opciók</h3>
                  {modifierGroups.map(group => (
                    <div key={group.id} className="modifier-group">
                      <div className="group-header">
                        <h4>{group.name}</h4>
                        {group.selection_type.includes('REQUIRED') && (
                          <span className="required-badge">Kötelező</span>
                        )}
                        {group.max_selection > 1 && (
                          <span className="limit-badge">
                            Max {group.max_selection} db
                          </span>
                        )}
                      </div>

                      <div className="modifiers-list">
                        {group.modifiers.map(modifier => {
                          const isSelected = selectedModifiers
                            .get(group.id)
                            ?.has(modifier.id) || false;

                          const isSingleChoice = group.selection_type.includes('SINGLE_CHOICE');

                          return (
                            <label
                              key={modifier.id}
                              className={`modifier-option ${isSelected ? 'selected' : ''}`}
                            >
                              <input
                                type={isSingleChoice ? 'radio' : 'checkbox'}
                                name={`group-${group.id}`}
                                checked={isSelected}
                                onChange={() =>
                                  handleModifierToggle(group.id, modifier.id, group.selection_type)
                                }
                              />
                              <span className="modifier-name">{modifier.name}</span>
                              {modifier.price_modifier !== 0 && (
                                <span className="modifier-price">
                                  {modifier.price_modifier > 0 ? '+' : ''}
                                  {formatPrice(modifier.price_modifier)}
                                </span>
                              )}
                            </label>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Course Selector */}
              <div className="form-group">
                <label htmlFor="course">Fogás típusa</label>
                <select
                  id="course"
                  value={course}
                  onChange={(e) => setCourse(e.target.value)}
                  className="course-select"
                >
                  {COURSE_OPTIONS.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Notes */}
              <div className="form-group">
                <label htmlFor="notes">Megjegyzés (opcionális)</label>
                <textarea
                  id="notes"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="pl. 'Kukorica nélkül', 'Extra fűszeres'..."
                  className="notes-textarea"
                  rows={3}
                />
              </div>

              {/* Validation Errors */}
              {validationErrors.length > 0 && (
                <div className="validation-errors">
                  {validationErrors.map((error, index) => (
                    <p key={index} className="error-message">
                      ⚠️ {error}
                    </p>
                  ))}
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <div className="quantity-control">
            <label>Mennyiség:</label>
            <button
              onClick={() => setQuantity(Math.max(1, quantity - 1))}
              className="qty-btn"
              disabled={quantity <= 1}
            >
              −
            </button>
            <span className="quantity-display">{quantity}</span>
            <button
              onClick={() => setQuantity(quantity + 1)}
              className="qty-btn"
            >
              +
            </button>
          </div>

          <div className="price-summary">
            <div className="price-row">
              <span>Egységár:</span>
              <span className="price">{formatPrice(unitPrice)}</span>
            </div>
            {quantity > 1 && (
              <div className="price-row total">
                <span>Összesen ({quantity} db):</span>
                <span className="price">{formatPrice(totalPrice)}</span>
              </div>
            )}
          </div>

          <button
            onClick={handleAddToCart}
            disabled={isLoading}
            className="add-to-cart-btn"
          >
            Hozzáadás a kosárhoz
          </button>
        </div>
      </div>
    </div>
  );
};
