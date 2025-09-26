// Dashboard Test Data Generator
// This file provides comprehensive test data for all dashboard modules

class DashboardTestData {
    constructor() {
        this.users = this.generateUsers();
        this.departments = this.generateDepartments();
        this.offices = this.generateOffices();
        this.checkins = this.generateCheckins();
        this.absences = this.generateAbsences();
        this.notifications = this.generateNotifications();
        this.areas = this.generateAreas();
    }

    // Generate sample users
    generateUsers() {
        return [
            {
                id: 1,
                username: 'admin',
                full_name: 'Nguyễn Văn Admin',
                email: 'admin@nov-reco.com',
                role: 'admin',
                department: 'IT',
                office: 'Hà Nội',
                is_active: true,
                last_login: '2024-01-15 08:30:00'
            },
            {
                id: 2,
                username: 'manager1',
                full_name: 'Trần Thị Manager',
                email: 'manager@nov-reco.com',
                role: 'manager',
                department: 'Kinh doanh',
                office: 'Hà Nội',
                is_active: true,
                last_login: '2024-01-15 09:15:00'
            },
            {
                id: 3,
                username: 'employee1',
                full_name: 'Lê Văn Employee',
                email: 'employee@nov-reco.com',
                role: 'employee',
                department: 'Kỹ thuật',
                office: 'TP.HCM',
                is_active: true,
                last_login: '2024-01-15 08:45:00'
            },
            {
                id: 4,
                username: 'hr1',
                full_name: 'Phạm Thị HR',
                email: 'hr@nov-reco.com',
                role: 'hcns',
                department: 'Nhân sự',
                office: 'Hà Nội',
                is_active: true,
                last_login: '2024-01-15 09:00:00'
            },
            {
                id: 5,
                username: 'secretary1',
                full_name: 'Hoàng Thị Secretary',
                email: 'secretary@nov-reco.com',
                role: 'secretary',
                department: 'Hành chính',
                office: 'Hà Nội',
                is_active: true,
                last_login: '2024-01-15 08:20:00'
            }
        ];
    }

    // Generate sample departments
    generateDepartments() {
        return [
            {
                id: 1,
                name: 'Kỹ thuật',
                office: 'Hà Nội',
                manager: 'Nguyễn Văn Tech Lead',
                deputy_manager: 'Trần Thị Senior Dev',
                employee_count: 15,
                description: 'Phòng phát triển phần mềm và công nghệ'
            },
            {
                id: 2,
                name: 'Kinh doanh',
                office: 'Hà Nội',
                manager: 'Lê Văn Sales Manager',
                deputy_manager: 'Phạm Thị Sales Lead',
                employee_count: 12,
                description: 'Phòng kinh doanh và phát triển thị trường'
            },
            {
                id: 3,
                name: 'Nhân sự',
                office: 'Hà Nội',
                manager: 'Hoàng Thị HR Manager',
                deputy_manager: 'Nguyễn Văn HR Specialist',
                employee_count: 8,
                description: 'Phòng quản lý nhân sự và phát triển nguồn nhân lực'
            },
            {
                id: 4,
                name: 'Kế toán',
                office: 'TP.HCM',
                manager: 'Trần Thị CFO',
                deputy_manager: 'Lê Văn Senior Accountant',
                employee_count: 6,
                description: 'Phòng kế toán và tài chính'
            },
            {
                id: 5,
                name: 'Marketing',
                office: 'TP.HCM',
                manager: 'Phạm Thị Marketing Director',
                deputy_manager: 'Hoàng Văn Marketing Lead',
                employee_count: 10,
                description: 'Phòng marketing và truyền thông'
            }
        ];
    }

    // Generate sample offices
    generateOffices() {
        return [
            {
                id: 1,
                name: 'Văn phòng Hà Nội',
                address: '123 Đường Láng, Đống Đa, Hà Nội',
                director: 'Nguyễn Văn Director',
                deputy_director: 'Trần Thị Deputy Director',
                employee_count: 35,
                description: 'Trụ sở chính tại Hà Nội'
            },
            {
                id: 2,
                name: 'Văn phòng TP.HCM',
                address: '456 Nguyễn Huệ, Quận 1, TP.HCM',
                director: 'Lê Văn Regional Director',
                deputy_director: 'Phạm Thị Regional Manager',
                employee_count: 25,
                description: 'Chi nhánh miền Nam'
            },
            {
                id: 3,
                name: 'Văn phòng Đà Nẵng',
                address: '789 Lê Duẩn, Hải Châu, Đà Nẵng',
                director: 'Hoàng Văn Branch Director',
                deputy_director: 'Nguyễn Thị Branch Manager',
                employee_count: 15,
                description: 'Chi nhánh miền Trung'
            }
        ];
    }

