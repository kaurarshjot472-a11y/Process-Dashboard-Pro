"""Background system and process sampling."""
import threading
import time
from datetime import datetime
import psutil
from PySide6.QtCore import QThread, Signal
from .config import SAMPLE_INTERVAL

class ProcessMonitor(QThread):

    snapshot_ready = Signal(object)

    monitor_error = Signal(str)



    def __init__(self, interval=SAMPLE_INTERVAL, parent=None):

        super().__init__(parent)

        self.interval = interval

        self._stop_event = threading.Event()

        self._refresh_event = threading.Event()

        self._cpu_processes = {}



    def request_refresh(self):

        self._refresh_event.set()



    def stop(self):

        self._stop_event.set()

        self._refresh_event.set()



    def run(self):

        # Prime system CPU measurement. Each process's first CPU sample may be 0.

        try:

            psutil.cpu_percent(interval=None)

        except Exception:

            pass



        previous_disk = None

        previous_net = None

        previous_time = time.monotonic()



        while not self._stop_event.is_set():

            started = time.monotonic()

            try:

                cpu_total = psutil.cpu_percent(interval=None)

                vm = psutil.virtual_memory()

                disk = psutil.disk_io_counters()

                net = psutil.net_io_counters()

                now = time.monotonic()

                elapsed = max(now - previous_time, 0.001)



                disk_read_rate = disk_write_rate = 0.0

                if disk and previous_disk:

                    disk_read_rate = max(0, disk.read_bytes - previous_disk.read_bytes) / elapsed

                    disk_write_rate = max(0, disk.write_bytes - previous_disk.write_bytes) / elapsed

                net_recv_rate = net_sent_rate = 0.0

                if net and previous_net:

                    net_recv_rate = max(0, net.bytes_recv - previous_net.bytes_recv) / elapsed

                    net_sent_rate = max(0, net.bytes_sent - previous_net.bytes_sent) / elapsed

                previous_disk, previous_net, previous_time = disk, net, now



                rows = []

                attrs = ["pid", "name", "status", "memory_info", "create_time",

                         "username", "num_threads", "ppid"]

                live_keys = set()

                for proc in psutil.process_iter(attrs=attrs, ad_value=None):

                    info = proc.info

                    pid = info.get("pid")

                    if pid is None:

                        continue

                    created = info.get("create_time")

                    key = (int(pid), created)

                    live_keys.add(key)

                    try:

                        cpu = proc.cpu_percent(interval=None)

                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):

                        cpu = 0.0

                    mem = info.get("memory_info")

                    rows.append({

                        "pid": int(pid), "name": info.get("name") or "<unknown>",

                        "status": info.get("status") or "unknown",

                        "cpu": float(cpu or 0.0),

                        "rss": int(getattr(mem, "rss", 0) or 0) if mem else 0,

                        "create_time": created, "username": info.get("username") or "",

                        "threads": int(info.get("num_threads") or 0),

                        "ppid": int(info.get("ppid") or 0),

                    })

                rows.sort(key=lambda r: r["name"].casefold())

                self.snapshot_ready.emit({

                    "timestamp": datetime.now().strftime("%H:%M:%S"),

                    "cpu_total": float(cpu_total or 0.0),

                    "memory_percent": float(vm.percent),

                    "memory_used": int(vm.used), "memory_total": int(vm.total),

                    "process_count": len(rows), "rows": rows,

                    "disk_read_rate": disk_read_rate, "disk_write_rate": disk_write_rate,

                    "net_recv_rate": net_recv_rate, "net_sent_rate": net_sent_rate,

                })

            except Exception as exc:

                self.monitor_error.emit(str(exc))



            self._refresh_event.wait(max(0.05, self.interval - (time.monotonic() - started)))

            self._refresh_event.clear()
