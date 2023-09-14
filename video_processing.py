from globals import VideoOptions
from helpers import print_info
from hdr_functions import get_video_data, build_cmd_for_hdr
from crf import crf_function
from two_pass import two_pass_function

import subprocess
import re
from typing import List, Union
from statistics import mode

# ========================================
# Video filters


def get_crop_data(file: str) -> Union[str, None]:
    """
    Detect unnecessary black bars and crop them
    """

    # IMAX movies have an uneven aspect ratio
    if "imax" in file.lower():
        return None

    crop_list = []

    try:
        for i in range(0, 60, 2):
            crop_process = subprocess.run(
                f"ffmpeg -nostats -ss 00:{str(i).zfill(2)}:00.00 -t 1 -i \"{file}\" "
                f"-vf cropdetect=round=2 -f null - 2>&1"
                f"| tail -3",
                shell=True,
                capture_output=True,
                timeout=3
            )

            # Eg. [('1920:1080:0:0', ':0')]
            crop_process = re.findall(
                r"crop=([0-9]+(:[0-9]+)+)", str(crop_process.stdout.decode('UTF-8')))

            if len(crop_process) == 1:
                # Eg. '1920:1080:0:0'
                crop_list.append(str(crop_process[0][0]))

    except subprocess.TimeoutExpired:
        pass

    # Min number of values
    if len(crop_list) < 5:
        return None

    crop = mode(crop_list)

    # If width < height
    def f(string, index): return string.split(':')[index]
    if int(f(crop, 0)) < int(f(crop, 1)):
        return None

    return crop


def build_video_filters_cmd(video_filters: List[str]) -> str:
    '''
    Join and format video filters for cmd use
    '''
    if video_filters:
        return f"-vf \"{' , '.join(video_filters)}\""
    return ""

# ========================================


def video_processing(file: str, codec: str, mode: str,
                     target_bitrate: int, crf: int = None,
                     autocropping: bool = True, denoising: bool = False) -> str:

    # Video filters
    # =================

    video_filters: List[str] = []

    # Filter 1 : autocrop
    if autocropping:
        print_info("Generating crop command...")
        crop_data = get_crop_data(file)

        if crop_data is not None:
            print_info(f"Cropping : {crop_data}")
            video_filters.append(f"\"crop={crop_data}\"")

    # Filter 2 : noise reduction
    if denoising:
        print_info("Generating denoise command...")
        video_filters.append("nlmeans=10.0:7:15:3:3")
        video_filters.append("smartblur=1.5:-0.35:-3.5:0.65:0.25:2.0")

    video_filters_cmd = build_video_filters_cmd(video_filters)

    # Video encoding
    # =================

    # Check input vars
    if mode.lower() not in ["2pass", "crf"]:
        return {'error': "Unexpected encoding mode"}

    # Step 1 : detect HDR
    video_data = get_video_data(file)
    video_cmd_hdr = build_cmd_for_hdr(video_data, file, target_bitrate)
    if video_cmd_hdr is not None:

        # Add HDR specific params to cmd
        VideoOptions.x265_params += ":" + video_cmd_hdr

        # Force x265
        codec = "x265"

    # Step 2 : encoding mode
    if mode == "crf":
        result = crf_function(
            file, codec, crf, target_bitrate, video_filters_cmd)

    elif mode == "2pass":
        result = two_pass_function(
            file, codec, target_bitrate, video_filters_cmd)

    return result
