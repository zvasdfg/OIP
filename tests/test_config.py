from __future__ import annotations

from src.config.loader import ConfigLoader
from src.config.settings import Settings


def test_config_loader_reads_organizations_and_profile(tmp_path) -> None:
    organizations_path = tmp_path / "organizations.yaml"
    profile_path = tmp_path / "professional_profile.yaml"
    organizations_path.write_text(
        """
- name: ExampleCo
  source: greenhouse
  identifier: example
  priority: high
  category: infrastructure
  tags: [cloud]
""",
        encoding="utf-8",
    )
    profile_path.write_text(
        """
expertise: [python]
preferred_domains: [infrastructure]
target_titles: [senior sdet]
excluded_titles: [manual tester]
""",
        encoding="utf-8",
    )

    loader = ConfigLoader(organizations_path, profile_path)

    assert loader.load_organizations()[0].identifier == "example"
    assert loader.load_profile().expertise == ["python"]


def test_settings_loads_environment(monkeypatch) -> None:
    monkeypatch.setenv("OIP_DATABASE_URL", "sqlite:///custom.sqlite3")
    monkeypatch.setenv("OIP_SMTP_TO", "a@example.com,b@example.com")

    settings = Settings.from_environment()

    assert settings.database_url == "sqlite:///custom.sqlite3"
    assert settings.smtp_to == ["a@example.com", "b@example.com"]


def test_config_loader_supports_300_plus_organizations(tmp_path) -> None:
    organizations_path = tmp_path / "organizations.yaml"
    profile_path = tmp_path / "professional_profile.yaml"
    organizations_path.write_text(
        "\n".join(
            [
                f"- name: Company {index}\n"
                "  source: greenhouse\n"
                f"  identifier: company-{index}\n"
                "  priority: medium\n"
                "  category: enterprise-software"
                for index in range(305)
            ]
        ),
        encoding="utf-8",
    )
    profile_path.write_text("expertise: []\n", encoding="utf-8")

    organizations = ConfigLoader(organizations_path, profile_path).load_organizations()

    assert len(organizations) == 305
    assert organizations[-1].identifier == "company-304"
