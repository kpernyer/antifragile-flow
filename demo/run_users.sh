
#!/bin/bash

for i in {1..5}
do
   python demo/user_client.py --user="user$i" &
   echo "Started user client for user$i"
done
