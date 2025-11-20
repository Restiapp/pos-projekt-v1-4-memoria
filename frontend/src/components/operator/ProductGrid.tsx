/**
 * ProductGrid - Product Selection Grid for Operator Page
 *
 * Features:
 * - Display products in a grid layout
 * - Category filtering
 * - Opens ProductBuilderModal for products with modifiers
 * - Direct add to cart for simple products
 */

import { useState, useEffect } from 'react';
import { getProducts, getCategories } from '@/services/menuService';
import type { Product, Category } from '@/types/menu';
import { ProductBuilderModal, type CartItem } from './ProductBuilderModal';
import './ProductGrid.css';

interface ProductGridProps {
  onAddToCart: (item: CartItem) => void;
}

export const ProductGrid = ({ onAddToCart }: ProductGridProps) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  // Load products and categories
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [productsResponse, categoriesResponse] = await Promise.all([
        getProducts(1, 100, true), // Load first 100 active products
        getCategories(1, 100, true), // Load all active categories
      ]);
      setProducts(productsResponse.items);
      setCategories(categoriesResponse.items);
    } catch (error) {
      console.error('Error loading products:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle product click
  const handleProductClick = (product: Product) => {
    // For now, always open the modal
    // In production, you might want to check if product has modifiers first
    setSelectedProduct(product);
    setIsModalOpen(true);
  };

  // Filter products by category
  const filteredProducts = selectedCategory
    ? products.filter(p => p.category_id === selectedCategory)
    : products;

  // Format price
  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('hu-HU', {
      style: 'currency',
      currency: 'HUF',
      minimumFractionDigits: 0,
    }).format(price);
  };

  if (isLoading) {
    return (
      <div className="product-grid-loading">
        <p>Termékek betöltése...</p>
      </div>
    );
  }

  return (
    <div className="product-grid-container">
      {/* Category Filter */}
      {categories.length > 0 && (
        <div className="category-filter">
          <button
            className={`category-btn ${selectedCategory === null ? 'active' : ''}`}
            onClick={() => setSelectedCategory(null)}
          >
            Összes
          </button>
          {categories.map(category => (
            <button
              key={category.id}
              className={`category-btn ${selectedCategory === category.id ? 'active' : ''}`}
              onClick={() => setSelectedCategory(category.id)}
            >
              {category.name}
            </button>
          ))}
        </div>
      )}

      {/* Product Grid */}
      <div className="product-grid">
        {filteredProducts.length === 0 ? (
          <div className="no-products">
            <p>Nincs elérhető termék ebben a kategóriában.</p>
          </div>
        ) : (
          filteredProducts.map(product => (
            <div
              key={product.id}
              className="product-card"
              onClick={() => handleProductClick(product)}
            >
              <div className="product-card-body">
                <h3 className="product-name">{product.name}</h3>
                {product.description && (
                  <p className="product-description">{product.description}</p>
                )}
              </div>
              <div className="product-card-footer">
                <span className="product-price">{formatPrice(product.base_price)}</span>
                <button className="add-btn">Választ</button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Product Builder Modal */}
      {selectedProduct && (
        <ProductBuilderModal
          product={selectedProduct}
          isOpen={isModalOpen}
          onClose={() => {
            setIsModalOpen(false);
            setSelectedProduct(null);
          }}
          onAddToCart={onAddToCart}
        />
      )}
    </div>
  );
};
