# Train

Train is an Amazon Web Services CLI tool used to manage VPC's, user keys/security, and labs (one or more instances grouped by tag) for training/testing.

Manages:

- VPC Objects
  - VPC
  - IAM profile, role, policy
  - Gateway
  - Route table
  - Network ACL
  - Subnets
  - Default security group and rules
- Key pairs for multiple users
- Labs (Grouping of one or more instances with specific configurations)
- Termination and clean-up of all created objects/files

## Quickstart

- Pull the Docker image: `docker pull kizbitz/train`
- Run the container (with required volume and environment settings): `docker run -ti --rm --env-file='train.env' -v $(pwd):/host kizbitz/train`
- Run `train` to view help

## Requirements

### Environment Variables

The following environment variables are required. All others are optional.

You can set them in the container by:

- Creating/using a Docker environment file (Used in the following examples)
- Pass them in when running the container
- Export them directly in the container

```
TRAINER=jbaker
AWS_DEFAULT_REGION=us-east-1
AWS_ACCESS_KEY_ID=<id>
AWS_SECRET_ACCESS_KEY=<key>
```

Notes:

- TRAINER is used for tagging VCP objects only. Not tied to any permissions.

### Host Volume

A local host volume needs to be mounted inside the container to `/host` when running the container. The scripts will output all user keys and user instance information into a 'share' directory.

## Optional Values

```
# Full path to lab directory (In the container)
LAB_DIR

# Full path to a user (list of user accounts) file (In the container)
USER_FILE

# Tag for VPC, labs, instances, etc...
TRAIN_TAG
```

## Walk-through

Pull the Docker image:

```
vagrant@dockertest:~$ docker pull kizbitz/train
Using default tag: latest
latest: Pulling from kizbitz/train
843e2bded498: Pull complete
  *content removed*
81395f1294cc: Pull complete
Digest: sha256:146ff25a5b7fa8a4dd9914359c93f0be2c35ff0ca4a19045a1585dc07e005e0b
Status: Downloaded newer image for kizbitz/train:latest
```

Create a temp working directory:

```
vagrant@dockertest:~$ mkdir sandbox
vagrant@dockertest:~$ cd sandbox/
```

Create a Docker environment file:

```
vagrant@dockertest:~/sandbox$ vim train.env
vagrant@dockertest:~/sandbox$ cat train.env
TRAINER=jbaker
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<your-aws-access-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret-access-key>
```

Create a **users.cfg** file:

This is a list of user accounts that will be used when creating key pairs and launching any lab instances.

Notes:

- User files are not required. If one isn't provided the TRAINER environment variable value will be set as the only user.
- One username per line

```
vagrant@dockertest:~/sandbox$ vim users.cfg
vagrant@dockertest:~/sandbox$ cat users.cfg
jbaker
mrcotton
```

Run the container with the environment file and mounting a host volume:

```
vagrant@dockertest:~/sandbox$ ls -al
total 16
drwxrwxr-x 2 vagrant vagrant 4096 Sep 23 10:04 .
drwxr-xr-x 9 vagrant vagrant 4096 Sep 23 10:04 ..
-rw-rw-r-- 1 vagrant vagrant  138 Sep 23 10:00 train.env
-rw-rw-r-- 1 vagrant vagrant   16 Sep 23 10:04 users.cfg
vagrant@dockertest:~/sandbox$ docker run -ti --rm --env-file='train.env' -v $(pwd):/host kizbitz/train
train@d7d8c5f68818:~$
```

Executing `train` without any arguments will display help:

```
train@d7d8c5f68818:~$ train
usage: train [-h] [-k] [-v] [-a] [-i <lab>] [-x <lab>] [-l] [-d <tag>] [-p]
             [-t]

Train: AWS CLI Tool

optional arguments:
  -h, --help  show this help message and exit
  -k          Create AWS key pairs
  -v          Create AWS VPC
  -a          List all available labs
  -i <lab>    View description for an available lab
  -x <lab>    Excecute a lab
  -l          List running labs and instances in AWS
  -d <tag>    Delete a lab from AWS
  -p          Purge/Delete all instances in vpc
  -t          Terminate environment (VPC and local files)
```

Generate key pairs for all users:

