from globals import VideoOptions

CMD = "-c:v:0 lib{codec} -preset {speed} {video_filters} {codec_specific_options} -{codec}-params " + \
    "{encoder_params} " + \
    "-crf {crf} -maxrate {maxrate}k -bufsize {bufsize}k " + \
    "-map_metadata:g -1 \"{output_filename}\""


def crf_function(file: str, codec: str, crf: int, maximum_bitrate: int, video_filters_cmd: str):

    if codec == "x264":
        codec_specific_options = " -tune film "
        encoder_params = VideoOptions.x264_params
        speed: str = "veryslow"

    elif codec == "x265":
        codec_specific_options = " -pix_fmt yuv420p10le -level:v 5.0 "
        encoder_params = VideoOptions.x265_params
        speed: str = "slow"

    else:
        raise ValueError("Incorrect codec requested")

    output_filename = f"{file}_[{codec}_CRF_{crf}].mkv"

    dict_string = {
        'file': file, 'codec': codec,
        'crf': crf, 'maxrate': maximum_bitrate, 'bufsize': maximum_bitrate*2,
        'speed': speed,
        'codec_specific_options': codec_specific_options, 'encoder_params': encoder_params,
        'output_filename': output_filename,
        'video_filters': video_filters_cmd,
    }

    return {
        'cmd': CMD.format(**dict_string),
        'output_filename': output_filename,
    }
