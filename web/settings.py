import pathlib

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, TomlConfigSettingsSource, SettingsConfigDict

BASEDIR = pathlib.Path(__file__).parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(toml_file=BASEDIR / "configs.toml")

    check_interval: int = 5

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
