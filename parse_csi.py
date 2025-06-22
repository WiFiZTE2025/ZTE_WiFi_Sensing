import struct
from collections import OrderedDict
import csv
import os
from datetime import datetime

VENDOR_MAP = {
    1: "qca",
    2: 'mtk',
    3: 'tbd'
}

CHIP_MAP = {
    1: "MTK 7916",
    2: "QCA 6224"
}

BW_MAP = {
    0: "20MHz",
    1: "40MHz",
    2: "80MHz",
    3: "160MHz"
}

MCS_MAP = {
    0: "MCS 0",
    1: "MCS 1",
    2: "MCS 2",
    3: "MCS 3",
    4: "MCS 4",
    5: "MCS 5",
    6: "MCS 6",
    7: "MCS 7",
    8: "MCS 8",
    9: "MCS 9",
    10: "MCS 10",
    11: "MCS 11",
    12: "MCS 12",
    13: "MCS 13",
    14: "MCS 14",
    15: "MCS 15"
}

class CSVCsiWriter:
    def __init__(self, max_records = 1000, output_dir = "data"):
        self.max_records = max_records
        self.output_dir = output_dir
        self.current_count = 0
        self.part_number = 0
        self.file = None
        self.writer = None
        self.base_filename = None
        os.makedirs(output_dir, exist_ok=True)
        self._new_file()
    
    def _new_file(self):
        if self.file:
            self.file.close()
        timestamp = datetime.now().strftime("%Y%m%d=%H%M%S")
        self.base_filename = f"{timestamp}_part{self.part_number}.csv"
        self.file_path = os.path.join(self.output_dir, self.base_filename)
        self.file = open(self.file_path, 'w', newline='')
        self.writer = csv.DictWriter(self.file, fieldnames=self._get_filenames())
        self.writer.writeheader()
        self.current_count = 0
        self.part_number += 1
    
    def _get_filenames(self):
        return [
            'magic_high', 'packet_sn', 'vendor', 'chip_id', 'timestamp',
            'status', 'bandwidth', 'phy_mode', 'rx_chain_num',
            'data_len_per_chain', 'tot_data_length', 'peer_mac',
            'chain_rssi', "chain_phase", "agc_gain", 'mcs', 'gi_type',
            'coding', 'stbc', 'beamformed', 'dcm', 'ltf_size', 'sgi', 'csi_cnt'
        ]

    def write(self, report):
        filtered = {k:v for k,v in report.items() if k not in ['csi_i', 'csi_q']}
        if self.current_count >= self.max_records:
            self._new_file()
        self.writer.writerow(filtered)
        self.current_count += 1
    
    def close(self):
        if self.file:
            self.file.close()
    
def parse_csi_data(data):
    try:
        magic_num = struct.upack_from('<I', data)[0]
        magic_high = (magic_num >> 16) & 0xFFFF
        packet_sn = magic_num & 0xFFFF

        result = OrderedDict()
        result['magic_high'] = f"0x{magic_high:04X}"
        result['packet_sn'] = packet_sn

        if magic_high != 0xCAFE:
            print(f"magic number check failed, get {magic_high:04X} expected 0xCAFE")
            return None
        fmt = '<'
        fmt += 'I'
        fmt += 'B'
        fmt += 'I'
        fmt += 'Q'
        fmt += 'I'
        fmt += 'I'
        fmt += 'I'
        fmt += 'B'
        fmt += 'H'
        fmt += 'I'
        fmt += '6B'
        fmt += '16i'
        fmt += '16i'
        fmt += '16B'
        fmt += 'H'
        fmt += '7B'
        fmt += 'Q'
        fmt += 'H'
        fmt += '512i'
        fmt += '512i'

        unpacked = struct.unpack_from(fmt, data)

        result['vendor'] = VENDOR_MAP.get(unpacked[1], f'unknown({unpacked[1]})')
        result['chip_id'] = CHIP_MAP.get(unpacked[2], f'unknown({unpacked[2]})')
        result['timestamp'] = unpacked[3]
        result['status'] = unpacked[4]
        result['bandwidth'] = BW_MAP.get(unpacked[5], f'unknown({unpacked[1]})')
        result['phy_mode'] = unpacked[6]
        result['rx_chain_num'] = unpacked[7]
        result['data_len_per_chain'] = unpacked[8]
        result['tot_data_length'] = unpacked[9]

        result['peer_mac'] = ':'.join(f"{b:02x}" for b in unpacked[10:16])

        result['chain_rssi'] = unpacked[16:32]
        result['chain_phase'] = unpacked[32:48]
        result['agc_gain'] = unpacked[48:64]

        result['mcs'] = unpacked[64]
        result['gi_type'] = unpacked[65]
        result['coding'] = unpacked[66]
        result['stbc'] = unpacked[67]
        result['beamformed'] = unpacked[68]
        result['dcm'] = unpacked[69]
        result['ltf_size'] = unpacked[70]
        result['sgi'] = unpacked[71]

        result['csi_cnt'] = unpacked[73]
        result['csi_i'] = unpacked[74:74+512]
        result['csi_q'] = unpacked[74+512:74+1024]

        return result
    
    except struct.error as e:
        print(f'parse failed {str(e)}')
        return None