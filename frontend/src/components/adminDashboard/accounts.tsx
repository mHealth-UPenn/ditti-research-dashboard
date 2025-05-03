/* Copyright 2025 The Trustees of the University of Pennsylvania
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may]
 * not use this file except in compliance with the License. You may obtain a
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

import React, { useEffect, useState } from "react";
import { Column, TableData } from "../table/table.types";
import { Table } from "../table/table";
import { AdminNavbar } from "./adminNavbar";
import { httpClient } from "../../lib/http";
import { Account, ResponseBody } from "../../types/api";
import { SmallLoader } from "../loader/loader";
import { ListView } from "../containers/lists/listView";
import { ListContent } from "../containers/lists/listContent";
import { Button } from "../buttons/button";
import { Link } from "react-router-dom";
import { useApiHandler } from "../../hooks/useApiHandler";

/**
 * Functional component representing Accounts.
 */
export const Accounts = () => {
  const [canCreate, setCanCreate] = useState(false);
  const [canEdit, setCanEdit] = useState(false);
  const [canArchive, setCanArchive] = useState(false);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [refreshKey, setRefreshKey] = useState(0);
  const [columns] = useState<Column[]>([
    {
      name: "Name",
      searchable: true,
      sortable: true,
      width: 20,
    },
    {
      name: "Email",
      searchable: true,
      sortable: true,
      width: 25,
    },
    {
      name: "Phone Number",
      searchable: true,
      sortable: true,
      width: 15,
    },
    {
      name: "Created On",
      searchable: false,
      sortable: true,
      width: 15,
    },
    {
      name: "Last Login",
      searchable: false,
      sortable: true,
      width: 15,
    },
    {
      name: "",
      searchable: false,
      sortable: false,
      width: 10,
    },
  ]);

  // API handler for fetching initial data (permissions and accounts)
  const { safeRequest: safeFetchData, isLoading: isLoadingData } =
    useApiHandler<{
      accounts: Account[];
      permissions: { create: boolean; edit: boolean; archive: boolean };
    }>({
      errorMessage: "Failed to load account data or permissions.",
      showDefaultSuccessMessage: false, // No success message needed for initial load
    });

  // API handler for archiving an account
  const { safeRequest: safeArchive } = useApiHandler<ResponseBody>({
    successMessage: (data) => data.msg,
    errorMessage: (error) => `Failed to archive account: ${error.message}`,
    onSuccess: () => {
      // Trigger a refresh of the account list
      setRefreshKey((prev) => prev + 1);
    },
  });

  useEffect(() => {
    const initialFetch = async () => {
      const fetchedData = await safeFetchData(async () => {
        // Define permission check requests
        // We assume a successful response means access granted, catch handles denial
        const checkPermission = async (
          appId: number,
          action: string,
          resource: string
        ): Promise<boolean> => {
          const url = `/auth/researcher/get-access?app=${String(appId)}&action=${action}&resource=${resource}`;
          try {
            // Make GET request and check response message
            const res = await httpClient.request<ResponseBody>(url); // GET is default
            return res.msg === "Authorized";
          } catch {
            return false; // Access denied or other error
          }
        };

        const adminAppId = 1; // Admin Dashboard = 1
        const createPerm = checkPermission(adminAppId, "Create", "Accounts");
        const editPerm = checkPermission(adminAppId, "Edit", "Accounts");
        const archivePerm = checkPermission(adminAppId, "Archive", "Accounts");

        // Define accounts fetch request
        const accountsReq = httpClient.request<Account[]>(
          "/admin/account?app=1"
        );

        // Execute all requests in parallel
        const [canCreate, canEdit, canArchive, accountsData] =
          await Promise.all([createPerm, editPerm, archivePerm, accountsReq]);

        // Return data for the hook to handle state updates
        return {
          accounts: accountsData,
          permissions: {
            create: canCreate,
            edit: canEdit,
            archive: canArchive,
          },
        };
      });

      // Update state if fetching was successful
      if (fetchedData) {
        setAccounts(fetchedData.accounts);
        setCanCreate(fetchedData.permissions.create);
        setCanEdit(fetchedData.permissions.edit);
        setCanArchive(fetchedData.permissions.archive);
      }
    };

    void initialFetch();
  }, [safeFetchData, refreshKey]);

  /**
   * Get the table's contents
   * @returns The table's contents, consisting of rows of table cells
   */
  const getData = (): TableData[][] => {
    const dateOptions: Intl.DateTimeFormatOptions = {
      year: "numeric",
      month: "short",
      day: "numeric",
    };

    return accounts.map((a: Account) => {
      const {
        createdOn,
        email,
        firstName,
        id,
        lastLogin,
        lastName,
        phoneNumber,
      } = a;
      const name = firstName + " " + lastName;

      const ago = Math.floor(
        Math.abs(new Date().getTime() - new Date(lastLogin).getTime()) /
          (1000 * 60 * 60 * 24)
      );

      return [
        {
          contents: <span>{name}</span>,
          searchValue: name,
          sortValue: name,
        },
        {
          contents: <span>{email}</span>,
          searchValue: email,
          sortValue: email,
        },
        {
          contents: <span>{phoneNumber}</span>,
          searchValue: phoneNumber,
          sortValue: phoneNumber,
        },
        {
          contents: (
            <span>
              {new Date(createdOn).toLocaleDateString("en-US", dateOptions)}
            </span>
          ),
          searchValue: "",
          sortValue: createdOn,
        },
        {
          contents: (
            <span>
              {lastLogin
                ? ago
                  ? `${String(ago)} day${ago === 1 ? "" : "s"} ago`
                  : "Today"
                : "Never"}
            </span>
          ),
          searchValue: "",
          sortValue: "",
        },
        {
          contents: (
            <div className="flex size-full">
              {canEdit && (
                <Button
                  variant="secondary"
                  size="sm"
                  className="h-full grow"
                  fullWidth={true}
                  fullHeight={true}
                >
                  <Link
                    className="flex size-full items-center justify-center"
                    to={`/coordinator/admin/accounts/edit?id=${String(id)}`}
                  >
                    Edit
                  </Link>
                </Button>
              )}
              {canArchive && (
                <Button
                  variant="danger"
                  size="sm"
                  className="h-full grow"
                  onClick={() => {
                    void deleteAccount(id);
                  }}
                >
                  Archive
                </Button>
              )}
            </div>
          ),
          searchValue: "",
          sortValue: "",
          paddingX: 0,
          paddingY: 0,
        },
      ];
    });
  };

  /**
   * Delete a table entry and archive it in the database
   * @param id - the entry's database primary key
   */
  const deleteAccount = async (id: number) => {
    const body = { app: 1, id }; // Admin Dashboard = 1
    const msg = "Are you sure you want to archive this account?";

    if (confirm(msg)) {
      await safeArchive(() =>
        httpClient.request<ResponseBody>("/admin/account/archive", {
          method: "POST",
          data: body,
        })
      );
    }
  };

  // If the user has permission to create, show the create button
  const tableControl = canCreate ? (
    <Link to={`/coordinator/admin/accounts/create`}>
      <Button variant="primary">Create +</Button>
    </Link>
  ) : (
    <React.Fragment />
  );

  const navbar = <AdminNavbar activeView="Accounts" />;

  if (isLoadingData) {
    return (
      <ListView>
        {navbar}
        <ListContent>
          <SmallLoader />
        </ListContent>
      </ListView>
    );
  }

  return (
    <ListView>
      {navbar}
      <ListContent>
        <Table
          columns={columns}
          control={tableControl}
          controlWidth={10}
          data={getData()}
          includeControl={true}
          includeSearch={true}
          paginationPer={10}
          sortDefault=""
        />
      </ListContent>
    </ListView>
  );
};
