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
import AdminView from "../containers/admin/adminView";
import AdminContent from "../containers/admin/adminContent";

const AboutSleepTemplates: React.FC<ViewProps> = ({
  flashMessage,
  goBack,
  handleClick,
}) => {
  const [canCreate, setCanCreate] = useState(false);
  const [canEdit, setCanEdit] = useState(false);
  const [canArchive, setCanArchive] = useState(false);
  const [aboutSleepTemplates, setAboutSleepTemplates] = useState<
    AboutSleepTemplate[]
  >([]);
  const [loading, setLoading] = useState(true);

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
            <>
              {canEdit &&
                <Button
                  variant="secondary"
                  size="sm"
                  className="h-full flex-grow"
                  onClick={() =>
                    handleClick(
                      ["Edit", name],
                      <AboutSleepTemplatesEdit
                        aboutSleepTemplateId={id}
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
                  onClick={() => deleteTemplate(id)}>
                    Archive
                </Button>
              }
            </>
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
    <Button
      variant="primary"
      onClick={() =>
        handleClick(
          ["Create"],
          <AboutSleepTemplatesEdit
            aboutSleepTemplateId={0}
            flashMessage={flashMessage}
            goBack={goBack}
            handleClick={handleClick} />
        )
      }>
        Create +
    </Button> :
    <React.Fragment />;

  const navbar =
    <Navbar
      active="About Sleep Templates"
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

export default AboutSleepTemplates;
