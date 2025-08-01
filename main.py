import argparse
import tkinter as tk
import socket
import threading
import time
import numpy as np

from tkinter import ttk

from statistic import Statistic
from parse_csi import *
from network import *
from hostcmd import Command

class ZTECsiTool:
    def __init__(self):
        self.command = Command(self)
        self.stat = Statistic()

        self.master = tk.Tk()
        self.master.title('ZTECsiTool')

        self.port = 12345

        self.sock = None
        self.ifcheckstatue = False

        self.stat_following = {
            'bw': 'discrete',
            'rssi0': 'integer',
            'rssi1': 'integer',
            'rssi2': 'integer',
            'rssi3': 'integer',
            'rssi4': 'integer',
            'rssi5': 'integer',
            'mcs': 'discrete'
        }

        self.current_csi_result = {'csi_i': None, 'csi_q': None}
        self.refresh_interval = 0.05
        self.is_csi_plot_updating = False
        self.is_stat_widget_updating = False
        self.init_csi_config()
        self.init_plot()
        self.init_stat()

    def init_csi_config(self):
        self.cfg_widget = {}
        self.cfg_widget['header'] = tk.Label(self.master, text="Configure")
        self.cfg_widget['header'].grid(row = 0, column = 0, sticky='w')

        self.cfg_widget['frame'] = tk.Frame(self.master)
        self.cfg_widget['frame'].grid(row = 1, column = 0, sticky='w')

        row = 0

        self.chk_button = tk.Button(self.cfg_widget['frame'], text='check connect', command=self.send_chk_connect_command, width=15)
        self.chk_button.grid(row=row, column=0, padx=5, pady=5)
        row += 1

        self.ip_group = tk.LabelFrame(self.cfg_widget['frame'], text='Gateway', padx=5, pady=5, font=('Arial', 10, 'bold'))
        self.ip_group.grid(row=row, column=0, columnspan=3, sticky='w', padx=5, pady=5)
        self.ip_label = tk.Label(self.ip_group, text='ZTE AP IP (gateway):')
        self.ip_label.grid(row=row, column=0, padx=5, pady=5, sticky='w')
        self.ip_entry = tk.Entry(self.ip_group)
        self.ip_entry.grid(row=row, column=1, padx=5, pady=5, sticky='w')
        self.default_ip = get_gateway_ip()
        self.current_ip = self.default_ip
        self.ip_entry.insert(0 ,self.default_ip)
        row += 1

        self.interface_group = tk.LabelFrame(self.cfg_widget['frame'], text='Interface Config', padx=5, pady=5, font=('Arial', 10, 'bold'))
        self.interface_group.grid(row=row, column=0, columnspan=3, sticky='w', padx=5, pady=5)
        self.interface_var = tk.StringVar(value='5G')
        self.interface_labal = tk.Label(self.interface_group, text='Interface')
        self.interface_labal.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.radio_24g = tk.Radiobutton(self.interface_group, text='2.4G', variable=self.interface_var, value='2.4G')
        self.radio_24g.grid(row=0, column=1, padx=(0,20), sticky='w')
        self.radio_5g = tk.Radiobutton(self.interface_group, text='5G', variable=self.interface_var, value='5G')
        self.radio_5g.grid(row=0, column=2, padx=(0,20), sticky='w')
        row += 1

        self.subtype_options = {
            "QoS Data b'1000": 8,
        }
        self.type_options = {
            "Mgmt b'00": 0,
            "Control b'01": 1,
            "Data b'10": 2,
            "Extension b'11": 3
        }
        
        self.csi_config_group = tk.LabelFrame(self.cfg_widget['frame'], text="CSI Config", padx=5, pady=5, font=('Arial', 10, 'bold')) 
        self.csi_config_group.grid(row=row, column=0, columnspan=3, sticky='w', padx=5, pady=5) 
    
        self.csi_frame_type_label = tk.Label(self.csi_config_group, text="CSI Frame Type:") 
        self.csi_frame_type_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='w') 
        # Subtype TOM 
        self.subtype_label = tk.Label(self.csi_config_group, text="Subtype") 
        self.subtype_label.grid(row=1, column=0, padx=2, pady=5, sticky='w') 
        self.subtype_combobox = ttk.Combobox(self.csi_config_group, values=list(self.subtype_options.keys()), width=15, state='readonly')
        self.subtype_combobox.grid(row=1, column=1, padx=2, pady=5, sticky='w') 
        self.subtype_combobox.current(0) 
        # Type 741a1 
        self.type_label = tk.Label(self.csi_config_group, text="Type") 
        self.type_label.grid(row=2, column=0, padx=2, pady=5, sticky='w') 
        self.type_combobox = ttk.Combobox(self.csi_config_group, values=list(self.type_options.keys()), width=15, state='readonly') 
        self.type_combobox.grid(row=2, column=1, padx=2, pady=5, sticky='w') 
        self.type_combobox.current(2) 
        # Chain Number 
        self.chain_num_label = tk.Label(self.csi_config_group, text="Chain Number")
        self.chain_num_label.grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.chain_num_entry = tk.Entry(self.csi_config_group, width=10)
        self.chain_num_entry.insert(0, 6)
        self.chain_num_entry.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        self.chain_idx_label = tk.Label(self.csi_config_group, text="Chain Index")
        self.chain_idx_label.grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.chain_idx_entry = tk.Entry(self.csi_config_group, width=10)
        self.chain_idx_entry.insert(0, 0)
        self.chain_idx_entry.grid(row=4, column=1, padx=5, pady=5, sticky='w')
        row += 1

        self.enable_frame = tk.Frame(self.cfg_widget['frame'])
        self.enable_frame.grid(row=row, column=0, columnspan=2, padx=5, sticky='w')
        self.enable_label = tk.Label(self.enable_frame, text='Enable:')
        self.enable_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.enable_var = tk.IntVar(value=1)
        self.enable_raio_1 = tk.Radiobutton(self.enable_frame, text='1', variable=self.enable_var, value=1)
        self.enable_raio_1.grid(row=0, column=1, padx=2, pady=5, sticky='w')
        self.enable_raio_0 = tk.Radiobutton(self.enable_frame, text='0', variable=self.enable_var, value=0)
        self.enable_raio_0.grid(row=0, column=1, padx=60, pady=5, sticky='w')
        self.enable_button = tk.Button(self.cfg_widget['frame'], text='Set', command=self.send_enable_command, width=5)
        self.enable_button.grid(row=row, column=2, padx=5, pady=5)
        row += 1

        self.mac_frame = tk.Frame(self.cfg_widget['frame'])
        self.mac_frame.grid(row=row, column=0, columnspan=2, padx=5, sticky='w')
        self.mac_label = tk.Label(self.mac_frame, text='MAC:')
        self.mac_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.mac_entry = tk.Entry(self.mac_frame)
        self.mac_entry.insert(0, '0a:19:c6:51:00:12')
        self.mac_entry.grid(row=0, column=1, padx=5, pady=5)
        self.mac_button = tk.Button(self.cfg_widget['frame'], text='Set', command=self.send_sta_filter_command, width=5)
        self.mac_button.grid(row=row, column=2, padx=5, pady=5)
        row += 1

        self.target_ip_frame = tk.Frame(self.cfg_widget['frame'])
        self.target_ip_frame.grid(row=row, column=0, columnspan=2, padx=5, sticky='w')
        self.target_ip_label = tk.Label(self.target_ip_frame, text='CSI Receiver IP:')
        self.target_ip_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.target_ip_entry = tk.Entry(self.target_ip_frame)
        self.target_ip_entry.insert(0, get_default_ip())
        self.target_ip_entry.grid(row=0, column=1, padx=5, pady=5)
        self.target_ip_button = tk.Button(self.cfg_widget['frame'], text='Set', command=self.send_ip_config_command, width=5)
        self.target_ip_button.grid(row=row, column=2, padx=5, pady=5)
        row += 1

        self.start_button = tk.Button(self.cfg_widget['frame'], text="COnfigure CSI Report", command=self.config_csi_all, width = 20)
        self.start_button.grid(row=row, column=0, columnspan=3, padx=5, pady=5, sticky='w')
        row += 1

        self.cfg_warn_lable = tk.Label(
            self.cfg_widget['frame'],
            text='Rebooting AP is required if configure CSI report again',
            fg='red',
            font=('Arial', 8)
        )
        self.cfg_warn_lable.grid(row=row, column=0, padx=5, pady=5)
        row += 1

        self.tot_row = row
    
    def init_plot(self):
        self.report_rate_label = tk.Label(self.master, text="report rate: 0/s")
        self.report_rate_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        self.fig = Figure(figsize=(6, 6), dpi=100)
        self.ax_iq = self.fig.add_subplot(311)
        self.ax_abs = self.fig.add_subplot(312)
        self.ax_arc = self.fig.add_subplot(313)

        self.ax_iq.set_title("CSI I/Q")
        self.ax_abs.set_title("CSI Mag")
        self.ax_arc.set_title("CSI Agnel")

        self.fig.tight_layout(pad=2.0)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().grid(row=1, column=1, padx=9, pady=10, sticky='nsew')

    def init_stat(self):
        for stat in self.stat_following.keys():
            self.stat.register(stat, self.stat_following[stat])
        
        self.stat_widget = {}

        self.stat_widget['header'] = tk.Label(self.master, text='Statistics')
        self.stat_widget['header'].grid(row=0, column=2, sticky='w')

        self.stat_widget['stat_frame'] = tk.Frame(self.master)
        self.stat_widget['stat_frame'].grid(row=1, column=2, sticky='w')
        row = 0

        self.stat_widget['bw_frame'] = tk.Frame(self.stat_widget['stat_frame'])
        self.stat_widget['bw_frame'].grid(row=row, column=4, sticky='w')
        self.stat_widget['bw'] = tk.Label(self.stat_widget['bw_frame'], text='Bandwidth Count')
        self.stat_widget['bw'].grid(row=0, column=0, columnspan=2, sticky='w')
        tmp_row_cnt = 1
        self.stat_widget['bw_header_name'] = tk.Label(self.stat_widget['bw_frame'], text='bw', width=15)
        self.stat_widget['bw_header_name'].grid(row=tmp_row_cnt, column=0, sticky='w')
        self.stat_widget['bw_header_tot'] = tk.Label(self.stat_widget['bw_frame'], text='Total', width=15)
        self.stat_widget['bw_header_tot'].grid(row=tmp_row_cnt, column=1, sticky='w')
        self.stat_widget['bw_header_5s'] = tk.Label(self.stat_widget['bw_frame'], text='Last 5s', width=15)
        self.stat_widget['bw_header_5s'].grid(row=tmp_row_cnt, column=2, sticky='w')
        tmp_row_cnt += 1
        for bw in ['20MHz', '40MHz', '80MHz', '160MHz']:
            self.stat_widget['bw_' + bw + '_label'] = tk.Label(self.stat_widget['bw_frame'], text=bw, width=15)
            self.stat_widget['bw_' + bw + '_label'].grid(row=tmp_row_cnt, column=0, sticky='w')
            self.stat_widget['bw_' + bw + '_tot_value'] = tk.Label(self.stat_widget['bw_frame'], text='0', width=15)
            self.stat_widget['bw_' + bw + '_tot_value'].grid(row=tmp_row_cnt, column=1, sticky='w')
            self.stat_widget['bw_' + bw + '_5s_value'] = tk.Label(self.stat_widget['bw_frame'], text='0', width=15)
            self.stat_widget['bw_' + bw + '_5s_value'].grid(row=tmp_row_cnt, column=2, sticky='w')
            tmp_row_cnt += 1
        row += 1

        self.stat_widget['mcs_frame'] = tk.Frame(self.stat_widget['stat_frame'])
        self.stat_widget['mcs_frame'].grid(row=row, column=4, sticky='w')
        self.stat_widget['mcs'] = tk.Label(self.stat_widget['mcs_frame'], text='MCS Count')
        self.stat_widget['mcs'].grid(row=0, column=0, columnspan=2, sticky='w')
        tmp_row_cnt = 1
        self.stat_widget['mcs_header_name'] = tk.Label(self.stat_widget['mcs_frame'], text='mcs', width=15)
        self.stat_widget['mcs_header_name'].grid(row=tmp_row_cnt, column=0, sticky='w')
        self.stat_widget['mcs_header_tot'] = tk.Label(self.stat_widget['mcs_frame'], text='Total', width=15)
        self.stat_widget['mcs_header_tot'].grid(row=tmp_row_cnt, column=1, sticky='w')
        self.stat_widget['mcs_header_5s'] = tk.Label(self.stat_widget['mcs_frame'], text='Last 5s', width=15)
        self.stat_widget['mcs_header_5s'].grid(row=tmp_row_cnt, column=2, sticky='w')
        tmp_row_cnt += 1
        for mcs in MCS_MAP:
            self.stat_widget['mcs_' + str(mcs) + '_label'] = tk.Label(self.stat_widget['mcs_frame'], text=MCS_MAP[mcs], width=15)
            self.stat_widget['mcs_' + str(mcs) + '_label'].grid(row=tmp_row_cnt, column=0, sticky='w')
            self.stat_widget['mcs_' + str(mcs) + '_tot_value'] = tk.Label(self.stat_widget['mcs_frame'], text='0', width=15)
            self.stat_widget['mcs_' + str(mcs) + '_tot_value'].grid(row=tmp_row_cnt, column=1, sticky='w')
            self.stat_widget['mcs_' + str(mcs) + '_5slabel'] = tk.Label(self.stat_widget['mcs_frame'], text='0', width=15)
            self.stat_widget['mcs_' + str(mcs) + '_5slabel'].grid(row=tmp_row_cnt, column=2, sticky='w')
            tmp_row_cnt += 1
        row += 1

        self.stat_widget['rssi_frame'] = tk.Frame(self.stat_widget['stat_frame'])
        self.stat_widget['rssi_frame'].grid(row=row, column=4, sticky='w')
        self.stat_widget['rssi'] = tk.Label(self.stat_widget['rssi_frame'], text='RSSI Statistic')
        self.stat_widget['rssi'].grid(row=0, column=0, columnspan=2, sticky='w')
        tmp_row_cnt = 1
        self.stat_widget['rssi_header_name'] = tk.Label(self.stat_widget['rssi_frame'], text='RSSI', width=15)
        self.stat_widget['rssi_header_name'].grid(row=tmp_row_cnt, column=0, sticky='w')
        self.stat_widget['rssi_header_min'] = tk.Label(self.stat_widget['rssi_frame'], text='Min', width=15)
        self.stat_widget['rssi_header_min'].grid(row=tmp_row_cnt, column=1, sticky='w')
        self.stat_widget['rssi_header_max'] = tk.Label(self.stat_widget['rssi_frame'], text='Max', width=15)
        self.stat_widget['rssi_header_max'].grid(row=tmp_row_cnt, column=2, sticky='w')
        self.stat_widget['rssi_header_mean'] = tk.Label(self.stat_widget['rssi_frame'], text='Mean', width=15)
        self.stat_widget['rssi_header_mean'].grid(row=tmp_row_cnt, column=3, sticky='w')
        tmp_row_cnt += 1
        self.stat_widget['rssi_0_tot_name'] = tk.Label(self.stat_widget['rssi_frame'], text='RSSI0(Tot)', width=15)
        self.stat_widget['rssi_0_tot_name'].grid(row=tmp_row_cnt, column=0, sticky='w')
        self.stat_widget['rssi_0_tot_min'] = tk.Label(self.stat_widget['rssi_frame'], text='0', width=15)
        self.stat_widget['rssi_0_tot_min'].grid(row=tmp_row_cnt, column=1, sticky='w')
        self.stat_widget['rssi_0_tot_max'] = tk.Label(self.stat_widget['rssi_frame'], text='0', width=15)
        self.stat_widget['rssi_0_tot_max'].grid(row=tmp_row_cnt, column=2, sticky='w')
        self.stat_widget['rssi_0_tot_mean'] = tk.Label(self.stat_widget['rssi_frame'], text='0', width=15)
        self.stat_widget['rssi_0_tot_mean'].grid(row=tmp_row_cnt, column=3, sticky='w')
        tmp_row_cnt += 1
        self.stat_widget['rssi_0_last5_name'] = tk.Label(self.stat_widget['rssi_frame'], text='RSSI0(Last 5)', width=15)
        self.stat_widget['rssi_0_last5_name'].grid(row=tmp_row_cnt, column=0, sticky='w')
        self.stat_widget['rssi_0_last5_min'] = tk.Label(self.stat_widget['rssi_frame'], text='0', width=15)
        self.stat_widget['rssi_0_last5_min'].grid(row=tmp_row_cnt, column=1, sticky='w')
        self.stat_widget['rssi_0_last5_max'] = tk.Label(self.stat_widget['rssi_frame'], text='0', width=15)
        self.stat_widget['rssi_0_last5_max'].grid(row=tmp_row_cnt, column=2, sticky='w')
        self.stat_widget['rssi_0_last5_mean'] = tk.Label(self.stat_widget['rssi_frame'], text='0', width=15)
        self.stat_widget['rssi_0_last5_mean'].grid(row=tmp_row_cnt, column=3, sticky='w')
        self.update_stat_display()

    def update_stat_display(self):
        for name in ['bw', 'mcs', 'rssi0']:
            report = self.stat.report(name)

    def do_update_statistic_widget(self):
        self.is_stat_widget_updating = True
        rssi0_rpt = self.stat.report('rssi0')
        self.stat_widget['rssi_0_tot_min'].config(text="%4.4f" % rssi0_rpt['all_time']['min'])
        self.stat_widget['rssi_0_tot_max'].config(text="%4.4f" % rssi0_rpt['all_time']['max'])
        self.stat_widget['rssi_0_tot_mean'].config(text="%4.4f" % rssi0_rpt['all_time']['mean'])
        self.stat_widget['rssi_0_last5_min'].config(text="%4.4f" % rssi0_rpt['last_5s']['min'])
        self.stat_widget['rssi_0_last5_max'].config(text="%4.4f" % rssi0_rpt['last_5s']['max'])
        self.stat_widget['rssi_0_last5_mean'].config(text="%4.4f" % rssi0_rpt['last_5s']['mean'])
        bw_rpt = self.stat.report('bw')
        for bw in bw_rpt['all_time'].keys():
            self.stat_widget['bw_' + bw + '_tot_value'].config(text=str(bw_rpt['all_time'][bw]))
        for bw in bw_rpt['last_5s'].keys():
            self.stat_widget['bw_' + bw + '_5s_value'].config(text=str(bw_rpt['last_5s'][bw]))
        mcs_rpt = self.stat.report('mcs')
        for mcs in mcs_rpt['all_time'].keys():
            self.stat_widget['mcs_' + str(mcs) + '_tot_value'].config(text=str(mcs_rpt['all_time'][mcs]))
        for mcs in mcs_rpt['last_5s'].keys():
            self.stat_widget['mcs_' + str(mcs) + '_5s_value'].config(text=str(mcs_rpt['last_5s'][mcs]))
        
    def update_statistic(self, report):
        self.stat.record('bw', report['bandwidth'])
        self.stat.record('rssi0', report['chain_rssi'][0])
        self.stat.record('rssi1', report['chain_rssi'][1])
        self.stat.record('rssi2', report['chain_rssi'][2])
        self.stat.record('rssi3', report['chain_rssi'][3])
        self.stat.record('rssi4', report['chain_rssi'][4])
        self.stat.record('rssi5', report['chain_rssi'][5])
        self.stat.record('mcs', report['mcs'])
        if self.is_stat_widget_updating == False:
            threading.Thread(target=self.do_update_statistic_widget).start()

    def update_report_rate(self, rate):
        self.report_rate_label.config(text=f"report rate: {rate}/s")

    def update_plot(self):
        self.is_csi_plot_updating = True
        start_time = time.time()

        csi_i = self.current_csi_result.get('csi_i')
        csi_q = self.current_csi_result.get('csi_q')

        if csi_i is None or csi_q is None:
            return
        
        if len(csi_i) != 512:
            return

        i_data = np.array(csi_i)
        q_data = np.array(csi_q)
        abs_data = np.sqrt(i_data ** 2 + q_data ** 2)
        angle_data = np.arctan2(q_data, i_data)

        self.ax_iq.clear()
        self.ax_abs.clear()
        self.ax_arc.clear()

        self.ax_iq.plot(i_data, label='I', color='blue')
        self.ax_iq.plot(q_data, label="q", color='red')
        self.ax_iq.legend(loc='upper left')
        self.ax_iq.set_title('csi i/q')
        self.ax_iq.set_ylim(-2048, 2048)

        self.ax_abs.plot(abs_data, label='|CSI|', color='green')
        self.ax_abs.legend(loc='upper left')
        self.ax_abs.set_title('csi mag')
        self.ax_abs.set_ylim(-100, 2048)

        self.ax_arc.plot(angle_data, label='Phase', color='purple')
        self.ax_arc.legend(loc='upper left')
        self.ax_arc.set_title('csi Phase')
        self.ax_arc.set_ylim(-np.pi, np.pi)

        self.canvas.draw()
        end_time = time.time()
        draw_duration = end_time - start_time

        if draw_duration <= self.refresh_interval:
            time.sleep(self.refresh_interval - draw_duration)

        self.is_csi_plot_updating = False
    
    def update_csi_result(self, csi_i, csi_q):
        self.current_csi_result['csi_i'] = csi_i
        self.current_csi_result['csi_q'] = csi_q

    def send_enable_command(self):
        enable = str(self.enable_var.get())
        if enable not in ['0', '1']:
            messagebox.showerror('Invalid input', 'enable must be 1 or 0')
            return
        self.command.send_enable_command(enable)
        print(f"sending enable command with value: {enable}")

    def send_sta_filter_command(self):
        mac_str = self.mac_entry.get()
        if len(mac_str.split(':')) != 6:
            messagebox.showerror('invalid input', 'mac address format is invalid')
            return
        self.command.send_sta_filter_command(mac_str)
        print(f"sending sta filter command with mac: {mac_str}")

    def send_csi_config_command(self):
        try:
            subtype_name = self.subtype_combobox.get()
            type_name = self.type_combobox.get()
            subtype_val = self.subtype_options.get(subtype_name, 0)
            type_val = self.type_options.get(type_name, 0)
            csi_frame_type = (subtype_val << 2) | type_val
            chain_num = int(self.chain_num_entry.get())
            chain_idx = int(self.chain_idx_entry.get())
            print(f"sending csi config command with: {csi_frame_type} {chain_num} {chain_idx}")
            self.command.send_csi_config_command(csi_frame_type, chain_num, chain_idx)
        except ValueError:
            messagebox.showerror('invalid input', 'all value must be integer')
            return
    
    def send_ip_config_command(self):
        target_ip = self.target_ip_entry.get()
        print(f"sending ip config command with ip: {target_ip}")
        self.command.send_ip_config_command(target_ip)
    
    def send_intf_config_command(self):
        interface = self.interface_var.get()
        if interface not in ['2.4G', '5G']:
            messagebox.showerror('invalid input', 'interface must be 2.4g or 5g')
            return
        print(f'sending interface config command with : {interface}')
        self.command.send_intf_config_command(interface)
    
    def send_chk_connect_command(self):
        self.command.send_chk_connect_command()
        self.ifcheckstatue = True
        if hasattr(self, 'ok_timeout_timer') and self.ok_timeout_timer:
            self.ok_timeout_timer.cancel()
        self.ok_received = False
        self.ok_timeout_timer = threading.Timer(1.0, lambda: self.handle_connection_timeout())
        self.ok_timeout_timer.start()
    
    def handle_connection_timeout(self):
        if not self.ok_received:
            messagebox.showwarning('connection timeout', 'no response received')

    def config_csi_all(self):
        self.send_intf_config_command()
        time.sleep(0.5)
        self.send_csi_config_command()
        time.sleep(0.5)
        self.send_enable_command()
        time.sleep(0.5)
        self.send_sta_filter_command()
        time.sleep(0.5)
        self.send_ip_config_command()
        time.sleep(0.5)

    def get_current_ip(self):
        self.current_ip = self.ip_entry.get()
        return self.current_ip

    def run(self):
        threading.Thread(target=udp_listener, args=(get_default_ip(), 8023, self), daemon=True).start()
        threading.Thread(target=udp_ok_listener, args=(get_default_ip(), self), daemon=True).start()
        print('ZTECsiTool started')
        self.master.mainloop()

if __name__ == "__main__":
    app = ZTECsiTool()
    app.run()