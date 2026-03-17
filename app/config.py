from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "sheet-update-service"
    app_env: str = "local"
    debug: bool = True
    dry_run: bool = True
    api_key: str = "change_me"

    default_spreadsheet_id: str = "stub_spreadsheet_id"
    default_worksheet_name: str = "Daily Data"
    google_service_account_file: str = "service_account.json"

    require_year_in_week_headers: bool = True
    allow_legacy_week_match: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()