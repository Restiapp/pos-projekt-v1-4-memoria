import { useState, useEffect } from 'react';
import { Stage, Layer, Group } from 'react-konva';
import { getTables } from '@/services/tableService';
import type { Table } from '@/types/table';
import { FurnitureShape } from './FurnitureShape';
import { OrderStartModal } from './OrderStartModal';
import { useToast } from '@/components/common/Toast';
import './TableMap.css';

interface TableMapProps {
    activeRoom: string | null; // room ID or name
}

export const TableMap = ({ activeRoom }: TableMapProps) => {
    const { showToast } = useToast();
    const [tables, setTables] = useState<Table[]>([]);
    const [selectedTableId, setSelectedTableId] = useState<number | null>(null);
    const [selectedTableForOrder, setSelectedTableForOrder] = useState<Table | null>(null);
    const [isOrderModalOpen, setIsOrderModalOpen] = useState(false);

    // Canvas dimensions
    const width = window.innerWidth;
    const height = window.innerHeight - 180; // Approximate available height

    useEffect(() => {
        const fetchTables = async () => {
            try {
                const data = await getTables();
                // Filter locally for now (until backend filter is active/passed)
                // Assuming mock activeRoom logic or just showing all
                setTables(data);
            } catch (e) {
                console.error("Failed to load tables", e);
                showToast('Nem sikerült betölteni az asztalokat', 'error');
            }
        };
        fetchTables();
    }, [activeRoom]);

    // Handle table click - open order start modal
    const handleTableClick = (table: Table) => {
        setSelectedTableForOrder(table);
        setIsOrderModalOpen(true);
    };

    // Handle successful order creation
    const handleOrderCreated = (orderId: number) => {
        showToast(`Rendelés sikeresen létrehozva! (ID: ${orderId})`, 'success');
        setIsOrderModalOpen(false);
        setSelectedTableForOrder(null);
    };

    return (
        <>
            <Stage
                width={width}
                height={height}
                draggable
                style={{ backgroundColor: '#2C2E33' }}
                onMouseDown={(e) => {
                    // Deselect if clicking on stage
                    if (e.target === e.target.getStage()) {
                        setSelectedTableId(null);
                    }
                }}
            >
                <Layer>
                    {tables.map((table) => (
                        <Group
                            key={table.id}
                            x={table.position_x || 100}
                            y={table.position_y || 100}
                            draggable
                            onClick={() => {
                                setSelectedTableId(table.id);
                                handleTableClick(table);
                            }}
                            onTap={() => {
                                setSelectedTableId(table.id);
                                handleTableClick(table);
                            }}
                            onDragEnd={(e) => {
                                console.log('New pos:', e.target.x(), e.target.y());
                                // TODO: Save to backend
                            }}
                        >
                            <FurnitureShape
                                shape={table.shape || 'rect'}
                                width={table.width || 80}
                                height={table.height || 80}
                                rotation={table.rotation || 0}
                                capacity={table.capacity || 4}
                                tableNumber={table.table_number}
                                isSelected={selectedTableId === table.id}
                            />
                        </Group>
                    ))}
                </Layer>
            </Stage>

            {/* Order Start Modal with Sequence Generator */}
            <OrderStartModal
                isOpen={isOrderModalOpen}
                onClose={() => {
                    setIsOrderModalOpen(false);
                    setSelectedTableForOrder(null);
                }}
                table={selectedTableForOrder}
                onOrderCreated={handleOrderCreated}
            />
        </>
    );
};
