import socket
import sys
from parse_csi import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
import tkinter.messagebox as messagebox

def get_default_ip():
    try:
        ip_list = []
        for info in socket.getaddrinfo(socket.gethostname(), None):
            family, _, _, _, sockaddr = info
            if family == socket.AF_INET:
                ip = sockaddr[0]
                if not ip.startswith('127.'):
                    ip_list.append(ip)
        for ip in ip_list:
            if ip.startswith("192.168."):
                return ip
        if ip_list:
            return ip_list[0]
        return '127.0.0.1'    
    except Exception:
        return '127.0.0.1'

def get_gateway_ip():
    local_ip = get_default_ip()
    try:
        parts = local_ip.split('.')
        if len(parts) == 4:
            parts[-1] = '1'
            gateway_ip = '.'.join(parts)
            return gateway_ip
        else:
            raise ValueError('Invalid Ip format')
    except Exception:
        return '192.168.1.1'

def send_udp_packet(ip, data, port=8021):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 8022))
        sock.sendto(data, (ip, port))
        print(f"Send to {ip}:{port} from port 8022 -> {data.hex()}")
    except Exception as e:
        print(f"Failed to send UDP packet: {e}")
    finally:
        sock.close()

def hexdump(data):
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_str = ' '.join(f"{b:02x}" for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
        print(f"{i:08x} {hex_str.ljust(47)} |{ascii_str}|")
        
def udp_ok_listener(ip, app):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.bind((ip, 8022))
        print(f"Listening on {ip}:8022...")
        while True:
            data, addr = sock.recvfrom(8192)
            if data == b'OK':
                print("get ok, device is rdy")
                if hasattr(app, "ok_timeout_timer") and app.ok_timeout_timer and app.ifcheckstatue:
                    app.ok_timeout_timer.cancel()
                    app.ok_received = True
                    messagebox.showinfo("connected", "device rdy")
                    app.ifcheckstatue = False
    except KeyboardInterrupt:
        print("\n Stopped by user")
    except Exception as e:
        print(f"Error:{str(e)}")
    finally:
        sock.close()

def udp_listener(ip, port, app):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    csv_writer = CSVCsiWriter(max_records = 10000)
    recv_cnt = 0
    report_cnt = 0
    last_time = time.time()

    try:
        sock.bind((ip, port))
        print(f"Listening on {ip}:{port}...")

        while True:
            data, addr = sock.recvfrom(8192)
            report = parse_csi_data(data)
            if report:
                app.update_csi_result(report['csi_i'], report['csi_q'])
                if app.is_csi_plot_updating == False:
                    threading.Thread(target=app.update_plot, daemon=True).start()
                app.update_statistic(report)
                csv_writer.write(report)
                recv_cnt += 1
                report_cnt += 1
            current_time = time.time()
            if current_time - last_time >= 1.0:
                app.update_report_rate(report_cnt)
                report_cnt = 0
                last_time = current_time
    except KeyboardInterrupt:
        print("\n Stopped by user")
    except Exception as e:
        print(f"Error:{str(e)}")
    finally:
        sock.close()