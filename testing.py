from subprocess import Popen, PIPE

program_path = "./abdada.exe"

p = Popen([program_path], stdout=PIPE, stdin=PIPE)


def write(move: str) -> None:
    p.stdin.write(bytes(move, "utf-8") + b"\n")
    p.stdin.flush()


def read() -> str:
    return str(p.stdout.readline().strip())[2:-1]

def kill() -> None:
    p.terminate()