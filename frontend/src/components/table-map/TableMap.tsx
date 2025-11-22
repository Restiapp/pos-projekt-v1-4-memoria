import { useState, useEffect, useCallback } from 'react';
import { Stage, Layer, Group } from 'react-konva';
import { getTables } from '@/services/tableService';
import type { Table } from '@/types/table';
import { FurnitureShape } from './FurnitureShape';
import { computeTableStatus } from '@/utils/tableStatusColor';

interface TableMapProps {
    activeRoom: string | null; // room ID or name
}

const POLLING_INTERVAL = 5000; // 5 seconds

export const TableMap = ({ activeRoom }: TableMapProps) => {
    const [tables, setTables] = useState<Table[]>([]);
    const [selectedTableId, setSelectedTableId] = useState<number | null>(null);
    const [loading, setLoading] = useState(true);

    // Canvas dimensions
    const width = window.innerWidth;
    const height = window.innerHeight - 180; // Approximate available height

    // Fetch tables with status computation
    const fetchTables = useCallback(async () => {
        try {
            const data = await getTables();

            // Compute status for each table (mock implementation for now)
            // TODO: Replace with real backend data when available
            const tablesWithStatus = data.map(table => ({
                ...table,
                // For demo purposes, assign random statuses
                // In production, this should come from orders/reservations data
                status: computeTableStatus(
                    Math.random() > 0.7, // hasActiveOrder
                    Math.random() > 0.8, // isPreparing
                    Math.random() > 0.9, // isPaying
                    Math.random() > 0.85  // isReserved
                )
            }));

            // Filter by room if activeRoom is set
            const filteredTables = activeRoom
                ? tablesWithStatus.filter(t => t.room_id?.toString() === activeRoom)
                : tablesWithStatus;

            setTables(filteredTables);
        } catch (e) {
            console.error("Failed to load tables", e);
        } finally {
            setLoading(false);
        }
    }, [activeRoom]);

    // Initial fetch
    useEffect(() => {
        fetchTables();
    }, [fetchTables]);

    // Set up polling for live refresh
    useEffect(() => {
        const intervalId = setInterval(() => {
            fetchTables();
        }, POLLING_INTERVAL);

        // Cleanup interval on unmount
        return () => clearInterval(intervalId);
    }, [fetchTables]);

    if (loading) {
        return (
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100%',
                color: '#fff'
            }}>
                Betöltés...
            </div>
        );
    }

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
                            status={table.status}
                            isSelected={selectedTableId === table.id}
                        />
                    </Group>
                ))}
            </Layer>
        </Stage>
    );
};
