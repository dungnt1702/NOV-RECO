from rest_framework import serializers

from .models import Department, User, UserRole


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer cho Department"""

    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            "id",
            "name",
            "description",
            "employee_count",
            "created_at",
            "updated_at",
        ]

    def get_employee_count(self, obj):
        return obj.employees.count()


class UserSerializer(serializers.ModelSerializer):
    """Serializer cho User"""

    department_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "role",
            "role_display",
            "department",
            "department_name",
            "phone",
            "avatar",
            "date_of_birth",
            "gender",
            "address",
            "emergency_contact",
            "emergency_phone",
            "position",
            "hire_date",
            "salary",
            "work_schedule",
            "skills",
            "notes",
            "is_active_employee",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_role_display(self, obj):
        return obj.get_role_display_name()


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer cho tạo User"""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "password_confirm",
            "role",
            "department",
            "phone",
            "date_of_birth",
            "gender",
            "address",
            "emergency_contact",
            "emergency_phone",
            "position",
            "hire_date",
            "salary",
            "work_schedule",
            "skills",
            "notes",
            "is_active_employee",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Mật khẩu không khớp")
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer cho cập nhật User"""

    password = serializers.CharField(write_only=True, required=False, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "password_confirm",
            "role",
            "department",
            "phone",
            "avatar",
            "date_of_birth",
            "gender",
            "address",
            "emergency_contact",
            "emergency_phone",
            "position",
            "hire_date",
            "salary",
            "work_schedule",
            "skills",
            "notes",
            "is_active_employee",
            "is_active",
        ]

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if password and password_confirm:
            if password != password_confirm:
                raise serializers.ValidationError("Mật khẩu không khớp")
        elif password and not password_confirm:
            raise serializers.ValidationError("Vui lòng xác nhận mật khẩu")
        elif not password and password_confirm:
            raise serializers.ValidationError("Vui lòng nhập mật khẩu mới")

        return attrs

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        validated_data.pop("password_confirm", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance
