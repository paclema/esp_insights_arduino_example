#!/usr/bin/env python

import json
import glob
import os
from os.path import join, isfile, exists
import shutil
import sys
import logging
import hashlib
import io
from typing import BinaryIO, Iterator
from pathlib import Path


from SCons.Script import DefaultEnvironment, SConscript


import progname

def create_build_folder():
    if not exists(fw_out_folder):
        os.makedirs(fw_out_folder)


def build_project_build_config(env) -> bool:
    CONFIG = {}
    CONFIG['project'] = {}
    CONFIG['project']['name'] = project_name
    CONFIG['project']['version'] = appver

    project_build_config_file_path = join(fw_out_folder, "project_build_config.json")
    with open(project_build_config_file_path, 'w+') as json_file:
        json.dump(CONFIG, json_file, indent=4)
    return True


def get_bootloader_image(variants_dir):
    bootloader_image_file = "bootloader.bin"
    if partitions_name.endswith("tinyuf2.csv"):
        bootloader_image_file = "bootloader-tinyuf2.bin"

    variant_bootloader = join(
        variants_dir,
        board_config.get("build.variant", ),
        board_config.get("build.arduino.custom_bootloader", bootloader_image_file),
    )
    
    boot_mode = board_config.get("build.flash_mode", "$BOARD_FLASH_MODE").lower()
    frequency = str(env.subst("$BOARD_F_FLASH")).replace("L", "")

    # print("boot_mode %s" % boot_mode)
    # print("f flash %s" % str(int(int(frequency) / 1000000)) + "m")
    

    return (
        variant_bootloader
        if isfile(variant_bootloader)
        else join(
            FRAMEWORK_DIR,
            "tools",
            "sdk",
            build_mcu,
            "bin",
            # "bootloader_${__get_board_boot_mode(__env__)}_${__get_board_f_flash(__env__)}.bin",
            "bootloader_" + boot_mode + "_" + str(int(int(frequency) / 1000000)) + "m" + ".bin",
        )
    )

def chunks(
    fd: BinaryIO, length=None, *, chunk_size=io.DEFAULT_BUFFER_SIZE
) -> Iterator[bytes]:
    """
    :param length:
        the total number of bytes to consume;  if `None`, exhaust stream,
        if negative, yield until that many bytes before EOF.
    :param chunk_size:
        the maximum length of each chunk (the last one maybe shorter)
    :return:
        an iterator over the chunks of the file
    """
    if length is None:
        yield from iter(lambda: fd.read(chunk_size), b"")
    else:
        if length < 0:
            fsize = Path(fd.name).stat().st_size
            length = fsize - fd.tell() + length  # negative `length` added!
        consumed = 0
        for chunk in iter(lambda: fd.read(min(chunk_size, length - consumed)), b""):
            yield chunk
            consumed += len(chunk)


def digest_stream(
    fd: BinaryIO, digester_factory, length, chunk_size=io.DEFAULT_BUFFER_SIZE
) -> bytes:
    """
    :param length:
        how many bytes to digest from the start of the file; if not positive,
        digesting stops that many bytes before EOF (eg 0 means all file).
    """
    digester = digester_factory()
    for chunk in chunks(fd, length, chunk_size=chunk_size):
        digester.update(chunk)
    return digester.digest()

def hash_image(img_path):
    with io.open(img_path, "r+b") as fd:
        fd.seek(0)
        hash = digest_stream(fd, FILE_HASHING_ALGO, -FILE_HASH_LENGTH)
        assert len(hash) == FILE_HASH_LENGTH, (hash, FILE_HASH_LENGTH)
        # After digesting hash, file positioned immediately before the hash-bytes.
        # print(
        #     f"  +--{FILE_HASHING_ALGO().name:10}({len(hash)}bytes@0x{fd.tell():08x}):"
        #     f" {hash.hex()}",
        # )
        return hash.hex()[:8]
        
def copy_bootloader(env):
    source = join(env.subst("$BUILD_DIR"), "patched_bootloader.bin")
    if not os.path.isfile(source):
        logging.warning("\x1b[33;20mFile patched_bootloader.bin does not appear to exist.")
        bootloader_image_path = get_bootloader_image(join(FRAMEWORK_DIR, "variants"))
        source = bootloader_image_path
        logging.warning("\x1b[33;20mIt will be taken bootloader from: %s" % (bootloader_image_path))

    target_path = join(fw_out_folder, "bootloader")
    target_file = join(target_path, "bootloader.bin")
    if not exists(target_path):
        os.makedirs(target_path)
    print("Copying bootloader: ", target_file)
    shutil.copy(source, target_file)

