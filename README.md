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


