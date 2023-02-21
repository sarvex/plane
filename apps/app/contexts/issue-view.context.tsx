import { createContext, useCallback, useEffect, useReducer } from "react";

import { useRouter } from "next/router";

import useSWR, { mutate } from "swr";

// components
import ToastAlert from "components/toast-alert";
// services
import projectService from "services/project.service";
// types
import type { IIssueFilterParams, TIssueGroupBy, TIssueOrderBy, TIssueType } from "types";
// fetch-keys
import { USER_PROJECT_VIEW, PROJECT_ISSUES_LIST } from "constants/fetch-keys";

export const issueViewContext = createContext<ContextType>({} as ContextType);

type IssueViewProps = {
  issueView: "list" | "kanban" | null;
  groupByProperty: TIssueGroupBy;
  filterIssue: TIssueType;
  orderBy: TIssueOrderBy;
};

type ReducerActionType = {
  type:
    | "REHYDRATE_THEME"
    | "SET_ISSUE_VIEW"
    | "SET_ORDER_BY_PROPERTY"
    | "SET_FILTER_ISSUES"
    | "SET_GROUP_BY_PROPERTY"
    | "RESET_TO_DEFAULT";
  payload?: Partial<IssueViewProps>;
};

type ContextType = {
  orderBy: TIssueOrderBy;
  issueView: "list" | "kanban" | null;
  groupByProperty: TIssueGroupBy;
  filterIssue: TIssueType;
  setGroupByProperty: (property: TIssueGroupBy) => void;
  setOrderBy: (property: TIssueOrderBy) => void;
  setFilterIssue: (property: TIssueType) => void;
  resetFilterToDefault: () => void;
  setNewFilterDefaultView: () => void;
  setIssueViewToKanban: () => void;
  setIssueViewToList: () => void;
};

type StateType = IIssueFilterParams & {
  issueView: "list" | "kanban" | null;
};

type ReducerFunctionType = (state: StateType, action: ReducerActionType) => StateType;

export const initialState: StateType = {
  issueView: "list",
  group_by: null,
  order_by: "created_at",
  type: "all",
};

export const reducer: ReducerFunctionType = (state, action) => {
  const { type, payload } = action;

  switch (type) {
    case "REHYDRATE_THEME": {
      let collapsed: any = localStorage.getItem("collapsed");
      collapsed = collapsed ? JSON.parse(collapsed) : false;
      return { ...initialState, ...payload, collapsed };
    }

    case "SET_ISSUE_VIEW": {
      const newState = {
        ...state,
        issueView: payload?.issueView || "list",
      };
      return {
        ...state,
        ...newState,
      };
    }

    case "SET_GROUP_BY_PROPERTY": {
      const newState = {
        ...state,
        group_by: payload?.groupByProperty || null,
      };
      return {
        ...state,
        ...newState,
      };
    }

    case "SET_ORDER_BY_PROPERTY": {
      const newState = {
        ...state,
        order_by: payload?.orderBy || null,
      };
      return {
        ...state,
        ...newState,
      };
    }

    case "SET_FILTER_ISSUES": {
      const newState = {
        ...state,
        type: payload?.filterIssue || "all",
      };
      return {
        ...state,
        ...newState,
      };
    }

    case "RESET_TO_DEFAULT": {
      return {
        ...initialState,
        ...payload,
      };
    }

    default: {
      return state;
    }
  }
};

const saveDataToServer = async (workspaceSlug: string, projectID: string, state: any) => {
  await projectService.setProjectView(workspaceSlug, projectID, {
    view_props: state,
  });
};

const setNewDefault = async (workspaceSlug: string, projectID: string, state: any) => {
  await projectService.setProjectView(workspaceSlug, projectID, {
    view_props: state,
    default_props: state,
  });
};

