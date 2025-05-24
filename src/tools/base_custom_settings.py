from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent


class BaseCustomSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            BASE_DIR / '.env.template',
            BASE_DIR / '.env',
        ),
        case_sensitive=False,
        extra='allow',
        env_prefix='',
        env_nested_delimiter='',
    )

    @classmethod
    def set_app_base(cls, app_base: Path):
        env_files = list(cls.model_config["env_file"])
        env_files.append(app_base / f'.env.template'),
        env_files.append(app_base / f'.env')

        cls.model_config["env_file"] = (
            *env_files,
        )
