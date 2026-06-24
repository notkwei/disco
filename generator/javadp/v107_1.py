from generator.utils import PackConfig, write_json, format_string
from rich.console import Console
console = Console()

PACK_FORMAT: float = 107.1

def generate_dp(audio_files: dict, config: PackConfig):
    pack_mcmeta = {"pack": {
        "pack_format": config.pack_format,
        "description": config.pack_description
    }}
    write_json(pack_mcmeta, config.output_path / "pack.mcmeta")



