import React, { useState, useEffect, createRef } from "react";
import TextField from "../fields/textField";
import {
  AboutSleepTemplate,
  IStudySubjectDetails,
  ResponseBody,
  Study,
  StudySubjectPrefill,
  User,
  UserDetails,
  ViewProps
} from "../../interfaces";
import { getStartAndExpiryTimes, makeRequest } from "../../utils";
import CheckField from "../fields/checkField";
import { SmallLoader } from "../loader";
import Select from "../fields/select";
import FormView from "../containers/forms/formView";
import Form from "../containers/forms/form";
import FormSummary from "../containers/forms/formSummary";
import FormTitle from "../text/formTitle";
import FormRow from "../containers/forms/formRow";
import FormField from "../containers/forms/formField";
import FormSummaryTitle from "../text/formSummaryTitle";
import FormSummaryText from "../containers/forms/formSummaryText";
import FormSummaryButton from "../containers/forms/formSummaryButton";
import FormSummarySubtext from "../containers/forms/formSummarySubtext";
import FormSummaryContent from "../containers/forms/formSummaryContent";
import { APP_ENV } from "../../environment";
import { useDittiDataContext } from "../../contexts/dittiDataContext";
import sanitize from "sanitize-html";
import { useCoordinatorStudySubjectContext } from "../../contexts/coordinatorStudySubjectContext";
import { useSearchParams } from "react-router-dom";
import { useStudiesContext } from "../../contexts/studiesContext";
import SubjectsEditContent from "../subjects/subjectsEditContent";


const WearableSubjectsEdit = () => {
  return <SubjectsEditContent app={"wearable"} />
};


export default WearableSubjectsEdit;
