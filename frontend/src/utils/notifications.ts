/**
 * Notification Utility - Kulturált hibajelzés alert() helyett
 *
 * Használat:
 *   - notify.error('Hiba történt!')
 *   - notify.success('Sikeres művelet!')
 *   - notify.info('Információ')
 */

type NotificationType = 'error' | 'success' | 'info' | 'warning';

interface NotificationOptions {
  duration?: number;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
}

class NotificationManager {
  private container: HTMLDivElement | null = null;

  private ensureContainer() {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'notification-container';
      this.container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        pointer-events: none;
      `;
      document.body.appendChild(this.container);
    }
    return this.container;
  }

  private show(message: string, type: NotificationType, options: NotificationOptions = {}) {
    const container = this.ensureContainer();
    const duration = options.duration || 4000;

    // Notification elem létrehozása
    const notification = document.createElement('div');
    notification.style.cssText = `
      background: ${this.getBackgroundColor(type)};
      color: white;
      padding: 12px 20px;
      margin-bottom: 10px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      pointer-events: auto;
      cursor: pointer;
      max-width: 400px;
      word-wrap: break-word;
      animation: slideIn 0.3s ease-out;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-size: 14px;
      line-height: 1.5;
    `;

    // Ikon + üzenet
    const icon = this.getIcon(type);
    notification.innerHTML = `
      <div style="display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 18px;">${icon}</span>
        <span>${message}</span>
      </div>
    `;

    // Kattintásra eltűnik
    notification.onclick = () => {
      this.remove(notification);
    };

    // Animáció CSS hozzáadása (ha még nincs)
    this.ensureAnimationStyles();

    // Hozzáadás a containerhez
    container.appendChild(notification);

    // Automatikus eltűnés
    setTimeout(() => {
      this.remove(notification);
    }, duration);
  }

  private ensureAnimationStyles() {
    if (!document.getElementById('notification-styles')) {
      const style = document.createElement('style');
      style.id = 'notification-styles';
      style.textContent = `
        @keyframes slideIn {
          from {
            transform: translateX(400px);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        @keyframes slideOut {
          from {
            transform: translateX(0);
            opacity: 1;
          }
          to {
            transform: translateX(400px);
            opacity: 0;
          }
        }
      `;
      document.head.appendChild(style);
    }
  }

  private remove(notification: HTMLDivElement) {
    notification.style.animation = 'slideOut 0.3s ease-in';
    setTimeout(() => {
      notification.remove();
    }, 300);
  }

  private getBackgroundColor(type: NotificationType): string {
    switch (type) {
      case 'error':
        return '#EF4444'; // Red
      case 'success':
        return '#10B981'; // Green
      case 'warning':
        return '#F59E0B'; // Orange
      case 'info':
        return '#3B82F6'; // Blue
      default:
        return '#6B7280'; // Gray
    }
  }

  private getIcon(type: NotificationType): string {
    switch (type) {
      case 'error':
        return '❌';
      case 'success':
        return '✅';
      case 'warning':
        return '⚠️';
      case 'info':
        return 'ℹ️';
      default:
        return '📢';
    }
  }

  error(message: string, options?: NotificationOptions) {
    console.error('[Notification Error]', message);
    this.show(message, 'error', options);
  }

  success(message: string, options?: NotificationOptions) {
    console.log('[Notification Success]', message);
    this.show(message, 'success', options);
  }

  warning(message: string, options?: NotificationOptions) {
    console.warn('[Notification Warning]', message);
    this.show(message, 'warning', options);
  }

  info(message: string, options?: NotificationOptions) {
    console.info('[Notification Info]', message);
    this.show(message, 'info', options);
  }
}

// Singleton export
export const notify = new NotificationManager();
