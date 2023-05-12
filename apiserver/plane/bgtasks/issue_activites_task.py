# Python imports
import json
import requests

# Django imports
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

# Third Party imports
from celery import shared_task
from sentry_sdk import capture_exception

# Module imports
from plane.db.models import (
    User,
    Issue,
    Project,
    Label,
    IssueActivity,
    State,
    Cycle,
    Module,
)
from plane.api.serializers import IssueActivitySerializer


# Track Chnages in name
def track_name(
    requested_data,
    current_instance,
    issue_id,
    project,
    actor,
    issue_activities,
):
    if current_instance.get("name") != requested_data.get("name"):
        issue_activities.append(
            IssueActivity(
                issue_id=issue_id,
                actor=actor,
                verb="updated",
                old_value=current_instance.get("name"),
                new_value=requested_data.get("name"),
                field="name",
                project=project,
                workspace=project.workspace,
                comment=f"{actor.email} updated the start date to {requested_data.get('name')}",
            )
        )


# Track changes in parent issue
def track_parent(
    requested_data,
    current_instance,
    issue_id,
    project,
    actor,
    issue_activities,
):
    if current_instance.get("parent") != requested_data.get("parent"):
        if requested_data.get("parent") is None:
            old_parent = Issue.objects.get(pk=current_instance.get("parent"))
            issue_activities.append(
                IssueActivity(
                    issue_id=issue_id,
                    actor=actor,
                    verb="updated",
                    old_value=f"{project.identifier}-{old_parent.sequence_id}",
                    new_value=None,
                    field="parent",
                    project=project,
                    workspace=project.workspace,
                    comment=f"{actor.email} updated the parent issue to None",
                    old_identifier=old_parent.id,
                    new_identifier=None,
                )
            )
        else:
            new_parent = Issue.objects.get(pk=requested_data.get("parent"))
            old_parent = Issue.objects.filter(pk=current_instance.get("parent")).first()
            issue_activities.append(
                IssueActivity(
                    issue_id=issue_id,
                    actor=actor,
                    verb="updated",
                    old_value=f"{project.identifier}-{old_parent.sequence_id}"
                    if old_parent is not None
                    else None,
                    new_value=f"{project.identifier}-{new_parent.sequence_id}",
                    field="parent",
                    project=project,
                    workspace=project.workspace,
                    comment=f"{actor.email} updated the parent issue to {new_parent.name}",
                    old_identifier=old_parent.id if old_parent is not None else None,
                    new_identifier=new_parent.id,
                )
            )


# Track changes in priority
def track_priority(
    requested_data,
    current_instance,
    issue_id,
    project,
    actor,
    issue_activities,
):
    if current_instance.get("priority") != requested_data.get("priority"):
        if requested_data.get("priority") is None:
            issue_activities.append(
                IssueActivity(
                    issue_id=issue_id,
                    actor=actor,
                    verb="updated",
                    old_value=current_instance.get("priority"),
                    new_value=None,
                    field="priority",
                    project=project,
                    workspace=project.workspace,
                    comment=f"{actor.email} updated the priority to None",
                )
            )
        else:
            issue_activities.append(
                IssueActivity(
                    issue_id=issue_id,
                    actor=actor,
                    verb="updated",
                    old_value=current_instance.get("priority"),
                    new_value=requested_data.get("priority"),
                    field="priority",
                    project=project,
                    workspace=project.workspace,
                    comment=f"{actor.email} updated the priority to {requested_data.get('priority')}",
                )
            )
    print(issue_activities)


# Track chnages in state of the issue
def track_state(
    requested_data,
    current_instance,
    issue_id,
    project,
    actor,
    issue_activities,
):
    if current_instance.get("state") != requested_data.get("state"):
        new_state = State.objects.get(pk=requested_data.get("state", None))
        old_state = State.objects.get(pk=current_instance.get("state", None))

        issue_activities.append(
            IssueActivity(
                issue_id=issue_id,
                actor=actor,
                verb="updated",
                old_value=old_state.name,
                new_value=new_state.name,
                field="state",
                project=project,
                workspace=project.workspace,
                comment=f"{actor.email} updated the state to {new_state.name}",
                old_identifier=old_state.id,
                new_identifier=new_state.id,
            )
        )


