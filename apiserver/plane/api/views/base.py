# Django imports
from django.urls import resolve
from django.conf import settings

# Third part imports
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from django_filters.rest_framework import DjangoFilterBackend

# Module imports
from plane.db.models import Workspace, Project
from plane.utils.paginator import BasePaginator


class BaseViewSet(ModelViewSet, BasePaginator):

    model = None

    permission_classes = [
        IsAuthenticated,
    ]

    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
    )

    filterset_fields = []

    search_fields = []

    def get_queryset(self):
        try:
            return self.model.objects.all()
        except Exception as e:
            print(e)
            raise APIException("Please check the view", status.HTTP_400_BAD_REQUEST)

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        if settings.DEBUG:
            from django.db import connection

            print(
                f"{request.method} - {request.get_full_path()} of Queries: {len(connection.queries)}"
            )
        return response

    @property
    def workspace_slug(self):
        return self.kwargs.get("slug", None)

    @property
    def project_id(self):
        if project_id := self.kwargs.get("project_id", None):
            return project_id

        if resolve(self.request.path_info).url_name == "project":
            return self.kwargs.get("pk", None)


class BaseAPIView(APIView, BasePaginator):

    permission_classes = [
        IsAuthenticated,
    ]

    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
    )

    filterset_fields = []

    search_fields = []

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        if settings.DEBUG:
            from django.db import connection

            print(
                f"{request.method} - {request.get_full_path()} of Queries: {len(connection.queries)}"
            )
        return response

    @property
    def workspace_slug(self):
        return self.kwargs.get("slug", None)

    @property
    def project_id(self):
        return self.kwargs.get("project_id", None)
