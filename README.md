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

## Extract Details on CSI format

Our arxiv paper may not cover all details of the CSI format. Here we present some frequently asked question over here. 

### Multi-Chain Support

AX3000 extracts CSI from all chains (6 chains at most for 5G, 4 chains at most for 2.4G). Each CSI has a timestamp. If two CSI has identical timestamp, which means it belongs to the same PPDU with different Chain. 

The order to the chain is as follow: 

For 3x2: H11 H12 H13 H21 H22 H23 H31 H32 H33. Three Rx antenna and 2 Tx antenna. Total 2 NSS

For 3x1: H11 H12 H13

For 2x2: H11 H12 H21 H22

For 2x1: H11 H12

For 1x1: H11


Note that, the number of chains depends on the NSS of the received PPDU. This means that AP don't have control on that. If STA is sending using NSS=1, then only H11 is extracted. 

Note that, based on the MIMO theory, the chain doesn't necessarily has physical or actual relation with the antenna. 


