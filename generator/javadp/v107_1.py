from pathlib import Path

from generator.utils import PackConfig, write_json
from rich.console import Console
import pathlib
console = Console()

PACK_FORMAT: float = 107.1


def generate_dp(audio_files: dict, config: PackConfig):
    jukebox_song_dir = config.output_path / "data" / config.pack_id / "jukebox_song"
    jukebox_song_dir.mkdir(parents=True, exist_ok=True)

    functions_dir = config.output_path / "data" / config.pack_id / "function"
    functions_dir.mkdir(parents=True, exist_ok=True)

    Path(functions_dir / "give_item").mkdir(parents=True, exist_ok=True)

    pack_mcmeta = {"pack": {
        "pack_format": config.pack_format,
        "description": config.pack_description
    }}
    write_json(pack_mcmeta, config.output_path / "pack.mcmeta")

    give_all_discs_mcfunction = []

    for disc in audio_files: # Main disc write loop
        jukebox_song_entry = {"comparator_output": disc["comparator_output"],
                              "description": disc["description"],
                              "length_in_seconds": disc["length"],
                              "sound_event": {
                                  "sound_id": config.pack_id + ":music_disc." + disc["id_string"],
                                  "range": config.audio_range
                              }}
        write_json(jukebox_song_entry, jukebox_song_dir / f"{disc["id_string"]}.json")

        give_item_mcfunction: str = "execute at @s run summon item ~ ~ ~ {Item:{id:minecraft:" + config.disc_item_string + ", Count:1b, components:{custom_model_data:" + disc["custom_model_data"] + ", jukebox_playable:{song:" + config.pack_id + ":" + disc["id_string"] + "}}}}"
        give_item_mcfunction_path: Path = functions_dir / "give_item" / f"{disc['id_string']}.mcfunction"

        with open(give_item_mcfunction_path, "w") as f:
            f.write(give_item_mcfunction)

        give_all_discs_mcfunction.append(give_item_mcfunction)

    with open(functions_dir / "give_all.mcfunction", "w") as f:
        f.write("\n".join(give_all_discs_mcfunction))



