from dataclasses import dataclass


# Constants
# ========================================


# File organization
HOME = "/data/"
FOLDER = "{HOME}scripts/"


# ffmpeg
ffmpeg_global_options: str = " -hide_banner -loglevel error -stats -n "
ffmpeg_standard_stream_options: str = " -map 0:v:0 -map 0:a? -map 0:s? -c copy "


# Video
@dataclass()
class VideoOptions:
    x264_params: str
    x265_params: str

    x264_speed: str
    x265_speed: str

x265_params = "no-info=1:profile=main10:ref=4:qcomp=0.65:ctu=64" + \
    ":rect=0:amp=0:nr-intra=100:nr-inter=100:selective-sao=2"

x264_params = "ref=4:bframes=4:keyint=250:min-keyint=25:qcomp=0.65:no-dct-decimate=1:8x8dct=1 " + \
    "-bsf:v 'filter_units=remove_types=6'"

x264_speed = "veryslow"
x265_speed = "slow"

VideoOptions = VideoOptions(x264_params, x265_params, x264_speed, x265_speed)


# Audio
@dataclass()
class AudioOptions:
    MAX_BITRATES: dict
    DEFAULT_BITRATE: int


MAX_MONO_AUDIO_BITRATE: int = 192_000
MAX_STEREO_AUDIO_BITRATE: int = 224_000
MAX_SURROUND_AUDIO_BITRATE: int = 448_000
DEFAULT_BITRATE: int = 448_000

MAX_BITRATES = {
    1: MAX_MONO_AUDIO_BITRATE,
    2: MAX_STEREO_AUDIO_BITRATE,
    3: DEFAULT_BITRATE,
    4: DEFAULT_BITRATE,
    5: DEFAULT_BITRATE,
    6: MAX_SURROUND_AUDIO_BITRATE,
    7: MAX_SURROUND_AUDIO_BITRATE,
    8: MAX_SURROUND_AUDIO_BITRATE
}

AudioOptions = AudioOptions(MAX_BITRATES, DEFAULT_BITRATE)
