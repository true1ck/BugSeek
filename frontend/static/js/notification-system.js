/**
 * BugSeek Notification System
 * ==========================
 * 
 * A comprehensive notification system for real-time updates,
 * progress indicators, and system status messages.
 */

class NotificationSystem {
    constructor() {
        this.notifications = [];
        this.container = null;
        this.maxNotifications = 5;
        this.defaultDuration = 5000;
        this.init();
    }

    init() {
        this.createContainer();
        this.setupStyles();
        this.connectToEventSource();
    }

    createContainer() {
        this.container = document.createElement('div');
        this.container.id = 'notification-container';
        this.container.className = 'notification-container';
        document.body.appendChild(this.container);
    }

    setupStyles() {
        if (document.getElementById('notification-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .notification-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
                max-width: 400px;
                pointer-events: none;
            }

            .notification {
                background: white;
                border-radius: 12px;
                padding: 1rem 1.25rem;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
                border-left: 4px solid;
                display: flex;
                align-items: flex-start;
                gap: 0.75rem;
                transform: translateX(100%);
                opacity: 0;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                pointer-events: auto;
                backdrop-filter: blur(10px);
                position: relative;
                overflow: hidden;
            }

            .notification::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
                pointer-events: none;
            }

            .notification.show {
                transform: translateX(0);
                opacity: 1;
            }

            .notification.hide {
                transform: translateX(100%);
                opacity: 0;
            }

            .notification.success {
                border-left-color: #10b981;
                background: linear-gradient(135deg, rgba(16, 185, 129, 0.05), rgba(255, 255, 255, 0.95));
            }

            .notification.error {
                border-left-color: #ef4444;
                background: linear-gradient(135deg, rgba(239, 68, 68, 0.05), rgba(255, 255, 255, 0.95));
            }

            .notification.warning {
                border-left-color: #f59e0b;
                background: linear-gradient(135deg, rgba(245, 158, 11, 0.05), rgba(255, 255, 255, 0.95));
            }

            .notification.info {
                border-left-color: #3b82f6;
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(255, 255, 255, 0.95));
            }

            .notification-icon {
                flex-shrink: 0;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                font-size: 0.875rem;
            }

            .notification.success .notification-icon {
                background: #10b981;
                color: white;
            }

            .notification.error .notification-icon {
                background: #ef4444;
                color: white;
            }

            .notification.warning .notification-icon {
                background: #f59e0b;
                color: white;
            }

            .notification.info .notification-icon {
                background: #3b82f6;
                color: white;
            }

            .notification-content {
                flex: 1;
                min-width: 0;
            }

            .notification-title {
                font-weight: 600;
                color: #1f2937;
                font-size: 0.875rem;
                margin-bottom: 0.25rem;
            }

            .notification-message {
                color: #6b7280;
                font-size: 0.8rem;
                line-height: 1.4;
                margin: 0;
            }

            .notification-close {
                flex-shrink: 0;
                background: none;
                border: none;
                color: #9ca3af;
                cursor: pointer;
                padding: 0;
                width: 16px;
                height: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: all 0.2s ease;
                font-size: 0.75rem;
            }

            .notification-close:hover {
                background: rgba(0, 0, 0, 0.05);
                color: #4b5563;
            }

            .notification-progress {
                position: absolute;
                bottom: 0;
                left: 0;
                height: 2px;
                background: rgba(0, 0, 0, 0.1);
                transition: width linear;
                border-radius: 0 0 12px 0;
            }

            .notification.success .notification-progress {
                background: #10b981;
            }

            .notification.error .notification-progress {
                background: #ef4444;
            }

            .notification.warning .notification-progress {
                background: #f59e0b;
            }

            .notification.info .notification-progress {
                background: #3b82f6;
            }

            .notification-action {
                background: none;
                border: 1px solid #d1d5db;
                color: #374151;
                padding: 0.375rem 0.75rem;
                border-radius: 6px;
                font-size: 0.75rem;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                margin-top: 0.5rem;
            }

            .notification-action:hover {
                background: #f9fafb;
                border-color: #9ca3af;
            }

