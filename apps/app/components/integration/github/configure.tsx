import { FC } from "react";
// components
import { IIntegrationData, GithubAuth } from "components/integration";
// types
import { IAppIntegrations } from "types";

type Props = {
  state: IIntegrationData;
  handleState: (key: string, valve: any) => void;
  workspaceSlug: string | undefined;
};

export const GithubConfigure: FC<Props> = ({ state, handleState, workspaceSlug }) => (
  <div className="space-y-5">
    <div className="flex items-center gap-2 py-5">
      <div className="w-full">
        <div className="font-medium">Configure</div>
        <div className="text-sm text-gray-600">Set up your Github import</div>
      </div>
      <div className="flex-shrink-0">
        <GithubAuth
          workspaceSlug={workspaceSlug}
          workspaceIntegration={state?.currentIntegration}
        />
      </div>
    </div>

    <div className="flex items-center justify-end">
      <button
        type="button"
        className={`rounded-sm bg-theme px-3 py-1.5 text-sm text-white transition-colors hover:bg-opacity-80 ${
          state?.currentIntegration && state?.currentIntegration?.id
            ? `bg-opacity-100`
            : `cursor-not-allowed bg-opacity-80`
        }`}
        onClick={() => handleState("state", "import-import-data")}
        disabled={state?.currentIntegration && state?.currentIntegration?.id ? false : true}
      >
        Next
      </button>
    </div>
  </div>
);
