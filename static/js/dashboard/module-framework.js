// Dashboard Module Integration Framework
// This framework allows external modules to integrate with the dashboard

class DashboardModuleFramework {
    constructor() {
        this.modules = new Map();
        this.widgets = new Map();
        this.eventBus = new EventTarget();
        this.isInitialized = false;
    }

    // Initialize the framework
    init() {
        if (this.isInitialized) return;
        
        console.log('Dashboard Module Framework initialized');
        this.setupEventListeners();
        this.loadRegisteredModules();
        this.isInitialized = true;
    }

    // Register a new module
    registerModule(moduleName, moduleConfig) {
        const module = {
            name: moduleName,
            config: moduleConfig,
            widgets: [],
            api: moduleConfig.api || {},
            permissions: moduleConfig.permissions || [],
            isActive: false
        };

        this.modules.set(moduleName, module);
        console.log(`Module registered: ${moduleName}`);
        
        // Emit module registered event
        this.eventBus.dispatchEvent(new CustomEvent('moduleRegistered', {
            detail: { moduleName, module }
        }));

        return module;
    }

    // Register a widget for a module
    registerWidget(moduleName, widgetName, widgetConfig) {
        const module = this.modules.get(moduleName);
        if (!module) {
            console.error(`Module ${moduleName} not found`);
            return null;
        }

        const widget = {
            name: widgetName,
            module: moduleName,
            config: widgetConfig,
            element: null,
            isRendered: false
        };

        module.widgets.push(widget);
        this.widgets.set(`${moduleName}:${widgetName}`, widget);
        
        console.log(`Widget registered: ${moduleName}:${widgetName}`);
        
        // Emit widget registered event
        this.eventBus.dispatchEvent(new CustomEvent('widgetRegistered', {
            detail: { moduleName, widgetName, widget }
        }));

        return widget;
    }

    // Activate a module
    activateModule(moduleName) {
        const module = this.modules.get(moduleName);
        if (!module) {
            console.error(`Module ${moduleName} not found`);
            return false;
        }

        module.isActive = true;
        console.log(`Module activated: ${moduleName}`);
        
        // Emit module activated event
        this.eventBus.dispatchEvent(new CustomEvent('moduleActivated', {
            detail: { moduleName, module }
        }));

        return true;
    }

    // Deactivate a module
    deactivateModule(moduleName) {
        const module = this.modules.get(moduleName);
        if (!module) {
            console.error(`Module ${moduleName} not found`);
            return false;
        }

        module.isActive = false;
        
        // Hide all widgets from this module
        module.widgets.forEach(widget => {
            this.hideWidget(moduleName, widget.name);
        });

        console.log(`Module deactivated: ${moduleName}`);
        
        // Emit module deactivated event
        this.eventBus.dispatchEvent(new CustomEvent('moduleDeactivated', {
            detail: { moduleName, module }
        }));

        return true;
    }

    // Render a widget
    renderWidget(moduleName, widgetName, containerId) {
        const widget = this.widgets.get(`${moduleName}:${widgetName}`);
        if (!widget) {
            console.error(`Widget ${moduleName}:${widgetName} not found`);
            return null;
        }

        const module = this.modules.get(moduleName);
        if (!module || !module.isActive) {
            console.error(`Module ${moduleName} is not active`);
            return null;
        }

        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return null;
        }

        // Create widget element
        const widgetElement = this.createWidgetElement(widget);
        container.appendChild(widgetElement);
        
        widget.element = widgetElement;
        widget.isRendered = true;

        console.log(`Widget rendered: ${moduleName}:${widgetName}`);
        
        // Emit widget rendered event
        this.eventBus.dispatchEvent(new CustomEvent('widgetRendered', {
            detail: { moduleName, widgetName, widget, containerId }
        }));

