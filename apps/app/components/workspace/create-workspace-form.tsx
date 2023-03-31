import { Dispatch, SetStateAction, useEffect, useState } from "react";

import { mutate } from "swr";

// react-hook-form
import { Controller, useForm } from "react-hook-form";
// services
import workspaceService from "services/workspace.service";
// hooks
import useToast from "hooks/use-toast";
// ui
import { CustomSelect, Input, PrimaryButton } from "components/ui";
// types
import { IWorkspace } from "types";
// fetch-keys
import { USER_WORKSPACES } from "constants/fetch-keys";
// constants
import { COMPANY_SIZE } from "constants/workspace";

type Props = {
  onSubmit: (res: IWorkspace) => void;
  defaultValues: {
    name: string;
    slug: string;
    company_size: number | null;
  };
  setDefaultValues: Dispatch<SetStateAction<any>>;
};

export const CreateWorkspaceForm: React.FC<Props> = ({
  onSubmit,
  defaultValues,
  setDefaultValues,
}) => {
  const [slugError, setSlugError] = useState(false);

  const { setToastAlert } = useToast();

  const {
    register,
    handleSubmit,
    control,
    setValue,
    getValues,
    formState: { errors, isSubmitting },
  } = useForm<IWorkspace>({ defaultValues });

  const handleCreateWorkspace = async (formData: IWorkspace) => {
    await workspaceService
      .workspaceSlugCheck(formData.slug)
      .then(async (res) => {
        if (res.status === true) {
          setSlugError(false);
          await workspaceService
            .createWorkspace(formData)
            .then((res) => {
              setToastAlert({
                type: "success",
                title: "Success!",
                message: "Workspace created successfully.",
              });
              mutate<IWorkspace[]>(USER_WORKSPACES, (prevData) => [res, ...(prevData ?? [])]);
              onSubmit(res);
            })
            .catch((err) => {
              console.error(err);
            });
        } else setSlugError(true);
      })
      .catch(() => {
        setToastAlert({
          type: "error",
          title: "Error!",
          message: "Some error occurred while creating workspace. Please try again.",
        });
      });
  };

  useEffect(
    () => () => {
      // when the component unmounts set the default values to whatever user typed in
      setDefaultValues(getValues());
    },
    [getValues, setDefaultValues]
  );

  return (
    <form
      className="flex w-full items-center justify-center"
      onSubmit={handleSubmit(handleCreateWorkspace)}
    >
      <div className="flex w-full max-w-xl flex-col">
        <div className="flex flex-col rounded-[10px] bg-white shadow-md">
          <div className="flex flex-col justify-between gap-3 px-4 py-7">
            <div className="flex flex-col items-start justify-center gap-2.5">
              <span>Workspace name</span>
              <Input
                name="name"
                register={register}
                autoComplete="off"
                onChange={(e) =>
                  setValue("slug", e.target.value.toLocaleLowerCase().trim().replace(/ /g, "-"))
                }
                validations={{
                  required: "Workspace name is required",
                }}
                placeholder="e.g. My Workspace"
                error={errors.name}
              />
            </div>
            <div className="flex flex-col items-start justify-center gap-2.5">
              <span>Workspace URL</span>
              <div className="flex w-full items-center rounded-md border border-gray-300 px-3">
                <span className="text-sm text-slate-600">https://app.plane.so/</span>
                <Input
                  mode="trueTransparent"
                  autoComplete="off"
                  name="slug"
                  register={register}
                  className="block w-full rounded-md bg-transparent py-2 px-0 text-sm"
                />
              </div>
              {slugError && (
                <span className="-mt-3 text-sm text-red-500">Workspace URL is already taken!</span>
              )}
            </div>
          </div>

          <div className="flex flex-col items-start justify-center gap-2.5 border-t border-gray-300 px-4 py-7">
            <span>How large is your company</span>
            <div className="w-full">
              <Controller
                name="company_size"
                control={control}
                rules={{ required: "This field is required" }}
                render={({ field: { value, onChange } }) => (
                  <CustomSelect
                    value={value}
                    onChange={onChange}
                    label={value ? value.toString() : "Select company size"}
                    input
                    width="w-full"
                  >
                    {COMPANY_SIZE?.map((item) => (
                      <CustomSelect.Option key={item.value} value={item.value}>
                        {item.label}
                      </CustomSelect.Option>
                    ))}
                  </CustomSelect>
                )}
              />
              {errors.company_size && (
                <span className="text-sm text-red-500">{errors.company_size.message}</span>
              )}
            </div>
          </div>

          <div className="flex w-full items-center justify-center rounded-b-[10px] py-7">
            <PrimaryButton
              type="submit"
              className="flex w-1/2 items-center justify-center text-center"
              size="md"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Creating..." : "Create Workspace"}
            </PrimaryButton>
          </div>
        </div>
      </div>
    </form>
  );
};
