from globals import VideoOptions

def two_pass_function(file: str, codec: str, target_bitrate: int, video_filters_cmd: str) -> str:
    codec_specific_options = {
        "x264": " -tune film ",
        "x265": " -pix_fmt yuv420p10le -level:v 5.0 ",
    }

    encoder_params = {
        "x264": VideoOptions.x264_params,
        "x265": VideoOptions.x265_params,
    }

    speed = {
        "x264": VideoOptions.x264_speed,
        "x265": VideoOptions.x265_speed,
    }

    two_pass_syntax = {
        "x264": " -pass {pass_nb} -passlogfile \"{file}\" ",
        "x265": ":pass={pass_nb}:stats=\"{file}_log\"",
    }

    output_filename = f"{file}[{codec}_2pass_{target_bitrate}k].mkv"

    cmd1 = f"-c:v:0 lib{codec} -preset {speed[codec]} {video_filters_cmd} {codec_specific_options[codec]} -{codec}-params {encoder_params[codec]}{two_pass_syntax[codec].format(pass_nb=1, file=file)} -b:v {target_bitrate}k -an -f null /dev/null && "
    cmd2 = f"-c:v:0 lib{codec} -preset {speed[codec]} {video_filters_cmd} {codec_specific_options[codec]} -{codec}-params {encoder_params[codec]}{two_pass_syntax[codec].format(pass_nb=2, file=file)} -b:v {target_bitrate}k \"{output_filename}\""

    return {
        'cmd1': cmd1,
        'cmd2': cmd2,
        'output_filename': output_filename,
    }
