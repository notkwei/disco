# Both v48 and v57 should be supported.
from pathlib import Path

from generator.utils import PackConfig, write_json
from rich.console import Console


console = Console()

PACK_FORMAT: float = 107.1


def generate_dp(audio_files: dict, config: PackConfig):
    pack_format: float = config.pack_format or PACK_FORMAT
    jukebox_song_dir = config.output_path / "data" / config.pack_id / "jukebox_song"
    jukebox_song_dir.mkdir(parents=True, exist_ok=True)

    functions_dir = config.output_path / "data" / config.pack_id / "function"
    functions_dir.mkdir(parents=True, exist_ok=True)

    Path(functions_dir / "give_item").mkdir(parents=True, exist_ok=True)

    if type(pack_format) is not int:
        versions = str(float(pack_format)).split(".")
    else:
        versions = [pack_format, 0]

    pack_mcmeta = {"pack": {"description": config.pack_description,
                            "min_format": [int(versions[0]), int(versions[1])],
                            "max_format": [int(versions[0]), int(versions[1])]}}
    write_json(pack_mcmeta, config.output_path / "pack.mcmeta")

    give_all_discs_mcfunction = []

    for disc in audio_files: # Main disc write loop
        console.print("[JAVA DP] Processing disc", audio_files[disc]["id_string"], style="grey50")
        jukebox_song_entry = {"comparator_output": config.jukebox_comparator_output,
                              "description": {
                                  "translate": f"item.{config.pack_id}.music_disc_{audio_files[disc]['id_string']}",
                                  "fallback": f"{audio_files[disc]['description']}"
                              },
                              "length_in_seconds": audio_files[disc]["length"],
                              "sound_event": {
                                  "sound_id": config.pack_id + ":music_disc." + audio_files[disc]["id_string"],
                                  "range": config.audio_range
                              }}
        write_json(jukebox_song_entry, jukebox_song_dir / f"{audio_files[disc]['id_string']}.json")

        # execute at @s run give @s music_disc_wait[minecraft:jukebox_playable="discodiscs:wagewarfourxfour",minecraft:custom_model_data={strings:["music_disc_wagewarfourxfour"]}]
        give_item_mcfunction: str = f'execute at @s run give @s {config.disc_item_string}[minecraft:jukebox_playable="{config.pack_id}:{audio_files[disc]["id_string"]}",minecraft:custom_model_data='+'{strings:["music_disc_'+audio_files[disc]["id_string"]+'"]}]' # Yes, this line uses single quotes instead of double quotes.
        give_item_mcfunction_path: Path = functions_dir / "give_item" / f"{audio_files[disc]['id_string']}.mcfunction"

        with open(give_item_mcfunction_path, "w") as f:
            f.write(give_item_mcfunction)

        give_all_discs_mcfunction.append(give_item_mcfunction)

    with open(functions_dir / "give_all.mcfunction", "w") as f:
        f.write("\n".join(give_all_discs_mcfunction))