        return widgetElement;
    }

    // Hide a widget
    hideWidget(moduleName, widgetName) {
        const widget = this.widgets.get(`${moduleName}:${widgetName}`);
        if (!widget || !widget.element) return false;

        widget.element.style.display = 'none';
        widget.isRendered = false;

        console.log(`Widget hidden: ${moduleName}:${widgetName}`);
        
        // Emit widget hidden event
        this.eventBus.dispatchEvent(new CustomEvent('widgetHidden', {
            detail: { moduleName, widgetName, widget }
        }));

        return true;
    }

    // Show a widget
    showWidget(moduleName, widgetName) {
        const widget = this.widgets.get(`${moduleName}:${widgetName}`);
        if (!widget || !widget.element) return false;

        widget.element.style.display = 'block';
        widget.isRendered = true;

        console.log(`Widget shown: ${moduleName}:${widgetName}`);
        
        // Emit widget shown event
        this.eventBus.dispatchEvent(new CustomEvent('widgetShown', {
            detail: { moduleName, widgetName, widget }
        }));

        return true;
    }

    // Create widget element
    createWidgetElement(widget) {
        const element = document.createElement('div');
        element.className = `dashboard-widget widget-${widget.module}-${widget.name}`;
        element.setAttribute('data-module', widget.module);
        element.setAttribute('data-widget', widget.name);

        // Add widget content based on type
        switch (widget.config.type) {
            case 'chart':
                element.innerHTML = this.createChartWidget(widget);
                break;
            case 'table':
                element.innerHTML = this.createTableWidget(widget);
                break;
            case 'metric':
                element.innerHTML = this.createMetricWidget(widget);
                break;
            case 'custom':
                element.innerHTML = widget.config.html || '';
                break;
            default:
                element.innerHTML = this.createDefaultWidget(widget);
        }

        return element;
    }

    // Create chart widget
    createChartWidget(widget) {
        return `
            <div class="widget-header">
                <h4>${widget.config.title || widget.name}</h4>
                <div class="widget-actions">
                    <button class="widget-refresh" data-widget="${widget.module}:${widget.name}">
                        <i class="fas fa-sync-alt"></i>
                    </button>
                    <button class="widget-settings" data-widget="${widget.module}:${widget.name}">
                        <i class="fas fa-cog"></i>
                    </button>
                </div>
            </div>
            <div class="widget-content">
                <canvas id="widget-${widget.module}-${widget.name}-chart" width="400" height="200"></canvas>
            </div>
        `;
    }

    // Create table widget
    createTableWidget(widget) {
        return `
            <div class="widget-header">
                <h4>${widget.config.title || widget.name}</h4>
                <div class="widget-actions">
                    <button class="widget-refresh" data-widget="${widget.module}:${widget.name}">
                        <i class="fas fa-sync-alt"></i>
                    </button>
                    <button class="widget-export" data-widget="${widget.module}:${widget.name}">
                        <i class="fas fa-download"></i>
                    </button>
                </div>
            </div>
            <div class="widget-content">
                <div class="widget-table-container">
                    <table class="widget-table">
                        <thead>
                            <tr>
                                ${widget.config.columns ? widget.config.columns.map(col => `<th>${col}</th>`).join('') : ''}
                            </tr>
                        </thead>
                        <tbody id="widget-${widget.module}-${widget.name}-table-body">
                            <!-- Data will be loaded here -->
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    // Create metric widget
    createMetricWidget(widget) {
        return `
            <div class="widget-header">
                <h4>${widget.config.title || widget.name}</h4>
                <div class="widget-actions">
                    <button class="widget-refresh" data-widget="${widget.module}:${widget.name}">
                        <i class="fas fa-sync-alt"></i>
                    </button>
                </div>
            </div>
            <div class="widget-content">
                <div class="widget-metric">
                    <div class="metric-value" id="widget-${widget.module}-${widget.name}-value">
                        ${widget.config.value || '0'}
                    </div>
                    <div class="metric-label">
                        ${widget.config.label || widget.name}
                    </div>
                    <div class="metric-change" id="widget-${widget.module}-${widget.name}-change">
                        ${widget.config.change || ''}
                    </div>
                </div>
            </div>
        `;
    }

    // Create default widget
    createDefaultWidget(widget) {
        return `
            <div class="widget-header">
                <h4>${widget.config.title || widget.name}</h4>
                <div class="widget-actions">
                    <button class="widget-refresh" data-widget="${widget.module}:${widget.name}">
                        <i class="fas fa-sync-alt"></i>
                    </button>
                </div>
            </div>
            <div class="widget-content">
                <div class="widget-placeholder">
                    <i class="fas fa-puzzle-piece"></i>
                    <p>Widget: ${widget.name}</p>
                    <small>Module: ${widget.module}</small>
                </div>
            </div>
        `;
    }

    // Setup event listeners
    setupEventListeners() {
        // Listen for widget actions
        document.addEventListener('click', (e) => {
            if (e.target.closest('.widget-refresh')) {
                const widgetId = e.target.closest('.widget-refresh').dataset.widget;
                this.refreshWidget(widgetId);
            }
            
            if (e.target.closest('.widget-settings')) {
                const widgetId = e.target.closest('.widget-settings').dataset.widget;
                this.showWidgetSettings(widgetId);
            }
            
            if (e.target.closest('.widget-export')) {
                const widgetId = e.target.closest('.widget-export').dataset.widget;
                this.exportWidget(widgetId);
            }
        });
    }

    // Refresh a widget
    refreshWidget(widgetId) {
        const [moduleName, widgetName] = widgetId.split(':');
        const widget = this.widgets.get(widgetId);
        
        if (!widget) return false;

        console.log(`Refreshing widget: ${widgetId}`);
        
        // Emit widget refresh event
        this.eventBus.dispatchEvent(new CustomEvent('widgetRefresh', {
            detail: { moduleName, widgetName, widget }
        }));

        return true;
    }

    // Show widget settings
    showWidgetSettings(widgetId) {
        const [moduleName, widgetName] = widgetId.split(':');
        const widget = this.widgets.get(widgetId);
        
        if (!widget) return false;

        console.log(`Showing settings for widget: ${widgetId}`);
        
        // Emit widget settings event
        this.eventBus.dispatchEvent(new CustomEvent('widgetSettings', {
            detail: { moduleName, widgetName, widget }
        }));

        return true;
    }

    // Export widget data
    exportWidget(widgetId) {
        const [moduleName, widgetName] = widgetId.split(':');
        const widget = this.widgets.get(widgetId);
        
        if (!widget) return false;

        console.log(`Exporting widget: ${widgetId}`);
        
        // Emit widget export event
        this.eventBus.dispatchEvent(new CustomEvent('widgetExport', {
            detail: { moduleName, widgetName, widget }
        }));

        return true;
    }

    // Load registered modules from localStorage
    loadRegisteredModules() {
        const savedModules = JSON.parse(localStorage.getItem('dashboardModules') || '{}');
        
        Object.entries(savedModules).forEach(([moduleName, moduleData]) => {
            this.registerModule(moduleName, moduleData.config);
            if (moduleData.isActive) {
                this.activateModule(moduleName);
            }
        });
    }

    // Save modules to localStorage
    saveModules() {
        const modulesData = {};
        
        this.modules.forEach((module, moduleName) => {
            modulesData[moduleName] = {
                config: module.config,
                isActive: module.isActive
            };
        });
        
        localStorage.setItem('dashboardModules', JSON.stringify(modulesData));
    }

    // Get module API
    getModuleAPI(moduleName) {
        const module = this.modules.get(moduleName);
        return module ? module.api : null;
    }

    // Call module API method
    callModuleAPI(moduleName, method, ...args) {
        const api = this.getModuleAPI(moduleName);
        if (!api || !api[method]) {
            console.error(`API method ${method} not found for module ${moduleName}`);
            return null;
        }

        return api[method](...args);
    }

    // Get all active modules
    getActiveModules() {
        return Array.from(this.modules.values()).filter(module => module.isActive);
    }

    // Get all widgets for a module
    getModuleWidgets(moduleName) {
        const module = this.modules.get(moduleName);
        return module ? module.widgets : [];
    }

    // Get all rendered widgets
    getRenderedWidgets() {
        return Array.from(this.widgets.values()).filter(widget => widget.isRendered);
    }
}

// Create global instance
window.DashboardModuleFramework = new DashboardModuleFramework();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.DashboardModuleFramework.init();
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardModuleFramework;
}
