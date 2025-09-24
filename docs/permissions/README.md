# 🔐 Permission System Documentation

Tài liệu về hệ thống phân quyền Django Groups + Permissions của NOV-RECO.

## 📄 Files

- **`PERMISSION_SYSTEM_MIGRATION.md`** - Quá trình migration từ role-based sang Groups + Permissions
- **`PERMISSION_SYSTEM_COMPLETION.md`** - Tổng kết hoàn thành migration

## 🎯 Nội dung

### PERMISSION_SYSTEM_MIGRATION.md
- Phân tích hệ thống cũ (role-based)
- Kế hoạch migration chi tiết
- Các bước thực hiện migration
- Custom permissions definition
- Groups và permissions assignment
- User migration process

### PERMISSION_SYSTEM_COMPLETION.md
- Tổng kết migration hoàn thành
- Kết quả test hệ thống
- Phân bổ users theo groups
- Lợi ích của hệ thống mới
- Trạng thái hiện tại

## 👥 Groups & Permissions

### Groups
- **Super Admin** - Toàn quyền (101 permissions)
- **Admin** - Quản lý toàn bộ trừ role management (99 permissions)
- **Manager** - Quản lý User, Department, Checkin, Area (33 permissions)
- **HR** - Quản lý User, Department, Area (24 permissions)
- **Secretary** - Quản lý Checkin, Area (19 permissions)
- **Employee** - Quyền cơ bản (6 permissions)

### Custom Permissions
- **User Management**: can_manage_users, can_view_users, can_create_users, etc.
- **Checkin Management**: can_manage_checkins, can_view_all_checkins, etc.
- **Area Management**: can_manage_areas, can_view_areas, can_create_areas, etc.

## 🔗 Liên kết

- [Tài liệu chính](../README.md)
- [Hướng dẫn phát triển](../development/DEVELOPMENT.md)
- [User Guide](../user-guides/USER_GUIDE.md)
