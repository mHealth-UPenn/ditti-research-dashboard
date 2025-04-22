# Ditti Research Dashboard
# Copyright (C) 2025 the Trustees of the University of Pennsylvania
#
# Ditti Research Dashboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Ditti Research Dashboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from install.installer import Installer


def main() -> None:
    """
    Run the Ditti Research Dashboard installation process.

    Creates and initializes the installation process for the development
    environment. Currently only supports the 'dev' environment.

    Returns
    -------
    None
    """
    installer = Installer(env="dev")  # NOTE: Only dev is supported for now
    installer.run()


if __name__ == "__main__":
    main()
