// types
import { TIssueType, TIssueGroupBy, TIssueOrderBy } from "types";

export const GROUP_BY_OPTIONS: Array<{ name: string; key: TIssueGroupBy }> = [
  { name: "State", key: "state" },
  { name: "Priority", key: "priority" },
  { name: "Assignee", key: "assignees" },
  { name: "None", key: null },
];

export const ORDER_BY_OPTIONS: Array<{ name: string; key: TIssueOrderBy }> = [
  // { name: "Manual", key: "manual" },
  { name: "Last created", key: "created_at" },
  { name: "Last updated", key: "updated_at" },
  { name: "Priority", key: "priority" },
  // { name: "None", key: null },
];

export const FILTER_ISSUE_OPTIONS: Array<{
  name: string;
  key: TIssueType;
}> = [
  {
    name: "All",
    key: "all",
  },
  {
    name: "Active Issues",
    key: "active",
  },
  {
    name: "Backlog Issues",
    key: "backlog",
  },
];
