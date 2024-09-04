import * as React from "react";
import { Component } from "react";
import {
  Study,
  TapDetails,
  User,
  UserDetails,
  ViewProps
} from "../../interfaces";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import { add, differenceInDays, isWithinInterval, sub } from "date-fns";
import "./studySubjects.css";
import SubjectVisuals from "./subjectVisuals";
import { dummyUsers } from "../dummyData";
import { loadavg } from "os";

/**
 * studyPrefix: the ditti app prefix of the current study
 * getTaps: get tap data
 * studyDetials: the current study's information
 */
interface StudySubjectsProps extends ViewProps {
  studyPrefix: string;
  getTaps: () => TapDetails[];
  studyDetails: Study;
}

/**
 * users: all ditti app users that are enrolled in this study
 * loader: whether to show the loader
 */
interface StudySubjectsState {
  users: UserDetails[];
  loading: boolean;
}

class StudySubjects extends React.Component<
  StudySubjectsProps,
  StudySubjectsState
> {
  state = { users: [], loading: true };

  componentDidMount() {

    // get all users that are enrolled in this study
    // makeRequest(
    //   `/aws/scan?app=2&key=User&query=user_permission_idBEGINS"${this.props.studyPrefix}"`
    // ).then((res: User[]) => {

    //   // map the user data to user details
    //   const users: UserDetails[] = res.map((user) => {
    //     return {
    //       tapPermission: user.tap_permission,
    //       information: user.information,
    //       userPermissionId: user.user_permission_id,
    //       expTime: user.exp_time,
    //       teamEmail: user.team_email,
    //       createdAt: user.createdAt
    //     };
    //   });

    //   this.setState({ users, loading: false });
    // });
    this.setState({ users: dummyUsers, loading: false });
  }

  /**
   * Render recent summary tap data for a user
   * @param user 
   * @returns 
   */
  getSubjectSummary = (user: UserDetails): React.ReactElement => {
    const { flashMessage, getTaps, goBack, handleClick } = this.props;
    let summaryTaps: React.ReactElement[];
    let hasTapsToday = false;

    // if the user has access to tapping
    if (user.tapPermission) {

      // for each day of the week
      summaryTaps = [6, 5, 4, 3, 2, 1, 0].map((i) => {
        const today = new Date(new Date().setHours(9, 0, 0, 0));

        // start from today minus i
        const start = sub(today, { days: i });

        // end at start plus 1 day
        const end = add(start, { days: 1 });

        // get taps and filter for only taps between start and end
        const taps = this.props
          .getTaps()
          .filter(
            (t) =>
              t.dittiId == user.userPermissionId &&
              isWithinInterval(new Date(t.time), { start, end })
          ).length;

        // if i is 0 and there are taps
        hasTapsToday = !i && taps > 0;

        // get the current weekday (Mon, Tue, Wed, etc.)
        const weekday = i
          ? start.toLocaleString("en-US", { weekday: "narrow" })
          : "Today";

        return (
          <div key={i} className="subject-summary-taps-day border-light-l">
            <span>{weekday}</span>
            <span>{taps}</span>
          </div>
        );
      });

      const today = new Date(new Date().setHours(9, 0, 0, 0));

      // get all taps starting from 7 days ago
      const start = sub(today, { days: 7 });
      const totalTaps = this.props
        .getTaps()
        .filter(
          (t) =>
            t.dittiId == user.userPermissionId &&
            isWithinInterval(new Date(t.time), { start, end: new Date() })
        ).length;

      summaryTaps.push(
        <div key={"total"} className="subject-summary-taps-day border-light-l">
          <span>
            <b>Total</b>
          </span>
          <span>
            <b>{totalTaps}</b>
          </span>
        </div>
      );
    } else {
      summaryTaps = [
        <div key={0} className="subject-summary-no-access">
          No tapping access
        </div>
      ];
    }

    // get the number of days until the user's id expires
    const expiresOn = differenceInDays(new Date(user.expTime), new Date());

    return (
      <div
        key={user.userPermissionId}
        className="subject-summary border-light-b"
      >

        {/* active tapping icon */}
        <div
          className={"icon " + (hasTapsToday ? "icon-success" : "icon-gray")}
        ></div>

        {/* link to the user's summary page */}
        <div className="subject-summary-name">
          <span
            className="link"
            onClick={() =>
              handleClick(
                [user.userPermissionId],
                <SubjectVisuals
                  flashMessage={flashMessage}
                  getTaps={getTaps}
                  goBack={goBack}
                  handleClick={handleClick}
                  studyDetails={this.props.studyDetails}
                  user={user}
                />
              )
            }
          >
            {user.userPermissionId}
          </span>

          {/* days until expiry */}
          <span>
            <i>Expires in: {expiresOn ? expiresOn + " days" : "Today"}</i>
          </span>
        </div>

        {/* summary tap data */}
        <div className="subject-summary-taps">{summaryTaps}</div>
      </div>
    );
  };

  render() {
    const { users, loading } = this.state;

    // all users whose ids have not expired
    const activeUsers = users.filter(
      (u: UserDetails) => new Date() < new Date(u.expTime)
    );

    return loading ? (
      <SmallLoader />
    ) : (
      <React.Fragment>
        {activeUsers.length
          ? activeUsers.map(this.getSubjectSummary)
          : "No active subjects"}
      </React.Fragment>
    );
  }
}

export default StudySubjects;
