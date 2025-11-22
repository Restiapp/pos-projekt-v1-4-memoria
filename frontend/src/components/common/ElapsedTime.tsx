/**
 * ElapsedTime Component - Displays elapsed time since a given timestamp
 *
 * Features:
 * - Auto-refreshes every 1 second
 * - Color-coded based on elapsed time:
 *   - < 10 min: gray
 *   - 10-20 min: yellow
 *   - > 20 min: red
 * - Displays in Hungarian format: "X perc / Y másodperce"
 *
 * Usage:
 * <ElapsedTime timestamp="2025-11-22T10:30:00Z" />
 */

import { useState, useEffect } from 'react';
import './ElapsedTime.css';

interface ElapsedTimeProps {
  timestamp: string; // ISO datetime string
  className?: string; // Optional additional CSS class
}

export const ElapsedTime = ({ timestamp, className = '' }: ElapsedTimeProps) => {
  const [elapsedSeconds, setElapsedSeconds] = useState<number>(0);

  // Update elapsed time every second
  useEffect(() => {
    // Calculate elapsed time in seconds
    const calculateElapsed = () => {
      const startTime = new Date(timestamp).getTime();
      const now = Date.now();
      return Math.floor((now - startTime) / 1000);
    };

    // Initial calculation
    setElapsedSeconds(calculateElapsed());

    // Set up interval to update every second
    const interval = setInterval(() => {
      setElapsedSeconds(calculateElapsed());
    }, 1000);

    // Cleanup interval on unmount
    return () => clearInterval(interval);
  }, [timestamp]);

  // Calculate minutes and seconds
  const minutes = Math.floor(elapsedSeconds / 60);
  const seconds = elapsedSeconds % 60;

  // Determine color class based on elapsed minutes
  const getColorClass = (): string => {
    if (minutes < 10) return 'elapsed-time-gray';
    if (minutes < 20) return 'elapsed-time-yellow';
    return 'elapsed-time-red';
  };

  // Format the display text
  const formatElapsedTime = (): string => {
    if (minutes === 0) {
      return `${seconds} másodperce`;
    } else if (seconds === 0) {
      return `${minutes} perc`;
    } else {
      return `${minutes} perc / ${seconds} másodperce`;
    }
  };

  return (
    <span className={`elapsed-time ${getColorClass()} ${className}`}>
      {formatElapsedTime()}
    </span>
  );
};
