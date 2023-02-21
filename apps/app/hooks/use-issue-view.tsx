import { useContext, useEffect, useState } from "react";

import { useRouter } from "next/router";

import useSWR from "swr";

// contexts
import { issueViewContext } from "contexts/issue-view.context";
// types
import { IIssue } from "types";
// services
import issuesServices from "services/issues.service";
// fetch-keys
import { PROJECT_ISSUES_LIST } from "constants/fetch-keys";

const useIssueView = () => {
  const {
    issueView,
    groupByProperty,
    setGroupByProperty,
    orderBy,
    setOrderBy,
    filterIssue,
    setFilterIssue,
    resetFilterToDefault,
    setNewFilterDefaultView,
    setIssueViewToKanban,
    setIssueViewToList,
  } = useContext(issueViewContext);

  const [groupedByIssues, setGroupedByIssues] = useState<{
    [key: string]: IIssue[];
  } | null>(null);

  const router = useRouter();
  const { workspaceSlug, projectId } = router.query;

  const { data: issues } = useSWR(
    workspaceSlug && projectId
      ? PROJECT_ISSUES_LIST(workspaceSlug as string, projectId as string)
      : null,
    workspaceSlug && projectId
      ? () =>
          issuesServices.getIssues(workspaceSlug as string, projectId as string, {
            group_by: groupByProperty,
            order_by: orderBy,
            type: filterIssue,
          })
      : null
  );

  useEffect(() => {
    if (!issues) return;

    if (typeof issues === "object" && !Array.isArray(issues)) setGroupedByIssues(issues as any);
    else if (Array.isArray(issues)) setGroupedByIssues({ "All Issues": issues });
  }, [issues]);

  return {
    groupedByIssues,
    issueView,
    groupByProperty,
    setGroupByProperty,
    orderBy,
    setOrderBy,
    filterIssue,
    setFilterIssue,
    resetFilterToDefault,
    setNewFilterDefaultView,
    setIssueViewToKanban,
    setIssueViewToList,
  } as const;
};

export default useIssueView;
