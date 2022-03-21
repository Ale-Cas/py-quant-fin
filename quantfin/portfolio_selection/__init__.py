import os
import platform

if platform.system() == "Darwin" and "arm64" in platform.mac_ver():
    os.system("/usr/bin/arch -x86_64 /bin/zsh")
