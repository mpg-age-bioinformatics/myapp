#!/bin/bash

rm -rf /myapp/requirements.txt
while read line ; 
    do 
        pip3 list | grep ${line} | awk '{ print $1"=="$2 }' >> /myapp/requirements.txt
done < /myapp/utils/requirements.min.txt

pip3 list | sed '1,2d' | awk '{ print $1"=="$2 }' > /myapp/utils/requirements.all.txt

# rm -rf /myapp/.stable.txt
# pip3 list | sed '1,2d' | awk '{ print $1"=="$2 }' > /myapp/.stable.txt
# while read line ; 
#     do 
#         grep -v ${line} /myapp/.stable.txt > /myapp/.stable.txt.tmp
#         mv /myapp/.stable.txt.tmp /myapp/.stable.txt
# done < /myapp/stable.txt

# cat /myapp/.stable.txt >> /myapp/stable.txt
# mv /myapp/stable.txt /myapp/requirements.txt
# rm /myapp/.stable.txt

exit