    // Generate sample check-ins
    generateCheckins() {
        const checkins = [];
        const today = new Date();
        const areas = ['Văn phòng chính', 'Địa điểm A', 'Địa điểm B', 'Địa điểm C'];
        const types = ['check-in', 'check-out'];
        
        for (let i = 0; i < 50; i++) {
            const date = new Date(today);
            date.setDate(date.getDate() - Math.floor(Math.random() * 30));
            date.setHours(7 + Math.floor(Math.random() * 10), Math.floor(Math.random() * 60), 0);
            
            checkins.push({
                id: i + 1,
                user_id: Math.floor(Math.random() * 5) + 1,
                user_name: this.users[Math.floor(Math.random() * this.users.length)].full_name,
                location_name: areas[Math.floor(Math.random() * areas.length)],
                checkin_type: types[Math.floor(Math.random() * types.length)],
                created_at: date.toISOString(),
                latitude: 21.0285 + (Math.random() - 0.5) * 0.01,
                longitude: 105.8542 + (Math.random() - 0.5) * 0.01,
                photo_url: '/static/images/checkin_placeholder.jpg',
                notes: Math.random() > 0.7 ? 'Check-in đặc biệt' : null
            });
        }
        
        return checkins.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    }

    // Generate sample absences
    generateAbsences() {
        const absences = [];
        const types = ['Nghỉ phép', 'Nghỉ ốm', 'Nghỉ việc riêng', 'Nghỉ lễ'];
        const statuses = ['pending', 'approved', 'rejected'];
        
        for (let i = 0; i < 20; i++) {
            const startDate = new Date();
            startDate.setDate(startDate.getDate() + Math.floor(Math.random() * 30));
            const endDate = new Date(startDate);
            endDate.setDate(endDate.getDate() + Math.floor(Math.random() * 5) + 1);
            
            absences.push({
                id: i + 1,
                user_id: Math.floor(Math.random() * 5) + 1,
                user_name: this.users[Math.floor(Math.random() * this.users.length)].full_name,
                absence_type: types[Math.floor(Math.random() * types.length)],
                start_date: startDate.toISOString().split('T')[0],
                end_date: endDate.toISOString().split('T')[0],
                reason: 'Lý do nghỉ phép cá nhân',
                status: statuses[Math.floor(Math.random() * statuses.length)],
                created_at: new Date().toISOString(),
                approved_by: Math.random() > 0.5 ? 'Nguyễn Văn Manager' : null
            });
        }
        
        return absences.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    }

    // Generate sample notifications
    generateNotifications() {
        return [
            {
                id: 1,
                title: 'Chào mừng đến với hệ thống',
                message: 'Chào mừng bạn đến với hệ thống quản lý check-in NOV-RECO',
                type: 'welcome',
                is_read: false,
                created_at: '2024-01-15 08:00:00',
                icon: 'fas fa-bell'
            },
            {
                id: 2,
                title: 'Check-in thành công',
                message: 'Bạn đã check-in thành công tại Văn phòng chính',
                type: 'checkin',
                is_read: false,
                created_at: '2024-01-15 08:30:00',
                icon: 'fas fa-map-marker-alt'
            },
            {
                id: 3,
                title: 'Đơn vắng mặt được phê duyệt',
                message: 'Đơn nghỉ phép của bạn đã được phê duyệt',
                type: 'absence',
                is_read: true,
                created_at: '2024-01-14 16:30:00',
                icon: 'fas fa-calendar-check'
            },
            {
                id: 4,
                title: 'Thông báo hệ thống',
                message: 'Hệ thống sẽ bảo trì vào 22:00 ngày 20/01/2024',
                type: 'system',
                is_read: false,
                created_at: '2024-01-15 09:00:00',
                icon: 'fas fa-tools'
            },
            {
                id: 5,
                title: 'Nhắc nhở check-out',
                message: 'Đừng quên check-out khi kết thúc ca làm việc',
                type: 'reminder',
                is_read: true,
                created_at: '2024-01-15 17:00:00',
                icon: 'fas fa-clock'
            }
        ];
    }

    // Generate sample areas
    generateAreas() {
        return [
            {
                id: 1,
                name: 'Văn phòng chính',
                latitude: 21.0285,
                longitude: 105.8542,
                radius: 100,
                is_active: true,
                description: 'Địa điểm văn phòng chính tại Hà Nội'
            },
            {
                id: 2,
                name: 'Địa điểm A',
                latitude: 21.0300,
                longitude: 105.8560,
                radius: 50,
                is_active: true,
                description: 'Địa điểm làm việc A'
            },
            {
                id: 3,
                name: 'Địa điểm B',
                latitude: 21.0270,
                longitude: 105.8520,
                radius: 75,
                is_active: true,
                description: 'Địa điểm làm việc B'
            },
            {
                id: 4,
                name: 'Địa điểm C',
                latitude: 21.0290,
                longitude: 105.8580,
                radius: 60,
                is_active: false,
                description: 'Địa điểm làm việc C (tạm ngưng)'
            }
        ];
    }

