# Identify some types of attacks with a self organised map (SOM)
## IPre-requisities of the python script
The Python script is written in Python 3.
First you need to install some Python library:
* json
* numpy
* matplotlib
* [somoclu](https://somoclu.readthedocs.io/en/stable/download.html) which is the library for the SOM

The python script needs a packet capture file transformed into a json file with the tshark command line program to analyze the data. As the creation of all the data is automated in a shell script if you want some details about this command you can look into the shell script simulation.sh

## Options to setup in the script
### Group the packets by source or destination host
You can group by all the packets by their source host or by the destination host, just comment/uncomment this line:

```python
self.groupby = "src_host"
# self.groupby = "dst_host"
```
### Group the packets on different timeframe
You can change the timeframe to group the packets by changing this variable:

```python
self.timeframe = 3
```
### List of the files to analyze
To work this script needs the packets data from a JSON file and the power consumption from a log file. For each attacks you should provide a pair of a JSON file which is created from a pcap file and log file created by Cooja. Those files should be inserted in the script like mentioned below.

```python
p = ProcessFiles([
    ("/home/remi/Documents/internship/shared/script-experiments/benign-udp/output.json", "/home/remi/Documents/internship/shared/script-experiments/benign-udp/powertracker.log"),
    ("/home/remi/Documents/internship/shared/script-experiments/decreased-rank-udp/output.json", "/home/remi/Documents/internship/shared/script-experiments/decreased-rank-udp/powertracker.log"),
    ("/home/remi/Documents/internship/shared/script-experiments/flooding-udp/output.json", "/home/remi/Documents/internship/shared/script-experiments/flooding-udp/powertracker.log"),
    ("/home/remi/Documents/internship/shared/script-experiments/increased-version-udp/output.json", "/home/remi/Documents/internship/shared/script-experiments/increased-version-udp/powertracker.log")
])
```

## Produce data to analyze
To speed up the proccess of creating sets of data you can find the script 'simulation.sh' that automate the simulation and the transformation of the pcap file. At the end the script will return the path of all the files that you will need to analyze. Those paths need to be copy-pasted in the list of files mentioned above.

### Options to set up the shell script
First you need to set up all the variable in the shell script simulation.sh
```shell
FILES=./*.csc
COOJA=../../contiki/tools/cooja/dist/cooja.jar
CONTIKI=../../contiki
FILE_DESTINATION=/media/sf_shared/script-experiments/
```
The $FILE_DESTINATION variable will be the destination of the JSON and LOG files and $FILES variable is the place where all your csc files that you would like to simulate are. 

Be sure to have the folder "data" in the same folder than the shell script or it will not work because this folder is the destination for all the log and data files.

### How to create a good csc file for simulation
To facilitate the creation and the configuration of the csc file I really encourage you to look at the csc file given in example in this repositery.

As the simulation is completely automated your simulation has to have a script file written in js that is provided in this repositery (script.js), this file was taken from this repositery: https://github.com/dhondta/rpl-attacks
In Cooja, the script module has to include this script and it has to be activated in the options of the module in cooja ("Run -> Activate")

The powertracker module and the radio messages module has to be open too. And the radio messages module has to be on the mode "Analyzer -> 6LowPan Analyzer with PCAP" in order to produce the pcap file.

You can the create all the csc file you want and now execute the simulation script and it will launch all the simulation one by one and store all the log file in the directory of your choice to be analyzed later by the python script.

**Warning: the json file could be very big (~500Mo for 10 motes and 3 minutes of simulation in case of a flooding attack for example) so make sure you have enough space available on your computer.**








