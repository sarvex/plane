import { FC, useEffect, useState } from "react";
// next imports
import Link from "next/link";
import Image from "next/image";
// swr
import useSWR from "swr";
// icons
import GithubLogo from "public/logos/github-square.png";
import { CogIcon, CloudUploadIcon, UsersIcon, ImportLayersIcon, CheckIcon } from "components/icons";
import { ArrowLeftIcon } from "@heroicons/react/24/outline";
// components
import {
  GithubConfigure,
  GithubImportData,
  GithubIssuesSelect,
  GithubUsersSelect,
  GithubConfirm,
} from "components/integration";
// types
import { IAppIntegrations } from "types";
// api services
import GithubIntegrationService from "services/integration/github.service";

type Props = {
  workspaceSlug: string | undefined;
  provider: string | undefined;
  allIntegrations: IAppIntegrations[] | undefined;
  allIntegrationsError: Error | undefined;
  allWorkspaceIntegrations: any | undefined;
  allWorkspaceIntegrationsError: Error | undefined;
  allIntegrationImporters: any | undefined;
  allIntegrationImportersError: Error | undefined;
};

export interface IIntegrationData {
  state: string;
  currentIntegration: any;
  repositoryId: string | null;
  projectId: string | null;
}

export const GithubIntegrationRoot: FC<Props> = ({
  workspaceSlug,
  provider,
  allIntegrations,
  allIntegrationsError,
  allWorkspaceIntegrations,
  allWorkspaceIntegrationsError,
  allIntegrationImporters,
  allIntegrationImportersError,
}) => {
  const integrationWorkflowData = [
    {
      title: "Configure",
      key: "import-configure",
      icon: CogIcon,
    },
    {
      title: "Import Data",
      key: "import-import-data",
      icon: CloudUploadIcon,
    },
    { title: "Issues", key: "migrate-issues", icon: ImportLayersIcon },
    {
      title: "Users",
      key: "migrate-users",
      icon: UsersIcon,
    },
    {
      title: "Confirm",
      key: "migrate-confirm",
      icon: CheckIcon,
    },
  ];
  const activeIntegrationState = () => {
    const currentElementIndex = integrationWorkflowData.findIndex(
      (_item) => _item?.key === integrationData?.state
    );

    return currentElementIndex;
  };

  const [integrationData, setIntegrationData] = useState<IIntegrationData>({
    state: "import-configure",
    currentIntegration: null,
    repositoryId: null,
    projectId: null,
  });
  const handleIntegrationData = (key: string, value: any) => {
    setIntegrationData((previousData) => ({ ...previousData, [key]: value }));
  };

  console.log("integrationData", integrationData);

  // fetching github repositories
  // const { data: githubRepositories, error: githubRepositoriesError } = useSWR<
  //   IAppIntegrations[] | undefined,
  //   Error
  // >(
  //   integrationData && integrationData?.currentIntegration != null && workspaceSlug
  //     ? `ALL_INTEGRATIONS_${workspaceSlug.toUpperCase()}`
  //     : null,
  //   integrationData && integrationData?.currentIntegration != null && workspaceSlug
  //     ? () =>
  //         GithubIntegrationService.listAllRepositories(
  //           workspaceSlug,
  //           integrationData?.currentIntegration?.integration
  //         )
  //     : null
  // );

  // console.log("githubRepositories", githubRepositories);

  // fetching all the projects under the workspace
  // const { data: workspaceProjects, error: workspaceProjectsError } = useSWR<
  //   IAppIntegrations[] | undefined,
  //   Error
  // >(
  //   workspaceSlug ? `ALL_INTEGRATIONS_${workspaceSlug.toUpperCase()}` : null,
  //   workspaceSlug ? () => WorkspaceIntegrationService.listAllIntegrations() : null
  // );

  useEffect(() => {
    if (
      integrationData?.currentIntegration === null &&
      allIntegrations &&
      allIntegrations.length > 0 &&
      allWorkspaceIntegrations &&
      allWorkspaceIntegrations.length > 0
    ) {
      const currentIntegration =
        allIntegrations &&
        allIntegrations.length > 0 &&
        allIntegrations.find((_integration) => _integration.provider === provider);

      if (currentIntegration)
        setIntegrationData((previousData) => ({
          ...previousData,
          currentIntegration: allWorkspaceIntegrations.find(
            (_integration: any) => _integration.integration_detail.id === currentIntegration.id
          ),
        }));
    }
  }, [allIntegrations, allWorkspaceIntegrations, provider, integrationData]);

  return (
    <div className="space-y-4">
      <Link href={`/${workspaceSlug}/settings/import-export`}>
        <div className="inline-flex cursor-pointer items-center gap-2 text-sm font-medium text-gray-600 hover:text-gray-900">
          <div>
            <ArrowLeftIcon className="h-3 w-3" />
          </div>
          <div>Back</div>
        </div>
      </Link>

      <div className="space-y-4 rounded border border-gray-200 bg-white p-4">
        <div className="flex items-center gap-2">
          <div className="h-10 w-10 flex-shrink-0">
            <Image src={GithubLogo} alt="GithubLogo" />
          </div>
          <div className="flex h-full w-full items-center justify-center">
            {integrationWorkflowData.map((_integration, _idx) => (
              <>
                <div
                  key={_integration?.key}
                  className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full border
              ${
                _idx <= activeIntegrationState()
                  ? `border-[#3F76FF] bg-[#3F76FF] text-white ${
                      _idx === activeIntegrationState()
                        ? `border-opacity-100 bg-opacity-100`
                        : `border-opacity-80 bg-opacity-80`
                    }`
                  : `border-gray-300`
              }
              `}
                >
                  <_integration.icon
                    width={`18px`}
                    height={`18px`}
                    color={_idx <= activeIntegrationState() ? "#ffffff" : "#d1d5db"}
                  />
                </div>
                {_idx < integrationWorkflowData.length - 1 && (
                  <div
                    key={_idx}
                    className={`border-b  px-7 ${
                      _idx <= activeIntegrationState() - 1 ? `border-[#3F76FF]` : `border-gray-300`
                    }`}
                  >
                    {" "}
                  </div>
                )}
              </>
            ))}
          </div>
        </div>

        <div className="relative w-full space-y-4 overflow-hidden">
          <div className="w-full">
            {integrationData?.state === "import-configure" && (
              <GithubConfigure
                state={integrationData}
                handleState={handleIntegrationData}
                workspaceSlug={workspaceSlug}
              />
            )}
            {integrationData?.state === "import-import-data" && (
              <GithubImportData
                state={integrationData}
                handleState={handleIntegrationData}
                // workspaceSlug={workspaceSlug}
                // provider={provider}
                // allIntegrations={allIntegrations}
                // allIntegrationsError={allIntegrationsError}
                // allWorkspaceIntegrations={allWorkspaceIntegrations}
                // allWorkspaceIntegrationsError={allWorkspaceIntegrationsError}
              />
            )}
            {integrationData?.state === "migrate-issues" && (
              <GithubIssuesSelect state={integrationData} handleState={handleIntegrationData} />
            )}
            {integrationData?.state === "migrate-users" && (
              <GithubUsersSelect state={integrationData} handleState={handleIntegrationData} />
            )}
            {integrationData?.state === "migrate-confirm" && (
              <GithubConfirm state={integrationData} handleState={handleIntegrationData} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
