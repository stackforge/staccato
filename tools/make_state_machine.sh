#!/bin/bash

source /home/jbresnah/Dev/OpenStack/openstackVE/bin/activate
f=`mktemp`
python -c 'import staccato.xfer.events as e;e._print_state_machine()' > $f
#dot -T png  -o $1 $f
dot -T pdf  -o $1 $f
rm $f
echo "Made $1"
