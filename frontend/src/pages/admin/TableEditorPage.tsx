/**
 * TableEditorPage - Visual Table Layout Editor
 *
 * Features:
 * - Grid background with 10px snap
 * - Room selector
 * - Table icon selector (add new tables)
 * - Drag & drop tables with grid snap
 * - Rotate tables (+90°)
 * - Save layout to backend
 * - Desktop only (mobile drag disabled)
 */

import { useState, useEffect, useRef } from 'react';
import { Stage, Layer, Rect, Group, Line } from 'react-konva';
import Konva from 'konva';
import { getTables, updateTable, createTable, getRooms } from '@/services/tableService';
import { FurnitureShape } from '@/components/table-map/FurnitureShape';
import type { Table, TableCreate, TableUpdate } from '@/types/table';
import type { Room } from '@/types/room';
import { useToast } from '@/components/common/Toast';
import './TableEditorPage.css';

const GRID_SIZE = 10; // 10px grid snap
const STAGE_WIDTH = 1200;
const STAGE_HEIGHT = 800;

// Table template types for icon selector
interface TableTemplate {
  id: string;
  name: string;
  shape: 'rect' | 'round';
  width: number;
  height: number;
  capacity: number;
}

const TABLE_TEMPLATES: TableTemplate[] = [
  { id: 'rect-2', name: 'Rect 2p', shape: 'rect', width: 60, height: 60, capacity: 2 },
  { id: 'rect-4', name: 'Rect 4p', shape: 'rect', width: 80, height: 80, capacity: 4 },
  { id: 'rect-6', name: 'Rect 6p', shape: 'rect', width: 120, height: 80, capacity: 6 },
  { id: 'round-4', name: 'Round 4p', shape: 'round', width: 80, height: 80, capacity: 4 },
  { id: 'round-6', name: 'Round 6p', shape: 'round', width: 100, height: 100, capacity: 6 },
];