```
train@d7d8c5f68818:~$ train -k
Checking for existing key pair: jbaker-train ...
Creating key pair: jbaker-train ...
Key 'jbaker-train' created and saved ...
Checking for existing key pair: mrcotton-train ...
Creating key pair: mrcotton-train ...
Key 'mrcotton-train' created and saved ...

'jbaker-train' VPC doesn't exist.
Create it by running the command: train -v

train@d7d8c5f68818:~$
```

Create the VCP:

```
train@d7d8c5f68818:~$ train -v
Creating AWS VPC ...
Creating IAM Profile: jbaker-train ...
IAM profile, role, and policy created ...
Creating VPC: jbaker-train ...
Creating gateway: jbaker-train-igw ...
Creating route table: jbaker-train-route-table ...
Configuring network ACL: jbaker-train-network-acl ...
10.0.10.0/24
Creating subnet: jbaker-train-us-east-1b ...
10.0.11.0/24
Creating subnet: jbaker-train-us-east-1c ...
10.0.12.0/24
Creating subnet: jbaker-train-us-east-1d ...
10.0.13.0/24
Creating subnet: jbaker-train-us-east-1e ...
Configuring default security group ...
Adding default egress rules ...
Adding your current location IP (68.53.176.34) to default security group ...
train@d7d8c5f68818:~$
```

List available labs:

```
train@d7d8c5f68818:~$ train -a

Available Labs:
  acp-workshop
  base
  template

train@d7d8c5f68818:~$
```

Display a lab description:

```
train@d7d8c5f68818:~$ train -i acp-workshop

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
```

Run a lab:

```
train@d7d8c5f68818:~$ train -x acp-workshop                                                                                                                                                        [228/972]
Available configurations for the 'acp-workshop' lab:

  -  ubuntu

Which configuration would you like to execute?: ubuntu
Launching 'acp-workshop' lab with tag: acp-workshop-1
Launching instance: jbaker-node-0 ...
Launching instance: jbaker-node-1 ...
Launching instance: jbaker-node-2 ...
Launching instance: mrcotton-node-0 ...
Launching instance: mrcotton-node-1 ...
Launching instance: mrcotton-node-2 ...
Waiting for instances to initialize ...
Waiting for instance 'jbaker-node-0' to initialize ...
Waiting for instance 'jbaker-node-0' to initialize ...
Waiting for instance 'jbaker-node-0' to initialize ...
Waiting for instance 'jbaker-node-0' to initialize ...
Waiting for instance 'jbaker-node-1' to initialize ...
Waiting for instance 'jbaker-node-1' to initialize ...
Waiting for instance 'jbaker-node-1' to initialize ...
Waiting for instance 'jbaker-node-2' to initialize ...
Waiting for instance 'mrcotton-node-0' to initialize ...
Waiting for instance 'mrcotton-node-1' to initialize ...
Waiting for instance 'mrcotton-node-2' to initialize ...
Elastic ip not specified for: jbaker-node-0. Skipping ...
Creating instance tags for: jbaker-node-0...
Elastic ip not specified for: jbaker-node-1. Skipping ...
Creating instance tags for: jbaker-node-1...
Elastic ip not specified for: jbaker-node-2. Skipping ...
Creating instance tags for: jbaker-node-2...
Elastic ip not specified for: mrcotton-node-0. Skipping ...
Creating instance tags for: mrcotton-node-0...
Elastic ip not specified for: mrcotton-node-1. Skipping ...
Creating instance tags for: mrcotton-node-1...
Elastic ip not specified for: mrcotton-node-2. Skipping ...
Creating instance tags for: mrcotton-node-2...

Lab 'acp-workshop' launched with tag 'acp-workshop-1':

  Instances:

    Name:         jbaker-node-0
      Lab:        acp-workshop-1
      Region:     us-east-1
      IP:         54.165.231.65
      Public DNS: ec2-54-165-231-65.compute-1.amazonaws.com

    Name:         jbaker-node-1
      Lab:        acp-workshop-1
      Region:     us-east-1
      IP:         54.172.241.249
      Public DNS: ec2-54-172-241-249.compute-1.amazonaws.com

    Name:         jbaker-node-2
      Lab:        acp-workshop-1
      Region:     us-east-1
      IP:         54.88.139.250
      Public DNS: ec2-54-88-139-250.compute-1.amazonaws.com

    Name:         mrcotton-node-0
      Lab:        acp-workshop-1
      Region:     us-east-1
      IP:         54.165.248.154
      Public DNS: ec2-54-165-248-154.compute-1.amazonaws.com

    Name:         mrcotton-node-1
      Lab:        acp-workshop-1
      Region:     us-east-1
      IP:         54.172.214.6
      Public DNS: ec2-54-172-214-6.compute-1.amazonaws.com

    Name:         mrcotton-node-2
      Lab:        acp-workshop-1
      Region:     us-east-1
      IP:         54.173.55.9
      Public DNS: ec2-54-173-55-9.compute-1.amazonaws.com
```

