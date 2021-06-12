import socketserver
import subprocess
from typing import Tuple


def get_free_port():
    with socketserver.TCPServer(("localhost", 0), None) as s:
        free_port = s.server_address[1]
        return free_port


def kubectl_port_forward(
    ns: str, what: str, port_remote: int
) -> Tuple[subprocess.Popen, int]:
    port_local = get_free_port()
    p = subprocess.Popen(
        [
            "kubectl",
            "-n",
            "feast-dev",
            "port-forward",
            what,
            f"{port_local}:{port_remote}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    print(f"pid: {p.pid}")
    try:
        n_sec = 2
        stdout, stderr = p.communicate(timeout=n_sec)
        raise ValueError(
            f"Port-forward process for {what} has terminated within "
            f"{n_sec} sec: stdout={str(stdout)}, stderr={str(stderr)}"
        )
    except subprocess.TimeoutExpired:
        print(
            f"Port-forward process for '{what}' seems to be working:"
            f"check 'localhost:{port_local}'"
        )

    return p, port_local
