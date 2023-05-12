# Python imports
import re

# Django imports
from django.db.models import Q

# Third party imports
from rest_framework import status
from rest_framework.response import Response
from sentry_sdk import capture_exception

# Module imports
from .base import BaseAPIView
from plane.db.models import Workspace, Project, Issue, Cycle, Module, Page, IssueView
from plane.utils.issue_search import search_issues


class GlobalSearchEndpoint(BaseAPIView):
    """Endpoint to search across multiple fields in the workspace and
    also show related workspace if found
    """

    def filter_workspaces(self, query, slug, project_id):
        fields = ["name"]
        q = Q()
        for field in fields:
            q |= Q(**{f"{field}__icontains": query})
        return (
            Workspace.objects.filter(q, workspace_member__member=self.request.user)
            .distinct()
            .values("name", "id", "slug")
        )

    def filter_projects(self, query, slug, project_id):
        fields = ["name"]
        q = Q()
        for field in fields:
            q |= Q(**{f"{field}__icontains": query})
        return (
            Project.objects.filter(
                q,
                Q(project_projectmember__member=self.request.user) | Q(network=2),
                workspace__slug=slug,
            )
            .distinct()
            .values("name", "id", "identifier", "workspace__slug")
        )

    def filter_issues(self, query, slug, project_id):
        fields = ["name", "sequence_id"]
        q = Q()
        for field in fields:
            if field == "sequence_id":
                sequences = re.findall(r"\d+\.\d+|\d+", query)
                for sequence_id in sequences:
                    q |= Q(**{"sequence_id": sequence_id})
            else:
                q |= Q(**{f"{field}__icontains": query})
        return (
            Issue.objects.filter(
                q,
                project__project_projectmember__member=self.request.user,
                workspace__slug=slug,
                project_id=project_id,
            )
            .distinct()
            .values(
                "name",
                "id",
                "sequence_id",
                "project__identifier",
                "project_id",
                "workspace__slug",
            )
        )

    def filter_cycles(self, query, slug, project_id):
        fields = ["name"]
        q = Q()
        for field in fields:
            q |= Q(**{f"{field}__icontains": query})
        return (
            Cycle.objects.filter(
                q,
                project__project_projectmember__member=self.request.user,
                workspace__slug=slug,
                project_id=project_id,
            )
            .distinct()
            .values(
                "name",
                "id",
                "project_id",
                "workspace__slug",
            )
        )

    def filter_modules(self, query, slug, project_id):
        fields = ["name"]
        q = Q()
        for field in fields:
            q |= Q(**{f"{field}__icontains": query})
        return (
            Module.objects.filter(
                q,
                project__project_projectmember__member=self.request.user,
                workspace__slug=slug,
                project_id=project_id,
            )
            .distinct()
            .values(
                "name",
                "id",
                "project_id",
                "workspace__slug",
            )
        )

    def filter_pages(self, query, slug, project_id):
        fields = ["name"]
        q = Q()
        for field in fields:
            q |= Q(**{f"{field}__icontains": query})
        return (
            Page.objects.filter(
                q,
                project__project_projectmember__member=self.request.user,
                workspace__slug=slug,
                project_id=project_id,
            )
            .distinct()
            .values(
                "name",
                "id",
                "project_id",
                "workspace__slug",
            )
        )

    def filter_views(self, query, slug, project_id):
        fields = ["name"]
        q = Q()
        for field in fields:
            q |= Q(**{f"{field}__icontains": query})
        return (
            IssueView.objects.filter(
                q,
                project__project_projectmember__member=self.request.user,
                workspace__slug=slug,
                project_id=project_id,
            )
            .distinct()
            .values(
                "name",
                "id",
                "project_id",
                "workspace__slug",
            )
        )

    def get(self, request, slug, project_id):
        try:
            query = request.query_params.get("search", False)
            if not query:
                return Response(
                    {
                        "results": {
                            "workspace": [],
                            "project": [],
                            "issue": [],
                            "cycle": [],
                            "module": [],
                            "issue_view": [],
                            "page": [],
                        }
                    },
                    status=status.HTTP_200_OK,
                )

            MODELS_MAPPER = {
                "workspace": self.filter_workspaces,
                "project": self.filter_projects,
                "issue": self.filter_issues,
                "cycle": self.filter_cycles,
                "module": self.filter_modules,
                "issue_view": self.filter_views,
                "page": self.filter_pages,
            }

            results = {}

            for model in MODELS_MAPPER:
                func = MODELS_MAPPER.get(model, None)
                results[model] = func(query, slug, project_id)
            return Response({"results": results}, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response(
                {"error": "Something went wrong please try again later"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class IssueSearchEndpoint(BaseAPIView):
    def get(self, request, slug, project_id):
        try:
            query = request.query_params.get("search", False)
            parent = request.query_params.get("parent", False)
            blocker_blocked_by = request.query_params.get("blocker_blocked_by", False)
            issue_id = request.query_params.get("issue_id", False)

            issues = search_issues(query)
            issues = issues.filter(
                workspace__slug=slug,
                project_id=project_id,
                project__project_projectmember__member=self.request.user,
            )

            if parent == "true" and issue_id:
                issue = Issue.objects.get(pk=issue_id)
                issues = issues.filter(
                    ~Q(pk=issue_id), ~Q(pk=issue.parent_id), parent__isnull=True
                )
            if blocker_blocked_by == "true" and issue_id:
                issues = issues.filter(blocker_issues=issue_id, blocked_issues=issue_id)

            return Response(
                issues.values(
                    "name",
                    "id",
                    "sequence_id",
                    "project__identifier",
                    "project_id",
                    "workspace__slug",
                ),
                status=status.HTTP_200_OK,
            )
        except Issue.DoesNotExist:
            return Response(
                {"error": "Issue Does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {"error": "Something went wrong please try again later"},
                status=status.HTTP_400_BAD_REQUEST,
            )
