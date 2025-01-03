import LinkComponent from "../links/linkComponent";
import { Link } from "react-router-dom";


/**
 * @property {string} activeView - The name of the active view
 */
interface NavbarProps {
  activeView: "Accounts" | "Studies" | "Roles" | "Access Groups" | "About Sleep Templates";
}

const Navbar = ({ activeView }: NavbarProps) => {
  const views = [
    {
      active: false,
      name: "Accounts",
      link: "/coordinator/admin/accounts"
    },
    {
      active: false,
      name: "Studies",
      link: "/coordinator/admin/studies"
    },
    {
      active: false,
      name: "Roles",
      link: "/coordinator/admin/roles"
    },
    {
      active: false,
      name: "Access Groups",
      link: "/coordinator/admin/access-groups"
    },
    {
      active: false,
      name: "About Sleep Templates",
      link: "/coordinator/admin/about-sleep-templates"
    }
  ];

  // Set the current view as active
  views.forEach(v => {
    if (v.name === activeView) {
      v.active = true;
    }
  });

  return (
    <div className="flex items-center justify-left px-6 lg:px-12 bg-white select-none whitespace-nowrap">
      {/* If the view is active, highlight it using bg-dark */}
      {views.map((v, i) => (
        v.active ?
          <div
            key={i}
            className="flex px-4 lg:px-8 items-center justify-center h-full py-4 bg-dark text-center">
              {v.name}
          </div> :
          <div key={i} className="flex h-full">
            <Link to={v.link}>
              <LinkComponent className="flex items-center justify-center px-3 lg:px-4 xl:px-8 h-full w-full no-underline hover:bg-extra-light text-center">
                  {v.name}
              </LinkComponent>
            </Link>
          </div>
      ))}
    </div>
  );
};

export default Navbar;