            /* Toast-style animations */
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }

            @keyframes slideOutRight {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }

            /* Mobile responsive */
            @media (max-width: 768px) {
                .notification-container {
                    top: 80px;
                    left: 16px;
                    right: 16px;
                    max-width: none;
                }

                .notification {
                    margin: 0;
                    transform: translateY(-100%);
                }

                .notification.show {
                    transform: translateY(0);
                }

                .notification.hide {
                    transform: translateY(-100%);
                }
            }
        `;

        document.head.appendChild(styles);
    }

    connectToEventSource() {
        // Simulate real-time connection (in production, use WebSocket or SSE)
        this.simulateRealTimeEvents();
    }

    simulateRealTimeEvents() {
        // Simulate various system events
        setTimeout(() => {
            this.show({
                type: 'info',
                title: 'System Status',
                message: 'BugSeek is running smoothly. All systems operational.',
                duration: 3000
            });
        }, 2000);

        // Simulate periodic health checks
        setInterval(() => {
            if (Math.random() < 0.1) { // 10% chance
                this.show({
                    type: 'success',
                    title: 'Health Check',
                    message: 'All services are running normally.',
                    duration: 2000
                });
            }
        }, 30000); // Every 30 seconds
    }

    show(options) {
        const notification = this.createNotification(options);
        this.addToContainer(notification);
        this.scheduleRemoval(notification, options.duration || this.defaultDuration);
        return notification;
    }

    createNotification(options) {
        const {
            type = 'info',
            title = '',
            message = '',
            action = null,
            persistent = false,
            progress = false
        } = options;

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.setAttribute('data-id', Date.now().toString());

        const iconMap = {
            success: 'fas fa-check',
            error: 'fas fa-times',
            warning: 'fas fa-exclamation',
            info: 'fas fa-info'
        };

        let actionHtml = '';
        if (action) {
            actionHtml = `<button class="notification-action" onclick="${action.handler}">${action.text}</button>`;
        }

        let progressHtml = '';
        if (progress) {
            progressHtml = '<div class="notification-progress" style="width: 0%"></div>';
        }

        notification.innerHTML = `
            <div class="notification-icon">
                <i class="${iconMap[type]}"></i>
            </div>
            <div class="notification-content">
                ${title ? `<div class="notification-title">${title}</div>` : ''}
                <div class="notification-message">${message}</div>
                ${actionHtml}
            </div>
            ${!persistent ? '<button class="notification-close"><i class="fas fa-times"></i></button>' : ''}
            ${progressHtml}
        `;

        // Add close handler
        if (!persistent) {
            const closeBtn = notification.querySelector('.notification-close');
            closeBtn.addEventListener('click', () => {
                this.hide(notification);
            });
        }

        return notification;
    }

    addToContainer(notification) {
        this.container.appendChild(notification);
        
        // Trigger show animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 50);

        this.notifications.push(notification);

        // Remove oldest notifications if we exceed max
        while (this.notifications.length > this.maxNotifications) {
            const oldest = this.notifications.shift();
            this.hide(oldest);
        }
    }

    scheduleRemoval(notification, duration) {
        const progressBar = notification.querySelector('.notification-progress');
        
        if (progressBar) {
            // Animate progress bar
            progressBar.style.width = '100%';
            progressBar.style.transition = `width ${duration}ms linear`;
            
            setTimeout(() => {
                progressBar.style.width = '0%';
            }, 50);
        }

        setTimeout(() => {
            this.hide(notification);
        }, duration);
    }

    hide(notification) {
        notification.classList.add('hide');
        notification.classList.remove('show');

        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
            
            // Remove from notifications array
            const index = this.notifications.indexOf(notification);
            if (index > -1) {
                this.notifications.splice(index, 1);
            }
        }, 300);
    }

    success(message, title = 'Success', options = {}) {
        return this.show({
            type: 'success',
            title,
            message,
            ...options
        });
    }

    error(message, title = 'Error', options = {}) {
        return this.show({
            type: 'error',
            title,
            message,
            ...options
        });
    }

    warning(message, title = 'Warning', options = {}) {
        return this.show({
            type: 'warning',
            title,
            message,
            ...options
        });
    }

    info(message, title = 'Info', options = {}) {
        return this.show({
            type: 'info',
            title,
            message,
            ...options
        });
    }

    progress(message, title = 'Processing', options = {}) {
        return this.show({
            type: 'info',
            title,
            message,
            progress: true,
            persistent: true,
            ...options
        });
    }

    clear() {
        this.notifications.forEach(notification => {
            this.hide(notification);
        });
    }

    // System-specific notification methods
    errorUploaded(filename) {
        return this.success(
            `${filename} has been uploaded successfully`,
            'File Uploaded',
            { duration: 4000 }
        );
    }

    analysisStarted(reportId) {
        return this.info(
            `AI analysis has started for report ${reportId}`,
            'Analysis Started',
            { 
                duration: 3000,
                action: {
                    text: 'View Report',
                    handler: `window.location.href='/report/${reportId}'`
                }
            }
        );
    }

    solutionFound(reportId) {
        return this.success(
            `A potential solution has been found for this error`,
            'Solution Available',
            { 
                duration: 6000,
                action: {
                    text: 'View Solution',
                    handler: `window.location.href='/report/${reportId}#solutions'`
                }
            }
        );
    }

    systemAlert(message, severity = 'warning') {
        return this.show({
            type: severity,
            title: 'System Alert',
            message,
            duration: 8000,
            persistent: severity === 'error'
        });
    }

    apiConnectionLost() {
        return this.error(
            'Connection to the API server has been lost. Some features may not work properly.',
            'Connection Lost',
            { persistent: true }
        );
    }

    apiConnectionRestored() {
        return this.success(
            'Connection to the API server has been restored.',
            'Connection Restored',
            { duration: 3000 }
        );
    }
}

// Global notification system instance
window.notifications = new NotificationSystem();

// Convenience global functions
window.showNotification = (message, type = 'info', title = '', options = {}) => {
    return window.notifications.show({
        type,
        title,
        message,
        ...options
    });
};

window.showSuccess = (message, title = 'Success') => {
    return window.notifications.success(message, title);
};

window.showError = (message, title = 'Error') => {
    return window.notifications.error(message, title);
};

window.showWarning = (message, title = 'Warning') => {
    return window.notifications.warning(message, title);
};

window.showInfo = (message, title = 'Info') => {
    return window.notifications.info(message, title);
};

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // The NotificationSystem is already initialized above
    console.log('🔔 BugSeek Notification System initialized');
});

export default NotificationSystem;
