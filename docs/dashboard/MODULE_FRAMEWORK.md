# 📊 Dashboard Module Framework Documentation

## Tổng quan

Dashboard Module Framework là một hệ thống mở rộng cho phép tích hợp các module tùy chỉnh vào dashboard chính. Framework này cung cấp một kiến trúc linh hoạt và dễ sử dụng để phát triển các widget và module mới.

## 🏗️ Kiến trúc

### Core Components

1. **DashboardModuleFramework Class**: Class chính quản lý tất cả modules và widgets
2. **Module System**: Hệ thống đăng ký và quản lý modules
3. **Widget System**: Hệ thống tạo và render widgets
4. **Event Bus**: Hệ thống giao tiếp giữa các modules
5. **API Integration**: Tích hợp API cho external modules

### File Structure

```
static/js/dashboard/
├── module-framework.js    # Core framework
├── main.js               # Main dashboard logic
└── test-data.js          # Test data generator

static/css/dashboard/
├── main.css              # Main dashboard styles
└── module-framework.css  # Module framework styles
```

## 🚀 Sử dụng cơ bản

### 1. Khởi tạo Framework

```javascript
// Framework được tự động khởi tạo khi DOM ready
// Truy cập qua window.DashboardModuleFramework
const framework = window.DashboardModuleFramework;
```

### 2. Đăng ký Module

```javascript
// Đăng ký module mới
const module = framework.registerModule('myModule', {
    title: 'My Module',
    type: 'chart',
    description: 'Module mô tả',
    api: {
        getData: function() {
            return Promise.resolve({
                success: true,
                data: { /* your data */ }
            });
        }
    },
    permissions: ['dashboard.view']
});
```

### 3. Đăng ký Widget

```javascript
// Đăng ký widget cho module
const widget = framework.registerWidget('myModule', 'myWidget', {
    title: 'My Widget',
    type: 'chart',
    description: 'Widget mô tả'
});
```

### 4. Kích hoạt Module

```javascript
// Kích hoạt module
framework.activateModule('myModule');

// Render widget
const container = document.getElementById('widget-container');
framework.renderWidget('myModule', 'myWidget', container.id);
```

## 📋 API Reference

### DashboardModuleFramework Methods

#### `registerModule(moduleName, moduleConfig)`
Đăng ký module mới.

**Parameters:**
- `moduleName` (string): Tên module
- `moduleConfig` (object): Cấu hình module

**Module Config:**
```javascript
{
    title: 'Module Title',
    type: 'chart|table|metric|custom',
    description: 'Module description',
    api: {
        getData: function() { /* return Promise */ },
        // other API methods
    },
    permissions: ['permission1', 'permission2']
}
```

#### `registerWidget(moduleName, widgetName, widgetConfig)`
Đăng ký widget cho module.

**Parameters:**
- `moduleName` (string): Tên module
- `widgetName` (string): Tên widget
- `widgetConfig` (object): Cấu hình widget

#### `activateModule(moduleName)`
Kích hoạt module.

#### `deactivateModule(moduleName)`
Vô hiệu hóa module.

#### `renderWidget(moduleName, widgetName, containerId)`
Render widget vào container.

#### `hideWidget(moduleName, widgetName)`
Ẩn widget.

#### `showWidget(moduleName, widgetName)`
Hiển thị widget.

## 🎨 Widget Types

### 1. Chart Widget
```javascript
{
    type: 'chart',
    title: 'Chart Title',
    data: {
        labels: ['Label1', 'Label2'],
        datasets: [{
            label: 'Dataset',
            data: [10, 20],
            backgroundColor: 'rgba(102, 126, 234, 0.8)'
        }]
    }
}
```

### 2. Table Widget
```javascript
{
    type: 'table',
    title: 'Table Title',
    columns: ['Column1', 'Column2'],
    data: [
        { column1: 'Value1', column2: 'Value2' }
    ]
}
```

### 3. Metric Widget
```javascript
{
    type: 'metric',
    title: 'Metric Title',
    value: 100,
    label: 'Total',
    change: '+5%'
}
```