    // Generate dashboard statistics
    generateDashboardStats() {
        const today = new Date();
        const weekStart = new Date(today);
        weekStart.setDate(today.getDate() - today.getDay());
        const monthStart = new Date(today.getFullYear(), today.getMonth(), 1);

        return {
            today_checkins: this.checkins.filter(c => 
                new Date(c.created_at).toDateString() === today.toDateString()
            ).length,
            week_checkins: this.checkins.filter(c => 
                new Date(c.created_at) >= weekStart
            ).length,
            month_checkins: this.checkins.filter(c => 
                new Date(c.created_at) >= monthStart
            ).length,
            total_employees: this.users.filter(u => u.role === 'employee').length,
            total_areas: this.areas.filter(a => a.is_active).length,
            pending_absences: this.absences.filter(a => a.status === 'pending').length,
            approved_absences: this.absences.filter(a => a.status === 'approved').length,
            unread_notifications: this.notifications.filter(n => !n.is_read).length
        };
    }

    // Generate chart data
    generateChartData(type, days = 7) {
        const data = [];
        const labels = [];
        const today = new Date();

        for (let i = days - 1; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            labels.push(date.toLocaleDateString('vi-VN', { weekday: 'short' }));

            switch (type) {
                case 'attendance':
                    data.push(Math.floor(Math.random() * 30) + 10);
                    break;
                case 'department':
                    data.push(Math.floor(Math.random() * 20) + 5);
                    break;
                case 'time':
                    data.push(Math.floor(Math.random() * 15) + 3);
                    break;
                default:
                    data.push(Math.floor(Math.random() * 25) + 8);
            }
        }

        return { labels, data };
    }

    // Generate real-time data for WebSocket
    generateRealtimeData() {
        return {
            stats_update: {
                type: 'stats_update',
                data: this.generateDashboardStats()
            },
            activity_update: {
                type: 'activity_update',
                data: this.checkins.slice(0, 5)
            },
            checkin_alert: {
                type: 'checkin_alert',
                data: {
                    user_name: this.users[Math.floor(Math.random() * this.users.length)].full_name,
                    location_name: this.areas[Math.floor(Math.random() * this.areas.length)].name,
                    timestamp: new Date().toISOString()
                }
            },
            notification: {
                type: 'notification',
                data: {
                    title: 'Thông báo mới',
                    message: 'Có dữ liệu mới được cập nhật',
                    icon: 'fas fa-bell',
                    color: '#667eea'
                }
            }
        };
    }

    // Get sample data for specific module
    getModuleData(moduleName) {
        switch (moduleName) {
            case 'sales':
                return {
                    title: 'Bán hàng',
                    type: 'chart',
                    data: this.generateChartData('attendance', 7),
                    metrics: {
                        total_sales: 1250000,
                        growth: '+12.5%',
                        target: 1000000
                    }
                };
            case 'hr':
                return {
                    title: 'Nhân sự',
                    type: 'table',
                    data: this.users.map(user => ({
                        name: user.full_name,
                        role: user.role,
                        department: user.department,
                        status: user.is_active ? 'Active' : 'Inactive'
                    })),
                    metrics: {
                        total_employees: this.users.length,
                        active_employees: this.users.filter(u => u.is_active).length,
                        departments: this.departments.length
                    }
                };
            case 'marketing':
                return {
                    title: 'Marketing',
                    type: 'metric',
                    data: {
                        value: 85,
                        label: 'Campaign Performance',
                        change: '+8.2%',
                        target: 80
                    }
                };
            case 'finance':
                return {
                    title: 'Tài chính',
                    type: 'chart',
                    data: this.generateChartData('attendance', 30),
                    metrics: {
                        revenue: 2500000,
                        expenses: 1800000,
                        profit: 700000
                    }
                };
            default:
                return {
                    title: 'Module mẫu',
                    type: 'custom',
                    data: { message: 'Dữ liệu mẫu cho module' }
                };
        }
    }

    // Export all data
    exportAllData() {
        return {
            users: this.users,
            departments: this.departments,
            offices: this.offices,
            checkins: this.checkins,
            absences: this.absences,
            notifications: this.notifications,
            areas: this.areas,
            dashboard_stats: this.generateDashboardStats(),
            chart_data: {
                attendance: this.generateChartData('attendance', 7),
                department: this.generateChartData('department', 7),
                time: this.generateChartData('time', 7)
            },
            realtime_data: this.generateRealtimeData()
        };
    }
}

// Create global instance
window.DashboardTestData = new DashboardTestData();

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardTestData;
}