export const TableEditorPage = () => {
  const { showToast } = useToast();
  const stageRef = useRef<Konva.Stage>(null);

  const [rooms, setRooms] = useState<Room[]>([]);
  const [selectedRoomId, setSelectedRoomId] = useState<number | null>(null);
  const [tables, setTables] = useState<Table[]>([]);
  const [selectedTableId, setSelectedTableId] = useState<number | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Check if mobile device
  const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

  // Load rooms on mount
  useEffect(() => {
    loadRooms();
  }, []);

  // Load tables when room changes
  useEffect(() => {
    if (selectedRoomId !== null) {
      loadTables();
    }
  }, [selectedRoomId]);

  const loadRooms = async () => {
    try {
      const roomsData = await getRooms();
      setRooms(roomsData);
      if (roomsData.length > 0 && selectedRoomId === null) {
        setSelectedRoomId(roomsData[0].id);
      }
    } catch (error) {
      console.error('Error loading rooms:', error);
      showToast('Failed to load rooms', 'error');
    }
  };

  const loadTables = async () => {
    try {
      const tablesData = await getTables();
      // Filter by selected room
      const roomTables = tablesData.filter(t => t.room_id === selectedRoomId);
      setTables(roomTables);
      setHasChanges(false);
    } catch (error) {
      console.error('Error loading tables:', error);
      showToast('Failed to load tables', 'error');
    }
  };

  // Snap to grid
  const snapToGrid = (value: number): number => {
    return Math.round(value / GRID_SIZE) * GRID_SIZE;
  };

  // Handle table drag end
  const handleTableDragEnd = (tableId: number, e: Konva.KonvaEventObject<DragEvent>) => {
    if (isMobile) return; // Disable on mobile

    const newX = snapToGrid(e.target.x());
    const newY = snapToGrid(e.target.y());

    // Update local state
    setTables(prevTables =>
      prevTables.map(t =>
        t.id === tableId
          ? { ...t, position_x: newX, position_y: newY }
          : t
      )
    );

    setHasChanges(true);
    setIsDragging(false);
  };

  // Rotate selected table +90°
  const handleRotateTable = () => {
    if (selectedTableId === null) {
      showToast('Please select a table first', 'warning');
      return;
    }

    setTables(prevTables =>
      prevTables.map(t =>
        t.id === selectedTableId
          ? { ...t, rotation: (t.rotation + 90) % 360 }
          : t
      )
    );

    setHasChanges(true);
  };

  // Add new table from template
  const handleAddTable = async (template: TableTemplate) => {
    if (selectedRoomId === null) {
      showToast('Please select a room first', 'warning');
      return;
    }

    try {
      // Generate unique table number
      const tableNumber = `T-${Date.now().toString().slice(-6)}`;

      const newTableData: TableCreate = {
        table_number: tableNumber,
        room_id: selectedRoomId,
        position_x: 100,
        position_y: 100,
        width: template.width,
        height: template.height,
        shape: template.shape,
        capacity: template.capacity,
        rotation: 0,
      };

      const createdTable = await createTable(newTableData);
      setTables(prev => [...prev, createdTable]);
      showToast(`Table ${tableNumber} added`, 'success');
    } catch (error) {
      console.error('Error adding table:', error);
      showToast('Failed to add table', 'error');
    }
  };

  // Delete selected table
  const handleDeleteTable = () => {
    if (selectedTableId === null) {
      showToast('Please select a table first', 'warning');
      return;
    }

    // For now, just remove from local state (you can add API call to delete)
    setTables(prev => prev.filter(t => t.id !== selectedTableId));
    setSelectedTableId(null);
    setHasChanges(true);
    showToast('Table removed (save to persist)', 'info');
  };

  // Save all changes to backend
  const handleSaveLayout = async () => {
    setIsSaving(true);

    try {
      // Update each table
      await Promise.all(
        tables.map(table => {
          const updateData: TableUpdate = {
            position_x: table.position_x,
            position_y: table.position_y,
            rotation: table.rotation,
            width: table.width,
            height: table.height,
          };
          return updateTable(table.id, updateData);
        })
      );

      setHasChanges(false);
      showToast('Layout saved successfully', 'success');
    } catch (error) {
      console.error('Error saving layout:', error);
      showToast('Failed to save layout', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  // Reset to last saved state
  const handleResetLayout = () => {
    loadTables();
    setSelectedTableId(null);
  };

  // Draw grid background
  const renderGrid = () => {
    const lines = [];

    // Vertical lines
    for (let i = 0; i <= STAGE_WIDTH; i += GRID_SIZE) {
      lines.push(
        <Line
          key={`v-${i}`}
          points={[i, 0, i, STAGE_HEIGHT]}
          stroke="#3a3a3a"
          strokeWidth={i % 50 === 0 ? 1 : 0.5}
          opacity={i % 50 === 0 ? 0.3 : 0.15}
        />
      );
    }

    // Horizontal lines
    for (let i = 0; i <= STAGE_HEIGHT; i += GRID_SIZE) {
      lines.push(
        <Line
          key={`h-${i}`}
          points={[0, i, STAGE_WIDTH, i]}
          stroke="#3a3a3a"
          strokeWidth={i % 50 === 0 ? 1 : 0.5}
          opacity={i % 50 === 0 ? 0.3 : 0.15}
        />
      );
    }

    return lines;
  };

  return (
    <div className="table-editor-page">
      {/* Top Toolbar */}
      <div className="editor-toolbar">
        <div className="toolbar-section">
          <h2>Table Layout Editor</h2>

          {/* Room Selector */}
          <div className="room-selector">
            <label htmlFor="room-select">Room:</label>
            <select
              id="room-select"
              value={selectedRoomId || ''}
              onChange={(e) => setSelectedRoomId(Number(e.target.value))}
            >
              <option value="">Select room...</option>
              {rooms.map(room => (
                <option key={room.id} value={room.id}>
                  {room.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="toolbar-section">
          <button
            onClick={handleRotateTable}
            disabled={selectedTableId === null}
            className="btn btn-secondary"
            title="Rotate selected table 90°"
          >
            ↻ Rotate +90°
          </button>

          <button
            onClick={handleDeleteTable}
            disabled={selectedTableId === null}
            className="btn btn-danger"
            title="Delete selected table"
          >
            🗑 Delete
          </button>

          <button
            onClick={handleResetLayout}
            disabled={!hasChanges}
            className="btn btn-secondary"
          >
            ⟲ Reset
          </button>

          <button
            onClick={handleSaveLayout}
            disabled={!hasChanges || isSaving}
            className="btn btn-primary"
          >
            {isSaving ? '💾 Saving...' : '💾 Save Layout'}
          </button>
        </div>
      </div>

      <div className="editor-content">
        {/* Left Sidebar - Table Icon Selector */}
        <div className="table-palette">
          <h3>Add Table</h3>
          {isMobile && (
            <div className="mobile-warning">
              ⚠️ Drag & drop disabled on mobile
            </div>
          )}
          <div className="template-list">
            {TABLE_TEMPLATES.map(template => (
              <div
                key={template.id}
                className="template-item"
                onClick={() => handleAddTable(template)}
                title={`Add ${template.name}`}
              >
                <div className="template-preview">
                  <div
                    className={`preview-shape ${template.shape}`}
                    style={{
                      width: template.width / 2,
                      height: template.height / 2,
                    }}
                  />
                </div>
                <div className="template-label">{template.name}</div>
              </div>
            ))}
          </div>

          {hasChanges && (
            <div className="changes-indicator">
              ⚠️ Unsaved changes
            </div>
          )}
        </div>

        {/* Main Canvas */}
        <div className="canvas-container">
          {selectedRoomId === null ? (
            <div className="empty-state">
              <p>Please select a room to edit</p>
            </div>
          ) : (
            <Stage
              ref={stageRef}
              width={STAGE_WIDTH}
              height={STAGE_HEIGHT}
              className="konva-stage"
              onMouseDown={(e) => {
                // Deselect if clicking on stage background
                if (e.target === e.target.getStage()) {
                  setSelectedTableId(null);
                }
              }}
            >
              {/* Grid Layer */}
              <Layer>
                <Rect
                  x={0}
                  y={0}
                  width={STAGE_WIDTH}
                  height={STAGE_HEIGHT}
                  fill="#2C2E33"
                />
                {renderGrid()}
              </Layer>

              {/* Tables Layer */}
              <Layer>
                {tables.map(table => (
                  <Group
                    key={table.id}
                    x={table.position_x || 100}
                    y={table.position_y || 100}
                    draggable={!isMobile}
                    onClick={() => setSelectedTableId(table.id)}
                    onTap={() => setSelectedTableId(table.id)}
                    onDragStart={() => setIsDragging(true)}
                    onDragEnd={(e) => handleTableDragEnd(table.id, e)}
                    dragBoundFunc={(pos) => {
                      return {
                        x: Math.max(0, Math.min(pos.x, STAGE_WIDTH - (table.width || 80))),
                        y: Math.max(0, Math.min(pos.y, STAGE_HEIGHT - (table.height || 80))),
                      };
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
          )}
        </div>
      </div>

      {/* Info Panel */}
      <div className="info-panel">
        {selectedTableId && tables.find(t => t.id === selectedTableId) && (
          <div className="selected-table-info">
            <h4>Selected Table</h4>
            {(() => {
              const table = tables.find(t => t.id === selectedTableId);
              return table ? (
                <div className="table-details">
                  <div><strong>Number:</strong> {table.table_number}</div>
                  <div><strong>Position:</strong> ({table.position_x}, {table.position_y})</div>
                  <div><strong>Size:</strong> {table.width}x{table.height}</div>
                  <div><strong>Rotation:</strong> {table.rotation}°</div>
                  <div><strong>Capacity:</strong> {table.capacity}</div>
                  <div><strong>Shape:</strong> {table.shape}</div>
                </div>
              ) : null;
            })()}
          </div>
        )}

        <div className="help-section">
          <h4>Controls</h4>
          <ul>
            <li><strong>Click</strong> table to select</li>
            <li><strong>Drag</strong> table to move (snaps to 10px grid)</li>
            <li><strong>Rotate</strong> button: +90° rotation</li>
            <li><strong>Add</strong> new tables from left palette</li>
            <li><strong>Save</strong> to persist changes</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
