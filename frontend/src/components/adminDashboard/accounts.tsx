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
import { getAccess, makeRequest } from "../../utils";
import { Account, ResponseBody } from "../../types/api";
import { SmallLoader } from "../loader/loader";
import { ListView } from "../containers/lists/listView";
import { ListContent } from "../containers/lists/listContent";
import { Button } from "../buttons/button";
import { Link } from "react-router-dom";
import { useFlashMessages } from "../../hooks/useFlashMessages";

/**
 * Functional component representing Accounts.
 */
export const Accounts = () => {
  const [canCreate, setCanCreate] = useState(false);
  const [canEdit, setCanEdit] = useState(false);
  const [canArchive, setCanArchive] = useState(false);
  const [accounts, setAccounts] = useState<Account[]>([]);
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
  const [loading, setLoading] = useState(true);
  const { flashMessage } = useFlashMessages();

  useEffect(() => {
    // Check user permissions
    const fetchPermissions = async () => {
      try {
        await getAccess(1, "Create", "Accounts");
        setCanCreate(true);
      } catch {
        setCanCreate(false);
      }

      try {
        await getAccess(1, "Edit", "Accounts");
        setCanEdit(true);
      } catch {
        setCanEdit(false);
      }

      try {
        await getAccess(1, "Archive", "Accounts");
        setCanArchive(true);
      } catch {
        setCanArchive(false);
      }
    };

    // Fetch account data
    const fetchAccounts = async () => {
      try {
        const accounts = await makeRequest("/admin/account?app=1");
        setAccounts(accounts as unknown as Account[]);
      } catch (error) {
        console.error("Error fetching accounts:", error);
      }
    };

    void Promise.all([fetchPermissions(), fetchAccounts()]).then(() => {
      setLoading(false);
    });
  }, []);

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
                    deleteAccount(id);
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
  const deleteAccount = (id: number): void => {
    const body = { app: 1, id }; // Admin Dashboard = 1
    const opts = { method: "POST", body: JSON.stringify(body) };

    const msg = "Are you sure you want to archive this account?";

    if (confirm(msg)) {
      makeRequest("/admin/account/archive", opts)
        .then(handleSuccess)
        .catch(handleFailure);
    }
  };

  /**
   * Handle a successful response
   * @param res - the response body
   */
  const handleSuccess = (res: ResponseBody) => {
    flashMessage(<span>{res.msg}</span>, "success");
    setLoading(true);

    // Refresh the table's data
    void makeRequest("/admin/account?app=1")
      .then((accounts) => {
        setAccounts(accounts as unknown as Account[]);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  /**
   * Handle a failed response
   * @param res - the response body
   */
  const handleFailure = (res: ResponseBody) => {
    const msg = (
      <span>
        <b>An unexpected error occurred</b>
        <br />
        {res.msg ? res.msg : "Internal server error"}
      </span>
    );

    flashMessage(msg, "danger");
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

  if (loading) {
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
