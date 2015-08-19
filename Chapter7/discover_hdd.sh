#!/bin/bash
disks=`ls -l /dev/sd* | awk '{print $NF}' | sed 's/[0-9]//g' | uniq`
elementn=`echo $disks| wc -w`
echo "{"
echo "\"data\":["
i=1
for disk in $disks
do
if [ $i == $elementn ]
then
    echo "    {\"{#DISKNAME}\":\"$disk\",\"{#SHORTDISKNAME}\":\"${disk:5}\"}"
else
    echo "    {\"{#DISKNAME}\":\"$disk\",\"{#SHORTDISKNAME}\":\"${disk:5}\"},"
fi
i=$((i+1))
done
echo "]"
echo "}"