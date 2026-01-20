import os
import subprocess
import platform
import shutil
from pathlib import Path

GNUPG_DIR = Path.home() / ".gnupg"
GPG_CONF = GNUPG_DIR / "gpg.conf"
GPG_AGENT_CONF = GNUPG_DIR / "gpg-agent.conf"


def detect_pinentry():
    """Detecta el pinentry apropiado basado en el entorno."""
    system = platform.system()
    if system == "Windows":
        # En Windows, buscar pinentry-w32.exe o pinentry.exe
        possible_names = ["pinentry-w32.exe", "pinentry.exe"]
        for name in possible_names:
            path = shutil.which(name)
            if path:
                return path
        return "pinentry.exe"  # fallback, aunque no exista
    else:
        # Para Linux/Unix, detectar si hay DISPLAY
        if os.environ.get('DISPLAY'):
            return "pinentry-gtk-2"  # o pinentry-qt
        else:
            return "pinentry-tty"


def init_gpg() -> None:
    print("🔐 Inicializando configuración GPG...")

    # Verificar si gpg está instalado
    gpg_path = shutil.which("gpg")
    if not gpg_path:
        raise FileNotFoundError("GPG no está instalado o no está en el PATH. Instala Gpg4win en Windows.")

    subprocess.run([gpg_path, "--version"], check=True)

    # Crear directorio con permisos correctos
    GNUPG_DIR.mkdir(mode=0o700, exist_ok=True)
    os.chmod(GNUPG_DIR, 0o700)

    # Configurar gpg.conf con opciones optimizadas
    gpg_conf_content = """# Configuración optimizada para GPG
use-agent
keyserver hkps://keys.openpgp.org
keyserver-options timeout=10
personal-cipher-preferences AES256 AES192 AES CAST5
personal-digest-preferences SHA512 SHA384 SHA256 SHA224
personal-compress-preferences ZLIB BZIP2 ZIP Uncompressed
default-preference-list SHA512 SHA384 SHA256 SHA224 AES256 AES192 AES CAST5 ZLIB BZIP2 ZIP Uncompressed
cert-digest-algo SHA512
default-cert-level 2
"""

    GPG_CONF.write_text(gpg_conf_content)
    os.chmod(GPG_CONF, 0o600)

    # Configurar gpg-agent.conf con pinentry apropiado
    pinentry = detect_pinentry()
    gpg_agent_content = f"""pinentry-program {pinentry}
pinentry-mode loopback
allow-loopback-pinentry
max-cache-ttl 86400
default-cache-ttl 3600
"""

    GPG_AGENT_CONF.write_text(gpg_agent_content)
    os.chmod(GPG_AGENT_CONF, 0o600)

    # Recargar agente
    subprocess.run(["gpg-connect-agent", "reloadagent", "/bye"])

    # Establecer configuración de confianza básica
    print("🔄 Inicializando base de datos de confianza...")
    subprocess.run([gpg_path, "--update-trustdb"], check=True)

    print("✅ GPG inicializado correctamente")