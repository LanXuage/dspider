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


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.CharField(max_length=100, null=False,
                           verbose_name='任务第一个请求的URL')
    method = models.CharField(max_length=25, null=True, verbose_name='请求方法')
    headers = models.TextField(null=True)
    payload = models.TextField(null=True)
    timeout = models.IntegerField(null=True)
    use_robots = models.BooleanField(null=False, default=False)
    use_tor = models.BooleanField(null=False, default=False)
    use_proxy = models.BooleanField(null=False, default=False)
    generator_id = models.CharField(max_length=32, null=False)
    generator_cfg = models.TextField(null=True)
    matcher_id = models.CharField(max_length=32, null=False)
    matcher_cfg = models.TextField(null=True)
    exporter_id = models.CharField(max_length=32, null=False)
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
