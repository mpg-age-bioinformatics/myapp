#!/bin/bash

rm -rf /myapp/utils/requirements.all.txt
while read line ; 
    do 
        pip3 list | grep ${line} | awk '{ print $1"=="$2 }' >> /myapp/utils/requirements.all.txt
done < /myapp/utils/requirements.min.txt

pip3 list | sed '1,2d' | awk '{ print $1"=="$2 }' > /myapp/utils/.requirements.all.txt

while read line ; 
    do 
        grep -v ${line} /myapp/utils/.requirements.all.txt > /myapp/utils/.requirements.all.txt.tmp
        mv /myapp/utils/.requirements.all.txt.tmp /myapp/utils/.requirements.all.txt
done < /myapp/utils/requirements.all.txt

cat /myapp/utils/.requirements.all.txt >> /myapp/utils/requirements.all.txt
rm -rf /myapp/utils/.requirements.all.txt

exit
