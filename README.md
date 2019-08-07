# Identify some types of attacks with a self organised map (SOM)
## Installation of the python script
The Python script is written in Python 3.
First you need to install some Python library:
* json
* numpy
* matplotlib
* [somoclu](https://somoclu.readthedocs.io/en/stable/download.html) which is the library for the SOM

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

### Options to set up in the shell script






