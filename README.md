# ZTE_WiFi_Sensing

Wi-Fi sensing has emerged as a powerful technology, leveraging channel state information (CSI) extracted from
wireless data packets to enable diverse applications, ranging from human presence detection to gesture recognition and health monitoring.

ZTE has annouced AX3000 and AX3000 Pro will support CSI extraction on SDP sensing competition. The release manual of ZTECSITools provides detailed commands to obtain CSI from their devices. 

In this project, we have provided an upper computer. According to the user manual provided by ZTE, participants can configure the device through the GUI interface.

The details of manual can be obtained from SDP competition platform or arxiv preprint paper [Wi-Fi Sensing Tool Release: Gathering 802.11ax Channel State Information from a Commercial Wi-Fi Access Point](https://arxiv.org/pdf/2506.16957)

## Before using GUI in this project

### Supported devices
- AX3000 (3C Type E2631) [AX3000 Product Link](https://item.jd.com/100022746195.html)

- AX3000 Pro (3C Type ZXSLC SR6110) [AX3000 Pro Product Link](https://item.jd.com/100071901001.html)

- More will come.

### Update the firmware of your devices

CSI extraction ability is not a default function for AX3000/AX3000 Pro. For now, user need to update the firmware of your device. 

To update ZTECSITool firmware, the following step needs
to be done:


- Login to the management web page of ZTE AP (by
default 192.168.5.1). On the bottom of the main page,
record the sequence number.
- Send an email to the author or contributor of this project [(Email)](zs.wang.prc@gmail.com) and attach
the sequence number.
- Users will receive confirmation from the author and your
device will be ready for the experimental test.
- Connect your ZTE AP to Internet through WAN. Login
to the management web page. On the system - upgrade,
click ”request update” bottom. Your ZTE AP will download the experimental firmware and reboot.
- Use ZTECSITool PC software to collection CSI Information.

### FAQ

**Why no csi come out after commands have been sent?**

The answer to this question varies:

- First, only AP recevies packets, AP can generate CSI and report. So make sure some STA is sending PPDU to your AP (or send to somewhere else through your AP)

- Please double check if the configured MAC is the same the MAC of STA who is sending CSI. Some mobile phone may change MAC address every time it connect to the AP. Don't trust your memory.

- Set enable to 0 and then set enable to 1. 

- leave an issue to this repo


