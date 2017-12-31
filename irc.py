import curses
import socket
import threading
from time import sleep

from curses import wrapper

UDP_PORT = 5005
B_IP = "255.255.255.255"

class ScreenThread(threading.Thread):
    def __init__(self, stdscr):
        curses.echo()

        height = curses.LINES - 2; width = curses.COLS
        self.chat_win = curses.newwin(height, width)
        self.chat_win.scrollok(True)

        begin_x = 0; begin_y = curses.LINES - 1
        self.input_win = curses.newwin(1, width, begin_y, begin_x)

        self.line = curses.newwin(1, width, begin_y - 1, begin_x)
        self.line.hline("-", width)
        self.line.refresh()

        self._end = False

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if hasattr(socket,'SO_BROADCAST'):
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.printlock = threading.Lock()

        threading.Thread.__init__ ( self )

    def run(self):
        self.sock.bind(("", UDP_PORT))
        self.sock.settimeout(0.02)
        while not self._end:
            try:
                data, addr = self.sock.recvfrom(1024)
                data = data.strip()
                if data:
                    self.printline(addr[0], data)
            except socket.timeout:
                pass

    def readline(self):
        message = self.input_win.getstr()
        message = message.strip()
        self.input_win.clear()
        return message

    def printline(self, addr, message):
        with self.printlock:
            message = message.decode('ascii',errors='ignore').replace("\n", "")
            m = "<{}> {}\n".format(addr, message)
            self.chat_win.addstr(m)
            self.chat_win.refresh()

    def stop(self):
        self._end = True

    def send(self, message):
        self.sock.sendto(message, (B_IP, UDP_PORT))

    def is_running(self):
        return not self._end





def main(stdscr):
    screen = ScreenThread(stdscr)
    screen.start()

    while screen.is_running():
        try:
            m = screen.readline()
        except KeyboardInterrupt:
            m = b"/quit"

        if m == b"/quit":
            screen.stop()
            print("end")
            screen.join(timeout=0.5)
            break
        else:
            #screen.printline("you", m)
            screen.send(m)


if __name__ == "__main__":
    wrapper(main)
