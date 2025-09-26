# Generated migration for location app

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Tên địa điểm', max_length=120)),
                ('description', models.TextField(blank=True, help_text='Mô tả địa điểm')),
                ('address', models.TextField(blank=True, help_text='Địa chỉ chi tiết')),
                ('lat', models.FloatField(help_text='Vĩ độ trung tâm')),
                ('lng', models.FloatField(help_text='Kinh độ trung tâm')),
                ('radius_m', models.PositiveIntegerField(default=100, help_text='Bán kính (mét)')),
                ('is_active', models.BooleanField(default=True, help_text='Địa điểm có hoạt động')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, help_text='Người tạo địa điểm', null=True, on_delete=django.db.models.deletion.CASCADE, to='users.user')),
            ],
            options={
                'verbose_name': 'Địa điểm',
                'verbose_name_plural': 'Địa điểm',
                'ordering': ['-created_at'],
            },
        ),
    ]