At this point all user keys and the lab instance information within saved in the container in `/host/share` (and in the host directory):

Note: On Windows open the *.txt files with Wordpad (or some other app that will render the \n's correctly)
```
train@d7d8c5f68818:~$ tree /host/share
/host/share
├── jbaker
│   ├── acp-workshop-1.txt
│   └── jbaker-train.pem
└── mrcotton
    ├── acp-workshop-1.txt
    └── mrcotton-train.pem

2 directories, 4 files
train@d7d8c5f68818:~$
```

List running labs and instances: 

```
train@42102c2291fc:~$ train -l

Running labs:
  acp-workshop-1
  base-1

Instances running in lab 'acp-workshop-1':

    Name:         jbaker-node-0
      Lab:        acp-workshop-1
      Region:     us-east-1
      IP:         54.165.231.65
      Public DNS: ec2-54-165-231-65.compute-1.amazonaws.com

    Name:         jbaker-node-1
      Lab:        acp-workshop-1
      Region:     us-east-1
      IP:         54.172.241.249
      Public DNS: ec2-54-172-241-249.compute-1.amazonaws.com

    Name:         jbaker-node-2
      Lab:        acp-workshop-1
      Region:     us-east-1
      IP:         54.88.139.250
      Public DNS: ec2-54-88-139-250.compute-1.amazonaws.com

    Name:         mrcotton-node-0
      Lab:        acp-workshop-1
      Region:     us-east-1
      IP:         54.165.248.154
      Public DNS: ec2-54-165-248-154.compute-1.amazonaws.com

    Name:         mrcotton-node-1
      Lab:        acp-workshop-1
      Region:     us-east-1
      IP:         54.172.214.6
      Public DNS: ec2-54-172-214-6.compute-1.amazonaws.com

    Name:         mrcotton-node-2
      Lab:        acp-workshop-1
      Region:     us-east-1
      IP:         54.173.55.9
      Public DNS: ec2-54-173-55-9.compute-1.amazonaws.com

Instances running in lab 'base-1':

    Name:         jbaker-ubuntu
      Lab:        base-1
      Region:     us-east-1
      IP:         54.85.250.151
      Public DNS: ec2-54-85-250-151.compute-1.amazonaws.com

    Name:         mrcotton-ubuntu
      Lab:        base-1
      Region:     us-east-1
      IP:         54.152.230.197
      Public DNS: ec2-54-152-230-197.compute-1.amazonaws.com
```

Delete a lab and instances:

```
train@42102c2291fc:~$ train -d base-1

Terminate request sent for all lab instances ...
Lab 'base-1' has been deleted ...

train@42102c2291fc:~$
```

Purge all labs and instances (Keeps user keys):

```
train@42102c2291fc:~$ train -p

Terminate request sent for all instances ...
```

Terminate environment. Removes all VPC objects, labs, instances, and user keys:

```
train@42102c2291fc:~$ train -t
Terminating instances ...
Terminate request sent for all instances ...
  Waiting for all instances to terminate ...
  Waiting for all instances to terminate ...
  Waiting for all instances to terminate ...
  Waiting for all instances to terminate ...
  Waiting for all instances to terminate ...
  Waiting for all instances to terminate ...
  Waiting for all instances to terminate ...
Deleting IAM Profile: jbaker-train ...
Deleting key pair: jbaker-train ...
Deleting key pair: mrcotton-train ...
Deleting VPC: jbaker-train ...
Environment deleted ...
```
