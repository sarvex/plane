import { FC } from "react";
// types
import { IIntegrationData } from "components/integration";

type Props = { state: IIntegrationData; handleState: (key: string, valve: any) => void };

export const GithubUsersSelect: FC<Props> = ({ state, handleState }) => (
  <div className="space-y-5">
    <div className="space-y-4 py-5">
      <div className="flex items-center gap-2">
        <div className="w-full space-y-1">
          <div className="font-medium">Users</div>
          <div className="text-sm text-gray-600">
            Update, invite or choose not to invite assignee
          </div>
        </div>
        <div className="w-full">Switch button</div>
      </div>

      <div className="border-t border-gray-200"> </div>

      <div className="space-y-4">
        <div className="flex items-center">
          <div className="w-full text-sm font-medium text-gray-500">Name</div>
          <div className="w-full text-sm font-medium text-gray-500">Import as</div>
        </div>

        <div className="flex items-center">
          <div className="flex w-full items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-gray-100">
              {" "}
            </div>
            <div className="text-sm font-medium text-gray-500">Vihar Kurama</div>
          </div>
          <div className="w-full">User Dorpdown</div>
        </div>

        <div className="flex items-center">
          <div className="flex w-full items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-gray-100">
              {" "}
            </div>
            <div className="text-sm font-medium text-gray-500">Vihar Kurama</div>
          </div>
          <div className="w-full">User Dorpdown</div>
        </div>
      </div>
    </div>

    <div className="flex items-center justify-end gap-2">
      <button
        type="button"
        className={`rounded-sm bg-gray-200 px-3 py-1.5 text-sm text-black transition-colors hover:bg-opacity-80`}
        onClick={() => handleState("state", "migrate-issues")}
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
        onClick={() => handleState("state", "migrate-confirm")}
        disabled={state?.currentIntegration && state?.currentIntegration?.id ? false : true}
      >
        Next
      </button>
    </div>
  </div>
);
