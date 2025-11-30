import { useEffect, useMemo, useRef, useState } from 'react';
import {
  ActionIcon,
  Alert,
  Badge,
  Button,
  Divider,
  Group,
  Modal,
  NumberInput,
  ScrollArea,
  Select,
  Stack,
  Switch,
  Text,
  TextInput,
} from '@mantine/core';
import {
  IconCopy,
  IconDeviceFloppy,
  IconEdit,
  IconPlus,
  IconRefresh,
} from '@tabler/icons-react';
import { useToast } from '@/components/common/Toast';
import { getRooms, createRoom, updateRoom } from '@/services/roomService';
import { getTables, updateTable, createTable } from '@/services/tableService';
import type { Room } from '@/types/room';
import type { Table, TableShape, TableStatus } from '@/types/table';
import './AdminFloorPlanPage.css';

type RoomModalMode = 'add' | 'edit';

const statusOptions: { label: string; value: TableStatus }[] = [
  { label: 'Szabad', value: 'FREE' },
  { label: 'Rendelés alatt', value: 'ORDERING' },
  { label: 'Folyamatban', value: 'IN_PROGRESS' },
  { label: 'Fizetés', value: 'PAYING' },
  { label: 'Foglalt', value: 'RESERVED' },
  { label: 'Inaktív', value: 'INACTIVE' },
];

const shapeOptions: { label: string; value: TableShape }[] = [
  { label: 'Kör', value: 'ROUND' },
  { label: 'Négyzet', value: 'SQUARE' },
  { label: 'Téglalap', value: 'RECTANGLE' },
];

const statusColors: Record<TableStatus, { bg: string; text: string; border: string }> = {
  FREE: { bg: '#d3f9d8', text: '#2b8a3e', border: '#8ce99a' },
  ORDERING: { bg: '#d0ebff', text: '#1c7ed6', border: '#91d5ff' },
  IN_PROGRESS: { bg: '#fff4e6', text: '#e67700', border: '#ffd8a8' },
  PAYING: { bg: '#ffe3e3', text: '#c92a2a', border: '#ffc9c9' },
  RESERVED: { bg: '#f1f3f5', text: '#495057', border: '#dee2e6' },
  INACTIVE: { bg: '#e9ecef', text: '#495057', border: '#ced4da' },
};

/**
 * Színpaletta asztalokhoz - vibráló neon színek
 */
const tableColorPresets: Array<{ name: string; bg: string; text: string; border: string }> = [
  { name: 'Neon Pink', bg: '#FF6EC7', text: '#000000', border: '#FF99D6' },
  { name: 'Electric Lime', bg: '#CCFF00', text: '#000000', border: '#DDFF66' },
  { name: 'Bright Cyan', bg: '#00FFFF', text: '#000000', border: '#66FFFF' },
  { name: 'Hot Magenta', bg: '#FF00FF', text: '#ffffff', border: '#FF66FF' },
  { name: 'Laser Lemon', bg: '#FEFE22', text: '#000000', border: '#FEFE88' },
  { name: 'Electric Blue', bg: '#7DF9FF', text: '#000000', border: '#A8FBFF' },
  { name: 'Radioactive Green', bg: '#39FF14', text: '#000000', border: '#7AFF5C' },
  { name: 'Vivid Violet', bg: '#9F00FF', text: '#ffffff', border: '#BF66FF' },
  { name: 'Blaze Orange', bg: '#FF6700', text: '#000000', border: '#FF9966' },
  { name: 'Shocking Pink', bg: '#FC0FC0', text: '#ffffff', border: '#FD6FD6' },
  { name: 'Neon Turquoise', bg: '#00F5FF', text: '#000000', border: '#66F8FF' },
  { name: 'Electric Purple', bg: '#BF00FF', text: '#ffffff', border: '#D966FF' },
  { name: 'Chartreuse', bg: '#7FFF00', text: '#000000', border: '#A8FF66' },
  { name: 'Highlighter Yellow', bg: '#FFF700', text: '#000000', border: '#FFF966' },
  { name: 'Neon Red', bg: '#FF073A', text: '#ffffff', border: '#FF6780' },
  { name: 'Atomic Tangerine', bg: '#FF9966', text: '#000000', border: '#FFB999' },
  { name: 'Electric Indigo', bg: '#6F00FF', text: '#ffffff', border: '#9F66FF' },
  { name: 'Wild Strawberry', bg: '#FF43A4', text: '#000000', border: '#FF87C3' },
  { name: 'Vivid Raspberry', bg: '#FF0090', text: '#ffffff', border: '#FF66B8' },
  { name: 'Electric Ultramarine', bg: '#120A8F', text: '#ffffff', border: '#4F48B8' },
  { name: 'Csillogó Fekete', bg: '#28282B', text: '#ffffff', border: '#5A5A5F' },
];

/**
 * Mintázat paletta termekhez - vibráló modern minták és textúrák
 */
