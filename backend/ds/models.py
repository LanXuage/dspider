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
    update_time = models.DateTimeField(null=False, default=timezone.now)
    create_time = models.DateTimeField(null=False, default=timezone.now)


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_name = models.CharField(max_length=50, null=False, default='')
    url = models.CharField(max_length=100, null=False,
                           verbose_name='任务第一个请求的URL')
    method = models.CharField(max_length=25, null=True, verbose_name='请求方法')
    headers = models.TextField(null=True)
    payload = models.BinaryField(null=True)
    timeout = models.IntegerField(null=True)
    use_robots = models.BooleanField(null=False, default=False)
    use_tor = models.BooleanField(null=False, default=False)
    use_proxy = models.BooleanField(null=False, default=False)
    generator = models.ForeignKey(
        Plugin, on_delete=models.CASCADE, related_name='g_task_set')
    generator_cfg = models.TextField(null=True)
    matcher = models.ForeignKey(
        Plugin, on_delete=models.CASCADE, related_name='m_task_set')
    matcher_cfg = models.TextField(null=True)
    exporter = models.ForeignKey(
        Plugin, on_delete=models.CASCADE, related_name='e_task_set')
    exporter_cfg = models.TextField(null=True)
    is_periodic = models.BooleanField(null=False, default=False)
    task_status = models.SmallIntegerField(null=False, default=0)
    cron_expn = models.CharField(max_length=60, null=True)
    req_interval = models.IntegerField(null=True)
    start_time = models.DateTimeField(null=False, default=timezone.now)
    update_time = models.DateTimeField(null=False, default=timezone.now)
    create_time = models.DateTimeField(null=False, default=timezone.now)


class Page(models.Model):
    page_name = models.CharField(max_length=100, null=False)
    parent = models.ForeignKey(
        'self', related_name='children', on_delete=models.SET_NULL, null=True)
    user_permissions = models.ManyToManyField(Permission, 'pages')