# Track issue description
def track_description(
    requested_data,
    current_instance,
    issue_id,
    project,
    actor,
    issue_activities,
):
    if current_instance.get("description_html") != requested_data.get(
        "description_html"
    ):
        issue_activities.append(
            IssueActivity(
                issue_id=issue_id,
                actor=actor,
                verb="updated",
                old_value=current_instance.get("description_html"),
                new_value=requested_data.get("description_html"),
                field="description",
                project=project,
                workspace=project.workspace,
                comment=f"{actor.email} updated the description to {requested_data.get('description_html')}",
            )
        )


# Track changes in issue target date
def track_target_date(
    requested_data,
    current_instance,
    issue_id,
    project,
    actor,
    issue_activities,
):
    if current_instance.get("target_date") != requested_data.get("target_date"):
        if requested_data.get("target_date") is None:
            issue_activities.append(
                IssueActivity(
                    issue_id=issue_id,
                    actor=actor,
                    verb="updated",
                    old_value=current_instance.get("target_date"),
                    new_value=requested_data.get("target_date"),
                    field="target_date",
                    project=project,
                    workspace=project.workspace,
                    comment=f"{actor.email} updated the target date to None",
                )
            )
        else:
            issue_activities.append(
                IssueActivity(
                    issue_id=issue_id,
                    actor=actor,
                    verb="updated",
                    old_value=current_instance.get("target_date"),
                    new_value=requested_data.get("target_date"),
                    field="target_date",
                    project=project,
                    workspace=project.workspace,
                    comment=f"{actor.email} updated the target date to {requested_data.get('target_date')}",
                )
            )


# Track changes in issue start date
def track_start_date(
    requested_data,
    current_instance,
    issue_id,
    project,
    actor,
    issue_activities,
):
    if current_instance.get("start_date") != requested_data.get("start_date"):
        if requested_data.get("start_date") is None:
            issue_activities.append(
                IssueActivity(
                    issue_id=issue_id,
                    actor=actor,
                    verb="updated",
                    old_value=current_instance.get("start_date"),
                    new_value=requested_data.get("start_date"),
                    field="start_date",
                    project=project,
                    workspace=project.workspace,
                    comment=f"{actor.email} updated the start date to None",
                )
            )
        else:
            issue_activities.append(
                IssueActivity(
                    issue_id=issue_id,
                    actor=actor,
                    verb="updated",
                    old_value=current_instance.get("start_date"),
                    new_value=requested_data.get("start_date"),
                    field="start_date",
                    project=project,
                    workspace=project.workspace,
                    comment=f"{actor.email} updated the start date to {requested_data.get('start_date')}",
                )
            )


# Track changes in issue labels
def track_labels(
    requested_data,
    current_instance,
    issue_id,
    project,
    actor,
    issue_activities,
):
    # Label Addition
    if len(requested_data.get("labels_list")) > len(current_instance.get("labels")):
        for label in requested_data.get("labels_list"):
            if label not in current_instance.get("labels"):
                label = Label.objects.get(pk=label)
                issue_activities.append(
                    IssueActivity(
                        issue_id=issue_id,
                        actor=actor,
                        verb="updated",
                        old_value="",
                        new_value=label.name,
                        field="labels",
                        project=project,
                        workspace=project.workspace,
                        comment=f"{actor.email} added label {label.name}",
                        new_identifier=label.id,
                        old_identifier=None,
                    )
                )

    # Label Removal
    if len(requested_data.get("labels_list")) < len(current_instance.get("labels")):
        for label in current_instance.get("labels"):
            if label not in requested_data.get("labels_list"):
                label = Label.objects.get(pk=label)
                issue_activities.append(
                    IssueActivity(
                        issue_id=issue_id,
                        actor=actor,
                        verb="updated",
                        old_value=label.name,
                        new_value="",
                        field="labels",
                        project=project,
                        workspace=project.workspace,
                        comment=f"{actor.email} removed label {label.name}",
                        old_identifier=label.id,
                        new_identifier=None,
                    )
                )


