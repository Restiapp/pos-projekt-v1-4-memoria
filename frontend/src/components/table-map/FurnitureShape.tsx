/**
 * Deprecated: legacy Konva-based renderer kept for reference.
 * The modern table map now uses Mantine + DOM elements instead of Konva.
 */
import { Group, Rect, Circle, Text } from 'react-konva';
import { useRef, useEffect } from 'react';
import Konva from 'konva';

interface FurnitureShapeProps {
    shape: 'rect' | 'round';
    width: number;
    height: number;
    rotation: number;
    capacity: number;
    tableNumber: string;
    isSelected?: boolean;
    onSelect?: () => void;
}

export const FurnitureShape = ({
    shape,
    width,
    height,
    rotation,
    capacity,
    tableNumber,
    isSelected
}: FurnitureShapeProps) => {
    const groupRef = useRef<Konva.Group>(null);

    // Helper to calculate chair positions
    const getChairPositions = () => {
        const chairs = [];
        const chairRadius = 8;
        const chairDistance = 15; // distance from table edge

        if (shape === 'round') {
            // Distribute around circle
            const radius = width / 2;
            const angleStep = 360 / capacity;
            for (let i = 0; i < capacity; i++) {
                const angle = i * angleStep * (Math.PI / 180);
                chairs.push({
                    x: (radius + chairDistance) * Math.cos(angle) + width/2,
                    y: (radius + chairDistance) * Math.sin(angle) + height/2,
                });
            }
        } else {
            // Rectangular distribution logic (simplified for now)
            // Just placing them around for demo
            const perimeter = 2 * (width + height);
            // This is complex to do perfectly generic, simple approach:
            // 1 per side if < 4, etc.
            // For now, let's just put them in corners/sides based on capacity
             const seatsPerSide = Math.ceil(capacity / 4);
             // ... actually, let's use a simpler radial distribution for rect too for v1
             // or just static positions for standard sizes.

             // Simple Radial fallback for Rect (looks okay-ish)
             const radius = Math.max(width, height) / 2 + chairDistance;
             const angleStep = 360 / capacity;
             for (let i = 0; i < capacity; i++) {
                const angle = i * angleStep * (Math.PI / 180);
                chairs.push({
                    x: radius * Math.cos(angle) + width/2,
                    y: radius * Math.sin(angle) + height/2,
                });
            }
        }
        return chairs;
    };

    const chairs = getChairPositions();

    return (
        <Group
            rotation={rotation}
            ref={groupRef}
            offset={{ x: width / 2, y: height / 2 }} // Center rotation
            x={width / 2} // Compensate offset
            y={height / 2}
        >
            {/* Chairs */}
            {chairs.map((pos, i) => (
                <Circle
                    key={i}
                    x={pos.x}
                    y={pos.y}
                    radius={8}
                    fill="#4A3121"
                    shadowBlur={2}
                />
            ))}

            {/* Table Body */}
            {shape === 'round' ? (
                <Circle
                    width={width}
                    height={height}
                    fill="#694832"
                    stroke={isSelected ? '#228BE6' : '#3E2C1F'}
                    strokeWidth={isSelected ? 3 : 1}
                    shadowBlur={5}
                    x={width/2}
                    y={height/2}
                />
            ) : (
                <Rect
                    width={width}
                    height={height}
                    fill="#694832"
                    cornerRadius={4}
                    stroke={isSelected ? '#228BE6' : '#3E2C1F'}
                    strokeWidth={isSelected ? 3 : 1}
                    shadowBlur={5}
                />
            )}

            {/* Table Number */}
            <Text
                text={tableNumber}
                fontSize={16}
                fontStyle="bold"
                fill="white"
                align="center"
                verticalAlign="middle"
                width={width}
                height={height}
                x={0}
                y={0}
            />
        </Group>
    );
};
