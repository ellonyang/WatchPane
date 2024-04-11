import pathlib

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, TomlConfigSettingsSource, SettingsConfigDict

BASEDIR = pathlib.Path(__file__).parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(toml_file=BASEDIR / "config.toml")

    check_interval: int = 60
    api: str
    watch_url: str
    async_page: int = 2

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            TomlConfigSettingsSource(settings_cls),
        )