export const IssueViewContextProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialState);

  const router = useRouter();
  const { workspaceSlug, projectId } = router.query;

  const { data: myViewProps, mutate: mutateMyViewProps } = useSWR(
    workspaceSlug && projectId ? USER_PROJECT_VIEW(projectId as string) : null,
    workspaceSlug && projectId
      ? () => projectService.projectMemberMe(workspaceSlug as string, projectId as string)
      : null
  );

  const setIssueViewToKanban = useCallback(() => {
    dispatch({
      type: "SET_ISSUE_VIEW",
      payload: {
        issueView: "kanban",
      },
    });
    dispatch({
      type: "SET_GROUP_BY_PROPERTY",
      payload: {
        groupByProperty: "state",
      },
    });

    if (!workspaceSlug || !projectId) return;
    mutate(PROJECT_ISSUES_LIST(workspaceSlug as string, projectId as string));
    saveDataToServer(workspaceSlug as string, projectId as string, {
      ...state,
      issueView: "kanban",
      groupByProperty: "state",
    });
  }, [workspaceSlug, projectId, state]);

  const setIssueViewToList = useCallback(() => {
    dispatch({
      type: "SET_ISSUE_VIEW",
      payload: {
        issueView: "list",
      },
    });
    dispatch({
      type: "SET_GROUP_BY_PROPERTY",
      payload: {
        groupByProperty: null,
      },
    });

    if (!workspaceSlug || !projectId) return;
    mutate(PROJECT_ISSUES_LIST(workspaceSlug as string, projectId as string));
    saveDataToServer(workspaceSlug as string, projectId as string, {
      ...state,
      issueView: "list",
      groupByProperty: null,
    });
  }, [workspaceSlug, projectId, state]);

  const setGroupByProperty = useCallback(
    (property: TIssueGroupBy | null) => {
      dispatch({
        type: "SET_GROUP_BY_PROPERTY",
        payload: {
          groupByProperty: property,
        },
      });

      if (!workspaceSlug || !projectId) return;
      mutate(PROJECT_ISSUES_LIST(workspaceSlug as string, projectId as string));
      saveDataToServer(workspaceSlug as string, projectId as string, {
        ...state,
        groupByProperty: property,
      });
    },
    [projectId, workspaceSlug, state]
  );

  const setOrderBy = useCallback(
    (property: TIssueOrderBy) => {
      dispatch({
        type: "SET_ORDER_BY_PROPERTY",
        payload: {
          orderBy: property,
        },
      });

      if (!workspaceSlug || !projectId) return;
      mutate(PROJECT_ISSUES_LIST(workspaceSlug as string, projectId as string));
      saveDataToServer(workspaceSlug as string, projectId as string, state);
    },
    [projectId, workspaceSlug, state]
  );

  const setFilterIssue = useCallback(
    (property: TIssueType) => {
      dispatch({
        type: "SET_FILTER_ISSUES",
        payload: {
          filterIssue: property,
        },
      });

      if (!workspaceSlug || !projectId) return;
      mutate(PROJECT_ISSUES_LIST(workspaceSlug as string, projectId as string));
      saveDataToServer(workspaceSlug as string, projectId as string, {
        ...state,
        filterIssue: property,
      });
    },
    [projectId, workspaceSlug, state]
  );

  const setNewDefaultView = useCallback(() => {
    if (!workspaceSlug || !projectId) return;
    setNewDefault(workspaceSlug as string, projectId as string, state).then(() => {
      mutateMyViewProps();
    });
  }, [projectId, workspaceSlug, state, mutateMyViewProps]);

  const resetToDefault = useCallback(() => {
    dispatch({
      type: "RESET_TO_DEFAULT",
      payload: myViewProps?.default_props,
    });

    if (!workspaceSlug || !projectId) return;
    mutate(PROJECT_ISSUES_LIST(workspaceSlug as string, projectId as string));
    saveDataToServer(workspaceSlug as string, projectId as string, myViewProps?.default_props);
  }, [projectId, workspaceSlug, myViewProps]);

  useEffect(() => {
    dispatch({
      type: "REHYDRATE_THEME",
      payload: myViewProps?.view_props,
    });
  }, [myViewProps]);

  return (
    <issueViewContext.Provider
      value={{
        issueView: state.issueView,
        groupByProperty: state.group_by,
        setGroupByProperty,
        orderBy: state.order_by,
        setOrderBy,
        filterIssue: state.type,
        setFilterIssue,
        resetFilterToDefault: resetToDefault,
        setNewFilterDefaultView: setNewDefaultView,
        setIssueViewToKanban,
        setIssueViewToList,
      }}
    >
      <ToastAlert />
      {children}
    </issueViewContext.Provider>
  );
};
