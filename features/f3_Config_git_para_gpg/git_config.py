import subprocess
import os
import shutil
import sys
import re
from typing import Tuple


def run(cmd: list[str]) -> str:
    return subprocess.check_output(
        cmd,
        stderr=subprocess.DEVNULL,
        text=True
    )


def check_gpg_available():
    if shutil.which("gpg") is None:
        raise RuntimeError("GPG no está disponible en el PATH")


def find_signing_subkey() -> str:
    output = run(["gpg", "--list-secret-keys", "--with-colons"])

    for line in output.splitlines():
        if line.startswith("ssb") and "s" in line.split(":")[11]:
            return line.split(":")[4]

    raise RuntimeError("No se encontró subclave de firma (S)")


def extract_name_email() -> Tuple[str, str]:
    output = run(["gpg", "--list-keys", "--with-colons"])

    for line in output.splitlines():
        if line.startswith("uid"):
            uid = line.split(":")[9]
            match = re.match(r"(.*)<(.*)>", uid)
            if match:
                return match.group(1).strip(), match.group(2).strip()

    raise RuntimeError("No se pudo extraer nombre/email desde GPG")


def git_config(key: str, value: str):
    subprocess.run(
        ["git", "config", "--global", key, value],
        check=True
    )


def setup_gpg_tty():
    if sys.stdin.isatty():
        tty = run(["tty"]).strip()
        os.environ["GPG_TTY"] = tty


def setup_gpg_automation():
    os.environ["GIT_TERMINAL_PROMPT"] = "0"
    os.environ["GPG_BATCH"] = "1"


def configure_git_with_gpg():
    print("🔧 Configurando Git con GPG...")

    check_gpg_available()

    signing_key = find_signing_subkey()
    name, email = extract_name_email()

    git_config("user.signingkey", signing_key)
    git_config("commit.gpgsign", "true")
    git_config("tag.gpgSign", "true")
    git_config("user.name", name)
    git_config("user.email", email)

    setup_gpg_tty()
    setup_gpg_automation()

    print("✅ Git configurado correctamente con GPG")