import React, { useEffect, useState } from "react";
import AccountsEdit from "./accountsEdit";
import { Column, TableData } from "../table/table";
import Table from "../table/table";
import Navbar from "./navbar";
import { getAccess, makeRequest } from "../../utils";
import { Account, ResponseBody, ViewProps } from "../../interfaces";
import { SmallLoader } from "../loader";
import AdminView from "../containers/admin/adminView";
import AdminContent from "../containers/admin/adminContent";
import Button from "../buttons/button";

/**
 * Functional component representing Accounts.
 */
const Accounts: React.FC<ViewProps> = ({ flashMessage, goBack, handleClick }) => {
  const [canCreate, setCanCreate] = useState(false);
  const [canEdit, setCanEdit] = useState(false);
  const [canArchive, setCanArchive] = useState(false);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [columns] = useState<Column[]>([
    {
      name: "Name",
      searchable: true,
      sortable: true,
      width: 20
    },
    {
      name: "Email",
      searchable: true,
      sortable: true,
      width: 25
    },
    {
      name: "Phone Number",
      searchable: true,
      sortable: true,
      width: 15
    },
    {
      name: "Created On",
      searchable: false,
      sortable: true,
      width: 15
    },
    {
      name: "Last Login",
      searchable: false,
      sortable: true,
      width: 15
    },
    {
      name: "",
      searchable: false,
      sortable: false,
      width: 10
    }
  ]);
  const [loading, setLoading] = useState(true);

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
        setAccounts(accounts);
      } catch (error) {
        console.error("Error fetching accounts:", error);
      }
    };

    Promise.all([fetchPermissions(), fetchAccounts()]).then(() => {
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
      day: "numeric"
    };

    return accounts.map((a: Account) => {
      const {
        createdOn,
        email,
        firstName,
        id,
        lastLogin,
        lastName,
        phoneNumber
      } = a;
      const name = firstName + " " + lastName;

      const ago = Math.floor(
        Math.abs(new Date().getTime() - new Date(lastLogin).getTime()) /
          (1000 * 60 * 60 * 24)
      );

      return [
        {
          contents: (
            <span>{name}</span>
          ),
          searchValue: name,
          sortValue: name
        },
        {
          contents: (
            <span>{email}</span>
          ),
          searchValue: email,
          sortValue: email
        },
        {
          contents: (
            <span>{phoneNumber}</span>
          ),
          searchValue: phoneNumber,
          sortValue: phoneNumber
        },
        {
          contents: (
            <span>
              {new Date(createdOn).toLocaleDateString("en-US", dateOptions)}
            </span>
          ),
          searchValue: "",
          sortValue: createdOn
        },
        {
          contents: (
            <span>
              {lastLogin
                ? ago
                  ? `${ago} day${ago === 1 ? "" : "s"} ago`
                  : "Today"
                : "Never"}
            </span>
          ),
          searchValue: "",
          sortValue: ""
        },
        {
          contents: (
            <>
              {canEdit &&
                <Button
                  variant="secondary"
                  size="sm"
                  className="h-full flex-grow"
                  onClick={() =>
                    handleClick(
                      ["Edit", name],
                      <AccountsEdit
                        accountId={id}
                        flashMessage={flashMessage}
                        goBack={goBack}
                        handleClick={handleClick} />
                    )
                  }>
                    Edit
                </Button>
              }
              {canArchive &&
                <Button
                  variant="danger"
                  size="sm"
                  className="h-full flex-grow"
                  onClick={() => deleteAccount(id)}>
                    Archive
                </Button>
              }
            </>
          ),
          searchValue: "",
          sortValue: "",
          paddingX: 0,
          paddingY: 0,
        }
      ];
    });
  };

  /**
   * Delete a table entry and archive it in the database
   * @param id - the entry's database primary key
   */
  const deleteAccount = (id: number): void => {
    const body = { app: 1, id };  // Admin Dashboard = 1
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
    makeRequest("/admin/account?app=1").then((accounts) =>
      setAccounts(accounts)
    ).finally(() => setLoading(false));
  };

  /**
   * Handle a failed response
   * @param res - the response body
   */
  const handleFailure = (res: ResponseBody) => {
    const msg = (
      <span>
        <b>An unexpected error occured</b>
        <br />
        {res.msg ? res.msg : "Internal server error"}
      </span>
    );

    flashMessage(msg, "danger");
  };

  // If the user has permission to create, show the create button
  const tableControl = canCreate ? (
    <Button
      variant="primary"
      onClick={() =>
        handleClick(
          ["Create"],
          <AccountsEdit
            accountId={0}
            flashMessage={flashMessage}
            goBack={goBack}
            handleClick={handleClick} />
        )
      } >
        Create +
    </Button>
  ) : <React.Fragment />;

  const navbar =
    <Navbar
      active="Accounts"
      flashMessage={flashMessage}
      goBack={goBack}
      handleClick={handleClick} />;

  if (loading) {
    return (
      <AdminView>
        {navbar}
        <AdminContent>
          <SmallLoader />
        </AdminContent>
      </AdminView>
    );
  }

  return (
    <AdminView>
      {navbar}
      <AdminContent>
        <Table
          columns={columns}
          control={tableControl}
          controlWidth={10}
          data={getData()}
          includeControl={true}
          includeSearch={true}
          paginationPer={10}
          sortDefault="" />
      </AdminContent>
    </AdminView>
  );
};

export default Accounts;
