import { FC } from "react";
// types
import { IIntegrationData } from "components/integration";

type Props = { state: IIntegrationData; handleState: (key: string, valve: any) => void };

export const GithubImportData: FC<Props> = ({ state, handleState }) => (
  <div className="space-y-5">
    <div className="space-y-8 py-5">
      <div className="flex items-center gap-2">
        <div className="w-full space-y-1">
          <div className="font-medium">Repository Name</div>
          <div className="text-sm text-gray-600">
            Select the repository name that you want to import.
          </div>
        </div>
        <div className="w-full">Dropdown all repositories</div>
      </div>

      <div className="flex items-center gap-2">
        <div className="w-full space-y-1">
          <div className="font-medium">Import to Plane project</div>
          <div className="text-sm text-gray-600">Select the plane project.</div>
        </div>
        <div className="w-full">Dropdown all Projects</div>
      </div>

      <div className="flex items-center gap-2">
        <div className="w-full space-y-1">
          <div className="font-medium">Do you want to Import all the closed issues too?</div>
        </div>
        <div className="w-full">Switch button</div>
      </div>
    </div>

    <div className="flex items-center justify-end gap-2">
      <button
        type="button"
        className={`rounded-sm bg-gray-200 px-3 py-1.5 text-sm text-black transition-colors hover:bg-opacity-80`}
        onClick={() => handleState("state", "import-configure")}
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
        onClick={() => handleState("state", "migrate-issues")}
        disabled={state?.currentIntegration && state?.currentIntegration?.id ? false : true}
      >
        Next
      </button>
    </div>
  </div>
);
