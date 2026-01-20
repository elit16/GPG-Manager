import sys
from command import register

commands = {}

command_name, func = register()
commands[command_name] = func

if len(sys.argv) < 2:
    print(f"Usa: python app/main.py {command_name}")
    sys.exit(1)

cmd = sys.argv[1]

if cmd not in commands:
    print("Comando no válido")
    sys.exit(1)

commands[cmd]()
