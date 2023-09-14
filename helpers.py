import subprocess
import os
import re
from typing import List, Union
import json
import argparse
from colorama import Fore
from statistics import mode
from enum import IntEnum

# ==========================================================================
# Helpers


def print_error(string: str) -> None:
    print(Fore.LIGHTRED_EX + string + Fore.WHITE)


def print_info(string: str) -> None:
    print(Fore.CYAN + string + Fore.WHITE)


def create_output_dir(output_dir):
    # Create output directory
    subprocess.run(
        f"mkdir -p \"{output_dir}\"",
        shell=True
    )
    return


def check_outfile_exists(filepath, outfolder) -> bool:
    if os.path.exists(f"{outfolder}{filepath.rsplit('/', maxsplit=1)[-1]}"):
        return True
    return False


def move_to_output_dir(file, output_dir):
    print_info(f"mv \"{file}\" \"{output_dir}\"")
    subprocess.run(
        f"mv \"{file}\" \"{output_dir}\"",
        shell=True
    )
    return


def remove_file(file):
    subprocess.run(
        f"rm \"{file}\"",
        shell=True
    )
    return
