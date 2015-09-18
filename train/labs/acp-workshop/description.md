Name: acp-workshop

Description: Docker ACP Enablement Workshop

Creates 3 nodes per user:

- Node 0:
  - apt-get update
  - apt-get -y upgrade
  - apt-get install -y linux-image-extra-virtual
  - reboot

- Node 1:
  - curl -sSL https://get.docker.com/ | sh
  - reboot

- Node 2:
  - curl -sSL https://get.docker.com/ | sh
  - reboot
