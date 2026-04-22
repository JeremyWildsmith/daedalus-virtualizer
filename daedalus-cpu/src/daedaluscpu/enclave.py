import subprocess
import argparse
import os
import signal
import ctypes
import sys
import queue
import time
import threading
import termios
import tty
import select

libc = ctypes.CDLL("libc.so.6", use_errno=True)

class EnclaveChannel:
    def __init__(self, fd_in, fd_out):
        self.fd_in = fd_in
        self.fd_out = fd_out
        
        self.recv_queue = queue.Queue()
        self.transmit_queue = queue.Queue()

        self.stop = threading.Event()
        self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self.transmit_thread = threading.Thread(target=self._transmit_loop, daemon=True)

        self.recv_thread.start()
        self.transmit_thread.start()

    def _recv_loop(self):
        while not self.stop.is_set():
            
            r, _, _ = select.select([self.fd_out], [], [], 0.1)
            
            if not r:
                continue

            try:
                data = os.read(self.fd_out, 4096)
            except BlockingIOError:
                continue

            if data:
                self.recv_queue.put(data)
            else:
                self.stop.set()
                break

    def _transmit_loop(self):
        while not self.stop.is_set():
            try:
                write_data = self.transmit_queue.get(timeout=0)
            except queue.Empty:
                continue
            
            if not write_data:
                continue
            
            while write_data and not self.stop.is_set():
                try:
                    n = os.write(self.fd_in, write_data)
                    write_data = write_data[n:]
                except InterruptedError:
                    continue
                except BrokenPipeError:
                    self.stop.set()
                    break

    def send(self, data: bytes):
        self.transmit_queue.put(bytes(data))

    def recv(self, timeout: float | None = None) -> bytes | None:
        try:
            return self.recv_queue.get(timeout=timeout)
        except queue.Empty:
            return b""

    def close(self):
        self.stop.set()
        self.transmit_queue.put(None)

        try:
            os.close(self.fd_in)
        except OSError:
            pass
        
        try:
            os.close(self.fd_out)
        except OSError:
            pass

def launch_enclave(interpreter: str, firmware: str) -> EnclaveChannel:
    def set_pdeathsig(sig=signal.SIGTERM):
        def callback():
            return libc.prctl(1, sig)

        return callback

    proc = subprocess.Popen(
        [interpreter, "--pipe", firmware],
        stdout=sys.stdout,
        stderr=sys.stderr,
        preexec_fn=set_pdeathsig(signal.SIGTERM)
    )
    
    print("Attempting to establish connection with secure enclave...", file=sys.stderr)
    for _ in range(10):
        try:
            fd_in = os.open(f"/tmp/daedalus.pid{proc.pid}.input", os.O_WRONLY)
            fd_out = os.open(f"/tmp/daedalus.pid{proc.pid}.output", os.O_RDONLY | os.O_NONBLOCK)
            break
        except FileNotFoundError as e:
            time.sleep(1)
            pass
    
    if not fd_in or not fd_out:
        raise Exception("Connection error")
    
    print("Connection established.", file=sys.stderr)
        
    return EnclaveChannel(fd_in, fd_out)

def execute_pty(channel: EnclaveChannel):
    stdin_fd = sys.stdin.fileno()
    old_term = termios.tcgetattr(stdin_fd)
    #tty.setraw(stdin_fd)

    print("Launched a PTY to the secure enclave MMIO input and output channel.\n")

    try:
        while True:
            r, _, _ = select.select([stdin_fd], [], [], 0.05)
            if r:
                ch = os.read(stdin_fd, 1)
                if ch:
                    channel.send(ch)

            out = channel.recv(timeout=0)
            if out:
                os.write(sys.stdout.fileno(), out)
                sys.stdout.flush()

    except KeyboardInterrupt:
        pass
    finally:
        termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_term)
        channel.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "interpreter",
        help="Path to interpreter"
    )
    
    parser.add_argument(
        "firmware",
        help="Path to firmware to execute on the interpreter"
    )

    args = parser.parse_args()
    
    enclave = launch_enclave(args.interpreter, args.firmware)
    
    execute_pty(enclave)
