#!/bin/sh

# Author : Gaillard Rémi
FOO=""


FILES=./*.csc
COOJA=../../contiki/tools/cooja/dist/cooja.jar
CONTIKI=../../contiki
FILE_DESTINATION=/media/sf_shared/script-experiments/

for f in $FILES
do
  echo "Launching simulation with $f file"
  java -jar $COOJA -hidden=$f -contiki=$CONTIKI
  NAME=$(basename $f .csc)
  mkdir -p $FILE_DESTINATION$NAME && cp data/* $FILE_DESTINATION$NAME
  echo "MKDIR AND COPY OK"
  tshark -T json -r $FILE_DESTINATION$NAME/output.pcap > $FILE_DESTINATION$NAME/output.json
  echo "TSHARK OK"
  foo="$foo (\"$FILE_DESTINATION$NAME/output.json\", \"$FILE_DESTINATION$NAME/powertracker.log\"),"
  echo "Log files saved to $FILE_DESTINATION$NAME folder"
done

echo "$foo"


