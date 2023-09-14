from globals import AudioOptions

import json
import subprocess

# ========================================

def get_audio_data(file: str) -> str:
    """
    Get info of audio streams
    """

    audio_data = subprocess.run(
        f"mediainfo --output=JSON \"{file}\""
        "| jq '.media.track[] | select(.[\"@type\"]==\"Audio\") | "
        "{StreamOrder: .StreamOrder, Bitrate: .BitRate, Channels: .Channels, Format: .Format}'",
        shell=True,
        capture_output=True
    )

    # Format output to JSON
    audio_data = "[" + audio_data.stdout.decode(
        'UTF-8').strip('\n').replace("}\n{", "},{") + "]"
    return audio_data


def build_audio_options(data: str) -> str:
    """
    For each audio stream, if bitrate > max_bitrate : add ffmpeg cmd to reencode
    """
    if data == "[]":
        return ""

    audio_options = ""

    for stream_number, stream in enumerate(json.loads(data)):
        try:
            bitrate = int(stream["Bitrate"])
            channels = int(stream["Channels"])

        # Unable to parse stream
        except (ValueError, KeyError):
            pass

        MAX_BITRATE = AudioOptions.MAX_BITRATES.get(channels, AudioOptions.DEFAULT_BITRATE)

        if bitrate > MAX_BITRATE:
            audio_options += f"-c:a:{stream_number} ac3 -b:a:{stream_number} {MAX_BITRATE} -ar 48k "

    return audio_options


def audio_processing(filepath: str) -> str:
    audio_cmd: str = build_audio_options(get_audio_data(filepath))
    return audio_cmd