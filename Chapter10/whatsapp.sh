#!/bin/bash
BASEDIR=/home/yowsup/yowsup-master
#echo "sudo -u yowsup $BASEDIR/yowsup-cli demos -c $BASEDIR/yowsup.config -s $1 \"$2 $3\"" >> /var/log/whatsapp.log
sudo -u yowsup $BASEDIR/yowsup-cli demos -c $BASEDIR/yowsup.config -s $1 "$2 $3"