# Track changes in issue assignees
def track_assignees(
    requested_data,
    current_instance,
    issue_id,
    project,
    actor,
    issue_activities,
):
    # Assignee Addition
    if len(requested_data.get("assignees_list")) > len(
        current_instance.get("assignees")
    ):
        for assignee in requested_data.get("assignees_list"):
            if assignee not in current_instance.get("assignees"):
                assignee = User.objects.get(pk=assignee)
                issue_activities.append(
                    IssueActivity(
                        issue_id=issue_id,
                        actor=actor,
                        verb="updated",
                        old_value="",
                        new_value=assignee.email,
                        field="assignees",
                        project=project,
                        workspace=project.workspace,
                        comment=f"{actor.email} added assignee {assignee.email}",
                        new_identifier=actor.id,
                    )
                )

    # Assignee Removal
    if len(requested_data.get("assignees_list")) < len(
        current_instance.get("assignees")
    ):
        for assignee in current_instance.get("assignees"):
            if assignee not in requested_data.get("assignees_list"):
                assignee = User.objects.get(pk=assignee)
                issue_activities.append(
                    IssueActivity(
                        issue_id=issue_id,
                        actor=actor,
                        verb="updated",
                        old_value=assignee.email,
                        new_value="",
                        field="assignee",
                        project=project,
                        workspace=project.workspace,
                        comment=f"{actor.email} removed assignee {assignee.email}",
                        old_identifier=actor.id,
                    )
                )


# Track changes in blocking issues
def track_blocks(
    requested_data,
    current_instance,
    issue_id,
    project,
    actor,
    issue_activities,
):
    if len(requested_data.get("blocks_list")) > len(
        current_instance.get("blocked_issues")
    ):
        for block in requested_data.get("blocks_list"):
            if not [
                blocked
                for blocked in current_instance.get("blocked_issues")
                if blocked.get("block") == block
            ]:
                issue = Issue.objects.get(pk=block)
                issue_activities.append(
                    IssueActivity(
                        issue_id=issue_id,
                        actor=actor,
                        verb="updated",
                        old_value="",
                        new_value=f"{project.identifier}-{issue.sequence_id}",
                        field="blocks",
                        project=project,
                        workspace=project.workspace,
                        comment=f"{actor.email} added blocking issue {project.identifier}-{issue.sequence_id}",
                        new_identifier=issue.id,
                    )
                )

    # Blocked Issue Removal
    if len(requested_data.get("blocks_list")) < len(
        current_instance.get("blocked_issues")
    ):
        for blocked in current_instance.get("blocked_issues"):
            if blocked.get("block") not in requested_data.get("blocks_list"):
                issue = Issue.objects.get(pk=blocked.get("block"))
                issue_activities.append(
                    IssueActivity(
                        issue_id=issue_id,
                        actor=actor,
                        verb="updated",
                        old_value=f"{project.identifier}-{issue.sequence_id}",
                        new_value="",
                        field="blocks",
                        project=project,
                        workspace=project.workspace,
                        comment=f"{actor.email} removed blocking issue {project.identifier}-{issue.sequence_id}",
                        old_identifier=issue.id,
                    )
                )


# Track changes in blocked_by issues
def track_blockings(
    requested_data,
    current_instance,
    issue_id,
    project,
    actor,
    issue_activities,
):
    if len(requested_data.get("blockers_list")) > len(
        current_instance.get("blocker_issues")
    ):
        for block in requested_data.get("blockers_list"):
            if not [
                blocked
                for blocked in current_instance.get("blocker_issues")
                if blocked.get("blocked_by") == block
            ]:
                issue = Issue.objects.get(pk=block)
                issue_activities.append(
                    IssueActivity(
                        issue_id=issue_id,
                        actor=actor,
                        verb="updated",
                        old_value="",
                        new_value=f"{project.identifier}-{issue.sequence_id}",
                        field="blocking",
                        project=project,
                        workspace=project.workspace,
                        comment=f"{actor.email} added blocked by issue {project.identifier}-{issue.sequence_id}",
                        new_identifier=issue.id,
                    )
                )

    # Blocked Issue Removal
    if len(requested_data.get("blockers_list")) < len(
        current_instance.get("blocker_issues")
    ):
        for blocked in current_instance.get("blocker_issues"):
            if blocked.get("blocked_by") not in requested_data.get("blockers_list"):
                issue = Issue.objects.get(pk=blocked.get("blocked_by"))
                issue_activities.append(
                    IssueActivity(
                        issue_id=issue_id,
                        actor=actor,
                        verb="updated",
                        old_value=f"{project.identifier}-{issue.sequence_id}",
                        new_value="",
                        field="blocking",
                        project=project,
                        workspace=project.workspace,
                        comment=f"{actor.email} removed blocked by issue {project.identifier}-{issue.sequence_id}",
                        old_identifier=issue.id,
                    )
                )


