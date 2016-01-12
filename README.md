# Train

Train is a set Amazon Web Services CLI tools (provided in a [Docker](www.docker.com) container) used to manage AWS users, VPC's, user keys/security, AMI's, custom labs (one or more AWS instances grouped by tag), and sets of labs to be used for demos, testing, and training.

- **train**: Primary tool - Manages all VPC Objects and instances
- **train-users**: Mananges additional users allowed to use **train**
- **train-images**: Manages associated lab AMI's


The tools provide a simple way to quickly create, manage, and destroy:

### VPC Objects

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

### AWS IAM Users

- Manage (Create, list, and delete) AWS IAM Users

### AMIs

- Manage (Create, list, and delete) AMI's associated with custom labs.

### Registration for training/testing

- Bulk registration (Launch labs for users listed in a text file)
- Registration mode: A 'Kiosk' style registration mode that provides a welcome message and prompts for email address used to launch labs. 

## Requirements

### AWS Permissions

It's recommended you create a separate AWS account separate from your prod, dev, staging account. **Train** requires extensive IAM roles/permissions. (Create, list, and destroy: VPC's, EC2 instances/objects, IAM users, etc...)

Any user created with the `train-users` tool has the following policy: https://github.com/kizbitz/train/blob/master/train/vpc/users.py#L12-L41

### Environment Variables

Environment variables can be set in the container by:

- Creating/using a Docker environment file (Used in the following examples)
- Pass them in when running the container
- Export them directly in the container

#### Required Environment Variables

```
TRAINER=jbaker
AWS_DEFAULT_REGION=us-east-1
AWS_ACCESS_KEY_ID=<id>
AWS_SECRET_ACCESS_KEY=<key>
```