const roomColorPresets: Array<{ name: string; bg: string }> = [
  { name: 'Alapértelmezett', bg: '#f8fafc' },
  // CSS Gradient alapú minták
  { name: 'Elektromos Fa', bg: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%), repeating-linear-gradient(90deg, transparent, transparent 20px, rgba(57, 255, 20, 0.3) 20px, rgba(57, 255, 20, 0.3) 22px)' },
  { name: 'Neon Terrazzo', bg: 'radial-gradient(circle at 20% 30%, #FF00FF 0px, transparent 8px), radial-gradient(circle at 60% 70%, #00FFFF 0px, transparent 6px), radial-gradient(circle at 80% 20%, #FEFE22 0px, transparent 10px), radial-gradient(circle at 30% 80%, #FF6EC7 0px, transparent 7px), radial-gradient(circle at 50% 50%, #39FF14 0px, transparent 5px), #f0f0f0' },
  { name: 'Halszálka Blokk', bg: 'repeating-linear-gradient(45deg, #228be6 0px, #228be6 40px, #ffd43b 40px, #ffd43b 80px, #ff6b6b 80px, #ff6b6b 120px)' },
  { name: 'Gyanta Folyó', bg: 'linear-gradient(90deg, #3d3d3d 0%, #3d3d3d 40%, #9F00FF 40%, #9F00FF 45%, #00F5FF 45%, #00F5FF 50%, #9F00FF 50%, #9F00FF 55%, #00F5FF 55%, #00F5FF 60%, #3d3d3d 60%, #3d3d3d 100%)' },
  { name: 'Beton Geometria', bg: 'linear-gradient(45deg, transparent 30%, rgba(255, 0, 144, 0.7) 30%, rgba(255, 0, 144, 0.7) 40%, transparent 40%), linear-gradient(-45deg, transparent 60%, rgba(0, 255, 255, 0.7) 60%, rgba(0, 255, 255, 0.7) 70%, transparent 70%), #6c757d' },
  { name: 'Ombre Plywood', bg: 'linear-gradient(180deg, #9F00FF 0%, #BF00FF 25%, #FF00FF 50%, #7FFF00 75%, #39FF14 100%)' },
  { name: 'Pixel Mozaik', bg: 'repeating-conic-gradient(from 0deg at 50% 50%, #00FFFF 0deg 90deg, #FF00FF 90deg 180deg, #FEFE22 180deg 270deg, #000000 270deg 360deg) 0 0 / 20px 20px' },
  { name: 'Kromatikus Olvadás', bg: 'radial-gradient(ellipse at 30% 50%, #FF00FF 0%, transparent 50%), radial-gradient(ellipse at 70% 60%, #00FFFF 0%, transparent 50%), radial-gradient(ellipse at 50% 30%, #FEFE22 0%, transparent 50%), linear-gradient(135deg, #9F00FF, #FF6EC7)' },
  { name: 'Acid Jungle', bg: 'radial-gradient(ellipse at 20% 80%, rgba(159, 0, 255, 0.6) 0%, transparent 50%), radial-gradient(ellipse at 60% 20%, rgba(0, 255, 255, 0.6) 0%, transparent 50%), radial-gradient(ellipse at 80% 70%, rgba(255, 110, 199, 0.6) 0%, transparent 50%), #000000' },
  { name: 'Cyberpunk Rács', bg: 'linear-gradient(0deg, transparent 24%, rgba(0, 255, 255, 0.5) 25%, rgba(0, 255, 255, 0.5) 26%, transparent 27%, transparent 74%, rgba(255, 0, 144, 0.5) 75%, rgba(255, 0, 144, 0.5) 76%, transparent 77%), linear-gradient(90deg, transparent 24%, rgba(0, 255, 255, 0.5) 25%, rgba(0, 255, 255, 0.5) 26%, transparent 27%, transparent 74%, rgba(255, 0, 144, 0.5) 75%, rgba(255, 0, 144, 0.5) 76%, transparent 77%), #0a0a1a' },
  { name: 'Memphis Max', bg: 'repeating-linear-gradient(45deg, #FF00FF 0px, #FF00FF 10px, #00FFFF 10px, #00FFFF 20px, #FEFE22 20px, #FEFE22 30px), repeating-linear-gradient(-45deg, transparent 0px, transparent 10px, rgba(255, 255, 255, 0.3) 10px, rgba(255, 255, 255, 0.3) 11px)' },
  { name: 'Elektromos Márvány', bg: 'linear-gradient(135deg, #ffffff 25%, transparent 25%), linear-gradient(225deg, #ffffff 25%, transparent 25%), linear-gradient(45deg, rgba(0, 255, 255, 0.3) 10%, transparent 10%), linear-gradient(135deg, rgba(159, 0, 255, 0.3) 10%, transparent 10%), linear-gradient(225deg, rgba(255, 215, 0, 0.3) 10%, transparent 10%), #f5f5f5' },
  { name: 'Neon Wireframe', bg: 'linear-gradient(0deg, transparent 48%, rgba(0, 255, 255, 0.8) 49%, rgba(0, 255, 255, 0.8) 51%, transparent 52%), linear-gradient(90deg, transparent 48%, rgba(255, 0, 144, 0.8) 49%, rgba(255, 0, 144, 0.8) 51%, transparent 52%), #0a0a0a' },
  { name: 'Gradient Halftone', bg: 'radial-gradient(circle, #FF00FF 20%, transparent 20%), radial-gradient(circle, #00FFFF 20%, transparent 20%), radial-gradient(circle, #FEFE22 20%, transparent 20%), linear-gradient(90deg, #FF00FF, #00FFFF, #FEFE22)' },
  { name: 'Izzó Topográfia', bg: 'repeating-radial-gradient(circle at 50% 50%, transparent 0px, transparent 20px, rgba(0, 255, 255, 0.4) 20px, rgba(0, 255, 255, 0.4) 21px, transparent 21px, transparent 40px, rgba(255, 0, 144, 0.4) 40px, rgba(255, 0, 144, 0.4) 41px), #000000' },
];

const shapeVariant = (shape?: TableShape): 'round' | 'square' | 'rect' => {
  if (shape === 'ROUND') return 'round';
  if (shape === 'SQUARE') return 'square';
  return 'rect'; // RECTANGLE -> rect for visual rendering
};

const deriveStatus = (table: Table): TableStatus => {
  const metaStatus = (table.metadata_json as Record<string, unknown> | null | undefined)?.status as
    | TableStatus
    | undefined;
  return table.status ?? metaStatus ?? 'FREE';
};

const deriveBoolean = (
  table: Table,
  key: 'is_active' | 'is_online_bookable' | 'is_smoking',
  fallback = false
) => {
  const meta = table.metadata_json as Record<string, unknown> | null | undefined;
  const metaValue = typeof meta?.[key] === 'boolean' ? (meta[key] as boolean) : undefined;
  const directValue = (
    table as Partial<Record<'is_active' | 'is_online_bookable' | 'is_smoking', boolean>>
  )[key];
  return directValue ?? metaValue ?? fallback;
};

/**
 * Egyedi szín lekérése a metadata-ból, ha van
 */
const getCustomColor = (table: Table): { bg: string; text: string; border: string } | null => {
  const meta = table.metadata_json as Record<string, unknown> | null | undefined;
  if (meta?.customColor && typeof meta.customColor === 'object') {
    const color = meta.customColor as { bg?: string; text?: string; border?: string };
    if (color.bg && color.text && color.border) {
      return { bg: color.bg, text: color.text, border: color.border };
    }
  }
  return null;
};

/**
 * Asztal név lekérése a metadata-ból
 */