def track_cycles(
    requested_data,
    current_instance,
    issue_id,
    project,
    actor,
    issue_activities,
):
    # Updated Records:
    updated_records = current_instance.get("updated_cycle_issues", [])
    created_records = json.loads(current_instance.get("created_cycle_issues", []))

    for updated_record in updated_records:
        old_cycle = Cycle.objects.filter(
            pk=updated_record.get("old_cycle_id", None)
        ).first()
        new_cycle = Cycle.objects.filter(
            pk=updated_record.get("new_cycle_id", None)
        ).first()

        issue_activities.append(
            IssueActivity(
                issue_id=updated_record.get("issue_id"),
                actor=actor,
                verb="updated",
                old_value=old_cycle.name,
                new_value=new_cycle.name,
                field="cycles",
                project=project,
                workspace=project.workspace,
                comment=f"{actor.email} updated cycle from {old_cycle.name} to {new_cycle.name}",
                old_identifier=old_cycle.id,
                new_identifier=new_cycle.id,
            )
        )

    for created_record in created_records:
        cycle = Cycle.objects.filter(
            pk=created_record.get("fields").get("cycle")
        ).first()

        issue_activities.append(
            IssueActivity(
                issue_id=created_record.get("fields").get("issue"),
                actor=actor,
                verb="created",
                old_value="",
                new_value=cycle.name,
                field="cycles",
                project=project,
                workspace=project.workspace,
                comment=f"{actor.email} added cycle {cycle.name}",
                new_identifier=cycle.id,
            )
        )


def track_modules(
    requested_data,
    current_instance,
    issue_id,
    project,
    actor,
    issue_activities,
):
    # Updated Records:
    updated_records = current_instance.get("updated_module_issues", [])
    created_records = json.loads(current_instance.get("created_module_issues", []))

    for updated_record in updated_records:
        old_module = Module.objects.filter(
            pk=updated_record.get("old_module_id", None)
        ).first()
        new_module = Module.objects.filter(
            pk=updated_record.get("new_module_id", None)
        ).first()

        issue_activities.append(
            IssueActivity(
                issue_id=updated_record.get("issue_id"),
                actor=actor,
                verb="updated",
                old_value=old_module.name,
                new_value=new_module.name,
                field="modules",
                project=project,
                workspace=project.workspace,
                comment=f"{actor.email} updated module from {old_module.name} to {new_module.name}",
                old_identifier=old_module.id,
                new_identifier=new_module.id,
            )
        )

    for created_record in created_records:
        module = Module.objects.filter(
            pk=created_record.get("fields").get("module")
        ).first()
        issue_activities.append(
            IssueActivity(
                issue_id=created_record.get("fields").get("issue"),
                actor=actor,
                verb="created",
                old_value="",
                new_value=module.name,
                field="modules",
                project=project,
                workspace=project.workspace,
                comment=f"{actor.email} added module {module.name}",
                new_identifier=module.id,
            )
        )


def create_issue_activity(
    requested_data, current_instance, issue_id, project, actor, issue_activities
):
    issue_activities.append(
        IssueActivity(
            issue_id=issue_id,
            project=project,
            workspace=project.workspace,
            comment=f"{actor.email} created the issue",
            verb="created",
            actor=actor,
        )
    )


