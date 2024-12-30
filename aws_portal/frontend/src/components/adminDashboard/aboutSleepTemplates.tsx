import React, { useState, useEffect } from "react";
import {
  AboutSleepTemplate,
  ResponseBody,
  ViewProps,
} from "../../interfaces";
import { getAccess, makeRequest } from "../../utils";
import Table, { Column, TableData } from "../table/table";
import Navbar from "./navbar";
import AboutSleepTemplatesEdit from "./aboutSleepTemplatesEdit";
import { SmallLoader } from "../loader";
import Button from "../buttons/button";
import ListView from "../containers/lists/listView";
import ListContent from "../containers/lists/listContent";
import { Link } from "react-router-dom";
import { useFlashMessageContext } from "../../contexts/flashMessagesContext";

const AboutSleepTemplates = () => {
  const [canCreate, setCanCreate] = useState(false);
  const [canEdit, setCanEdit] = useState(false);
  const [canArchive, setCanArchive] = useState(false);
  const [aboutSleepTemplates, setAboutSleepTemplates] = useState<
    AboutSleepTemplate[]
  >([]);
  const [loading, setLoading] = useState(true);
  const { flashMessage } = useFlashMessageContext();

  const columns: Column[] = [
    {
      name: "Name",
      searchable: true,
      sortable: true,
      width: 90,
    },
    {
      name: "",
      searchable: false,
      sortable: false,
      width: 10,
    },
  ];

  useEffect(() => {
    // check whether the user has permission to create
    const create = getAccess(1, "Create", "About Sleep Templates")
      .then(() => setCanCreate(true))
      .catch(() => setCanCreate(false));

    // check whether the user has permissions to edit
    const edit = getAccess(1, "Edit", "About Sleep Templates")
      .then(() => setCanEdit(true))
      .catch(() => setCanEdit(false));

    // check whether the user has permissions to archive
    const archive = getAccess(1, "Archive", "About Sleep Templates")
      .then(() => setCanArchive(true))
      .catch(() => setCanArchive(false));

    // get the table's data
    const fetchTemplates = makeRequest(
      "/admin/about-sleep-template?app=1"
    ).then((templates) => setAboutSleepTemplates(templates));

    // when all requests are complete, hide the loading screen
    Promise.all([create, edit, archive, fetchTemplates]).then(() =>
      setLoading(false)
    );
  }, []);

  /**
   * Get the table's contents
   * @returns The table's contents, consisting of rows of table cells
   */
  const getData = (): TableData[][] => {
    return aboutSleepTemplates.map((s: AboutSleepTemplate) => {
      const { id, name } = s;

      // map each row to a set of cells for each table column
      return [
        {
          contents: (
            <span>{name}</span>
          ),
          searchValue: name,
          sortValue: name,
        },
        {
          contents: (
            <div className="flex w-full h-full">
              {canEdit &&
                <Button
                  variant="secondary"
                  size="sm"
                  className="h-full flex-grow"
                  fullWidth={true}
                  fullHeight={true}>
                    <Link
                      className="w-full h-full flex items-center justify-center"
                      to={`/coordinator/admin/about-sleep-templates/edit?id=${id}`}>
                        Edit
                    </Link>
                </Button>
              }
              {canArchive &&
                <Button
                  variant="danger"
                  size="sm"
                  className="h-full flex-grow"
                  onClick={() => deleteTemplate(id)}>
                    Archive
                </Button>
              }
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
  const deleteTemplate = (id: number): void => {
    // prepare the request
    const body = { app: 1, id }; // Admin Dashboard = 1
    const opts = { method: "POST", body: JSON.stringify(body) };

    // confirm deletion
    const msg = "Are you sure you want to archive this about sleep template?";

    if (confirm(msg))
      makeRequest("/admin/about-sleep-template/archive", opts)
        .then(handleSuccess)
        .catch(handleFailure);
  };

  /**
   * Handle a successful response
   * @param res - the response body
   */
  const handleSuccess = (res: ResponseBody) => {
    // show the loading screen
    setLoading(true);
    flashMessage(<span>{res.msg}</span>, "success");

    // refresh the table's data
    makeRequest("/admin/about-sleep-template?app=1").then(
      (templates) => {
        setAboutSleepTemplates(templates);
        setLoading(false);
      }
    );
  };

  /**
   * Handle a failed response
   * @param res - the response body
   */
  const handleFailure = (res: ResponseBody) => {
    // flash the message returned from the endpoint or "Internal server error"
    const msg = (
      <span>
        <b>An unexpected error occurred</b>
        <br />
        {res.msg || "Internal server error"}
      </span>
    );

    flashMessage(msg, "danger");
  };

  // if the user has permission to create, show the create button
  const tableControl = canCreate ?
    <Link to={`/coordinator/admin/about-sleep-templates/create`}>
      <Button variant="primary">Create +</Button>
    </Link> :
    <React.Fragment />;

  const navbar = <Navbar active="About Sleep Templates" />;

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
          sortDefault="" />
      </ListContent>
    </ListView>
  );
};

export default AboutSleepTemplates;
