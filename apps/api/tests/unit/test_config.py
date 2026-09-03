from app.core import config


def test_settings_loads_env_without_overwriting_process_values(tmp_path, monkeypatch) -> None:
    environment_file = tmp_path / ".env"
    environment_file.write_text(
        "DATABASE_URL=postgresql://from-file\nTMDB_API_KEY=from-file\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(config, "ENV_FILE", environment_file)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("TMDB_API_KEY", "from-process")

    settings = config.Settings.from_environment()

    assert settings.database_url == "postgresql://from-file"
    assert settings.tmdb_api_key == "from-process"