def track_estimate_points(
    requested_data, current_instance, issue_id, project, actor, issue_activities
):
    if current_instance.get("estimate_point") != requested_data.get("estimate_point"):
        if requested_data.get("estimate_point") is None:
            issue_activities.append(
                IssueActivity(
                    issue_id=issue_id,
                    actor=actor,
                    verb="updated",
                    old_value=current_instance.get("estimate_point"),
                    new_value=requested_data.get("estimate_point"),
                    field="estimate_point",
                    project=project,
                    workspace=project.workspace,
                    comment=f"{actor.email} updated the estimate point to None",
                )
            )
        else:
            issue_activities.append(
                IssueActivity(
                    issue_id=issue_id,
                    actor=actor,
                    verb="updated",
                    old_value=current_instance.get("estimate_point"),
                    new_value=requested_data.get("estimate_point"),
                    field="estimate_point",
                    project=project,
                    workspace=project.workspace,
                    comment=f"{actor.email} updated the estimate point to {requested_data.get('estimate_point')}",
                )
            )


def update_issue_activity(
    requested_data, current_instance, issue_id, project, actor, issue_activities
):
    ISSUE_ACTIVITY_MAPPER = {
        "name": track_name,
        "parent": track_parent,
        "priority": track_priority,
        "state": track_state,
        "description": track_description,
        "target_date": track_target_date,
        "start_date": track_start_date,
        "labels_list": track_labels,
        "assignees_list": track_assignees,
        "blocks_list": track_blocks,
        "blockers_list": track_blockings,
        "cycles_list": track_cycles,
        "modules_list": track_modules,
        "estimate_point": track_estimate_points,
    }

    requested_data = json.loads(requested_data) if requested_data is not None else None
    current_instance = (
        json.loads(current_instance) if current_instance is not None else None
    )

    for key in requested_data:
        func = ISSUE_ACTIVITY_MAPPER.get(key, None)
        if func is not None:
            func(
                requested_data,
                current_instance,
                issue_id,
                project,
                actor,
                issue_activities,
            )


def delete_issue_activity(
    requested_data, current_instance, issue_id, project, actor, issue_activities
):
    issue_activities.append(
        IssueActivity(
            project=project,
            workspace=project.workspace,
            comment=f"{actor.email} deleted the issue",
            verb="deleted",
            actor=actor,
            field="issue",
        )
    )


def create_comment_activity(
    requested_data, current_instance, issue_id, project, actor, issue_activities
):
    requested_data = json.loads(requested_data) if requested_data is not None else None
    current_instance = (
        json.loads(current_instance) if current_instance is not None else None
    )

    issue_activities.append(
        IssueActivity(
            issue_id=issue_id,
            project=project,
            workspace=project.workspace,
            comment=f"{actor.email} created a comment",
            verb="created",
            actor=actor,
            field="comment",
            new_value=requested_data.get("comment_html", ""),
            new_identifier=requested_data.get("id", None),
            issue_comment_id=requested_data.get("id", None),
        )
    )


def update_comment_activity(
    requested_data, current_instance, issue_id, project, actor, issue_activities
):
    requested_data = json.loads(requested_data) if requested_data is not None else None
    current_instance = (
        json.loads(current_instance) if current_instance is not None else None
    )

    if current_instance.get("comment_html") != requested_data.get("comment_html"):
        issue_activities.append(
            IssueActivity(
                issue_id=issue_id,
                project=project,
                workspace=project.workspace,
                comment=f"{actor.email} updated a comment",
                verb="updated",
                actor=actor,
                field="comment",
                old_value=current_instance.get("comment_html", ""),
                old_identifier=current_instance.get("id"),
                new_value=requested_data.get("comment_html", ""),
                new_identifier=current_instance.get("id", None),
                issue_comment_id=current_instance.get("id", None),
            )
        )


def delete_comment_activity(
    requested_data, current_instance, issue_id, project, actor, issue_activities
):
    issue_activities.append(
        IssueActivity(
            issue_id=issue_id,
            project=project,
            workspace=project.workspace,
            comment=f"{actor.email} deleted the comment",
            verb="deleted",
            actor=actor,
            field="comment",
        )
    )


def create_link_activity(
    requested_data, current_instance, issue_id, project, actor, issue_activities
):
    requested_data = json.loads(requested_data) if requested_data is not None else None
    current_instance = (
        json.loads(current_instance) if current_instance is not None else None
    )

    issue_activities.append(
        IssueActivity(
            issue_id=issue_id,
            project=project,
            workspace=project.workspace,
            comment=f"{actor.email} created a link",
            verb="created",
            actor=actor,
            field="link",
            new_value=requested_data.get("url", ""),
            new_identifier=requested_data.get("id", None),
        )
    )


