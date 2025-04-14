from install_scripts.project_config.project_config_provider import ProjectConfigProvider


class TestProjectConfigProvider:
    def test_project_config_provider(logger_mock):
        project_config_provider = ProjectConfigProvider(
            logger=logger_mock,
            project_suffix="test-project-suffix",
        )

        assert project_config_provider.logger == logger_mock
        assert project_config_provider.project_suffix == "test-project-suffix"
        assert project_config_provider.project_config is None
        assert project_config_provider.user_input is None
