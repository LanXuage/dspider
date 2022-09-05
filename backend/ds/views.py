from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken import views, models
from rest_framework.response import Response
from django.db.models.query import QuerySet
from django.contrib.auth.signals import user_logged_in
from ds.serializers import Task, User, Permission, Page, TaskSerializer, UserSerializer, PermissionSerializer, PageSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects
    serializer_class = TaskSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects
    serializer_class = PermissionSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects
    serializer_class = PageSerializer


class AuthView(views.ObtainAuthToken):
    user_fields_to_be_removed = ['id', 'is_staff',
                                 'is_superuser', 'user_permissions']

    def all_children(self, node):
        ret = []
        for child in node.children.all():
            ret.append({'name': child.page_name,
                       'children': self.all_children(child)})
        return ret

    def all_paths(self, nodes, targets):
        ret = []
        matched = False
        for node in nodes:
            if node in targets:
                matched = True
            sub_node = {'name': node.page_name}
            if matched:
                sub_node['children'] = self.all_children(node)
                ret.append(sub_node)
            else:
                sub_node['children'], sub_matched = self.all_paths(
                    node.children.all(), targets)
                if sub_matched:
                    ret.append(sub_node)
        return ret, matched

    def get_pages(self, user: User):
        pages = None
        for user_permission in user.get_user_permissions():
            content_type_app_label, user_permission_codename = user_permission.split(
                '.')
            for permission in Permission.objects.filter(codename=user_permission_codename, content_type__app_label=content_type_app_label):
                if not pages:
                    pages = Page.objects.filter(
                        user_permissions__pk=permission.pk)
                else:
                    pages = pages.union(Page.objects.filter(
                        user_permissions__pk=permission.pk))
        ret, _ = self.all_paths(Page.objects.filter(parent=None), pages)
        return ret

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = models.Token.objects.get_or_create(user=user)
        user_logged_in.send(User, user=user)
        user_data = UserSerializer(user).data
        user_data['pages'] = self.get_pages(user)
        for f in self.user_fields_to_be_removed:
            del user_data[f]
        user_data['token'] = token.key
        return Response(user_data)
