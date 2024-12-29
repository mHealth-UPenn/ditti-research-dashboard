import React, { useEffect, useState } from "react";
import { Column, TableData } from "../table/table";
import Table from "../table/table";
import { getAccess } from "../../utils";
import { IStudySubjectDetails, Study, UserDetails, ViewProps } from "../../interfaces";
import { SmallLoader } from "../loader";
import SubjectsEdit from "./wearableSubjectsEdit";
import { APP_ENV } from "../../environment";
import Button from "../buttons/button";
import ViewContainer from "../containers/viewContainer";
import Card from "../cards/card";
import LinkComponent from "../links/linkComponent";
import Title from "../text/title";
import Subtitle from "../text/subtitle";
import ListView from "../containers/lists/listView";
import ListContent from "../containers/lists/listContent";
import { useDittiDataContext } from "../../contexts/dittiDataContext";
import { useCoordinatorStudySubjectContext } from "../../contexts/coordinatorStudySubjectContext";
import { Link, useSearchParams } from "react-router-dom";
import { useStudiesContext } from "../../contexts/studiesContext";
import SubjectsContent from "../subjects/subjectsContent";


const WearableSubjects = () => {
  return <SubjectsContent app={"wearable"} />;
};


export default WearableSubjects;
