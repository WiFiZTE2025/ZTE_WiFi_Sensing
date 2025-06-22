import struct
import ipaddress
from network import send_udp_packet

class Command:
    def __init__(self, app):
        self.app = app
    
    def build_and_send_host_cmd_packet(self, ip, cmd_type, cmd_content, port = 8021):
        try:
            magic = 0xCAFE2025
            header = struct.pack(">I", magic)
            type_byte = struct.pack("B", cmd_type)

            if cmd_content == '':
                cmd_content = b''
            
            data = header + type_byte + cmd_content

            print(f'Data to send: {data.hex()}')
            send_udp_packet(ip, data, port = port)
        except Exception as e:
            print(f"Failed to build/send udp packet: {e}")
    
    def send_enable_command(self, enable):
        ip = self.app.get_current_ip()
        cmd_type = 1
        cmd_content = b'\x01' if enable == '1' else b'\x00'
        self.build_and_send_host_cmd_packet(ip, cmd_type, cmd_content)

    def send_sta_filter_command(self, mac_str: str):
        ip = self.app.get_current_ip()
        cmd_type = 2
        mac_bytes = bytes(int(part, 16) for part in mac_str.split(":"))
        if len(mac_bytes) != 6:
            raise ValueError("Invalid MAC address format")
    
        self.build_and_send_host_cmd_packet(ip, cmd_type, mac_bytes)

    def send_csi_config_command(self, csi_frame_type, chain_num, chain_idx):
        ip = self.app.get_current_ip()
        cmd_type = 3
        for val in (cai_frame_type, chain_num, chain_idx):
            if not (0 <= val <= 255):
                raise ValueError("Each input must be in 0-255")
        
        cmd_content = bytes([csi_frame_type, chain_num, chain_idx])
        self.build_and_send_host_cmd_packet(ip, cmd_type, cmd_content)

    def send_ip_config_command(self, target_ip_str: str):
        ip = self.app.get_current_ip()
        cmd_type = 4
        ip_bytes = ipaddress.IPv4Address(target_ip_str).packed
        self.build_and_send_host_cmd_packet(ip, cmd_type, ip_bytes)

    def send_intf_config_command(self, interface):
        ip = self.app.get_current_ip()
        cmd_type = 5
        if interface == '2.4G':
            cmd_content = b'\x00'
        elif interface == '5G':
            cmd_content = b'\x01'
        else:
            raise ValueError("band must be 2.4G or 5G")
        self.build_and_send_host_cmd_packet(ip, cmd_type, cmd_content)

    def send_chk_connect_command(self):
        ip = self.app.get_current_ip()
        cmd_type = 6
        self.build_and_send_host_cmd_packet(ip, cmd_type, '')