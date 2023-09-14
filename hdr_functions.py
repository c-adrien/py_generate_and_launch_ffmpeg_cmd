import subprocess
from typing import List, Union
import json
from helpers import *

hdr_params = "hdr10-opt=1:repeat-headers=1:colorprim=bt2020:transfer=smpte2084:colormatrix=bt2020nc:chromaloc=2:aud=1:hrd=1:master-display=\"G({GREEN_X},{GREEN_Y})B({BLUE_X},{BLUE_Y})R({RED_X},{RED_Y})WP({WP_X},{WP_Y})L({LUMINANCE_MAX},{LUMINANCE_MIN})\":max-cll={MAX_CLL},{MAX_FALL}"


# ==========================================================================

def get_video_data(file: str) -> str:

    # Get info of audio streams
    video_data = subprocess.run(
        f"mediainfo --output=JSON \"{file}\""
        "| jq '.media.track[] | select(.[\"@type\"]==\"Video\")'",
        shell=True,
        capture_output=True
    )

    # Format output to JSON
    video_data = "[" + video_data.stdout.decode(
        'UTF-8').strip('\n').replace("}\n{", "},{") + "]"
    return video_data


def parse_hdr_data(stream: list, filepath: str) -> dict:
    """
    Parse HDR data from a MediaInfo stream object.
    """
    try:
        HDR_Format_Compatibility = stream["HDR_Format_Compatibility"]
    except KeyError:
        return {'not_found': 'No HDR base layer'}

    if "HDR10" in HDR_Format_Compatibility:

        # HDR10+ and Dolby Vision presence
        HDR10PLUS = "HDR10+" in HDR_Format_Compatibility
        DOLBY_VISION = "Dolby Vision" in stream["HDR_Format"]

        color_dict = get_mastering_display_data(filepath)

        for color, value in color_dict.items():
            if int(value.split("/")[1]) != 50_000:
                return {'error': 'Not supported: wrong divider Mastering display'}
            else:
                color_dict[color] = int(value.split("/")[0])

        # Luminance data
        luminance_list = stream["MasteringDisplay_Luminance"].split()
        LUMINANCE_MAX = int(luminance_list[4]) * 10_000
        LUMINANCE_MIN = int(float(luminance_list[1]) * 10_000)

        # MaxFALL/MaxCLL
        MAX_CLL = stream["MaxCLL"].split()[0]
        MAX_FALL = stream["MaxFALL"].split()[0]

        return {
            'HDR10+': HDR10PLUS,
            'DOLBY_VISION': DOLBY_VISION,
            'LUMINANCE_MAX': LUMINANCE_MAX,
            'LUMINANCE_MIN': LUMINANCE_MIN,
            'MAX_CLL': MAX_CLL,
            'MAX_FALL': MAX_FALL,
            **color_dict
        }

    return {'not_found': 'No HDR base layer'}


def get_mastering_display_data(filepath):
    cmd_rbg = f"ffprobe -hide_banner -loglevel warning -select_streams v -print_format json -show_frames " + \
        f"-read_intervals \"%+#1\" -show_entries \"frame=color_space,color_primaries,color_transfer,side_data_list,pix_fmt\" -i \"{filepath}\""

    sbp = subprocess.run(cmd_rbg, shell=True, capture_output=True)
    sbp = "[" + \
        sbp.stdout.decode('UTF-8').strip('\n').replace("}\n{", "},{") + "]"

    color_info = json.loads(sbp)[0]["frames"][0]["side_data_list"][0]

    color_dict = {
        "RED_X": color_info["red_x"],
        "RED_Y": color_info["red_y"],
        "GREEN_X": color_info["green_x"],
        "GREEN_Y": color_info["green_y"],
        "BLUE_X": color_info["blue_x"],
        "BLUE_Y": color_info["blue_y"],
        "WP_X": color_info["white_point_x"],
        "WP_Y": color_info["white_point_y"],
    }

    return color_dict


def extract_rpu(filepath: str) -> str:
    extraction_cmd = f"ffmpeg -i \"{filepath}\" -c:v copy -vbsf hevc_mp4toannexb -f hevc - | " + \
                     f"dovi_tool extract-rpu - -o \"{filepath}.bin\""

    cmd_exec(extraction_cmd)


def extract_hdr10plus_metadata(filepath: str, suffix: str = "hdr10plus"):
    extraction_cmd = f"ffmpeg -i \"{filepath}\" -map 0:v:0 -c copy -vbsf hevc_mp4toannexb -f hevc - | " + \
                     f"hdr10plus_tool --skip-validation extract -o \"{filepath}_{suffix}.json\" -"
    cmd_exec(extraction_cmd)


def build_cmd_for_hdr(data: str, filepath: str, bitrate: int) -> Union[str, None]:
    """
    Build a command to encode a HDR video.
    """
    for stream in json.loads(data):
        result = parse_hdr_data(stream, filepath)

        if 'not_found' in result:
            return None

        if 'error' in result:
            print_error(result['error'])
            exit(0)

        if result["HDR10+"]:
            extract_hdr10plus_metadata(filepath)

        if result["DOLBY_VISION"]:
            extract_rpu(filepath)

        return hdr_params.format(**result)
    return None


def encode_hdr(cmd: str, filepath: str) -> None:
    print(cmd)
    process = cmd_exec(cmd)

    if process:
        remove_file(f"{filepath}_log")
        remove_file(f"{filepath}_log.cutree")
    return


def cmd_exec(cmd: str):
    print_info("Executing...")

    process = subprocess.run(cmd, shell=True)

    if process.returncode != 0:
        print_error("ERROR : command failed")
        return False
    return True
