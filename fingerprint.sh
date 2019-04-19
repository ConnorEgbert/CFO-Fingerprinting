#!/bin/bash

sample_count=$1
freq=$2

if [ $# -ne 2 ]; then
    echo "Usage: ./fingerprint.sh <sample_count> <frequency/10e6>"
    echo "Example: ./fingerprint.sh 10000 5600"
    exit 1
fi

echo -ne "Requested samples:\t$sample_count\n"
echo -ne "Frequency:\t\t$freq\n"

of="data_$(date +"%m-%d-%Y-%T").txt"

if [ ! -d ./CFO_data ]; then
  mkdir -p ./CFO_data
fi

if [ ! -d ./error.log.d ]; then
  mkdir -p ./error.log.d
fi

python base_wifi_rx.py $freq > ./CFO_data/$of 2>/dev/null &

pid=$!
disown $pid

touch ./CFO_data/$of
echo -ne "Progress:\t\t%0\r"
sleep 3

while true; do
	sleep 1
	# Doing bash math is impossible.
	# Welcome to jankville. Population: this script.
	percent=$(bc -l <<< "scale=2; $(wc -l < ./CFO_data/$of) / $sample_count * 100")
	echo -ne "Progress:\t\t%$percent\r"

	if [ $(wc -l < ./CFO_data/$of) -ge $sample_count ]; then
		break
	fi
done

kill $pid &>/dev/null

echo
echo "Calculating values..."

python3 colorMapping.py ./CFO_data/$of $freq

python offset_analysis.py ./CFO_data/$of 
