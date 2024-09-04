import * as React from "react";
import { Component } from "react";
import StudiesView from "./dittiApp/studies";
import Header from "./header";
import Home from "./home";
import Navbar from "./navbar";
import StudiesMenu from "./studiesMenu";
import "./dashboard.css";
import { Tap, TapDetails, UserDetails } from "../interfaces";
import { dummyTaps } from "./dummyData";
import { differenceInMilliseconds } from "date-fns";
import { makeRequest } from "../utils";

/**
 * breadcrumbs: the breadcrumbs to display in the navbar
 * flashMessages: messages to be displayed on the page
 * history: a history stack for user navigation
 * taps: tap data
 * users: this is unused
 * view: the current view
 */
interface DashboardState {
  breadcrumbs: { name: string; view: React.ReactElement }[];
  flashMessages: { id: number; element: React.ReactElement }[];
  history: { name: string; view: React.ReactElement }[][];
  taps: TapDetails[];
  users: UserDetails[];
  view: React.ReactElement;
}

class Dashboard extends React.Component<any, DashboardState> {
  constructor(props: any) {
    super(props);

    // set the home page as the default view
    const view = (
      <Home
        getTapsAsync={this.getTapsAsync}
        getTaps={this.getTaps}
        handleClick={this.setView}
        goBack={this.goBack}
        flashMessage={this.flashMessage}
      />
    );

    this.state = {
      breadcrumbs: [{ name: "Home", view: view }],
      flashMessages: [],
      history: [],
      taps: [],
      users: [],
      view: view
    };
  }

  /**
   * Either query AWS for tap data or, if AWS was already queried once, return
   * the result of the first query
   * @returns - tap data
   */
  getTapsAsync = async (): Promise<TapDetails[]> => {
    // let { taps } = this.state;

    // // if AWS has not been queried yet
    // if (!taps.length) {
    //   taps = await makeRequest("/aws/get-taps?app=2").then((res: Tap[]) => {
    //     return res.map((tap) => {
    //       return { dittiId: tap.dittiId, time: new Date(tap.time) };
    //     });
    //   });

    //   // sort taps by timestamp
    //   taps = taps.sort((a, b) =>
    //     differenceInMilliseconds(new Date(a.time), new Date(b.time))
    //   );

    //   this.setState({ taps });
    // }

    // uncomment when using dummy data
    const taps = dummyTaps.sort((a, b) =>
      differenceInMilliseconds(new Date(a.time), new Date(b.time))
    );
    this.setState({ taps });

    return taps;
  };

  getTaps = (): TapDetails[] => {
    return this.state.taps;
  };

  /**
   * Set a new view for the dashboard and add the current view to the history
   * stack
   * @param name - a list of names to be used for breadcrumbs, where the last
   *               element is the name of the new view. Preceding elements will
   *               be added as breadcrumbs but not added to the history stack
   * @param view - the new view
   * @param replace - whether the new view replaces the top breadcrum
   */
  setView = (name: string[], view: React.ReactElement, replace?: boolean) => {
    let { breadcrumbs } = this.state;
    const { history } = this.state;

    // add the current view to the history stack
    history.push(breadcrumbs.slice(0));

    // if replacing the top breadcrumb
    if (replace) breadcrumbs.pop();

    // for each breadcrumb
    let i = 0;
    for (const b of breadcrumbs) {

      // if this breadcrumb matches the first name to be used as breadcrumbs
      if (b.name === name[0]) {

        // then remove the following breadcrumbs to continue from this point
        breadcrumbs = breadcrumbs.slice(0, i + 1);
        break;
      } else if (i === breadcrumbs.length - 1) {

        // else add each name to the breadcrumbs
        for (const i in name) {

          // add the view only for the last name
          breadcrumbs.push({
            name: name[i],
            view: parseInt(i) === name.length - 1 ? view : <React.Fragment />
          });
        }

        break;
      }

      i++;
    }

    this.setState({ breadcrumbs, history, view });
  };

  /**
   * 
   * @param name 
   * @param view 
   */
  setStudy = (name: string, view: React.ReactElement): void => {
    const { history } = this.state;
    let { breadcrumbs } = this.state;
    history.push(breadcrumbs.slice(0));

    breadcrumbs = breadcrumbs.slice(0, 2);

    if (breadcrumbs.length == 1) {
      const appView = (
        <StudiesView
          getTapsAsync={this.getTapsAsync}
          getTaps={this.getTaps}
          handleClick={this.setView}
          goBack={this.goBack}
          flashMessage={this.flashMessage}
        />
      );

      breadcrumbs.push({ name: "Ditti App", view: appView });
    }

    breadcrumbs.push({ name: name, view: view });
    this.setState({ breadcrumbs, history, view: <React.Fragment /> }, () =>
      this.setState({ view })
    );
  };

  /**
   * Navigate to the previous view in the history stack
   */
  goBack = () => {
    const { history } = this.state;

    // get the last set of breadcrumbs
    const breadcrumbs = history.pop();

    // if there was any history to begin with
    if (breadcrumbs) {

      // set the last view in the history as the new view
      const view = breadcrumbs[breadcrumbs.length - 1].view;

      if (breadcrumbs.length == this.state.breadcrumbs.length)
        this.setState({ breadcrumbs, history, view: <React.Fragment /> }, () =>
          this.setState({ view })
        );
      else this.setState({ breadcrumbs, history, view });
    }
  };

  /**
   * Add a message to the page
   * @param msg - the message content
   * @param type = the message type (success, info, danger, etc.)
   */
  flashMessage = (msg: React.ReactElement, type: string): void => {
    const { flashMessages } = this.state;

    // set the element's key to 0 or the last message's key + 1
    const id = flashMessages.length
      ? flashMessages[flashMessages.length - 1].id + 1
      : 0;

    const element = (
      <div key={id} className={"shadow flash-message flash-message-" + type}>
        <div className="flash-message-content">
          <span>{msg}</span>
        </div>
        <div
          className="flash-message-close"
          onClick={() => this.popMessage(id)}
        >
          <span>x</span>
        </div>
      </div>
    );

    // add the message to the page
    flashMessages.push({ id, element });
    this.setState({ flashMessages });
  };

  /**
   * Remove a message from the page
   * @param id - The id of the message to remove
   */
  popMessage = (id: number): void => {
    let { flashMessages } = this.state;
    flashMessages = flashMessages.filter((fm) => fm.id != id);
    this.setState({ flashMessages });
  };

  render() {
    const { breadcrumbs, flashMessages, history, view } = this.state;

    return (
      <main className="bg-light dashboard-container">

        {/* header with the account menu  */}
        <Header
          handleClick={this.setView}
          goBack={this.goBack}
          flashMessage={this.flashMessage}
        />
        <div
          style={{
            display: "flex",
            flexGrow: 1,
            maxHeight: "calc(100vh - 4rem)"
          }}
        >

          {/* list of studies on the left of the screen */}
          <StudiesMenu
            setView={this.setStudy}
            flashMessage={this.flashMessage}
            handleClick={this.setView}
            getTaps={this.getTaps}
            goBack={this.goBack}
          />

          {/* main dashboard */}
          <div className="dashboard-content">

            {/* navigation bar */}
            <Navbar
              breadcrumbs={breadcrumbs}
              handleBack={this.goBack}
              handleClick={this.setView}
              hasHistory={history.length > 0}
            />

            {/* flash messages */}
            {flashMessages.length ? (
              <div className="flash-message-container">
                {flashMessages.map((fm) => fm.element)}
              </div>
            ) : null}

            {/* current view */}
            {view}
          </div>
        </div>
      </main>
    );
  }
}

export default Dashboard;