### 4. Custom Widget
```javascript
{
    type: 'custom',
    title: 'Custom Title',
    html: '<div>Custom HTML content</div>'
}
```

## 🔧 Event System

Framework sử dụng EventTarget để giao tiếp giữa các modules.

### Available Events

- `moduleRegistered`: Module được đăng ký
- `moduleActivated`: Module được kích hoạt
- `moduleDeactivated`: Module bị vô hiệu hóa
- `widgetRegistered`: Widget được đăng ký
- `widgetRendered`: Widget được render
- `widgetHidden`: Widget bị ẩn
- `widgetShown`: Widget được hiển thị
- `widgetRefresh`: Widget được refresh
- `widgetSettings`: Widget settings được mở
- `widgetExport`: Widget được export

### Listening to Events

```javascript
framework.eventBus.addEventListener('moduleRegistered', (event) => {
    console.log('Module registered:', event.detail);
});

framework.eventBus.addEventListener('widgetRefresh', (event) => {
    const { moduleName, widgetName, widget } = event.detail;
    // Handle widget refresh
});
```

## 🎯 Best Practices

### 1. Module Design
- Tạo modules có chức năng rõ ràng và độc lập
- Sử dụng API methods để tương tác với backend
- Implement proper error handling

### 2. Widget Development
- Tạo widgets responsive và accessible
- Sử dụng consistent styling với framework
- Implement loading states và error handling

### 3. Performance
- Lazy load data khi cần thiết
- Implement caching cho API calls
- Optimize rendering cho large datasets

### 4. Security
- Validate permissions trước khi render widgets
- Sanitize user input
- Implement proper authentication

## 📝 Examples

### Example 1: Sales Module

```javascript
// Register sales module
const salesModule = framework.registerModule('sales', {
    title: 'Sales Analytics',
    type: 'chart',
    description: 'Sales performance analytics',
    api: {
        getData: async function() {
            const response = await fetch('/api/sales/data');
            return response.json();
        }
    },
    permissions: ['dashboard.view', 'sales.view']
});

// Register sales widget
const salesWidget = framework.registerWidget('sales', 'salesChart', {
    title: 'Sales Performance',
    type: 'chart',
    description: 'Monthly sales performance'
});

// Activate and render
framework.activateModule('sales');
framework.renderWidget('sales', 'salesChart', 'sales-container');
```

### Example 2: HR Module

```javascript
// Register HR module
const hrModule = framework.registerModule('hr', {
    title: 'Human Resources',
    type: 'table',
    description: 'Employee management',
    api: {
        getEmployees: async function() {
            const response = await fetch('/api/hr/employees');
            return response.json();
        }
    },
    permissions: ['dashboard.view', 'hr.view']
});

// Register HR widget
const hrWidget = framework.registerWidget('hr', 'employeeTable', {
    title: 'Employee List',
    type: 'table',
    description: 'Current employees',
    columns: ['Name', 'Department', 'Role', 'Status']
});
```

## 🐛 Debugging

### Console Logging
Framework cung cấp detailed logging để debug:

```javascript
// Enable debug mode
localStorage.setItem('dashboardDebug', 'true');

// Check module status
console.log('Active modules:', framework.getActiveModules());
console.log('Rendered widgets:', framework.getRenderedWidgets());
```

### Common Issues

1. **Module not rendering**: Kiểm tra module đã được activate chưa
2. **Widget not showing**: Kiểm tra container ID có đúng không
3. **API errors**: Kiểm tra network tab và console errors
4. **Permission denied**: Kiểm tra user permissions

## 🔄 Migration Guide

### From v1 to v2
1. Update module registration syntax
2. Update widget configuration
3. Update event listeners
4. Test all functionality

### Breaking Changes
- Module config structure changed
- Widget rendering API updated
- Event names standardized

## 📞 Support

- **Documentation**: [docs/dashboard/](./)
- **Issues**: GitHub Issues
- **Email**: support@nov-reco.com

---

**Made with ❤️ by NOV-RECO Team**
