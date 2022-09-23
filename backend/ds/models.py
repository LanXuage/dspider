from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token

User = get_user_model()


@receiver(post_save, sender=User)
def create_auth_token(sender, user=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=user)


class Plugin(models.Model):
    id = models.CharField(max_length=32, null=False, primary_key=True)
    plugin_name = models.CharField(max_length=50, null=False, default='')
    plugin_type = models.SmallIntegerField(null=False, default=0)
    plugin_plain = models.TextField(null=True, default='')
    code_obj = models.BinaryField(null=False)
    code_obj_version = models.CharField(max_length=32, null=False, default='')
    update_time = models.DateTimeField(null=False, default=timezone.now)
    create_time = models.DateTimeField(null=False, default=timezone.now)


class Plan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan_name = models.CharField(max_length=50, null=False, default='')
    url = models.CharField(max_length=100, null=False)
    method = models.CharField(max_length=25, null=True)
    headers = models.TextField(null=True)
    payload = models.BinaryField(null=True)
    timeout = models.IntegerField(null=True)
    use_robots = models.BooleanField(null=False, default=False)
    use_tor = models.BooleanField(null=False, default=False)
    use_proxy = models.BooleanField(null=False, default=False)
    generator = models.ForeignKey(
        Plugin, on_delete=models.CASCADE, related_name='g_plans')
    generator_cfg = models.TextField(null=True, default='{}')
    matcher = models.ForeignKey(
        Plugin, on_delete=models.CASCADE, related_name='m_plans')
    matcher_cfg = models.TextField(null=False, default='{}')
    exporter = models.ForeignKey(
        Plugin, on_delete=models.CASCADE, related_name='e_plans')
    exporter_cfg = models.TextField(null=False, default='{}')
    is_periodic = models.BooleanField(null=False, default=False)
    plan_status = models.SmallIntegerField(null=False, default=0)
    cron_expn = models.CharField(max_length=60, null=True)
    req_interval = models.IntegerField(null=True, default=5)
    start_time = models.DateTimeField(null=False, default=timezone.now)
    update_time = models.DateTimeField(null=False, default=timezone.now)
    create_time = models.DateTimeField(null=False, default=timezone.now)


class Task(models.Model):
    id = models.CharField(max_length=32, null=False, primary_key=True)
    plan = models.ForeignKey(
        Plan, on_delete=models.CASCADE, related_name='tasks', null=True)
    task_status = models.SmallIntegerField(null=False, default=0)
    total_reqs = models.IntegerField(null=False, default=1)
    reqs_processed = models.IntegerField(null=False, default=0)
    total_results = models.IntegerField(null=False, default=0)
    results_processed = models.IntegerField(null=False, default=0)
    start_time = models.DateTimeField(null=False, default=timezone.now)
    end_time = models.DateTimeField(null=True)
    update_time = models.DateTimeField(null=False, default=timezone.now)
    create_time = models.DateTimeField(null=False, default=timezone.now)


class Log(models.Model):
    state = models.SmallIntegerField(null=False, default=0)
    content = models.BinaryField(null=False, default=b'')
    plugin = models.ForeignKey(
        Plugin, on_delete=models.CASCADE, related_name='p_logs')
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name='t_logs')
    occur_time = models.DateTimeField(null=False, default=timezone.now)
    create_time = models.DateTimeField(null=False, default=timezone.now)


class Page(models.Model):
    page_name = models.CharField(max_length=100, null=False)
    parent = models.ForeignKey(
        'self', related_name='children', on_delete=models.SET_NULL, null=True)
    user_permissions = models.ManyToManyField(Permission, 'pages')
