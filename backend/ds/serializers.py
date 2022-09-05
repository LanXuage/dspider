from rest_framework import serializers
from ds.models import Page, Task, User
from django.contrib.auth.models import Permission


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'user_id', 'url', 'method', 'headers', 'payload',
                  'timeout', 'use_robots', 'use_tor', 'use_proxy', 'generator_id',
                  'generator_cfg', 'matcher_id', 'matcher_cfg', 'exporter_id',
                  'exporter_cfg', 'is_periodic', 'task_status', 'cron_expn',
                        'req_interval', 'start_time', 'update_time', 'create_time']


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['id', 'page_name', 'parent', 'children']


class PermissionSerializer(serializers.ModelSerializer):
    pages = PageSerializer(many=True, read_only=True)

    class Meta:
        model = Permission
        fields = ['id', 'pages']


class UserSerializer(serializers.ModelSerializer):
    user_permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'last_login', 'username', 'first_name', 'is_staff',
                  'last_name', 'is_superuser', 'email', 'user_permissions']
