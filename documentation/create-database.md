## Why you shouldn't use these steps

We have packaged up an image of our database for your convenience and safety. **You probably don't need to build one from scratch.** However, if you want to modify our database or build a newer one than the version that we have posted, we have provided step-by-step instructions for doing so below.

## Why you might need these steps

If you want to add new fields to the database or build a newer one than the version that we have posted, you will need these steps.

## Warning

**The following steps involve creating several virtual computers in the cloud. Every single one of them will be billed by the hour until you shut them off. They will also be vulnerable to hacking unless you take additional steps to secure them. Please only do this if you know what you're doing.**

## Instructions

1. Log into AWS
  1. Create account if needed
  1. Log into AWS
1. Creating a Spark EMR cluster
   1. Create an EC2 key pair (download key!)
   1. Create an EMR Spark cluster (this will cost $)
     1. Give a name such as "990-database-load"
     1. Under "Software configuration," choose the one that starts "Spark." As of this writing, it says "Spark: Spark 2.0.2 on Hadoop 2.7.3 YARN with Ganglia 3.7.2 and Zeppelin 0.6.2." But the versions will change over time.
     1. Default hardware configuration is fine.
     1. Choose the key pair you created.
     1. Click "Create cluster."
     1. Cluster will take about 15 minutes to start.
1. Create RDS (do while cluster is starting)
  1. Go to RDS menu
  1. Select MySQL engine
  1. Choose an m4.xlarge instance and provision 30gb of storage
  1. Under "advanced settings," leave all blank
1. Enable inbound traffic from SSH (for terminal) and a couple other things (for Github) on EMR master node
  1. Go to EMR console on AWS
  1. Click "cluster list"
  1. Go to the cluster you made and click "view cluster details"
  1. On the right, it says "Security groups for Master" and then there's a link. Click the link.
  1. If you see multiple options, click the one with the "Group ID" matching the text in the link from the previous page.
  1. On the bottom of the screen, navigate to the "Inbound" tab.
  1. Click "Edit."
  1. Click "Add rule." Where it says "Custom TCP rule," click the drop down and choose "SSH." Where it says "Custom," click the drop down and choose "Anywhere."
  1. Create additional rules allowing inbound traffic for ports 443, 9418, and 80 from 192.30.252.0/22 (Github).
1. Enable communication between your RDS instance and your EMR instance
  1. Basically, you want to follow [these steps](https://aws.amazon.com/premiumsupport/knowledge-center/rds-cannot-connect/). You want your RDS to allow inbound traffic over port 3306 from members of either the EMR master or slave security groups. 
1. Create an IAM access key
  1. Downloading from S3 costs money. Not much, but to do it, you have to authenticate as yourself. When doing this programatically, we use random sequences of characters called keys. Follow [these instructions](http://docs.aws.amazon.com/general/latest/gr/managing-aws-access-keys.html) to create a key. Be sure to write down your secret code, as you will never be able to view it again.
1. Connect to your EMR instance
  1. Go to the EC2 console
  1. Click on the instances you have running until you see the one whose security group is called `ElasticMapReduce-master`. Copy the Public IP address into your clipboard.
  1. From Linux or Mac, type `ssh -i my-ec2-key.pem hadoop@1.2.3.4`, where `my-ec2-key.pem` is the EC2 key you created and downloaded earlier, and `1.2.3.4` is the IP address of your master node. (Note to self: provide a link to Windows instructions -DBB)
  1. Acknowledge and accept the security warning, if any.
1. Verify that you configured everything correctly,
  1. Verify that you chose the right kind of EMR cluster by typing `spark-submit --help` and pressing enter. If you get an error, terminate the EMR cluster and make a new one with the right configuration. (See above.)
  1. Verify that you can connect to your RDS instance. Go to the RDS console, click on the RDS instance you created for this project, and copy the endpoint (except the `:3306` at the end) to your clipboard. Type `mysql -h my-endpoint-name -P 3306 -u my-root-name -p`, where `my-endpoint-name` is what's on your clipboard and `my-root-name` is the name of the root user you created for the database. Type your root password. If you get right to a MySQL prompt, you did everything correctly. If it hangs for a long time and then times out, your security groups are still messed up. 
1. Initialize your environment to build the database
  1. Type `sudo yum install git` and wait for git to install.
  1. Type `sudo pip install sqlalchemy` and wait for SQLAlchemy to install.
  1. Clone this repository from github by typing `git clone https://github.org/CharityNavigator/irs990` 
  1. Type `echo export PYTHONPATH=\"/home/hadoop/irs990\" >> .bash_profile`.
  1. Create a `.boto` file with your access key and secret key
  
## Notice

*Copyright 2017 Charity Navigator.*

*Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:*

*The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.*

*THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.*