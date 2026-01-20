import os
from getpass import getpass
import shutil
import subprocess
import sys
from pathlib import Path
import tempfile


##FIX: VALIDAR QUE CLAVES TIENE ANTES EL USUARIO
def collect_user_info():
    print("\n=== Generación de llave maestra GPG ===\n")

    name = input("Nombre completo: ").strip()
    email = input("Email: ").strip()
    comment = input("Comentario (opcional): ").strip()

    while True:
        pwd1 = getpass("Contraseña maestra: ")
        pwd2 = getpass("Confirmar contraseña: ")
        if pwd1 == pwd2 and pwd1:
            break
        print("Las contraseñas no coinciden o están vacías.\n")

    return {
        "name": name,
        "email": email,
        "comment": comment,
        "password": pwd1
    }

def find_gpg():
    gpg = shutil.which("gpg")
    if not gpg:
        raise RuntimeError("GPG no encontrado. Instala Gpg4win y reinicia la terminal.")
    return gpg

def build_master_key_config(user):
    lines = [
        "%echo Generating master key",
        "Key-Type: RSA",
        "Key-Length: 4096",
        "Key-Usage: cert,sign",
        "Subkey-Type: RSA",
        "Subkey-Length: 4096",
        "Subkey-Usage: sign",
        f"Name-Real: {user['name']}",
        f"Name-Email: {user['email']}",
        f"Name-Comment: {user['comment']}",
        "Expire-Date: 0",
        f"Passphrase: {user['password']}",
        "%commit",
        "%echo done"
    ]
    return "\n".join(lines)

def generate_master_key(user):
    gpg = find_gpg()
    config_content = build_master_key_config(user)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
        f.write(config_content)
        config_file = f.name



    try:
        print("Generando llave maestra...")

        result = subprocess.run(
            [gpg, "--batch", "--pinentry-mode", "loopback", "--generate-key", config_file],
            capture_output=True,
            text=True
        )

        print("STDOUT:\n", result.stdout)
        print("STDERR:\n", result.stderr)

        if result.returncode != 0:
            print("X Error generando llave maestra")
            sys.exit(1)

        print("Llave maestra generada.")

        result = subprocess.run(
            [gpg, "--list-secret-keys", "--with-colons", "--fingerprint", user["email"]],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("No se pudo obtener fingerprint")
            sys.exit(1)

        lines = result.stdout.splitlines()

        for i, line in enumerate(lines):
            if line.startswith("sec"):
                for j in range(i + 1, min(i + 10, len(lines))):
                    if lines[j].startswith("fpr:"):
                        fingerprint = lines[j].split(":")[9]
                        print(f"Huella digital: {fingerprint}")
                        return fingerprint

        print("No se pudo extraer huella digital")
        sys.exit(1)

    finally:
        os.unlink(config_file)



def run():
    user_info = collect_user_info()
    print("\nDatos capturados correctamente:")
    print(user_info["name"], user_info["email"])
    generate_master_key(user=user_info)