def copy_file_to_build_folder(filePath):

    target = join(fw_out_folder, os.path.basename(filePath))
    print("Copying file: ", target)
    shutil.copy(filePath, target)

def copy_partition_table_bin(env):
    source = join(env.subst("$BUILD_DIR"), "partitions.bin")
    target_path = join(fw_out_folder, "partition_table")
    target_file = join(target_path, "partition-table.bin")
    if not exists(target_path):
        os.makedirs(target_path)
    print("Copying partition-table:", target_file)
    shutil.copy(source, target_file)

def copy_partition_table_csv(env):
    source = env.subst("$PARTITIONS_TABLE_CSV")
    target = join(fw_out_folder, "partitions.csv")
    print("Copying partition-table CSV:", target)
    shutil.copy(source, target)

def copy_sdkconfig(env):
    source = join(env.subst("$PROJECT_CORE_DIR"), "packages", "framework-arduinoespressif32", "tools", "sdk", "esp32", "sdkconfig")
    target = join(fw_out_folder, "sdkconfig")
    print("Copying sdkconfig:", target)
    shutil.copy(source, target)

def SaveProject(source, target, env):

    # print("${BUILD_DIR}", env.subst("$BUILD_DIR"))
    # print("BUILD_TARGETS: ", BUILD_TARGETS)
    global fw_out_name
    global fw_out_folder

    elf_hash = hash_image(join(env.subst("$BUILD_DIR"), project_name + ".bin"))
    fw_out_name =  project_name + "-v" + appver + "-" + elf_hash
    fw_out_folder = join(env.subst("$BUILD_DIR"), fw_out_name)
    # date = env.GetProjectOption("custom_build_date", None)
    print("Generating firmware package:", fw_out_name)

    create_build_folder()

    build_project_build_config(env)
    copy_bootloader(env)
    copy_file_to_build_folder(join(env.subst("$BUILD_DIR"), project_name + ".bin"))
    copy_file_to_build_folder(join(env.subst("$BUILD_DIR"), project_name + ".elf"))
    copy_file_to_build_folder(join(env.subst("$BUILD_DIR"), project_name + ".map"))
    copy_partition_table_bin(env)
    copy_partition_table_csv(env)
    copy_sdkconfig(env)

    # env.Execute(f"tar -cvzf {fw_out_name}.zip {fw_out_folder}\ --format=zip")
    print("\nGenerating firmware package file: ", fw_out_name, ".zip in location folder: ", env.subst("$BUILD_DIR"), "\n" )
    file = shutil.make_archive(base_name=fw_out_folder,format='zip',root_dir=env.subst("$BUILD_DIR"),base_dir=fw_out_name)


def pack_firmwware(env):
    pack_fw_action = env.AddCustomTarget(
        "pack-fw",
        # ['patchappinfos', 'elf-hash'],
        'patchappinfos',
        SaveProject,
        title="Pack firmware",
        description="Pack firmware",
        always_build=True
    )

    env.AddPostAction('patchappinfos', pack_fw_action)
    env.Depends(target="upload", dependency=pack_fw_action)
    env.Default(pack_fw_action)



if __name__ == "SCons.Script":
    Import("env")

    root = logging.getLogger()
    root.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.WARNING)
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # handler.setFormatter(formatter)
    root.addHandler(handler)

    # Import("env", "projenv")
    # Dump global construction environment (for debug purpose)
    # print(env.Dump())
    # Dump project construction environment (for debug purpose)
    # print(projenv.Dump())

    # print("Current CLI targets", COMMAND_LINE_TARGETS)
    # print("Current Build targets")
    # for x in BUILD_TARGETS:
    #     print(x)

    FILE_HASHING_ALGO = hashlib.sha256
    #: The length (in bytes) of the hash256 at image's EOF.
    FILE_HASH_LENGTH = 32


    CONFIG = {}
    appver, appver_src = progname.get_program_ver(env)
    project_name, project_name_src = progname.get_program_name(env)
    fw_out_name = None
    fw_out_folder = None

    env = DefaultEnvironment()
    platform = env.PioPlatform()
    FRAMEWORK_DIR = platform.get_package_dir("framework-arduinoespressif32")
    board_config = env.BoardConfig()
    build_mcu = board_config.get("build.mcu", "").lower()
    partitions_name = board_config.get(
        "build.partitions", board_config.get("build.arduino.partitions", "")
    )


    pack_firmwware(env)
