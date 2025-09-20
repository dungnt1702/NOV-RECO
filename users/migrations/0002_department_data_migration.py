from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        # Create Department model first
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Tên phòng ban', max_length=100, unique=True)),
                ('description', models.TextField(blank=True, help_text='Mô tả phòng ban')),
                ('manager', models.ForeignKey(blank=True, help_text='Trưởng phòng ban', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managed_departments', to='users.user')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Phòng ban',
                'verbose_name_plural': 'Phòng ban',
                'ordering': ['name'],
            },
        ),
        
        # Add new department field as ForeignKey
        migrations.AddField(
            model_name='user',
            name='department_new',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employees', to='users.department'),
        ),
        
        # Create default departments
        migrations.RunPython(
            code=lambda apps, schema_editor: create_default_departments(apps, schema_editor),
            reverse_code=lambda apps, schema_editor: remove_departments(apps, schema_editor),
        ),
        
        # Migrate data from old department field to new one
        migrations.RunPython(
            code=lambda apps, schema_editor: migrate_department_data(apps, schema_editor),
            reverse_code=lambda apps, schema_editor: reverse_migrate_department_data(apps, schema_editor),
        ),
        
        # Remove old department field
        migrations.RemoveField(
            model_name='user',
            name='department',
        ),
        
        # Rename new field to department
        migrations.RenameField(
            model_name='user',
            old_name='department_new',
            new_name='department',
        ),
    ]


def create_default_departments(apps, schema_editor):
    Department = apps.get_model('users', 'Department')
    
    departments = [
        {'name': 'Phòng Kế toán', 'description': 'Quản lý tài chính và kế toán'},
        {'name': 'Phòng Nhân sự', 'description': 'Quản lý nhân sự và tuyển dụng'},
        {'name': 'Phòng Kỹ thuật', 'description': 'Phát triển và bảo trì hệ thống'},
        {'name': 'Phòng Kinh doanh', 'description': 'Phát triển kinh doanh và bán hàng'},
        {'name': 'Phòng Marketing', 'description': 'Marketing và quảng cáo'},
        {'name': 'Phòng Hành chính', 'description': 'Hành chính và quản lý'},
    ]
    
    for dept_data in departments:
        Department.objects.get_or_create(
            name=dept_data['name'],
            defaults={'description': dept_data['description']}
        )


def remove_departments(apps, schema_editor):
    Department = apps.get_model('users', 'Department')
    Department.objects.all().delete()


def migrate_department_data(apps, schema_editor):
    User = apps.get_model('users', 'User')
    Department = apps.get_model('users', 'Department')
    
    # Get all users with non-empty department strings
    users_with_departments = User.objects.exclude(department='').exclude(department__isnull=True)
    
    for user in users_with_departments:
        if user.department:
            # Try to find existing department or create new one
            department, created = Department.objects.get_or_create(
                name=user.department,
                defaults={'description': f'Phòng ban {user.department}'}
            )
            user.department_new = department
            user.save()


def reverse_migrate_department_data(apps, schema_editor):
    User = apps.get_model('users', 'User')
    
    # This is a simplified reverse migration
    # In practice, you might want to store the department names differently
    pass
