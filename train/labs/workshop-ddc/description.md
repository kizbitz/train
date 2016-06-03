Name: workshop-ddc

Description:

Training setup for Docker Datacenter workshop

4 Ubuntu 14.04 nodes:

- controller: UCP Controller
- node-0: Has latest UCP images
- DTR
- ldap: JTU's preinstalled ldap server

Packages:
  - git
  - tree
  - jq
  - linux-image-extra-4.2.0-23-generic
  - linux-image-4.2.0.23-generic

Cleanup script is located at: /usr/local/bin/docker-reset
