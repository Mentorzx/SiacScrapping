import importlib.util
import os
import sys

from cx_Freeze import Executable, setup

current_path = os.path.abspath(os.path.dirname(__file__))
src_path = os.path.join(current_path, "src")
sys.path.append(src_path)


def read_requirements():
    with open("requirements.txt") as f:
        return [line.split("==")[0].strip() for line in f.readlines() if line.strip()]


def detect_unavailable_modules():
    unavailable_modules = []
    available_modules = []
    for module in read_requirements():
        try:
            if importlib.util.find_spec(module):
                available_modules.append(module)
        except ModuleNotFoundError:
            unavailable_modules.append(module)
    return unavailable_modules, available_modules


available = detect_unavailable_modules()[1]
print("Available modules: ", available)

build_exe_options = {
    "packages": available,
    "include_files": ["src", "config", "logs"],
    "include_msvcr": True,
}

setup(
    name="SiacScrappingSync",
    version="1.1.3",
    description="Scrapping automation for Siac",
    options={"build_exe": build_exe_options},
    executables=[Executable("src/main.py", base="Win32GUI")],
)
