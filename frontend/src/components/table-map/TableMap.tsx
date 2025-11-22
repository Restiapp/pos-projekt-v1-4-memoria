import { useState, useEffect } from 'react';
import { Stage, Layer, Group } from 'react-konva';
import { getTables } from '@/services/tableService';
import type { Table } from '@/types/table';
import { FurnitureShape } from './FurnitureShape';
import { useToast } from '@/components/common/Toast';
import './TableMap.css';

interface TableMapProps {
    activeRoom?: string | null;
}

export const TableMap = ({ activeRoom }: TableMapProps) => {
    const { showToast } = useToast();
    const [tables, setTables] = useState<Table[]>([]);
    const [selectedTableId, setSelectedTableId] = useState<number | null>(null);

    // Canvas dimensions
    const width = window.innerWidth;
    const height = window.innerHeight - 180; // Approximate available height

    useEffect(() => {
        const fetchTables = async () => {
            try {
                const data = await getTables();
                setTables(data);
            } catch (e) {
                console.error("Failed to load tables", e);
            }
        };
        fetchTables();
    }, [activeRoom]);

    // Asztal kattintás kezelése
    const handleTableClick = (table: Table) => {
        showToast(`Asztal: ${table.table_number} (ID: ${table.id})`, 'info');
    };

    return (
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
                        onClick={() => setSelectedTableId(table.id)}
                        onTap={() => setSelectedTableId(table.id)}
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
    );
};
