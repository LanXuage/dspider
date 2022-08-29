from rest_framework import serializers
from ds.models import Task, User

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'user_id', 'url', 'method', 'headers', 'payload', \
            'timeout', 'use_robots', 'use_tor', 'use_proxy', 'generator_id', \
                'generator_cfg', 'matcher_id', 'matcher_cfg', 'exporter_id', \
                    'exporter_cfg', 'is_periodic', 'task_status', 'cron_expn', \
                        'req_interval', 'start_time', 'update_time', 'create_time']
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'password', 'last_login', 'is_superuser', 'username', \
            'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined']
    