import { FC } from "react";
// types
import { IIntegrationData } from "components/integration";

type Props = { state: IIntegrationData; handleState: (key: string, valve: any) => void };

export const GithubIssuesSelect: FC<Props> = ({ state, handleState }) => (
  <div className="space-y-5">
    <div className="space-y-8 py-5">
      <div className="flex items-center gap-2">
        <div className="w-full space-y-1">
          <div className="font-medium">Import Data</div>
          <div className="text-sm text-gray-600">Import Completed. We have found:</div>
        </div>
        <div className="flex w-full items-center gap-2">
          <div className="w-full space-y-1 text-center">
            <div className="text-xl font-medium">0</div>
            <div className="text-sm text-gray-600">Issues</div>
          </div>
          <div className="w-full space-y-1 text-center">
            <div className="text-xl font-medium">0</div>
            <div className="text-sm text-gray-600">Labels</div>
          </div>
          <div className="w-full space-y-1 text-center">
            <div className="text-xl font-medium">0</div>
            <div className="text-sm text-gray-600">Workflows</div>
          </div>
          <div className="w-full space-y-1 text-center">
            <div className="text-xl font-medium">0</div>
            <div className="text-sm text-gray-600">Users</div>
          </div>
        </div>
      </div>
    </div>

    <div className="flex items-center justify-end gap-2">
      <button
        type="button"
        className={`rounded-sm bg-gray-200 px-3 py-1.5 text-sm text-black transition-colors hover:bg-opacity-80`}
        onClick={() => handleState("state", "import-import-data")}
      >
        Back
      </button>
      <button
        type="button"
        className={`rounded-sm bg-theme px-3 py-1.5 text-sm text-white transition-colors hover:bg-opacity-80 ${
          state?.currentIntegration && state?.currentIntegration?.id
            ? `bg-opacity-100`
            : `cursor-not-allowed bg-opacity-80`
        }`}
        onClick={() => handleState("state", "migrate-users")}
        disabled={state?.currentIntegration && state?.currentIntegration?.id ? false : true}
      >
        Next
      </button>
    </div>
  </div>
);
