from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime


def filter_state(params, filter, method):
    if method == "GET":
        states = params.get("state").split(",")
        if len(states) and "" not in states:
            filter["state__in"] = states
    elif params.get("state", None) and len(params.get("state")):
        filter["state__in"] = params.get("state")
    return filter


def filter_priority(params, filter, method):
    if method == "GET":
        priorties = params.get("priority").split(",")
        if len(priorties) and "" not in priorties:
            filter["priority__in"] = priorties
    elif params.get("priority", None) and len(params.get("priority")):
        filter["priority__in"] = params.get("priority")
    return filter


def filter_parent(params, filter, method):
    if method == "GET":
        parents = params.get("parent").split(",")
        if len(parents) and "" not in parents:
            filter["parent__in"] = parents
    elif params.get("parent", None) and len(params.get("parent")):
        filter["parent__in"] = params.get("parent")
    return filter


def filter_labels(params, filter, method):
    if method == "GET":
        labels = params.get("labels").split(",")
        if len(labels) and "" not in labels:
            filter["labels__in"] = labels
    elif params.get("labels", None) and len(params.get("labels")):
        filter["labels__in"] = params.get("labels")
    return filter


def filter_assignees(params, filter, method):
    if method == "GET":
        assignees = params.get("assignees").split(",")
        if len(assignees) and "" not in assignees:
            filter["assignees__in"] = assignees
    elif params.get("assignees", None) and len(params.get("assignees")):
        filter["assignees__in"] = params.get("assignees")
    return filter


def filter_created_by(params, filter, method):
    if method == "GET":
        created_bys = params.get("created_by").split(",")
        if len(created_bys) and "" not in created_bys:
            filter["created_by__in"] = created_bys
    elif params.get("created_by", None) and len(params.get("created_by")):
        filter["created_by__in"] = params.get("created_by")
    return filter


def filter_name(params, filter, method):
    if params.get("name", "") != "":
        filter["name__icontains"] = params.get("name")
    return filter


def filter_created_at(params, filter, method):
    if method == "GET":
        created_ats = params.get("created_at").split(",")
        if len(created_ats) and "" not in created_ats:
            for query in created_ats:
                created_at_query = query.split(";")
                if len(created_at_query) == 2 and "after" in created_at_query:
                    filter["created_at__date__gte"] = created_at_query[0]
                else:
                    filter["created_at__date__lte"] = created_at_query[0]
    elif params.get("created_at", None) and len(params.get("created_at")):
        for query in params.get("created_at"):
            if query.get("timeline", "after") == "after":
                filter["created_at__date__gte"] = query.get("datetime")
            else:
                filter["created_at__date__lte"] = query.get("datetime")
    return filter


def filter_updated_at(params, filter, method):
    if method == "GET":
        updated_ats = params.get("updated_at").split(",")
        if len(updated_ats) and "" not in updated_ats:
            for query in updated_ats:
                updated_at_query = query.split(";")
                if len(updated_at_query) == 2 and "after" in updated_at_query:
                    filter["updated_at__date__gte"] = updated_at_query[0]
                else:
                    filter["updated_at__date__lte"] = updated_at_query[0]
    elif params.get("updated_at", None) and len(params.get("updated_at")):
        for query in params.get("updated_at"):
            if query.get("timeline", "after") == "after":
                filter["updated_at__date__gte"] = query.get("datetime")
            else:
                filter["updated_at__date__lte"] = query.get("datetime")
    return filter


def filter_start_date(params, filter, method):
    if method == "GET":
        start_dates = params.get("start_date").split(",")
        if len(start_dates) and "" not in start_dates:
            for query in start_dates:
                start_date_query = query.split(";")
                if len(start_date_query) == 2 and "after" in start_date_query:
                    filter["start_date__gte"] = start_date_query[0]
                else:
                    filter["start_date__lte"] = start_date_query[0]
    elif params.get("start_date", None) and len(params.get("start_date")):
        for query in params.get("start_date"):
            if query.get("timeline", "after") == "after":
                filter["start_date__gte"] = query.get("datetime")
            else:
                filter["start_date__lte"] = query.get("datetime")
    return filter


def filter_target_date(params, filter, method):
    if method == "GET":
        target_dates = params.get("target_date").split(",")
        if len(target_dates) and "" not in target_dates:
            for query in target_dates:
                target_date_query = query.split(";")
                if len(target_date_query) == 2 and "after" in target_date_query:
                    filter["target_date__gte"] = target_date_query[0]
                else:
                    filter["target_date__lte"] = target_date_query[0]
    elif params.get("target_date", None) and len(params.get("target_date")):
        for query in params.get("target_date"):
            if query.get("timeline", "after") == "after":
                filter["target_date__gte"] = query.get("datetime")
            else:
                filter["target_date__lte"] = query.get("datetime")

    return filter


def filter_completed_at(params, filter, method):
    if method == "GET":
        completed_ats = params.get("completed_at").split(",")
        if len(completed_ats) and "" not in completed_ats:
            for query in completed_ats:
                completed_at_query = query.split(";")
                if len(completed_at_query) == 2 and "after" in completed_at_query:
                    filter["completed_at__date__gte"] = completed_at_query[0]
                else:
                    filter["completed_at__lte"] = completed_at_query[0]
    elif params.get("completed_at", None) and len(params.get("completed_at")):
        for query in params.get("completed_at"):
            if query.get("timeline", "after") == "after":
                filter["completed_at__date__gte"] = query.get("datetime")
            else:
                filter["completed_at__lte"] = query.get("datetime")
    return filter


def filter_issue_state_type(params, filter, method):
    type = params.get("type", "all")
    group = ["backlog", "unstarted", "started", "completed", "cancelled"]
    if type == "active":
        group = ["unstarted", "started"]

    elif type == "backlog":
        group = ["backlog"]
    filter["state__group__in"] = group
    return filter


def issue_filters(query_params, method):
    filter = {}

    ISSUE_FILTER = {
        "state": filter_state,
        "priority": filter_priority,
        "parent": filter_parent,
        "labels": filter_labels,
        "assignees": filter_assignees,
        "created_by": filter_created_by,
        "name": filter_name,
        "created_at": filter_created_at,
        "updated_at": filter_updated_at,
        "start_date": filter_start_date,
        "target_date": filter_target_date,
        "completed_at": filter_completed_at,
        "type": filter_issue_state_type,
    }

    for key, value in ISSUE_FILTER.items():
        if key in query_params:
            func = value
            func(query_params, filter, method)

    return filter