def update_link_activity(
    requested_data, current_instance, issue_id, project, actor, issue_activities
):
    requested_data = json.loads(requested_data) if requested_data is not None else None
    current_instance = (
        json.loads(current_instance) if current_instance is not None else None
    )

    if current_instance.get("url") != requested_data.get("url"):
        issue_activities.append(
            IssueActivity(
                issue_id=issue_id,
                project=project,
                workspace=project.workspace,
                comment=f"{actor.email} updated a link",
                verb="updated",
                actor=actor,
                field="link",
                old_value=current_instance.get("url", ""),
                old_identifier=current_instance.get("id"),
                new_value=requested_data.get("url", ""),
                new_identifier=current_instance.get("id", None),
            )
        )


def delete_link_activity(
    requested_data, current_instance, issue_id, project, actor, issue_activities
):
    issue_activities.append(
        IssueActivity(
            issue_id=issue_id,
            project=project,
            workspace=project.workspace,
            comment=f"{actor.email} deleted the link",
            verb="deleted",
            actor=actor,
            field="link",
        )
    )


def create_attachment_activity(
    requested_data, current_instance, issue_id, project, actor, issue_activities
):
    requested_data = json.loads(requested_data) if requested_data is not None else None
    current_instance = (
        json.loads(current_instance) if current_instance is not None else None
    )

    issue_activities.append(
        IssueActivity(
            issue_id=issue_id,
            project=project,
            workspace=project.workspace,
            comment=f"{actor.email} created an attachment",
            verb="created",
            actor=actor,
            field="attachment",
            new_value=current_instance.get("access", ""),
            new_identifier=current_instance.get("id", None),
        )
    )


def delete_attachment_activity(
    requested_data, current_instance, issue_id, project, actor, issue_activities
):
    issue_activities.append(
        IssueActivity(
            issue_id=issue_id,
            project=project,
            workspace=project.workspace,
            comment=f"{actor.email} deleted the attachment",
            verb="deleted",
            actor=actor,
            field="attachment",
        )
    )


# Receive message from room group
@shared_task
def issue_activity(
    type, requested_data, current_instance, issue_id, actor_id, project_id
):
    try:
        issue_activities = []

        actor = User.objects.get(pk=actor_id)
        project = Project.objects.get(pk=project_id)

        ACTIVITY_MAPPER = {
            "issue.activity.created": create_issue_activity,
            "issue.activity.updated": update_issue_activity,
            "issue.activity.deleted": delete_issue_activity,
            "comment.activity.created": create_comment_activity,
            "comment.activity.updated": update_comment_activity,
            "comment.activity.deleted": delete_comment_activity,
            "link.activity.created": create_link_activity,
            "link.activity.updated": update_link_activity,
            "link.activity.deleted": delete_link_activity,
            "attachment.activity.created": create_attachment_activity,
            "attachment.activity.deleted": delete_attachment_activity,
        }

        func = ACTIVITY_MAPPER.get(type)
        if func is not None:
            func(
                requested_data,
                current_instance,
                issue_id,
                project,
                actor,
                issue_activities,
            )

        # Save all the values to database
        issue_activities_created = IssueActivity.objects.bulk_create(issue_activities)
        # Post the updates to segway for integrations and webhooks
        if len(issue_activities_created) and settings.PROXY_BASE_URL:
            for issue_activity in issue_activities_created:
                headers = {"Content-Type": "application/json"}
                issue_activity_json = json.dumps(
                    IssueActivitySerializer(issue_activity).data,
                    cls=DjangoJSONEncoder,
                )
                _ = requests.post(
                    f"{settings.PROXY_BASE_URL}/hooks/workspaces/{str(issue_activity.workspace_id)}/projects/{str(issue_activity.project_id)}/issues/{str(issue_activity.issue_id)}/issue-activity-hooks/",
                    json=issue_activity_json,
                    headers=headers,
                )
        return
    except Exception as e:
        print(e)
        capture_exception(e)
        return