When using the bulk registration feature or registration mode a [Mandrill API Key](https://www.mandrill.com/) is also required

```
MANDRILL_KEY=<mandrill-key>
```

Note: TRAINER is used for tagging VCP objects only. Not tied to any permissions.

#### Optional Environment Variables

```
# Root lab directory
LAB_DIR=<lab-directory>

# Full path to user configuration file
USER_FILE=<config-file>

# Tag for VPC, labs, instances, etc... (Recommended for different environments)
TRAIN_TAG=<tag>

# Template file for registration emails
EMAIL_TEMPLATE=<path-to-template-file>
```

### Host Volume

A local host volume needs to be mounted inside the container to `/host` when running the container. The scripts will output all user keys and user instance information into '/host' and a '/host/share' directory.

## Walk-through - Personal Use

The following section is a walk-through of usage for personal use (Useful for demos and individuals involved in QA/documentation/support teams) 

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

Create a Docker environment file with required environment variables:

```
vagrant@dockertest:~/sandbox$ vim train.env
vagrant@dockertest:~/sandbox$ cat train.env
TRAINER=jbaker
TRAIN_TAG=demo
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<your-aws-access-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret-access-key>
```

Run the container with the environment file and mount a host volume:

```
vagrant@dockertest:~/sandbox$ ls -al
total 12
drwxrwxr-x  2 vagrant vagrant 4096 Jan 12 10:46 .
drwxr-xr-x 10 vagrant vagrant 4096 Jan 12 10:46 ..
-rw-------  1 vagrant vagrant  219 Jan 12 10:46 train.env
vagrant@dockertest:~/sandbox$ docker run -ti --rm --env-file='train.env' -v $(pwd):/host kizbitz/train
jbaker-demo:us-east-1:~$
```

Executing `train` without any arguments will display help:

```
jbaker-demo:us-east-1:~$ train
usage: train [-h] [-k] [-v] [-a] [-i <lab>] [-x <lab>] [-r <lab>] [-e] [-l]
             [-d <tag>] [-p] [-t]

Train: AWS CLI Tool

optional arguments:
  -h, --help  show this help message and exit
  -k          Create AWS key pairs
  -v          Create AWS VPC
  -a          List all available labs
  -i <lab>    View description for an available lab
  -x <lab>    Execute a lab
  -r <lab>    Execute a lab in registration mode
  -e          Email instance information and credentials to users
  -l          List running labs and instances in AWS
  -d <tag>    Delete a lab from AWS
  -p          Purge/Delete all instances in VPC
  -t          Terminate environment (VPC and local files)
jbaker-demo:us-east-1:~$
```

Generate your key pair (from the TRAINER environment variable) and create a new VPC with required VPC objects using the `-k` and `-v` flags:

```
jbaker-demo:us-east-1:~$ train -kv
Checking for existing key pair: jbaker-demo ...
Creating key pair: jbaker-demo ...
Key 'jbaker-demo' created and saved ...
Creating AWS VPC ...
Creating IAM Profile: jbaker-demo ...
IAM profile, role, and policy created ...
Creating VPC: jbaker-demo ...
Creating gateway: jbaker-demo-igw ...
Creating route table: jbaker-demo-route-table ...
Configuring network ACL: jbaker-demo-network-acl ...
10.0.0.0/20
Creating subnet: jbaker-demo-us-east-1b ...
10.0.16.0/20
Creating subnet: jbaker-demo-us-east-1c ...
10.0.32.0/20
Creating subnet: jbaker-demo-us-east-1d ...
10.0.48.0/20
Creating subnet: jbaker-demo-us-east-1e ...
Configuring default security group ...
Adding default egress rules ...
jbaker-demo:us-east-1:~$
```

Key pairs (*.pem for *nix users and a *.pem for Windows/PuTTY users) are are created and saved in a `/host/share/<username>` directory.

```
jbaker-demo:us-east-1:~$ tree /host/share
/host/share
└── jbaker
    ├── jbaker-demo.pem
    └── jbaker-demo.ppk

1 directory, 2 files
jbaker-demo:us-east-1:~$
```

List available labs:

```
jbaker-demo:us-east-1:~$ train -a

Available Labs:
  base
  dtr-volume
  template
  training-atp
  ucp

jbaker-demo:us-east-1:~$
```

Display lab information:

```
jbaker-demo:us-east-1:~$ train -i dtr-volume

Name: dtr-volume

Description:

DTR with image storage configured on a separate volume.

- Ubuntu 14.04
- 4.0.23 Kernel
- Latest Docker CS Release

jbaker-demo:us-east-1:~$
```

This particular lab launches a base Ubuntu 14.04 instances with an attached volume, upgrades the kernel to 4.0.23, installs the latest Docker CS engine and Docker Trusted registry, then configures the DTR storage option to point to the attached volume. See: https://github.com/kizbitz/train/tree/master/train/labs/dtr-volume

Launch this lab:

```
jbaker-demo:us-east-1:~$ train -x dtr-volume
Launching 'dtr-volume' lab with tag: dtr-volume-1
Launching instance: jbaker-dtr ...
Waiting for instances to initialize ...
Waiting for instance 'jbaker-dtr' to initialize ...
Waiting for instance 'jbaker-dtr' to initialize ...
Waiting for instance 'jbaker-dtr' to initialize ...
Creating instance tags for: jbaker-dtr...

Lab 'dtr-volume' launched with tag 'dtr-volume-1':

  Instances:

    Name:         jbaker-dtr
      Lab:        dtr-volume-1
      Region:     us-east-1
      IP:         52.90.115.110
      Private IP: 10.0.7.235
      Public DNS: ec2-52-90-115-110.compute-1.amazonaws.com

jbaker-demo:us-east-1:~$
```

Launch another lab:

```
jbaker-demo:us-east-1:~$ train -x base
Available configurations for the 'base' lab:

 1) amazon-linux
 2) centos-7.0
 3) debian-jessie
 4) debian-wheez
 5) rhel-6.5
 6) rhel-6.6
 7) rhel-7.0
 8) rhel-7.1
 9) suse-sles-12
 10) ubuntu

Which configuration would you like to execute?: 10
How many instances would you like to launch: 2
Enter a custom AWS 'Name' tag: ubuntu-demo
Launching 'base' lab with tag: base-1
Launching instance: jbaker-ubuntu-demo-0 ...
Launching instance: jbaker-ubuntu-demo-1 ...
Waiting for instances to initialize ...
Waiting for instance 'jbaker-ubuntu-demo-0' to initialize ...
Waiting for instance 'jbaker-ubuntu-demo-0' to initialize ...
Waiting for instance 'jbaker-ubuntu-demo-0' to initialize ...
Creating instance tags for: jbaker-ubuntu-demo-0...
Creating instance tags for: jbaker-ubuntu-demo-1...

Lab 'base' launched with tag 'base-1':

  Instances:

    Name:         jbaker-ubuntu-demo-0
      Lab:        base-1
      Region:     us-east-1
      IP:         52.91.204.163
      Private IP: 10.0.1.109
      Public DNS: ec2-52-91-204-163.compute-1.amazonaws.com

    Name:         jbaker-ubuntu-demo-1
      Lab:        base-1
      Region:     us-east-1
      IP:         54.173.148.253
      Private IP: 10.0.19.225
      Public DNS: ec2-54-173-148-253.compute-1.amazonaws.com

jbaker-demo:us-east-1:~$
```

List running labs and instances:

```
jbaker-demo:us-east-1:~$ train -l

Running labs:
  base-1
  dtr-volume-1

Instances running in lab 'base-1':

    Name:         jbaker-ubuntu-demo-0
      Lab:        base-1
      Region:     us-east-1
      IP:         52.91.204.163
      Private IP: 10.0.1.109
      Public DNS: ec2-52-91-204-163.compute-1.amazonaws.com

    Name:         jbaker-ubuntu-demo-1
      Lab:        base-1
      Region:     us-east-1
      IP:         54.173.148.253
      Private IP: 10.0.19.225
      Public DNS: ec2-54-173-148-253.compute-1.amazonaws.com

Instances running in lab 'dtr-volume-1':

    Name:         jbaker-dtr
      Lab:        dtr-volume-1
      Region:     us-east-1
      IP:         52.90.115.110
      Private IP: 10.0.7.235
      Public DNS: ec2-52-90-115-110.compute-1.amazonaws.com

jbaker-demo:us-east-1:~$
```

Lab/Instance information is also saved in text files in: `/host/share/<user>`

```
jbaker-demo:us-east-1:~$ tree /host/share
/host/share
└── jbaker
    ├── base-1.txt
    ├── dtr-volume-1.txt
    ├── jbaker-demo.pem
    └── jbaker-demo.ppk

1 directory, 4 files
jbaker-demo:us-east-1:~$
```

Delete a lab:

```
jbaker-demo:us-east-1:~$ train -d dtr-volume-1

Terminate request sent for all lab instances ...
Lab 'dtr-volume-1' has been deleted ...

jbaker-demo:us-east-1:~$
```

Purge all instances in the VPC:

```
jbaker-demo:us-east-1:~$ train -p

Terminate request sent for all instances ...

jbaker-demo:us-east-1:~$
```

Confirmation:

```
jbaker-demo:us-east-1:~$ train -l

No labs running ...

jbaker-demo:us-east-1:~$ tree /host/share
/host/share
└── jbaker
    ├── jbaker-demo.pem
    └── jbaker-demo.ppk

1 directory, 2 files
jbaker-demo:us-east-1:~$
```

Terminate environment. Removes all VPC objects, labs, instances, and user keys:

```
jbaker-demo:us-east-1:~$ train -t
Terminating environment ...

VPC has no instances ...
Deleting IAM Profile: jbaker-demo ...
Deleting key pair for user: jbaker ...
Deleting VPC: jbaker-demo ...
Environment deleted ...
Finished ...
jbaker-demo:us-east-1:~$
```

## Walk-through - Registration Modes

In addition to all of the above functionality, **train** provides two **registration modes** that can be used for providing instances to particpants in training events or hands-on lab scenarios.

- Bulk registration
- Registration (Kiosk) mode

### Bulk Registration

To use the bulk registration mode you pass **train** a user config file. By default this is /host/users.cfg or optionally set a file path with the USER_FILE environment variable: https://github.com/kizbitz/train/blob/master/train/vpc/config.py#L52

Create a **users.cfg** file with a list of usernames and emails that will be used when creating key pairs and launching any lab instances.

- One user per line in the format: `<username>,<email>`

```
vagrant@dockertest:~/sandbox$ vim users.cfg
vagrant@dockertest:~/sandbox$ cat users.cfg
jbaker,jbaker@docker.com
mrcotton,mrcotton@simpledove.com
vagrant@dockertest:~/sandbox$
```

**Note**: This example only has two users specified but there is no limit except for your AWS limits.

Run the container with the environment file and mount a host volume:

```
vagrant@dockertest:~/sandbox$ ls -al
total 16
drwxrwxr-x  2 vagrant vagrant 4096 Jan 12 12:08 .
drwxr-xr-x 10 vagrant vagrant 4096 Jan 12 12:08 ..
-rw-------  1 vagrant vagrant  219 Jan 12 10:46 train.env
-rw-rw-r--  1 vagrant vagrant   58 Jan 12 12:08 users.cfg
vagrant@dockertest:~/sandbox$ docker run -ti --rm --env-file='train.env' -v $(pwd):/host kizbitz/train
jbaker-demo:us-east-1:~$
```

Create all keys and VPC:

```
jbaker-demo:us-east-1:~$ train -kv
Checking for existing key pair: jbaker-demo ...
Creating key pair: jbaker-demo ...
Key 'jbaker-demo' created and saved ...
Checking for existing key pair: mrcotton-demo ...
Creating key pair: mrcotton-demo ...
Key 'mrcotton-demo' created and saved ...
Creating AWS VPC ...
Creating IAM Profile: jbaker-demo ...
IAM profile, role, and policy created ...
Creating VPC: jbaker-demo ...
Creating gateway: jbaker-demo-igw ...
Creating route table: jbaker-demo-route-table ...
Configuring network ACL: jbaker-demo-network-acl ...
10.0.0.0/20
Creating subnet: jbaker-demo-us-east-1b ...
10.0.16.0/20
Creating subnet: jbaker-demo-us-east-1c ...
10.0.32.0/20
Creating subnet: jbaker-demo-us-east-1d ...
10.0.48.0/20
Creating subnet: jbaker-demo-us-east-1e ...
Configuring default security group ...
Adding default egress rules ...
jbaker-demo:us-east-1:~$
```

Launch a lab for all users:

```
jbaker-demo:us-east-1:~$ train -x dtr-volume
Launching 'dtr-volume' lab with tag: dtr-volume-1
Launching instance: jbaker-dtr ...
Launching instance: mrcotton-dtr ...
Waiting for instances to initialize ...
Waiting for instance 'jbaker-dtr' to initialize ...
Waiting for instance 'jbaker-dtr' to initialize ...
Waiting for instance 'jbaker-dtr' to initialize ...
Waiting for instance 'mrcotton-dtr' to initialize ...
Creating instance tags for: jbaker-dtr...
Creating instance tags for: mrcotton-dtr...

Lab 'dtr-volume' launched with tag 'dtr-volume-1':

  Instances:

    Name:         jbaker-dtr
      Lab:        dtr-volume-1
      Region:     us-east-1
      IP:         54.173.183.121
      Private IP: 10.0.4.30
      Public DNS: ec2-54-173-183-121.compute-1.amazonaws.com

    Name:         mrcotton-dtr
      Lab:        dtr-volume-1
      Region:     us-east-1
      IP:         54.165.187.76
      Private IP: 10.0.1.129
      Public DNS: ec2-54-165-187-76.compute-1.amazonaws.com

jbaker-demo:us-east-1:~$
```

At this point all user keys and the lab instance information within saved in the container in `/host/share` (and in the host directory):

Note: On Windows open the *.txt files with Wordpad (or some other app that will render the \n's correctly)

```
jbaker-demo:us-east-1:~$ tree /host/share
/host/share
├── jbaker
│   ├── dtr-volume-1.txt
│   ├── jbaker-demo.pem
│   └── jbaker-demo.ppk
└── mrcotton
    ├── dtr-volume-1.txt
    ├── mrcotton-demo.pem
    └── mrcotton-demo.ppk

2 directories, 6 files
jbaker-demo:us-east-1:~$
```

List running labs and instances: 

```
jbaker-demo:us-east-1:~$ train -l

Running labs:
  dtr-volume-1

Instances running in lab 'dtr-volume-1':

    Name:         jbaker-dtr
      Lab:        dtr-volume-1
      Region:     us-east-1
      IP:         54.173.183.121
      Private IP: 10.0.4.30
      Public DNS: ec2-54-173-183-121.compute-1.amazonaws.com

    Name:         mrcotton-dtr
      Lab:        dtr-volume-1
      Region:     us-east-1
      IP:         54.165.187.76
      Private IP: 10.0.1.129
      Public DNS: ec2-54-165-187-76.compute-1.amazonaws.com

jbaker-demo:us-east-1:~$
```

Email all users their lab instance information and keys:

Note:

- Requires a MANDRILL_KEY - See requirements section above.
- Recommended that you use a customized email template. See: https://github.com/kizbitz/train/blob/master/train/vpc/config.py#L58
  - T default template used is located here: https://github.com/kizbitz/train/blob/master/train/templates/email.py 

```
jbaker-demo:us-east-1:~$ train -e
Emailing user information and credentials ...
Enter the 'from email address' for the outgoing message: no-reply@docker.com
Enter the 'from name' for the outgoing message: Docker Training
Enter the 'Subject' for the outgoing message: Docker Training Demo
Welcome email sent to: 'jbaker' <jbaker@docker.com> ...
Welcome email sent to: 'mrcotton' <mrcotton@simpledove.com> ...
```

After training is complete terminate/purge all instances and VPC.

### Registration Mode

The alternative method of registration is using the `-r` flag to launch a lab.

This mode:

- Prompts for a welome message
- Displays the welome message and prompts for an email
- Creates a username from the email and creates the key pairs
- Launches the lab and then emails the user the connection info and keys

MANDRILL_KEY required and using a custom email template is recommend.

Notes:

- It's recommend to use a custom email template (with no prompts) that sets:
  - `from_email`, `from_name`, and `subject` variables with static entries.
    - See '/home/train/train/templates/email.py' in the container
- Specify 'EMAIL_TEMPLATE' environment variable with the path to your template
- The welcome message entered below will be shown to each individial before prompting for email.
- To exit registration mode type 'exit' during the email prompt.

Example usage:

```
jbaker-demo:us-east-1:~$ train -r dtr-volume

Registration Mode:

- It's recommend to use a custom email template (with no prompts) that sets:
    - from_email, from_name, and subject variables with static entries.
        - See '/home/train/train/templates/email.py'
    - Specify 'EMAIL_TEMPLATE' environment variable with the path to your template

- The welcome message entered below will be shown to each individial before prompting for email.
- To exit registration mode type 'exit' during the email prompt.

Enter a welcome message: Welcome to Docker Training!
```

After the welcome message is entered the registration loop starts:

```
Welcome to Docker Training!

Please enter a valid email address: jbaker@docker.com
Checking for existing key pair: jbaker-demo ...
Creating key pair: jbaker-demo ...
Key 'jbaker-demo' created and saved ...
Launching 'dtr-volume' lab with tag: dtr-volume-1
Launching instance: jbaker-dtr ...
Waiting for instances to initialize ...
Waiting for instance 'jbaker-dtr' to initialize ...
Waiting for instance 'jbaker-dtr' to initialize ...
Waiting for instance 'jbaker-dtr' to initialize ...
Creating instance tags for: jbaker-dtr...

Lab 'dtr-volume' launched with tag 'dtr-volume-1':

  Instances:

    Name:         jbaker-dtr
      Lab:        dtr-volume-1
      Region:     us-east-1
      IP:         52.90.51.247
      Private IP: 10.0.4.100
      Public DNS: ec2-52-90-51-247.compute-1.amazonaws.com

Emailing user information and credentials ...
Welcome email sent to: 'jbaker' <jbaker@docker.com> ...


-----------------------------------

Instances launched successfully ...

Press 'Enter' to continue
```

After enter is pressed the welcome message is displayed again and prompts for another email:

```
Welcome to Docker Training!

Please enter a valid email address:
```

When using the `-r` flag for registration usernames and emails are collected in the file `/host/registered-users.txt` for use with post-training surveys, etc...:

```
jbaker-demo:us-east-1:~$ cat /host/registered-users.txt
jbaker,jbaker@docker.com
mrcotton,mrcotton@simpledove.com
```

## train-images

The train-images CLI tool is used to manage AMI's for labs. Depending on how long it takes the cloud-init script to finish it can be quicker to create an AMI of the final instance to launch instead of the specified cloud-init script. (Especially during training events and hands-on labs)

Notes:

- Only one AMI is created per instance definition in instances.cfg. This will be the `<name>-0` instance when **NAME** is used in the definition or the zero index of the **NAMES** list. See: https://github.com/kizbitz/train/blob/master/train/labs/template/instances.cfg#L16-L22 
- When launching a lab **train** checks for existing AMI images for the lab and will use those if present. If not, the standard cloud-init script is used.

### Example usage

Executing `train-images` without any arguments will display help:

```
jbaker-demo:us-east-1:~$ train-images
usage: train-images [-h] [-c <lab>] [-d <lab>] [-l] [-r]

Train: AWS CLI AMI Management

optional arguments:
  -h, --help  show this help message and exit
  -c <lab>    Create lab AMI's
  -d <lab>    Deregister lab AMI's
  -l          List all AMI's
  -r          List running labs
jbaker-demo:us-east-1:~$
```

List running labs:

```
jbaker-demo:us-east-1:~$ train-images -r

Running labs:
  dtr-volume-1

jbaker-demo:us-east-1:~$
```

Create AMI's for a lab:

```
jbaker-demo:us-east-1:~$ train-images -c dtr-volume-1
Creating AMI's for lab: dtr-volume-1
Completed ...
```

Note: Depending on the current state of the AWS workers it could take a while before the final image is available.

List all AMI's

```
jbaker-demo:us-east-1:~$ train-images -l

AWS AMI's:

  ID: ami-94bfe4fe
  Name: jbaker-demo-dtr-volume-ubuntu-0
  Description: dtr-volume lab AMI
  Region: us-east-1
  Tags:
     Name: jbaker-demo-dtr-volume-ubuntu-0
     AMI-Key: 0
     Lab: dtr-volume

jbaker-demo:us-east-1:~$
```

Deregistering an AMI:

```
jbaker-demo:us-east-1:~$ train-images -d dtr-volume
Degristering jbaker-demo-dtr-volume-ubuntu-0 ...
Completed ...
jbaker-demo:us-east-1:~$
```

## train-users

**train-users** is a CLI tool for current AWS administrators to manage new **train** users.

Executing `train-users` without any arguments will display help:

```
jbaker-demo:us-east-1:~$ train-users
usage: train-users [-h] [-c <user>] [-d <user>] [-l]

Train: AWS CLI IAM/User Management

optional arguments:
  -h, --help  show this help message and exit
  -c <user>   Create IAM/User
  -d <user>   Delete AWS user
  -l          List all users
```

Using the `-c` flag will create a new user account and return the credentials that you can pass on.

```
baker-demo:us-east-1:~$ train-users -c mrcotton
Allow user to log into the AWS Console? [y/n]: y

'mrcotton' user created succesfully ...

Username: mrcotton
Password: 7F9@Yy2x33ye(Wwh4
Access Key ID: ABCDJEKAAUUBSXYZ2W7YB7A
Secret Access Key: KsappDockerfCUlc-SyuWdx9xBxROUof9nnSj3uz

jbaker-demo:us-east-1:~$
```

List all users:

```
jbaker-demo:us-east-1:~$ train-users -l

Current AWS user accounts:

- jbaker
- mrcotton

jbaker-demo:us-east-1:~$
```

Delete a user:

```
jbaker-demo:us-east-1:~$ train-users -d mrcotton
Are you sure you want to delete user: 'mrcotton'? [y/n]: y
'mrcotton' AWS user deleted ...
jbaker-demo:us-east-1:~$
```

**WARNING:** Security for your environment is **your** responsibility. Users created with this tool have a lot of permissions. Remember to audit your users and rotate keys/passwords to keep your environment secure.

### Finally

Thoughts, comments, suggestions, bug reports, and pull requests welcome....