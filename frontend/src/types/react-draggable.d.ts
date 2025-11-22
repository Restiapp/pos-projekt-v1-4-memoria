declare module 'react-draggable' {
  import * as React from 'react';

  export interface DraggableData {
    node: HTMLElement;
    x: number;
    y: number;
    deltaX: number;
    deltaY: number;
    lastX: number;
    lastY: number;
  }

  export type DraggableEvent = React.MouseEvent<HTMLElement | SVGElement> | React.TouchEvent<HTMLElement | SVGElement> | MouseEvent | TouchEvent;

  export interface DraggableProps {
    allowAnyClick?: boolean;
    axis?: 'both' | 'x' | 'y' | 'none';
    bounds?: { left?: number; right?: number; top?: number; bottom?: number } | string | false;
    cancel?: string;
    children?: React.ReactNode;
    defaultClassName?: string;
    defaultClassNameDragging?: string;
    defaultClassNameDragged?: string;
    defaultPosition?: { x: number; y: number };
    disabled?: boolean;
    grid?: [number, number];
    handle?: string;
    nodeRef?: React.RefObject<HTMLElement>;
    offsetParent?: HTMLElement;
    onMouseDown?: (e: MouseEvent) => void;
    onStart?: (e: DraggableEvent, data: DraggableData) => void | false;
    onDrag?: (e: DraggableEvent, data: DraggableData) => void | false;
    onStop?: (e: DraggableEvent, data: DraggableData) => void | false;
    position?: { x: number; y: number };
    positionOffset?: { x: number | string; y: number | string };
    scale?: number;
  }

  export default class Draggable extends React.Component<DraggableProps> {}
}
