/**
 * Menu Debug Page - Sprint D6
 * Simple debug view for testing Menu V1 API
 */

import React, { useEffect, useState } from 'react';
import { menuV1Service } from '@/services/menuV1Service';
import { MenuCategoryTree, Channel } from '@/types/menuV1';
import './MenuDebugPage.css';

export const MenuDebugPage: React.FC = () => {
  const [menuTree, setMenuTree] = useState<MenuCategoryTree[]>([]);
  const [channel, setChannel] = useState<Channel>('dine_in');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadMenuTree = async () => {
    setLoading(true);
    setError(null);
    try {
      const tree = await menuV1Service.getMenuTree(channel);
      setMenuTree(tree);
    } catch (err: any) {
      setError(err.message || 'Failed to load menu tree');
      console.error('Error loading menu tree:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMenuTree();
  }, [channel]);

  const renderModifierOption = (option: any) => (
    <div key={option.id} className="modifier-option">
      <span className="option-name">{option.name}</span>
      {option.price_delta_gross !== 0 && (
        <span className="option-price">+{option.price_delta_gross} Ft</span>
      )}
      {option.is_default && <span className="badge-default">Default</span>}
    </div>
  );

  const renderModifierGroup = (group: any) => (
    <div key={group.id} className="modifier-group">
      <div className="group-header">
        <strong>{group.name}</strong>
        <span className="badge">{group.selection_type}</span>
      </div>
      {group.description && <p className="group-desc">{group.description}</p>}
      <div className="group-meta">
        Min: {group.min_select} | Max: {group.max_select || 'unlimited'}
      </div>
      <div className="options-list">
        {group.options.map(renderModifierOption)}
      </div>
    </div>
  );

  const renderVariant = (variant: any) => (
    <div key={variant.id} className="variant">
      <span className="variant-name">{variant.name}</span>
      {variant.price_delta !== 0 && (
        <span className="variant-delta">
          {variant.price_delta > 0 ? '+' : ''}
          {variant.price_delta} Ft
        </span>
      )}
      {variant.is_default && <span className="badge-default">Default</span>}
    </div>
  );

  const renderItem = (item: any) => (
    <div key={item.id} className="menu-item">
      <div className="item-header">
        <h4>{item.name}</h4>
        <span className="item-price">{item.base_price_gross} Ft</span>
      </div>
      {item.description && <p className="item-desc">{item.description}</p>}
      <div className="item-meta">
        <span>VAT Dine-in: {item.vat_rate_dine_in}%</span>
        <span>VAT Takeaway: {item.vat_rate_takeaway}%</span>
      </div>

      {item.variants && item.variants.length > 0 && (
        <div className="variants-section">
          <strong>Variants:</strong>
          <div className="variants-list">
            {item.variants.map(renderVariant)}
          </div>
        </div>
      )}

      {item.modifier_groups && item.modifier_groups.length > 0 && (
        <div className="modifiers-section">
          <strong>Modifier Groups:</strong>
          {item.modifier_groups.map(renderModifierGroup)}
        </div>
      )}
    </div>
  );

  const renderCategory = (category: MenuCategoryTree, level: number = 0) => (
    <div key={category.id} className="menu-category" style={{ marginLeft: `${level * 20}px` }}>
      <div className="category-header">
        <h3>
          {category.name}
          <span className="badge-category">ID: {category.id}</span>
        </h3>
      </div>
      {category.description && <p className="category-desc">{category.description}</p>}

      {category.items && category.items.length > 0 && (
        <div className="items-section">
          {category.items.map(renderItem)}
        </div>
      )}

      {category.subcategories && category.subcategories.length > 0 && (
        <div className="subcategories">
          {category.subcategories.map((subcat) => renderCategory(subcat, level + 1))}
        </div>
      )}
    </div>
  );

  return (
    <div className="menu-debug-page">
      <div className="debug-header">
        <h1>Menu V1 Debug View</h1>
        <div className="channel-selector">
          <label>Channel:</label>
          <select value={channel} onChange={(e) => setChannel(e.target.value as Channel)}>
            <option value="dine_in">Dine In</option>
            <option value="takeaway">Takeaway</option>
            <option value="delivery">Delivery</option>
          </select>
          <button onClick={loadMenuTree} disabled={loading}>
            {loading ? 'Loading...' : 'Reload'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <strong>Error:</strong> {error}
        </div>
      )}

      {loading && <div className="loading-spinner">Loading menu tree...</div>}

      {!loading && !error && menuTree.length === 0 && (
        <div className="empty-state">
          <p>No menu data found. Try importing seed data first.</p>
        </div>
      )}

      {!loading && menuTree.length > 0 && (
        <div className="menu-tree">
          <div className="tree-meta">
            <strong>Total Categories:</strong> {menuTree.length}
          </div>
          {menuTree.map((category) => renderCategory(category, 0))}
        </div>
      )}
    </div>
  );
};

export default MenuDebugPage;
