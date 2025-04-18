from install.installer import Installer


def main() -> None:
    installer = Installer(env="dev")  # NOTE: Only dev is supported for now
    installer.run()


if __name__ == "__main__":
    main()
