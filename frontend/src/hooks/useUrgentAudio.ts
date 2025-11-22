/**
 * useUrgentAudio - Hook for audio notifications on urgent KDS items
 *
 * Features:
 * - Plays audio alert when new urgent items appear
 * - Toggleable via localStorage
 * - Prevents duplicate alerts for the same item
 */

import { useEffect, useRef, useState } from 'react';
import type { KdsItem } from '@/types/kds';

const AUDIO_ENABLED_KEY = 'kds_urgent_audio_enabled';

export const useUrgentAudio = (items: KdsItem[]) => {
  const [audioEnabled, setAudioEnabled] = useState(() => {
    const stored = localStorage.getItem(AUDIO_ENABLED_KEY);
    return stored === null ? true : stored === 'true'; // Default enabled
  });

  const previousUrgentIdsRef = useRef<Set<number>>(new Set());

  useEffect(() => {
    if (!audioEnabled) return;

    // Get current urgent item IDs
    const currentUrgentIds = new Set(
      items.filter(item => item.is_urgent && item.kds_status !== 'SERVED').map(item => item.id)
    );

    // Find new urgent items (not in previous set)
    const newUrgentIds = Array.from(currentUrgentIds).filter(
      id => !previousUrgentIdsRef.current.has(id)
    );

    // Play audio if there are new urgent items
    if (newUrgentIds.length > 0) {
      playUrgentAlert();
    }

    // Update previous IDs for next comparison
    previousUrgentIdsRef.current = currentUrgentIds;
  }, [items, audioEnabled]);

  const playUrgentAlert = () => {
    try {
      // Use Web Audio API for a simple beep sound
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      // Configure beep (800Hz, 200ms)
      oscillator.frequency.value = 800;
      oscillator.type = 'sine';

      gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);

      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.2);
    } catch (error) {
      console.error('Failed to play urgent alert:', error);
    }
  };

  const toggleAudio = () => {
    const newValue = !audioEnabled;
    setAudioEnabled(newValue);
    localStorage.setItem(AUDIO_ENABLED_KEY, String(newValue));
  };

  return {
    audioEnabled,
    toggleAudio,
  };
};
