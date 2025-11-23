/**
 * AddItemModal - Modal for adding products to a specific round
 *
 * Features:
 * - Product selection from menu
 * - Quantity input
 * - Basic validation
 * - Adds items to specified round via orderService
 */

import { useState, useEffect } from 'react';
import {
  Modal,
  Button,
  Stack,
  Group,
  Text,
  TextInput,
  Select,
  NumberInput,
  ScrollArea,
  Paper,
  Badge,
} from '@mantine/core';
import { IconPlus } from '@tabler/icons-react';
import { getProducts } from '@/services/menuService';
import { addItemsToRound } from '@/services/orderService';
import { useToast } from '@/components/common/Toast';
import type { Product } from '@/types/menu';
import type { AddItemsToRoundRequest } from '@/types/order';
import './AddItemModal.css';

interface AddItemModalProps {
  isOpen: boolean;
  onClose: () => void;
  orderId: number;
  roundNumber: number;
  onItemsAdded: () => void;
}

interface SelectedProduct {
  product: Product;
  quantity: number;
}

export const AddItemModal = ({
  isOpen,
  onClose,
  orderId,
  roundNumber,
  onItemsAdded,
}: AddItemModalProps) => {
  const { showToast } = useToast();
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoadingProducts, setIsLoadingProducts] = useState<boolean>(true);
  const [selectedProducts, setSelectedProducts] = useState<SelectedProduct[]>([]);
  const [currentProductId, setCurrentProductId] = useState<string | null>(null);
  const [currentQuantity, setCurrentQuantity] = useState<number>(1);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  useEffect(() => {
    const loadProducts = async () => {
      setIsLoadingProducts(true);
      try {
        const response = await getProducts(1, 100, true); // Active products only
        setProducts(response.items);
      } catch (err) {
        console.error('Failed to load products', err);
        showToast('Nem sikerült betölteni a termékeket', 'error');
      } finally {
        setIsLoadingProducts(false);
      }
    };

    if (isOpen) {
      loadProducts();
    }
  }, [isOpen, showToast]);

  const handleAddProduct = () => {
    if (!currentProductId) {
      showToast('Válassz egy terméket', 'error');
      return;
    }

    const product = products.find((p) => p.id === parseInt(currentProductId));
    if (!product) {
      showToast('Érvénytelen termék', 'error');
      return;
    }

    if (currentQuantity <= 0) {
      showToast('A mennyiségnek nagyobbnak kell lennie nullánál', 'error');
      return;
    }

    // Check if product already added
    const existingIndex = selectedProducts.findIndex((sp) => sp.product.id === product.id);
    if (existingIndex >= 0) {
      // Update quantity
      const updated = [...selectedProducts];
      updated[existingIndex].quantity += currentQuantity;
      setSelectedProducts(updated);
    } else {
      // Add new
      setSelectedProducts([...selectedProducts, { product, quantity: currentQuantity }]);
    }

    // Reset
    setCurrentProductId(null);
    setCurrentQuantity(1);
  };

  const handleRemoveProduct = (productId: number) => {
    setSelectedProducts(selectedProducts.filter((sp) => sp.product.id !== productId));
  };

  const handleUpdateQuantity = (productId: number, newQuantity: number) => {
    if (newQuantity <= 0) {
      handleRemoveProduct(productId);
      return;
    }

    setSelectedProducts(
      selectedProducts.map((sp) =>
        sp.product.id === productId ? { ...sp, quantity: newQuantity } : sp
      )
    );
  };

  const handleSubmit = async () => {
    if (selectedProducts.length === 0) {
      showToast('Adj hozzá legalább egy terméket', 'error');
      return;
    }

    setIsSubmitting(true);
    try {
      const items: AddItemsToRoundRequest['items'] = selectedProducts.map((sp) => ({
        product_id: sp.product.id,
        quantity: sp.quantity,
        unit_price: sp.product.base_price,
        kds_station: 'COLD', // Default station, can be enhanced later
      }));

      await addItemsToRound(orderId, roundNumber, items);
      onItemsAdded();
    } catch (err) {
      console.error('Failed to add items to round', err);
      showToast('Nem sikerült hozzáadni a tételeket', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('hu-HU', {
      style: 'currency',
      currency: 'HUF',
      minimumFractionDigits: 0,
    }).format(price);
  };

  const totalAmount = selectedProducts.reduce(
    (sum, sp) => sum + sp.product.base_price * sp.quantity,
    0
  );

  return (
    <Modal
      opened={isOpen}
      onClose={onClose}
      title={`Tételek hozzáadása - ${roundNumber}. kör`}
      size="lg"
    >
      <Stack gap="md">
        {/* Product Selector */}
        <Paper withBorder p="sm">
          <Stack gap="sm">
            <Text fw={600} size="sm">
              Termék kiválasztása
            </Text>
            <Group align="flex-end">
              <Select
                label="Termék"
                placeholder="Válassz terméket"
                value={currentProductId}
                onChange={setCurrentProductId}
                data={products.map((p) => ({
                  value: p.id.toString(),
                  label: `${p.name} - ${formatPrice(p.base_price)}`,
                }))}
                searchable
                disabled={isLoadingProducts}
                style={{ flex: 1 }}
              />
              <NumberInput
                label="Mennyiség"
                value={currentQuantity}
                onChange={(value) => setCurrentQuantity(Number(value) || 1)}
                min={1}
                max={99}
                style={{ width: 100 }}
              />
              <Button
                leftSection={<IconPlus size={16} />}
                onClick={handleAddProduct}
                disabled={!currentProductId}
              >
                Hozzáad
              </Button>
            </Group>
          </Stack>
        </Paper>

        {/* Selected Products */}
        {selectedProducts.length > 0 && (
          <Paper withBorder p="sm">
            <Stack gap="xs">
              <Group justify="space-between">
                <Text fw={600} size="sm">
                  Kiválasztott tételek
                </Text>
                <Badge>{selectedProducts.length} tétel</Badge>
              </Group>
              <ScrollArea style={{ maxHeight: 300 }}>
                <Stack gap="xs">
                  {selectedProducts.map((sp) => (
                    <Paper key={sp.product.id} withBorder p="xs" className="selected-product-item">
                      <Group justify="space-between" align="center">
                        <div>
                          <Text fw={500}>{sp.product.name}</Text>
                          <Text size="sm" c="dimmed">
                            {formatPrice(sp.product.base_price)} × {sp.quantity} ={' '}
                            {formatPrice(sp.product.base_price * sp.quantity)}
                          </Text>
                        </div>
                        <Group gap="xs">
                          <NumberInput
                            value={sp.quantity}
                            onChange={(value) =>
                              handleUpdateQuantity(sp.product.id, Number(value) || 1)
                            }
                            min={1}
                            max={99}
                            size="xs"
                            style={{ width: 70 }}
                          />
                          <Button
                            size="xs"
                            variant="light"
                            color="red"
                            onClick={() => handleRemoveProduct(sp.product.id)}
                          >
                            Törlés
                          </Button>
                        </Group>
                      </Group>
                    </Paper>
                  ))}
                </Stack>
              </ScrollArea>
              <Group justify="space-between" mt="xs" pt="xs" style={{ borderTop: '1px solid #dee2e6' }}>
                <Text fw={600}>Összesen:</Text>
                <Text fw={700} size="lg">
                  {formatPrice(totalAmount)}
                </Text>
              </Group>
            </Stack>
          </Paper>
        )}

        {/* Actions */}
        <Group justify="flex-end" gap="sm">
          <Button variant="outline" onClick={onClose} disabled={isSubmitting}>
            Mégse
          </Button>
          <Button
            onClick={handleSubmit}
            loading={isSubmitting}
            disabled={selectedProducts.length === 0}
          >
            Tételek hozzáadása a körhöz
          </Button>
        </Group>
      </Stack>
    </Modal>
  );
};