const getTableName = (table: Table): string => {
  const meta = table.metadata_json as Record<string, unknown> | null | undefined;
  return typeof meta?.table_name === 'string' ? meta.table_name : '';
};

const defaultRoomSize = { width: 1200, height: 720 };

export const AdminFloorPlanPage = () => {
  const { showToast } = useToast();
  const [rooms, setRooms] = useState<Room[]>([]);
  const [tables, setTables] = useState<Table[]>([]);
  const [initialTables, setInitialTables] = useState<Table[]>([]); // Eredeti állapot tárolása
  const [selectedRoomId, setSelectedRoomId] = useState<number | null>(null);
  const [selectedTableId, setSelectedTableId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [roomModalOpen, setRoomModalOpen] = useState<boolean>(false);
  const [roomModalMode, setRoomModalMode] = useState<RoomModalMode>('add');
  const [roomForm, setRoomForm] = useState<{
    id: number | null;
    name: string;
    width: number;
    height: number;
    type: string;
    backgroundColor: string;
  }>({
    id: null,
    name: '',
    width: defaultRoomSize.width,
    height: defaultRoomSize.height,
    type: 'indoor',
    backgroundColor: '#f8fafc', // Alapértelmezett
  });
  const [tableModalOpen, setTableModalOpen] = useState<boolean>(false);
  const [tableForm, setTableForm] = useState<{
    table_number: string;
    shape: TableShape;
    capacity: number;
  }>({
    table_number: '',
    shape: 'RECTANGLE',
    capacity: 4,
  });
  const [draggingRoomId, setDraggingRoomId] = useState<number | null>(null);

  const canvasRef = useRef<HTMLDivElement | null>(null);
  const dragState = useRef<{ id: number; offsetX: number; offsetY: number } | null>(null);
  const resizeState = useRef<{
    id: number;
    startX: number;
    startY: number;
    startWidth: number;
    startHeight: number;
  } | null>(null);
  const roomResizeState = useRef<{
    roomId: number;
    startX: number;
    startY: number;
    startWidth: number;
    startHeight: number;
  } | null>(null);

  const activeRoom = useMemo(
    () => rooms.find((room) => room.id === selectedRoomId) ?? null,
    [rooms, selectedRoomId]
  );

  const filteredTables = useMemo(() => {
    if (!selectedRoomId) return tables;
    return tables.filter((table) => table.room_id === selectedRoomId);
  }, [tables, selectedRoomId]);

  useEffect(() => {
    if (filteredTables.length > 0 && !filteredTables.some((table) => table.id === selectedTableId)) {
      setSelectedTableId(filteredTables[0].id);
    }
  }, [filteredTables, selectedTableId]);

  const selectedTable = tables.find((table) => table.id === selectedTableId) ?? null;

  const updateTableState = (id: number, updater: (table: Table) => Table) => {
    setTables((prev) => prev.map((table) => (table.id === id ? updater(table) : table)));
  };

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [roomData, tableData] = await Promise.all([getRooms(), getTables()]);
      setRooms(roomData);
      setTables(tableData);
      setInitialTables([...tableData]); // Eredeti állapot mentése
      if (!selectedRoomId && roomData.length > 0) {
        setSelectedRoomId(roomData[0].id);
      }
    } catch (err) {
      console.error('Failed to load floor plan data', err);
      showToast('Nem sikerült betölteni az alaprajzot.', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const handlePointerMove = (event: PointerEvent) => {
      const canvasRect = canvasRef.current?.getBoundingClientRect();
      const roomWidth = activeRoom?.width ?? defaultRoomSize.width;
      const roomHeight = activeRoom?.height ?? defaultRoomSize.height;
      if (!canvasRect) return;

      if (dragState.current) {
        const { id, offsetX, offsetY } = dragState.current;
        const newX = Math.max(0, Math.min(roomWidth - 40, event.clientX - canvasRect.left - offsetX));
        const newY = Math.max(0, Math.min(roomHeight - 40, event.clientY - canvasRect.top - offsetY));

        updateTableState(id, (table) => ({
          ...table,
          position_x: Math.round(newX),
          position_y: Math.round(newY),
        }));
      }

      if (resizeState.current) {
        const { id, startX, startY, startWidth, startHeight } = resizeState.current;
        const deltaX = event.clientX - startX;
        const deltaY = event.clientY - startY;
        const nextWidth = Math.max(48, startWidth + deltaX);
        const nextHeight = Math.max(48, startHeight + deltaY);

        updateTableState(id, (table) => ({
          ...table,
          width: Math.round(nextWidth),
          height: Math.round(nextHeight),
        }));
      }

      if (roomResizeState.current) {
        const { roomId, startX, startY, startWidth, startHeight } = roomResizeState.current;
        const deltaX = event.clientX - startX;
        const deltaY = event.clientY - startY;
        const nextWidth = Math.max(400, startWidth + deltaX);
        const nextHeight = Math.max(300, startHeight + deltaY);

        setRooms((prev) =>
          prev.map((room) =>
            room.id === roomId
              ? { ...room, width: Math.round(nextWidth), height: Math.round(nextHeight) }
              : room
          )
        );
      }
    };

    const handlePointerUp = async () => {
      // Save table position after drag
      if (dragState.current) {
        const draggedTable = tables.find(t => t.id === dragState.current?.id);
        console.log('🔍 Drag ended, draggedTable:', draggedTable);
        if (draggedTable) {
          try {
            // Backend néha x,y néven küldi, néha position_x, position_y néven
            const tableAny = draggedTable as any;
            const position_x = tableAny.position_x ?? tableAny.x ?? 0;
            const position_y = tableAny.position_y ?? tableAny.y ?? 0;

            const payload = {
              position_x,
              position_y,
              metadata_json: draggedTable.metadata_json,
            };
            console.log('📤 Saving table position:', payload);
            await updateTable(draggedTable.id, payload);
            console.log('✅ Table position saved successfully');
            showToast('Asztal pozíció mentve!', 'success');
          } catch (err) {
            console.error('❌ Failed to save table position:', err);
            showToast('Nem sikerült menteni az asztal pozícióját.', 'error');
          }
        }
      }

      // Save table size after resize
      if (resizeState.current) {
        const resizedTable = tables.find(t => t.id === resizeState.current?.id);
        console.log('🔍 Resize ended, resizedTable:', resizedTable);
        if (resizedTable) {
          try {
            const payload = {
              width: resizedTable.width,
              height: resizedTable.height,
              metadata_json: resizedTable.metadata_json,
            };
            console.log('📤 Saving table size:', payload);
            await updateTable(resizedTable.id, payload);
            console.log('✅ Table size saved successfully');
            showToast('Asztal méret mentve!', 'success');
          } catch (err) {
            console.error('❌ Failed to save table size:', err);
            showToast('Nem sikerült menteni az asztal méretét.', 'error');
          }
        }
      }

      // Save room resize to backend
      if (roomResizeState.current && activeRoom) {
        try {
          const payload = {
            width: activeRoom.width,
            height: activeRoom.height,
          };
          console.log('📤 Saving room size:', payload);
          await updateRoom(roomResizeState.current.roomId, payload);
          console.log('✅ Room size saved successfully');
          showToast('Terem mérete mentve!', 'success');
        } catch (err) {
          console.error('❌ Failed to save room size:', err);
          showToast('Nem sikerült menteni a terem méretét.', 'error');
        }
      }

      dragState.current = null;
      resizeState.current = null;
      roomResizeState.current = null;
    };

    window.addEventListener('pointermove', handlePointerMove);
    window.addEventListener('pointerup', handlePointerUp);

    return () => {
      window.removeEventListener('pointermove', handlePointerMove);
      window.removeEventListener('pointerup', handlePointerUp);
    };
  }, [activeRoom]);

  const startDrag = (table: Table, event: React.PointerEvent<HTMLDivElement>) => {
    const canvasRect = canvasRef.current?.getBoundingClientRect();
    if (!canvasRect) return;
    const offsetX = event.clientX - canvasRect.left - (table.position_x ?? 0);
    const offsetY = event.clientY - canvasRect.top - (table.position_y ?? 0);
    dragState.current = { id: table.id, offsetX, offsetY };
    setSelectedTableId(table.id);
  };

  const startResize = (table: Table, event: React.PointerEvent<HTMLDivElement>) => {
    event.stopPropagation();
    const canvasRect = canvasRef.current?.getBoundingClientRect();
    if (!canvasRect) return;
    resizeState.current = {
      id: table.id,
      startX: event.clientX,
      startY: event.clientY,
      startWidth: table.width ?? 96,
      startHeight: table.height ?? 96,
    };
    setSelectedTableId(table.id);
  };

  const startRoomResize = (event: React.PointerEvent<HTMLDivElement>) => {
    event.stopPropagation();
    if (!activeRoom) return;
    roomResizeState.current = {
      roomId: activeRoom.id,
      startX: event.clientX,
      startY: event.clientY,
      startWidth: activeRoom.width,
      startHeight: activeRoom.height,
    };
  };

  const handleRoomDragOver = (roomId: number, event: React.DragEvent<HTMLElement>) => {
    event.preventDefault();
    if (!draggingRoomId || draggingRoomId === roomId) return;

    setRooms((prev) => {
      const currentIndex = prev.findIndex((room) => room.id === draggingRoomId);
      const targetIndex = prev.findIndex((room) => room.id === roomId);
      if (currentIndex === -1 || targetIndex === -1) return prev;

      const updated = [...prev];
      const [moved] = updated.splice(currentIndex, 1);
      updated.splice(targetIndex, 0, moved);
      return updated;
    });
  };

  const handleRoomDragEnd = () => {
    if (draggingRoomId) {
      showToast('Teremsorrend helyben mentve (TODO: backend PATCH)', 'info');
    }
    setDraggingRoomId(null);
  };

  const openRoomModal = (mode: RoomModalMode, room?: Room) => {
    setRoomModalMode(mode);
    // Extract color or pattern from background_image_url
    const bgValue =
      room?.background_image_url?.startsWith('color:') ?
        room.background_image_url.substring(6) :
        room?.background_image_url?.startsWith('pattern:') ?
        room.background_image_url.substring(8) :
        '#f8fafc';

    setRoomForm({
      id: room?.id ?? null,
      name: room?.name ?? '',
      width: room?.width ?? defaultRoomSize.width,
      height: room?.height ?? defaultRoomSize.height,
      type: room?.type ?? 'indoor',
      backgroundColor: bgValue,
    });
    setRoomModalOpen(true);
  };

  const handleSaveRoom = async () => {
    if (!roomForm.name.trim()) {
      showToast('Adj meg egy teremnevet.', 'error');
      return;
    }

    try {
      // Check if backgroundColor is a gradient/pattern or simple color
      const isPattern = roomForm.backgroundColor.includes('gradient') || roomForm.backgroundColor.includes('repeating');
      const roomData = {
        name: roomForm.name.trim(),
        width: roomForm.width,
        height: roomForm.height,
        type: roomForm.type,
        background_image_url: isPattern ? `pattern:${roomForm.backgroundColor}` : `color:${roomForm.backgroundColor}`,
      };

      console.log('🎨 Room Form Data:', roomForm);
      console.log('📤 Saving room with payload:', roomData);
      console.log('🔍 isPattern:', isPattern);

      if (roomModalMode === 'add') {
        const created = await createRoom(roomData);
        console.log('✅ Room created:', created);
        setRooms((prev) => [...prev, created]);
        setSelectedRoomId(created.id);
        showToast('Új terem hozzáadva.', 'success');
      } else if (roomForm.id) {
        const updated = await updateRoom(roomForm.id, roomData);
        console.log('✅ Room updated:', updated);
        setRooms((prev) => prev.map((room) => (room.id === updated.id ? updated : room)));
        showToast('Terem frissítve.', 'success');
      }
    } catch (err) {
      console.error('Failed to save room', err);
      showToast('Nem sikerült menteni a termet.', 'error');
    } finally {
      setRoomModalOpen(false);
    }
  };

  const handleSaveTable = async () => {
    if (!selectedTable) return;
    setIsSaving(true);
    try {
      const payload = {
        table_number: selectedTable.table_number,
        room_id: selectedTable.room_id ?? selectedRoomId ?? undefined,
        position_x: selectedTable.position_x ?? 0,
        position_y: selectedTable.position_y ?? 0,
        width: selectedTable.width ?? 96,
        height: selectedTable.height ?? 96,
        rotation: selectedTable.rotation ?? 0,
        shape: selectedTable.shape,
        capacity: selectedTable.capacity ?? 0,
        metadata_json: {
          ...(selectedTable.metadata_json ?? {}),
          status: deriveStatus(selectedTable),
          is_active: deriveBoolean(selectedTable, 'is_active', true),
          is_online_bookable: deriveBoolean(selectedTable, 'is_online_bookable', false),
          is_smoking: deriveBoolean(selectedTable, 'is_smoking', false),
        },
      };

      await updateTable(selectedTable.id, payload);
      showToast('Asztal mentve.', 'success');
    } catch (err) {
      console.error('Failed to save table', err);
      showToast('Nem sikerült menteni az asztalt.', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const openTableModal = () => {
    // Következő szabad asztalszám megkeresése
    const existingNumbers = tables.map(t => {
      const num = parseInt(t.table_number, 10);
      return isNaN(num) ? 0 : num;
    });
    const maxNumber = existingNumbers.length > 0 ? Math.max(...existingNumbers) : 0;
    const nextNumber = maxNumber + 1;

    setTableForm({
      table_number: nextNumber.toString(),
      shape: 'RECTANGLE',
      capacity: 4,
    });
    setTableModalOpen(true);
  };

  const handleCreateTable = async () => {
    if (!tableForm.table_number.trim()) {
      showToast('Az asztalszám megadása kötelező.', 'error');
      return;
    }
    if (!selectedRoomId) {
      showToast('Válassz ki egy termet az asztal létrehozásához.', 'error');
      return;
    }

    setIsSaving(true);
    try {
      const newTable = await createTable({
        table_number: tableForm.table_number,
        room_id: selectedRoomId,
        position_x: 0,  // Alapértelmezett pozíció - utána szabadon mozgatható
        position_y: 0,
        width: 80,
        height: 80,
        rotation: 0,
        shape: tableForm.shape,
        capacity: tableForm.capacity,
      });

      // Frissítjük a tables listát az új asztallal
      setTables((prev) => [...prev, newTable]);
      setSelectedTableId(newTable.id);
      setTableModalOpen(false);
      showToast('Asztal létrehozva. Most már szabadon mozgathatod!', 'success');
    } catch (err) {
      console.error('Failed to create table', err);
      showToast('Nem sikerült létrehozni az asztalt.', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  /**
   * Asztal duplikálása - másolat készítése a kiválasztott asztalból
   */
  const handleDuplicateTable = async () => {
    if (!selectedTable) return;
    if (!selectedRoomId) {
      showToast('Válassz ki egy termet a duplikáláshoz.', 'error');
      return;
    }

    setIsSaving(true);
    try {
      // Új asztalszám generálása (pl. "A1" -> "A1 (másolat)")
      const originalNumber = selectedTable.table_number;
      let newNumber = `${originalNumber} (másolat)`;

      // Ha már létezik ilyen nevű asztal, számot adunk hozzá
      let counter = 2;
      while (tables.some((t) => t.table_number === newNumber)) {
        newNumber = `${originalNumber} (másolat ${counter})`;
        counter++;
      }

      const duplicatedTable = await createTable({
        table_number: newNumber,
        room_id: selectedTable.room_id ?? selectedRoomId,
        position_x: (selectedTable.position_x ?? 0) + 20, // Kis eltolás, hogy látszódjon a másolat
        position_y: (selectedTable.position_y ?? 0) + 20,
        width: selectedTable.width ?? 96,
        height: selectedTable.height ?? 96,
        rotation: selectedTable.rotation ?? 0,
        shape: selectedTable.shape,
        capacity: selectedTable.capacity ?? 4,
        metadata_json: {
          ...(selectedTable.metadata_json ?? {}),
          table_name: getTableName(selectedTable) ? `${getTableName(selectedTable)} (másolat)` : '',
        },
      });

      setTables((prev) => [...prev, duplicatedTable]);
      setSelectedTableId(duplicatedTable.id);
      showToast('Asztal duplikálva! Szerkeszd a másolatot.', 'success');
    } catch (err) {
      console.error('Failed to duplicate table', err);
      showToast('Nem sikerült duplikálni az asztalt.', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  /**
   * Mentés összes változtatás - az összes módosított asztal mentése egyszerre
   */
  const handleSaveAllChanges = async () => {
    const modifiedTables = tables.filter((table) => {
      // Megkeressük az eredeti asztalt az initialTables-ből
      const original = initialTables.find((t) => t.id === table.id);
      if (!original) return false; // Új asztal, még nincs mentve

      // Összehasonlítjuk az értékeket
      return (
        table.table_number !== original.table_number ||
        table.position_x !== original.position_x ||
        table.position_y !== original.position_y ||
        table.width !== original.width ||
        table.height !== original.height ||
        table.shape !== original.shape ||
        table.capacity !== original.capacity ||
        JSON.stringify(table.metadata_json) !== JSON.stringify(original.metadata_json)
      );
    });

    if (modifiedTables.length === 0) {
      showToast('Nincs módosítás, amit menthetnénk.', 'info');
      return;
    }

    setIsSaving(true);
    let successCount = 0;
    let failCount = 0;

    try {
      // Párhuzamos mentések (Promise.allSettled)
      const results = await Promise.allSettled(
        modifiedTables.map((table) =>
          updateTable(table.id, {
            table_number: table.table_number,
            room_id: table.room_id,
            position_x: table.position_x,
            position_y: table.position_y,
            width: table.width,
            height: table.height,
            rotation: table.rotation,
            shape: table.shape,
            capacity: table.capacity,
            metadata_json: table.metadata_json,
          })
        )
      );

      results.forEach((result) => {
        if (result.status === 'fulfilled') {
          successCount++;
        } else {
          failCount++;
          console.error('Failed to update table:', result.reason);
        }
      });

      if (failCount === 0) {
        showToast(`${successCount} asztal sikeresen mentve!`, 'success');
        // Frissítjük az initialTables-t, hogy a következő összehasonlítás pontos legyen
        setInitialTables([...tables]);
      } else {
        showToast(
          `${successCount} asztal mentve, ${failCount} sikertelen.`,
          'error'
        );
      }
    } catch (err) {
      console.error('Error during bulk save:', err);
      showToast('Hiba történt a mentés során.', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="admin-floorplan-page">
      <Group justify="space-between" align="center" mb="md">
        <div>
          <Text fw={700} size="xl">
            Alaprajz szerkesztő
          </Text>
          <Text size="sm" c="dimmed">
            Húzd az asztalokat, szerkeszd a tulajdonságokat és mentsd a változásokat.
          </Text>
        </div>
        <Group gap="xs">
          <Button
            leftSection={<IconDeviceFloppy size={16} />}
            variant="filled"
            color="green"
            onClick={handleSaveAllChanges}
            loading={isSaving}
          >
            Mentés
          </Button>
          <Button
            leftSection={<IconPlus size={16} />}
            variant="light"
            onClick={() => openRoomModal('add')}
          >
            Új terem
          </Button>
          <Button
            leftSection={<IconPlus size={16} />}
            variant="filled"
            onClick={openTableModal}
            disabled={!selectedRoomId}
          >
            Új asztal
          </Button>
          <ActionIcon variant="light" color="blue" onClick={loadData} aria-label="Frissítés">
            <IconRefresh size={18} />
          </ActionIcon>
        </Group>
      </Group>

      {isLoading ? (
        <Alert color="blue" title="Betöltés" radius="md">
          Alaprajz adatok betöltése...
        </Alert>
      ) : (
        <div className="floorplan-layout">
          <div className="floorplan-panel rooms-panel">
            <Group justify="space-between" mb="sm">
              <Text fw={600}>Termek</Text>
              <ActionIcon variant="subtle" onClick={() => openRoomModal('add')}>
                <IconPlus size={16} />
              </ActionIcon>
            </Group>
            <div className="room-list">
              {rooms.length === 0 ? (
                <Alert color="gray" radius="md" title="Nincs terem">
                  Adj hozzá legalább egy termet az alaprajz szerkesztéséhez.
                </Alert>
              ) : (
                rooms.map((room) => (
                  <div
                    key={room.id}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        setSelectedRoomId(room.id);
                      }
                    }}
                    className={`room-item ${selectedRoomId === room.id ? 'active' : ''}`}
                    onClick={() => setSelectedRoomId(room.id)}
                    draggable
                    onDragStart={() => setDraggingRoomId(room.id)}
                    onDragOver={(event) => handleRoomDragOver(room.id, event)}
                    onDragEnd={handleRoomDragEnd}
                  >
                    <div className="room-item__text">
                      <span className="room-item__name">{room.name}</span>
                      <span className="room-item__meta">
                        {room.type === 'outdoor' ? 'Kültér' : 'Beltér'} · {room.width}×{room.height}
                      </span>
                    </div>
                    <ActionIcon
                      size="sm"
                      variant="subtle"
                      onClick={(event) => {
                        event.stopPropagation();
                        openRoomModal('edit', room);
                      }}
                    >
                      <IconEdit size={14} />
                    </ActionIcon>
                  </div>
                ))
              )}
            </div>
            <Text size="xs" c="dimmed" mt="sm">
              Fogd és húzd a sorokat az új sorrendhez (helyben tárolva).
            </Text>
          </div>

          <div className="floorplan-panel canvas-panel">
            <Group justify="space-between" mb="sm">
              <Text fw={600}>Terem alaprajz</Text>
              <Badge variant="light" color="gray">
                {filteredTables.length} asztal
              </Badge>
            </Group>
            <ScrollArea h="100%">
              <div
                ref={canvasRef}
                className="floorplan-canvas"
                style={{
                  width: activeRoom?.width ?? defaultRoomSize.width,
                  height: activeRoom?.height ?? defaultRoomSize.height,
                  ...(activeRoom?.background_image_url?.startsWith('color:') ?
                    { backgroundColor: activeRoom.background_image_url.substring(6) } :
                    activeRoom?.background_image_url?.startsWith('pattern:') ?
                    { background: activeRoom.background_image_url.substring(8) } :
                    { backgroundColor: '#f8fafc' }
                  ),
                }}
              >
                {filteredTables.map((table) => {
                  const status = deriveStatus(table);
                  const customColor = getCustomColor(table);
                  const palette = customColor ?? statusColors[status];
                  const variant = shapeVariant(table.shape);
                  const tableWidth = table.width ?? 96;
                  const height = variant === 'square' ? tableWidth : table.height ?? 96;

                  return (
                    <div
                      key={table.id}
                      className={`floorplan-table shape-${variant} ${
                        selectedTableId === table.id ? 'selected' : ''
                      }`}
                      style={{
                        left: table.position_x ?? 0,
                        top: table.position_y ?? 0,
                        width: tableWidth,
                        height,
                        backgroundColor: palette.bg,
                        color: palette.text,
                        borderColor: palette.border,
                      }}
                      onClick={() => setSelectedTableId(table.id)}
                      onPointerDown={(event) => startDrag(table, event)}
                    >
                      <div className="floorplan-table__header">
                        <span className="floorplan-table__number">
                          {getTableName(table) ? `${getTableName(table)} (${table.table_number})` : table.table_number}
                        </span>
                        <Badge variant="light" size="xs">
                          {statusOptions.find((option) => option.value === status)?.label}
                        </Badge>
                      </div>
                      <div className="floorplan-table__meta">
                        {table.capacity ?? '-'} fő ·{' '}
                        {table.shape === 'ROUND' ? 'Kör' : table.shape === 'SQUARE' ? 'Négyzet' : 'Téglalap'}
                      </div>
                      <div
                        className="resize-handle"
                        onPointerDown={(event) => startResize(table, event)}
                        role="presentation"
                      />
                    </div>
                  );
                })}
                {/* Room Resize Handle */}
                <div
                  className="room-resize-handle"
                  onPointerDown={startRoomResize}
                  role="presentation"
                  title="Húzd a termet átméretezni"
                />
              </div>
            </ScrollArea>
          </div>

          <div className="floorplan-panel inspector-panel">
            <Text fw={600} mb="sm">
              Asztal tulajdonságai
            </Text>
            {selectedTable ? (
              <Stack gap="sm">
                <TextInput
                  label="Asztal név"
                  placeholder="pl. VIP asztal, Panoráma"
                  value={getTableName(selectedTable)}
                  onChange={(event) => {
                    const newName = event.target.value;
                    console.log('✏️ Table name changed to:', newName);
                    updateTableState(selectedTable.id, (table) => ({
                      ...table,
                      metadata_json: {
                        ...(table.metadata_json ?? {}),
                        table_name: newName,
                      },
                    }));
                  }}
                  onBlur={async () => {
                    console.log('💾 Auto-saving table name on blur');
                    try {
                      await updateTable(selectedTable.id, {
                        metadata_json: selectedTable.metadata_json,
                      });
                      console.log('✅ Table name auto-saved');
                    } catch (err) {
                      console.error('❌ Failed to auto-save table name:', err);
                    }
                  }}
                />
                <TextInput
                  label="Asztalszám"
                  placeholder="pl. 1, A1, T01"
                  value={selectedTable.table_number}
                  onChange={(event) =>
                    updateTableState(selectedTable.id, (table) => ({
                      ...table,
                      table_number: event.target.value,
                    }))
                  }
                  required
                />
                <NumberInput
                  label="Kapacitás"
                  value={selectedTable.capacity ?? 0}
                  min={0}
                  onChange={(value) =>
                    updateTableState(selectedTable.id, (table) => ({
                      ...table,
                      capacity: Number(value) || 0,
                    }))
                  }
                />
                <Select
                  label="Forma"
                  data={shapeOptions}
                  value={selectedTable.shape}
                  onChange={(value) =>
                    updateTableState(selectedTable.id, (table) => ({
                      ...table,
                      shape: (value as TableShape) ?? table.shape,
                    }))
                  }
                />
                <Select
                  label="Státusz"
                  data={statusOptions}
                  value={deriveStatus(selectedTable)}
                  onChange={(value) => {
                    if (!value) return;
                    updateTableState(selectedTable.id, (table) => ({
                      ...table,
                      status: value as TableStatus,
                      metadata_json: { ...(table.metadata_json ?? {}), status: value },
                    }));
                  }}
                />

                <Divider label="Asztal színe" labelPosition="center" />
                <Stack gap="xs">
                  <Text size="sm" c="dimmed">
                    Válassz színpalettát:
                  </Text>
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(4, 1fr)',
                      gap: '6px',
                      maxHeight: '280px',
                      overflowY: 'auto',
                      padding: '4px',
                    }}
                  >
                    {tableColorPresets.map((preset, index) => {
                      const currentCustomColor = getCustomColor(selectedTable);
                      const isActive =
                        currentCustomColor?.bg === preset.bg &&
                        currentCustomColor?.text === preset.text &&
                        currentCustomColor?.border === preset.border;

                      return (
                        <div
                          key={index}
                          role="button"
                          tabIndex={0}
                          onClick={async () => {
                            console.log('🎨 Table color changed to:', preset.name);
                            updateTableState(selectedTable.id, (table) => ({
                              ...table,
                              metadata_json: {
                                ...(table.metadata_json ?? {}),
                                customColor: { bg: preset.bg, text: preset.text, border: preset.border },
                              },
                            }));
                            // Auto-save color change
                            try {
                              await updateTable(selectedTable.id, {
                                metadata_json: {
                                  ...(selectedTable.metadata_json ?? {}),
                                  customColor: { bg: preset.bg, text: preset.text, border: preset.border },
                                },
                              });
                              console.log('✅ Table color auto-saved');
                              showToast('Asztal szín mentve!', 'success');
                            } catch (err) {
                              console.error('❌ Failed to auto-save table color:', err);
                              showToast('Nem sikerült menteni az asztal színét.', 'error');
                            }
                          }}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                              updateTableState(selectedTable.id, (table) => ({
                                ...table,
                                metadata_json: {
                                  ...(table.metadata_json ?? {}),
                                  customColor: { bg: preset.bg, text: preset.text, border: preset.border },
                                },
                              }));
                            }
                          }}
                          style={{
                            padding: '6px 4px',
                            borderRadius: '6px',
                            backgroundColor: preset.bg,
                            border: `2px solid ${isActive ? '#228be6' : preset.border}`,
                            cursor: 'pointer',
                            textAlign: 'center',
                            fontSize: '0.65rem',
                            fontWeight: isActive ? 700 : 500,
                            color: preset.text,
                            transition: 'all 120ms ease',
                            boxShadow: isActive ? '0 2px 8px rgba(34, 139, 230, 0.35)' : '0 1px 3px rgba(0,0,0,0.1)',
                            transform: isActive ? 'scale(1.05)' : 'scale(1)',
                            minHeight: '32px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                          }}
                        >
                          {preset.name}
                        </div>
                      );
                    })}
                  </div>
                </Stack>

                <Divider />
                <NumberInput
                  label="X pozíció"
                  value={selectedTable.position_x ?? 0}
                  onChange={(value) =>
                    updateTableState(selectedTable.id, (table) => ({
                      ...table,
                      position_x: Number(value) || 0,
                    }))
                  }
                />
                <NumberInput
                  label="Y pozíció"
                  value={selectedTable.position_y ?? 0}
                  onChange={(value) =>
                    updateTableState(selectedTable.id, (table) => ({
                      ...table,
                      position_y: Number(value) || 0,
                    }))
                  }
                />
                <NumberInput
                  label="Szélesség"
                  value={selectedTable.width ?? 96}
                  min={40}
                  onChange={(value) =>
                    updateTableState(selectedTable.id, (table) => ({
                      ...table,
                      width: Number(value) || 40,
                    }))
                  }
                />
                <NumberInput
                  label="Magasság"
                  value={selectedTable.height ?? 96}
                  min={40}
                  onChange={(value) =>
                    updateTableState(selectedTable.id, (table) => ({
                      ...table,
                      height: Number(value) || 40,
                    }))
                  }
                />

                <Divider />
                <Switch
                  label="Aktív"
                  checked={!!deriveBoolean(selectedTable, 'is_active', true)}
                  onChange={(event) =>
                    updateTableState(selectedTable.id, (table) => ({
                      ...table,
                      is_active: event.currentTarget.checked,
                      metadata_json: { ...(table.metadata_json ?? {}), is_active: event.currentTarget.checked },
                    }))
                  }
                />
                <Switch
                  label="Online foglalható"
                  checked={!!deriveBoolean(selectedTable, 'is_online_bookable', false)}
                  onChange={(event) =>
                    updateTableState(selectedTable.id, (table) => ({
                      ...table,
                      is_online_bookable: event.currentTarget.checked,
                      metadata_json: {
                        ...(table.metadata_json ?? {}),
                        is_online_bookable: event.currentTarget.checked,
                      },
                    }))
                  }
                />
                <Switch
                  label="Dohányzó"
                  checked={!!deriveBoolean(selectedTable, 'is_smoking', false)}
                  onChange={(event) =>
                    updateTableState(selectedTable.id, (table) => ({
                      ...table,
                      is_smoking: event.currentTarget.checked,
                      metadata_json: { ...(table.metadata_json ?? {}), is_smoking: event.currentTarget.checked },
                    }))
                  }
                />

                <Group gap="xs" grow>
                  <Button
                    leftSection={<IconCopy size={16} />}
                    variant="light"
                    onClick={handleDuplicateTable}
                    loading={isSaving}
                  >
                    Duplikálás
                  </Button>
                  <Button
                    leftSection={<IconDeviceFloppy size={16} />}
                    onClick={handleSaveTable}
                    loading={isSaving}
                  >
                    Mentés
                  </Button>
                </Group>
              </Stack>
            ) : (
              <Alert color="gray" title="Nincs asztal kiválasztva" radius="md">
                Kattints egy asztalra az alaprajzon a szerkesztéshez.
              </Alert>
            )}
          </div>
        </div>
      )}

      <Modal
        opened={roomModalOpen}
        onClose={() => setRoomModalOpen(false)}
        title={roomModalMode === 'add' ? 'Új terem' : 'Terem szerkesztése'}
        centered
      >
        <Stack gap="sm">
          <TextInput
            label="Terem neve"
            value={roomForm.name}
            onChange={(event) => setRoomForm((prev) => ({ ...prev, name: event.target.value }))}
          />
          <NumberInput
            label="Szélesség"
            value={roomForm.width}
            min={400}
            onChange={(value) => setRoomForm((prev) => ({ ...prev, width: Number(value) || prev.width }))}
          />
          <NumberInput
            label="Magasság"
            value={roomForm.height}
            min={400}
            onChange={(value) => setRoomForm((prev) => ({ ...prev, height: Number(value) || prev.height }))}
          />
          <Select
            label="Típus"
            data={[
              { label: 'Beltér', value: 'indoor' },
              { label: 'Kültér', value: 'outdoor' },
            ]}
            value={roomForm.type}
            onChange={(value) => setRoomForm((prev) => ({ ...prev, type: value ?? prev.type }))}
          />

          <Divider label="Terem mintázat" labelPosition="center" />
          <Stack gap="xs">
            <Text size="sm" c="dimmed">
              Válassz háttér mintázatot:
            </Text>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '6px',
                maxHeight: '320px',
                overflowY: 'auto',
                padding: '4px',
              }}
            >
              {roomColorPresets.map((preset, index) => {
                const isActive = roomForm.backgroundColor === preset.bg;
                const isPattern = preset.bg.includes('gradient') || preset.bg.includes('repeating');

                return (
                  <div
                    key={index}
                    role="button"
                    tabIndex={0}
                    onClick={() => {
                      setRoomForm((prev) => ({ ...prev, backgroundColor: preset.bg }));
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        setRoomForm((prev) => ({ ...prev, backgroundColor: preset.bg }));
                      }
                    }}
                    style={{
                      padding: '8px 6px',
                      borderRadius: '6px',
                      background: isPattern ? preset.bg : 'none',
                      backgroundColor: isPattern ? 'transparent' : preset.bg,
                      border: `2px solid ${isActive ? '#228be6' : '#dee2e6'}`,
                      cursor: 'pointer',
                      textAlign: 'center',
                      fontSize: '0.65rem',
                      fontWeight: isActive ? 700 : 500,
                      color: isPattern ? '#ffffff' : '#495057',
                      textShadow: isPattern ? '0 1px 3px rgba(0,0,0,0.8)' : 'none',
                      transition: 'all 120ms ease',
                      boxShadow: isActive ? '0 2px 8px rgba(34, 139, 230, 0.35)' : '0 1px 3px rgba(0,0,0,0.1)',
                      transform: isActive ? 'scale(1.05)' : 'scale(1)',
                      minHeight: '48px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    {preset.name}
                  </div>
                );
              })}
            </div>
          </Stack>

          <Group justify="flex-end" mt="sm">
            <Button variant="default" onClick={() => setRoomModalOpen(false)}>
              Mégse
            </Button>
            <Button leftSection={<IconDeviceFloppy size={16} />} onClick={handleSaveRoom}>
              Mentés
            </Button>
          </Group>
        </Stack>
      </Modal>

      <Modal
        opened={tableModalOpen}
        onClose={() => setTableModalOpen(false)}
        title="Új asztal létrehozása"
        centered
      >
        <Stack gap="sm">
          <TextInput
            label="Asztalszám"
            placeholder="pl. 1, A1, T01"
            value={tableForm.table_number}
            onChange={(event) => setTableForm((prev) => ({ ...prev, table_number: event.target.value }))}
            required
          />
          <Select
            label="Forma"
            data={shapeOptions}
            value={tableForm.shape}
            onChange={(value) => setTableForm((prev) => ({ ...prev, shape: (value as TableShape) ?? prev.shape }))}
            required
          />
          <NumberInput
            label="Kapacitás (fő)"
            value={tableForm.capacity}
            min={1}
            max={20}
            onChange={(value) => setTableForm((prev) => ({ ...prev, capacity: Number(value) || prev.capacity }))}
          />
          <Alert color="blue" title="Pozíció" variant="light">
            Az asztal a (0,0) pozícióban jön létre. Mentés után szabadon mozgathatod az alaprajzon.
          </Alert>
          <Group justify="flex-end" mt="sm">
            <Button variant="default" onClick={() => setTableModalOpen(false)}>
              Mégse
            </Button>
            <Button
              leftSection={<IconDeviceFloppy size={16} />}
              onClick={handleCreateTable}
              loading={isSaving}
            >
              Létrehozás
            </Button>
          </Group>
        </Stack>
      </Modal>
    </div>
  );
};
