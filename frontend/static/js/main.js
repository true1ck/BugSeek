/**
 * BugSeek Main JavaScript
 * =======================
 * 
 * Core functionality and utilities for the BugSeek application.
 * Enhanced with mobile support and notification system integration.
 */

// Global app configuration
const BugSeekApp = {
    config: {
        apiEndpoint: '/api',
        uploadEndpoint: '/api/upload',
        maxFileSize: 50 * 1024 * 1024, // 50MB
        allowedExtensions: ['.log', '.txt', '.json', '.xml'],
        isMobile: window.innerWidth <= 768,
        isTouch: 'ontouchstart' in window
    },
    
    init() {
        this.detectDevice();
        this.setupEventListeners();
        this.initializeComponents();
        this.handleFlashMessages();
        this.initializeMobileEnhancements();
        this.connectNotificationSystem();
    },
    
    detectDevice() {
        this.config.isMobile = window.innerWidth <= 768;
        this.config.isTouch = 'ontouchstart' in window;
        
        // Update on resize
        window.addEventListener('resize', () => {
            const wasMobile = this.config.isMobile;
            this.config.isMobile = window.innerWidth <= 768;
            
            if (wasMobile !== this.config.isMobile) {
                this.handleDeviceChange();
            }
        });
    },
    
    handleDeviceChange() {
        // Reinitialize mobile-specific features
        if (this.config.isMobile) {
            this.initializeMobileEnhancements();
        } else {
            this.cleanupMobileEnhancements();
        }
    },
    
    initializeMobileEnhancements() {
        if (!this.config.isMobile) return;
        
        // Add mobile-specific classes
        document.body.classList.add('mobile-device');
        
        // Initialize mobile touch gestures
        this.initializeTouchGestures();
        
        // Initialize mobile table stacking
        this.initializeMobileTableStacking();
        
        // Initialize mobile search enhancements
        this.initializeMobileSearch();
        
        // Initialize mobile form enhancements
        this.initializeMobileFormEnhancements();
    },
    
    cleanupMobileEnhancements() {
        document.body.classList.remove('mobile-device');
        // Cleanup mobile-specific event listeners and modifications
    },
    
    initializeTouchGestures() {
        let startY = 0;
        let startX = 0;
        
        document.addEventListener('touchstart', (e) => {
            startY = e.touches[0].clientY;
            startX = e.touches[0].clientX;
        }, { passive: true });
        
        document.addEventListener('touchmove', (e) => {
            // Prevent bounce scrolling on iOS
            if (e.target === document.body) {
                e.preventDefault();
            }
        }, { passive: false });
    },
    
    initializeMobileTableStacking() {
        const tables = document.querySelectorAll('table:not(.no-mobile-stack)');
        
        tables.forEach(table => {
            if (this.config.isMobile) {
                this.stackTable(table);
            }
        });
    },
    
    stackTable(table) {
        const wrapper = table.closest('.table-container');
        if (wrapper && !wrapper.classList.contains('table-responsive-stack')) {
            wrapper.classList.add('table-responsive-stack');
            
            // Add data labels for mobile stacking
            const headers = table.querySelectorAll('th');
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                cells.forEach((cell, index) => {
                    if (headers[index]) {
                        cell.setAttribute('data-label', headers[index].textContent);
                    }
                });
            });
        }
    },
    
    initializeMobileSearch() {
        const searchInputs = document.querySelectorAll('input[type="search"], .search-input');
        
        searchInputs.forEach(input => {
            // Add clear button for mobile
            if (this.config.isMobile) {
                this.addMobileClearButton(input);
            }
            
            // Enhanced search experience
            input.addEventListener('focus', () => {
                if (this.config.isMobile) {
                    // Scroll input into view
                    setTimeout(() => {
                        input.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 300);
                }
            });
        });
    },
    
    addMobileClearButton(input) {
        if (input.nextElementSibling?.classList.contains('mobile-clear-btn')) return;
        
        const clearBtn = document.createElement('button');
        clearBtn.className = 'mobile-clear-btn';
        clearBtn.type = 'button';
        clearBtn.innerHTML = '<i class="fas fa-times"></i>';
        clearBtn.style.cssText = `
            position: absolute;
            right: 8px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: #9ca3af;
            cursor: pointer;
            padding: 4px;
            display: none;
        `;
        
        const wrapper = input.parentNode;
        wrapper.style.position = 'relative';
        wrapper.appendChild(clearBtn);
        
        input.addEventListener('input', () => {
            clearBtn.style.display = input.value ? 'block' : 'none';
        });
        
        clearBtn.addEventListener('click', () => {
            input.value = '';
            input.focus();
            clearBtn.style.display = 'none';
            input.dispatchEvent(new Event('input', { bubbles: true }));
        });
    },
    
    initializeMobileFormEnhancements() {
        // Enhance form validation for mobile
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');
            
            inputs.forEach(input => {
                // Add mobile-friendly validation
                input.addEventListener('invalid', (e) => {
                    e.preventDefault();
                    this.showMobileValidationError(input);
                });
                
                // Clear validation on input
                input.addEventListener('input', () => {
                    this.clearMobileValidationError(input);
                });
            });
        });
    },
    
    showMobileValidationError(input) {
        const errorMsg = input.validationMessage;
        if (!errorMsg) return;
        
        // Remove existing error
        this.clearMobileValidationError(input);
        
        const errorElement = document.createElement('div');
        errorElement.className = 'mobile-validation-error';
        errorElement.textContent = errorMsg;
        errorElement.style.cssText = `
            color: #ef4444;
            font-size: 0.8rem;
            margin-top: 0.25rem;
            animation: fadeInUp 0.3s ease;
        `;
        
        input.parentNode.appendChild(errorElement);
        input.classList.add('error');
        
        // Use notification system if available
        if (window.notifications) {
            window.notifications.error(errorMsg, 'Validation Error');
        }
    },
    
    clearMobileValidationError(input) {
        const errorElement = input.parentNode.querySelector('.mobile-validation-error');
        if (errorElement) {
            errorElement.remove();
        }
        input.classList.remove('error');
    },
    
    connectNotificationSystem() {
        // Override the simple toast system with the notification system if available
        if (window.notifications) {
            this.showToast = (message, type = 'info', title = '') => {
                return window.notifications.show({
                    type,
                    title,
                    message
                });
            };
            
            this.showSuccess = (message, title = 'Success') => {
                return window.notifications.success(message, title);
            };
            
            this.showError = (message, title = 'Error') => {
                return window.notifications.error(message, title);
            };
            
            this.showWarning = (message, title = 'Warning') => {
                return window.notifications.warning(message, title);
            };
            
            this.showInfo = (message, title = 'Info') => {
                return window.notifications.info(message, title);
            };
        }
    },
    
    setupEventListeners() {
        // Global click handler for dynamic content
        document.addEventListener('click', this.handleGlobalClicks.bind(this));
        
        // Handle form submissions
        document.addEventListener('submit', this.handleFormSubmissions.bind(this));
        
        // Handle drag and drop globally
        this.setupDragAndDrop();
        
        // Handle mobile-specific events
        if (this.config.isMobile) {
            this.setupMobileEventListeners();
        }
    },
    
    setupMobileEventListeners() {
        // Handle orientation change
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.handleOrientationChange();
            }, 100);
        });
        
        // Handle viewport changes (keyboard show/hide)
        let initialViewportHeight = window.innerHeight;
        
        window.addEventListener('resize', () => {
            const currentHeight = window.innerHeight;
            const heightDifference = initialViewportHeight - currentHeight;
            
            if (heightDifference > 150) {
                // Keyboard likely opened
                document.body.classList.add('keyboard-open');
            } else {
                // Keyboard likely closed
                document.body.classList.remove('keyboard-open');
            }
        });
    },
    
    handleOrientationChange() {
        // Recalculate layouts after orientation change
        this.initializeMobileTableStacking();
        
        // Scroll to focused element
        const activeElement = document.activeElement;
        if (activeElement && activeElement.tagName !== 'BODY') {
            setTimeout(() => {
                activeElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 300);
        }
    },
    
    initializeComponents() {
        // Initialize tooltips
        this.initializeTooltips();
        
        // Initialize modals
        this.initializeModals();
        
        // Initialize charts if Chart.js is available
        if (typeof Chart !== 'undefined') {
            this.initializeCharts();
        }
        
        // Initialize progressive web app features
        this.initializePWAFeatures();
    },
    
    initializePWAFeatures() {
        // Service Worker registration
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .catch(error => {
                    console.log('ServiceWorker registration failed: ', error);
                });
        }
        
        // Handle install prompt
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            
            // Show custom install button or notification
            if (window.notifications) {
                window.notifications.info(
                    'Install BugSeek for a better experience!',
                    'Install App',
                    {
                        duration: 8000,
                        action: {
                            text: 'Install',
                            handler: 'BugSeekApp.installPWA()'
                        }
                    }
                );
            }
        });
        
        this.deferredPrompt = deferredPrompt;
    },
    
    installPWA() {
        if (this.deferredPrompt) {
            this.deferredPrompt.prompt();
            
            this.deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    this.showSuccess('App installed successfully!');
                }
                this.deferredPrompt = null;
            });
        }
    },
    
    handleFlashMessages() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            // Convert flash messages to notification system if available
            if (window.notifications) {
                const isSuccess = alert.classList.contains('alert-success');
                const isError = alert.classList.contains('alert-error');
                const message = alert.textContent.trim();
                
                if (isSuccess) {
                    window.notifications.success(message);
                } else if (isError) {
                    window.notifications.error(message);
                } else {
                    window.notifications.info(message);
                }
                
                alert.remove();
            } else {
                // Fallback: Auto-hide alerts after 5 seconds
                setTimeout(() => {
                    alert.style.opacity = '0';
                    setTimeout(() => {
                        alert.remove();
                    }, 300);
                }, 5000);
            }
        });
    },
    
    handleGlobalClicks(event) {
        const target = event.target;
        
        // Handle copy buttons
        if (target.matches('.copy-btn') || target.closest('.copy-btn')) {
            this.handleCopyClick(target.closest('.copy-btn'));
        }
        
        // Handle delete buttons
        if (target.matches('.delete-btn') || target.closest('.delete-btn')) {
            this.handleDeleteClick(target.closest('.delete-btn'));
        }
        
        // Handle view buttons
        if (target.matches('.view-btn') || target.closest('.view-btn')) {
            this.handleViewClick(target.closest('.view-btn'));
        }
        
        // Handle mobile filter toggles
        if (target.matches('.filters-toggle') || target.closest('.filters-toggle')) {
            this.handleFilterToggle(target.closest('.filters-toggle'));
        }
        
        // Handle mobile view toggles
        if (target.matches('.view-toggle button')) {
            this.handleViewToggle(target);
        }
    },
    
    handleFilterToggle(button) {
        const panel = document.querySelector('.filters-panel');
        const icon = button.querySelector('i');
        
        if (panel) {
            panel.classList.toggle('show');
            
            if (icon) {
                icon.classList.toggle('fa-chevron-down');
                icon.classList.toggle('fa-chevron-up');
            }
        }
    },
    
    handleViewToggle(button) {
        const toggles = button.parentNode.querySelectorAll('button');
        const resultsContainer = document.querySelector('.search-results');
        
        toggles.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        if (resultsContainer) {
            resultsContainer.className = 'search-results ' + button.dataset.view + '-view';
        }
    },
    
    handleCopyClick(button) {
        const target = button.dataset.target;
        const element = document.querySelector(target);
        
        if (element) {
            const text = element.textContent || element.value;
            
            if (navigator.clipboard) {
                navigator.clipboard.writeText(text).then(() => {
                    this.showSuccess('Copied to clipboard!');
                }).catch(() => {
                    this.fallbackCopyTextToClipboard(text);
                });
            } else {
                this.fallbackCopyTextToClipboard(text);
            }
        }
    },
    
    fallbackCopyTextToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            const successful = document.execCommand('copy');
            if (successful) {
                this.showSuccess('Copied to clipboard!');
            } else {
                this.showError('Failed to copy to clipboard');
            }
        } catch (err) {
            this.showError('Failed to copy to clipboard');
        }
        
        document.body.removeChild(textArea);
    },
    
    handleDeleteClick(button) {
        const confirmMessage = button.dataset.confirm || 'Are you sure you want to delete this item?';
        
        if (confirm(confirmMessage)) {
            const url = button.dataset.url;
            if (url) {
                this.makeRequest(url, { method: 'DELETE' })
                    .then(response => {
                        if (response.success) {
                            this.showSuccess('Item deleted successfully');
                            // Remove the item from DOM or reload page
                            const itemElement = button.closest('.item, tr, .card');
                            if (itemElement) {
                                itemElement.style.animation = 'fadeOut 0.3s ease';
                                setTimeout(() => {
                                    itemElement.remove();
                                }, 300);
                            }
                        } else {
                            this.showError(response.message || 'Failed to delete item');
                        }
                    })
                    .catch(() => {
                        this.showError('Failed to delete item');
                    });
            }
        }
    },
    
    handleViewClick(button) {
        const url = button.dataset.url;
        if (url) {
            // Show loading state on mobile
            if (this.config.isMobile) {
                button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            }
            window.location.href = url;
        }
    },
    
    handleFormSubmissions(event) {
        const form = event.target;
        
        // Handle upload forms
        if (form.matches('.upload-form')) {
            this.handleUploadForm(form, event);
        }
        
        // Handle search forms
        if (form.matches('.search-form')) {
            this.handleSearchForm(form, event);
        }
        
        // Add mobile loading states
        if (this.config.isMobile) {
            const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitButton) {
                const originalText = submitButton.textContent || submitButton.value;
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                
                // Re-enable after a delay (fallback)
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.textContent = originalText;
                }, 10000);
            }
        }
    },
    
    setupDragAndDrop() {
        const dropZones = document.querySelectorAll('.upload-zone, .drop-zone');
        
        dropZones.forEach(zone => {
            // Enhanced drag and drop for mobile
            const events = this.config.isTouch 
                ? ['touchstart', 'touchmove', 'touchend']
                : ['dragover', 'dragleave', 'drop'];
            
            if (!this.config.isTouch) {
                zone.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    zone.classList.add('dragover');
                });
                
                zone.addEventListener('dragleave', (e) => {
                    e.preventDefault();
                    zone.classList.remove('dragover');
                });
                
                zone.addEventListener('drop', (e) => {
                    e.preventDefault();
                    zone.classList.remove('dragover');
                    this.handleFileDrop(e.dataTransfer.files, zone);
                });
            }
            
            // Add click handler for mobile file selection
            zone.addEventListener('click', () => {
                const fileInput = zone.querySelector('input[type="file"]') || this.createFileInput();
                fileInput.click();
            });
        });
    },
    
    createFileInput() {
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        input.accept = this.config.allowedExtensions.join(',');
        input.style.display = 'none';
        
        input.addEventListener('change', (e) => {
            this.handleFileDrop(e.target.files);
        });
        
        document.body.appendChild(input);
        return input;
    },
    
    handleUploadForm(form, event) {
        event.preventDefault();
        
        const formData = new FormData(form);
        const files = formData.getAll('file');
        
        // Validate files
        for (let file of files) {
            if (!this.validateFile(file)) {
                return;
            }
        }
        
        this.uploadFiles(formData, form);
    },
    
    handleSearchForm(form, event) {
        const query = form.querySelector('input[name="query"]')?.value;
        
        if (!query || query.trim().length < 2) {
            event.preventDefault();
            this.showWarning('Please enter at least 2 characters to search');
        }
    },
    
    validateFile(file) {
        // Check file size
        if (file.size > this.config.maxFileSize) {
            this.showError(`File "${file.name}" is too large. Maximum size is 50MB.`, 'File Too Large');
            return false;
        }
        
        // Check file extension
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        if (!this.config.allowedExtensions.includes(extension)) {
            this.showError(
                `File "${file.name}" has an unsupported format. Allowed: ${this.config.allowedExtensions.join(', ')}`,
                'Unsupported File Format'
            );
            return false;
        }
        
        return true;
    },
    
    handleFileDrop(files, zone) {
        const fileArray = Array.from(files);
        
        if (fileArray.length === 0) {
            this.showWarning('No files selected');
            return;
        }
        
        // Validate all files
        for (let file of fileArray) {
            if (!this.validateFile(file)) {
                return;
            }
        }
        
        // Show files being processed
        if (window.notifications) {
            fileArray.forEach(file => {
                window.notifications.info(
                    `Processing ${file.name} (${this.formatFileSize(file.size)})`,
                    'File Added'
                );
            });
        }
        
        // Create FormData and upload
        const formData = new FormData();
        fileArray.forEach(file => {
            formData.append('file', file);
        });
        
        this.uploadFiles(formData);
    },
    
    uploadFiles(formData, form = null) {
        const files = formData.getAll('file');
        
        // Show upload progress notification
        let progressNotification;
        if (window.notifications) {
            progressNotification = window.notifications.progress(
                `Uploading ${files.length} file${files.length > 1 ? 's' : ''}...`,
                'Upload in Progress'
            );
        }
        
        this.makeRequest(this.config.uploadEndpoint, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (progressNotification) {
                window.notifications.hide(progressNotification);
            }
            
            if (response.success) {
                // Show success for each file
                files.forEach(file => {
                    if (window.notifications) {
                        window.notifications.errorUploaded(file.name);
                    }
                });
                
                this.showSuccess(`${files.length} file${files.length > 1 ? 's' : ''} uploaded successfully!`);
                
                // Redirect after a short delay
                setTimeout(() => {
                    window.location.href = response.redirect || '/logs';
                }, 1500);
            } else {
                this.showError(response.message || 'Upload failed');
            }
        })
        .catch(error => {
            if (progressNotification) {
                window.notifications.hide(progressNotification);
            }
            this.showError('Upload failed: ' + error.message);
        });
    },
    
    makeRequest(url, options = {}) {
        const defaults = {
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        // Don't set Content-Type for FormData
        if (options.body instanceof FormData) {
            delete defaults.headers['Content-Type'];
        }
        
        const config = { ...defaults, ...options };
        
        return fetch(url, config)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .catch(error => {
                // Network error handling
                if (!navigator.onLine) {
                    throw new Error('No internet connection');
                }
                throw error;
            });
    },
    
    showToast(message, type = 'info', title = '') {
        // Fallback toast implementation if notification system isn't available
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                ${title ? `<div class="toast-title">${title}</div>` : ''}
                <div class="toast-message">${message}</div>
            </div>
        `;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#3b82f6'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
            z-index: 10000;
            transform: translateX(100%);
            opacity: 0;
            transition: all 0.3s ease;
            max-width: 400px;
        `;
        
        document.body.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
            toast.style.opacity = '1';
        }, 100);
        
        // Remove after delay
        setTimeout(() => {
            toast.style.transform = 'translateX(100%)';
            toast.style.opacity = '0';
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, type === 'error' ? 6000 : 3000);
        
        return toast;
    },
    
    // Convenience methods
    showSuccess(message, title = 'Success') {
        return this.showToast(message, 'success', title);
    },
    
    showError(message, title = 'Error') {
        return this.showToast(message, 'error', title);
    },
    
    showWarning(message, title = 'Warning') {
        return this.showToast(message, 'warning', title);
    },
    
    showInfo(message, title = 'Info') {
        return this.showToast(message, 'info', title);
    },
    
    initializeTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        tooltipElements.forEach(element => {
            if (this.config.isTouch) {
                // Use tap for touch devices
                element.addEventListener('touchstart', this.showTooltip.bind(this));
                element.addEventListener('touchend', () => {
                    setTimeout(() => this.hideTooltip.bind(this), 2000);
                });
            } else {
                element.addEventListener('mouseenter', this.showTooltip.bind(this));
                element.addEventListener('mouseleave', this.hideTooltip.bind(this));
            }
        });
    },
    
    showTooltip(event) {
        const element = event.target;
        const text = element.dataset.tooltip;
        
        if (!text) return;
        
        // Remove existing tooltip
        this.hideTooltip(event);
        
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = text;
        tooltip.style.cssText = `
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            z-index: 10000;
            pointer-events: none;
            white-space: nowrap;
            max-width: 200px;
            white-space: normal;
        `;
        
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        
        let left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
        let top = rect.top - tooltipRect.height - 8;
        
        // Adjust if tooltip goes off screen
        if (left < 0) left = 8;
        if (left + tooltipRect.width > window.innerWidth) {
            left = window.innerWidth - tooltipRect.width - 8;
        }
        if (top < 0) {
            top = rect.bottom + 8;
        }
        
        tooltip.style.left = left + 'px';
        tooltip.style.top = top + 'px';
        
        element._tooltip = tooltip;
    },
    
    hideTooltip(event) {
        const element = event.target;
        if (element._tooltip) {
            element._tooltip.remove();
            delete element._tooltip;
        }
    },
    
    initializeModals() {
        const modalTriggers = document.querySelectorAll('[data-modal]');
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', this.showModal.bind(this));
        });
        
        // Close modals on background click
        document.addEventListener('click', (event) => {
            if (event.target.matches('.modal-backdrop')) {
                this.hideModal();
            }
        });
        
        // Close modals on escape key
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                this.hideModal();
            }
        });
    },
    
    showModal(event) {
        const trigger = event.target.closest('[data-modal]');
        const modalId = trigger.dataset.modal;
        const modal = document.getElementById(modalId);
        
        if (modal) {
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden';
            
            // Add mobile-specific handling
            if (this.config.isMobile) {
                modal.classList.add('mobile-modal');
            }
        }
    },
    
    hideModal() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.style.display = 'none';
            modal.classList.remove('mobile-modal');
        });
        document.body.style.overflow = '';
    },
    
    initializeCharts() {
        if (typeof Chart === 'undefined') return;
        
        // Enhanced chart configuration for mobile
        Chart.defaults.font.family = 'Inter, sans-serif';
        Chart.defaults.color = '#6b7280';
        Chart.defaults.responsive = true;
        Chart.defaults.maintainAspectRatio = false;
        
        // Mobile-specific chart options
        if (this.config.isMobile) {
            Chart.defaults.plugins.legend.position = 'bottom';
            Chart.defaults.plugins.legend.labels.usePointStyle = true;
            Chart.defaults.plugins.legend.labels.padding = 20;
        }
    },
    
    // Utility functions
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    formatDate(dateString) {
        const date = new Date(dateString);
        const options = this.config.isMobile 
            ? { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }
            : { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
        return date.toLocaleDateString(undefined, options);
    },
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    // Network status handling
    initializeNetworkHandling() {
        window.addEventListener('online', () => {
            if (window.notifications) {
                window.notifications.apiConnectionRestored();
            }
        });
        
        window.addEventListener('offline', () => {
            if (window.notifications) {
                window.notifications.apiConnectionLost();
            }
        });
    }
};

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    BugSeekApp.init();
    BugSeekApp.initializeNetworkHandling();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BugSeekApp;
} else {
    window.BugSeekApp = BugSeekApp;
}
