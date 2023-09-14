import subprocess
import argparse

from helpers import *
from hdr_functions import *
from globals import *
from audio_processing import audio_processing
from video_processing import video_processing
# ==========================================================================


def encode(cmd: str, output_filename: str, output_directory: str) -> dict:
    '''
    Launch encoding
    '''

    print_info("Encoding...")

    if check_outfile_exists(output_filename, output_directory):
        return {'error': 'Output file already exists'}

    process = subprocess.run(cmd, shell=True)

    if process.returncode != 0:
        return {'error': 'Encoding failed'}

    move_to_output_dir(f"{output_filename}", output_directory)

    # Return output filepath
    return {'output': f"{output_directory}{output_filename.rsplit('/', maxsplit=1)[-1]}"}

# ==========================================================================


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("input", type=str, help="source file")
    parser.add_argument('-2pass', '--two_pass', nargs=1,
                        metavar=('BITRATE'), help='Encode in 2pass')
    parser.add_argument('-crf', '--crf', nargs=2, metavar=('CRF', 'MAXRATE'),
                        help='Encode using provided CRF and maxrate values')
    parser.add_argument('--x264', action='store_true',
                        help='Encode in h264, DEFAULT')
    parser.add_argument('--x265', action='store_true', help='Encode in HEVC')
    parser.add_argument('-d', '--dnr', action='store_true',
                        help='Apply denoising filter')
    parser.add_argument('-nc', '--no_crop',
                        action='store_true', help='Do not autocrop')
    parser.add_argument('-na', '--n_audio',
                        action='store_true', help='Do not reencode audio')

    args = parser.parse_args()

    # Create ouput dir
    # =================

    output_directory = f"{HOME}encode/"

    create_output_dir(output_directory)

    # ARGS
    # =================
    filepath = args.input

    # select codec
    # => defaults to x264
    # => If both codecs selected, x265 has priority
    codec = "x265" if args.x265 else "x264"

    # Encoding
    # =================

    # Audio
    if args.n_audio:
        AUDIO_CMD = ""
    else:
        AUDIO_CMD: str = audio_processing(filepath)

    # Base CMD
    INIT_CMD = f"ffmpeg {ffmpeg_global_options} -i \"{filepath}\" {ffmpeg_standard_stream_options} {AUDIO_CMD} "

    # Video
    if args.crf:
        mode = "crf"

        VIDEO_CMD = video_processing(
            filepath, codec,
            mode, crf=args.crf[0], target_bitrate=args.crf[1],
            autocropping=not args.no_crop, denoising=args.dnr
        )

        CMD = f"{INIT_CMD} {VIDEO_CMD['cmd']}"

    elif args.two_pass:
        mode = "2pass"

        VIDEO_CMD = video_processing(
            filepath, codec,
            mode, target_bitrate=args.two_pass[0],
            autocropping=not args.no_crop, denoising=args.dnr
        )

        CMD = f"{INIT_CMD} {VIDEO_CMD['cmd1']} {INIT_CMD} {VIDEO_CMD['cmd2']}"

    else:
        print_error("Error: Invalid encoding mode")
        return 0

    print(CMD)

    result = encode(CMD, VIDEO_CMD['output_filename'], output_directory)

    if 'error' in result:
        print_error(f"Error: {result['error']}")

    elif 'output' in result:
        print_info(result['output'])

    return


# ==========================================================================

if __name__ == "__main__":
    main()
