import { Link } from "react-router-dom";
import { IBreadcrumb } from "../interfaces";
import { useNavbarContext } from "../contexts/navbarContext";

interface IHandle {
  breadcrumbs: IBreadcrumb[];
}


const Navbar = () => {
  const { breadcrumbs } = useNavbarContext();

  return (
    <div className="bg-white flex items-center h-16 flex-shrink-0 select-none z-10 shadow">
      <div className="flex items-center h-12 pl-12">
        {breadcrumbs.map((b, i) => {
          // If this is the last breadcrumb or if there is no link associated with it
          if (i === breadcrumbs.length - 1 || b.link === null) {

            // Don't make the breadcrumb clickable
            return (
              <div key={i} className="flex items-center">
                <span>{b.name}&nbsp;&nbsp;/&nbsp;&nbsp;</span>
              </div>
            );
          } else {
            return (
              <>
                <div className="flex items-center text-link hover:text-link-hover cursor-pointer">
                  <Link to={b.link}>
                    <span>{b.name}</span>
                  </Link>
                </div>
                <div>
                  <span>&nbsp;&nbsp;/&nbsp;&nbsp;</span>
                </div>
              </>
            );
          }
        })}
      </div>
    </div>
  );
}

export default Navbar;
