Import("env")
#  More info: https://docs.platformio.org/en/latest/scripting/custom_targets.html


env.AddCustomTarget(
    name="envdump",
    dependencies=None,
    actions=[
        "pio run -t envdump"
    ],
    title="Show Build Options [envdump]",
    description="Show Build Options "
)
env.AddCustomTarget(
    name="prune",
    dependencies=None,
    actions=[
        "pio system prune -f"
    ],
    title="Prune System",
    description="Prune System"
)
env.AddCustomTarget(
    name="fuses-summary",
    dependencies=None,
    actions=[
        "pip3 install cryptography",
        "pip3 install ecdsa",
        "pip3 install bitstring",
        "pip3 install reedsolo",
        "python.exe c:/Users/pacle/.platformio/packages/tool-esptoolpy/espefuse.py --port COM5 summary"
    ],
    title="Fuses Summary",
    description="Fuses Summary"
)
env.AddCustomTarget(
    name="elf-hash",
    dependencies=None,
    actions=[
        "python.exe c:/Users/pacle/.platformio/packages/framework-arduinoespressif32/tools/esptool.py --chip esp32 image_info $BUILD_DIR/${PROGNAME}.bin"
    ],
    title="ELF hash",
    description="ELF hash"
)
import progname
from os.path import join
appver, appver_src = progname.get_program_ver(env)
project_name, project_name_src = progname.get_program_name(env)
fw_out_name =  project_name + "-v" + appver
new_bin = join(env.subst("$BUILD_DIR"), fw_out_name, project_name + ".bin")
old_bin = join(env.subst("$BUILD_DIR"), project_name + ".bin.old")
env.AddCustomTarget(
    name="elf-new-hash",
    dependencies=None,
    actions=[
        f"python.exe c:/Users/pacle/.platformio/packages/framework-arduinoespressif32/tools/esptool.py --chip esp32 image_info {new_bin}"
    ],
    title="ELF new hash",
    description="ELF new hash"
)
env.AddCustomTarget(
    name="elf-old-hash",
    dependencies=None,
    actions=[
        f"python.exe c:/Users/pacle/.platformio/packages/framework-arduinoespressif32/tools/esptool.py --chip esp32 image_info {old_bin}"
    ],
    title="ELF old hash",
    description="ELF old hash"
)
env.AddCustomTarget(
    name="docker-builder",
    dependencies=None,
    actions=[
        "docker build --tag esp32-arduino-lib-builder --file ./scripts/esp32-arduino-lib-builder.dockerfile .",
        "docker run -t -d --name esp32-arduino-lib-builder-container esp32-arduino-lib-builder"
    ],
    title="Setup lib-builder docker",
    description="Setup esp32-arduino-lib-builder docker container"
)
env.AddCustomTarget(
    name="docker-restart",
    dependencies=None,
    actions=[
        "docker stop esp32-arduino-lib-builder-container",
        "docker rm esp32-arduino-lib-builder-container",
        "docker build --tag esp32-arduino-lib-builder --file ./scripts/esp32-arduino-lib-builder.dockerfile .",
        "docker run -t -d --name esp32-arduino-lib-builder-container esp32-arduino-lib-builder"
    ],
    title="Restart lib-builder docker",
    description="Restart esp32-arduino-lib-builder docker container"
)