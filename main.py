import json
import math
import matplotlib.pyplot as plt


class ExtractDataFromFile:
    def __init__(self,file,filePower):
        self.step = 3
        self.max = 120
        self.timeframe = 5
        self.filePower = filePower
        self.file = file
        # self.groupby = "src_host"
        self.groupby = "dst_host"
        with open(file) as f:
            self.data = json.load(f)
        self.packetSummary = []
        self.extractData()
        self.extractPower()
        self.linkPower()
        print(self.packetSummary)
        #free memory
        # self.data = 0

    def linkPower(self):
        for timeframe in range(len(self.packetSummary)):
            for host in self.packetSummary[timeframe]:
                if host != "ff02::1a":
                    moteNumber = int(host[-1],16) - 1
                    if timeframe >= len(self.powerLinear[moteNumber]):
                        self.packetSummary[timeframe][host]["power"] = 0
                    elif timeframe == 0:
                        power = self.powerLinear[moteNumber][timeframe]
                    else:
                        power = self.powerLinear[moteNumber][timeframe] - self.powerLinear[moteNumber][timeframe-1]
                    power = power / (self.timeframe * 1000000)
                    self.packetSummary[timeframe][host]["power"] = power
                else:
                    self.packetSummary[timeframe][host]["power"] = 0


    def extractPower(self):
        self.power = {}

        #read the file and group the consumption by mote and time
        with open(self.filePower) as f:
            base = 0
            for line in f:
                info = line.split()
                if info[0] != "AVG":
                    id = int(info[0][4:]) - 1
                    if id not in self.power:
                        self.power[id] = []
                    if info[1] == "MONITORED":
                        if len(self.power[id]) == 0:
                            self.power[id].append({"time": int(info[2])})
                        elif self.power[id][-1]["time"] != int(info[2]):
                            self.power[id].append({"time": int(info[2])})
                    else:
                        self.power[id][-1][info[1]] = int(info[2])
        # print(self.power)
        #calculate the time on for each mote for each timeframe
        self.powerLinear = {}
        for id_mote in self.power:
            if id_mote not in self.powerLinear:
                self.powerLinear[id_mote] = []
            mote = self.power[id_mote]
            prev = 0
            for i in range(len(mote)):
                pos = mote[i]["time"]
                pos = math.trunc(pos/1000000)
                pos = pos // self.timeframe
                if pos > len(self.powerLinear[id_mote]):
                    timeAfter = mote[i]["time"]
                    timeBefore = mote[i-1]["time"]
                    powerAfter = mote[i]["ON"] + mote[i]["TX"] +mote[i]["RX"] + mote[i]["INT"]
                    powerBefore = mote[i-1]["ON"] + mote[i-1]["TX"] + mote[i-1]["RX"] + mote[i-1]["INT"]
                    a = (powerAfter - powerBefore) / (timeAfter-timeBefore)
                    b = powerBefore - a * timeBefore
                    while pos > len(self.powerLinear[id_mote]) :
                        powerTime = a * (len(self.powerLinear[id_mote])+1) * self.timeframe * 1000000 + b
                        #powerTime = powerTime / ((len(self.powerLinear[-1])+1) * self.timeframe * 1000000 )
                        self.powerLinear[id_mote].append(powerTime)

    def extractData(self):
        #packet counter
        a = 0
        for packet in self.data:
            a += 1
            # print(a)
            pos = float(packet["_source"]["layers"]["frame"]["frame.time_relative"])
            # print(pos)
            pos = math.trunc(pos)
            pos = pos // self.timeframe
            #pos indicates which time windows we are in
            #creation of all packet summary dictionnary
            while pos >= len(self.packetSummary):
                self.packetSummary.append({})
            #if the packet uses ipv6 protocol
            if "_source" in packet and "layers" in packet["_source"] and "ipv6" in packet["_source"]["layers"]:
                #groupby host in the dictionnary : host can be the source or the destination host of the packet
                host = packet["_source"]["layers"]["ipv6"]["ipv6."+self.groupby]
                #to aggreagate packet by source or destination we need to groupby ipv6 address with local link address of a single mote
                if host != "ff02::1a":
                    host = host[-1]
                if host not in self.packetSummary[pos]:
                    self.packetSummary[pos][host] = {"packet-number": 0, "dis": 0, "dio" : 0 , "dao" : 0, "version-changes" : 0, "rank-changes" : 0, "old-version": 0, "old-rank" : 0}
                    if pos > 0:
                        if host in self.packetSummary[pos-1]:
                            self.packetSummary[pos][host]["old-version"] = self.packetSummary[pos-1][host]["old-version"]
                            self.packetSummary[pos][host]["old-rank"] = self.packetSummary[pos-1][host]["old-rank"]
                # if "udp" in packet["_source"]["layers"]:
                #     self.packetSummary[pos][host]["packet-number"] += 1
                if "icmpv6" in packet["_source"]["layers"]:
                    self.packetSummary[pos][host]["packet-number"] += 1
                if "_source" in packet and "layers" in packet["_source"] and "icmpv6" in packet["_source"]["layers"] and "icmpv6.code" in packet["_source"]["layers"]["icmpv6"] :
                    if packet["_source"]["layers"]["icmpv6"]["icmpv6.code"] == "0":
                        self.packetSummary[pos][host]["dis"] += 1
                    elif packet["_source"]["layers"]["icmpv6"]["icmpv6.code"] == "1":
                        self.packetSummary[pos][host]["dio"] += 1
                        if self.packetSummary[pos][host]["old-version"] != packet["_source"]["layers"]["icmpv6"]["icmpv6.rpl.dio.version"]:
                            self.packetSummary[pos][host]["old-version"] = packet["_source"]["layers"]["icmpv6"]["icmpv6.rpl.dio.version"]
                            self.packetSummary[pos][host]["version-changes"] += 1
                        if self.packetSummary[pos][host]["old-rank"] != packet["_source"]["layers"]["icmpv6"]["icmpv6.rpl.dio.rank"]:
                            self.packetSummary[pos][host]["old-rank"] = packet["_source"]["layers"]["icmpv6"]["icmpv6.rpl.dio.rank"]
                            self.packetSummary[pos][host]["rank-changes"] += 1

                        # print(packet["_source"]["layers"]["icmpv6"]["icmpv6.rpl.dio.rank"])
                    elif packet["_source"]["layers"]["icmpv6"]["icmpv6.code"] == "2":
                        self.packetSummary[pos][host]["dao"] += 1
                    else:
                        print("erreur !!!!!!!!")

        hosts = []
        for window in self.packetSummary:
            for host in window:
                if window[host]["packet-number"] == 0:
                    window[host]["packet-number"] = 1
                window[host]["packet-number"] =1
                window[host]["dis"] /= window[host]["packet-number"]
                window[host]["dio"] /= window[host]["packet-number"]
                window[host]["dao"] /= window[host]["packet-number"]
                window[host]["rank-changes"] /= window[host]["packet-number"]
                window[host]["version-changes"] /= window[host]["packet-number"]
                if host not in hosts:
                    hosts.append(host)

        #hosts that have no packets in a timeframe are added
        # for window in self.packetSummary:
        #     for host in hosts:
        #         if host not in window:
        #             window[host] = {"packet-number": 0, "dis": 0, "dio" : 0 , "dao" : 0, "version-changes" : 0, "rank-changes" : 0, "old-version": 0, "old-rank" : 0}
        for window in self.packetSummary:
            for host in list(window):
                if window[host]["dis"] == 0 and window[host]["dio"] == 0 and window[host]["dao"] == 0 and window[host]["version-changes"] == 0  and window[host]["rank-changes"] == 0:
                    window.pop(host)
        x = []
        dis = []
        dio = []
        dao = []
        version = []
        rank = []
        for window in self.packetSummary:
            sumdis = 0
            sumdio = 0
            sumdao = 0
            sumversion = 0
            sumrank = 0
            for host in list(window):
                sumdis += window[host]["dis"]
                sumdio += window[host]["dio"]
                sumdao += window[host]["dao"]
                sumversion += window[host]["version-changes"]
                sumrank += window[host]["rank-changes"]
            x.append(self.timeframe*(len(x)+1))
            dis.append(sumdis)
            dio.append(sumdio)
            dao.append(sumdao)
            version.append(sumversion)
            rank.append(sumrank)
        self.data = {"file": self.file.split("/")[-2], "x": x, "dis": dis, "dio": dio, "dao": dao, "version": version, "rank": rank}

        # print(dis)
        # fig, ax = plt.subplots()
        # ax.plot(x, dis, label="dis")
        # ax.plot(x,dio, label="dio")
        # ax.plot(x, dao, label="dao")
        # ax.plot(x, version, label="version")
        # ax.plot(x, rank, label="rank")
        # ax.legend()
        # plt.show()




    def normalizePacketSummary(self, param):
        maxItem = max(self.packetSummary, key=lambda x: x[param])
        minItem = min(self.packetSummary, key=lambda x: x[param])
        for window in self.packetSummary:
            window[param] = ((window[param] - minItem) * (1 + 1)) / (maxItem - minItem)

#gather the data from the list of files and create a matrix that contains all the vectors needed to train the SOM
class ProcessFiles:
    def __init__(self, files):
        self.data = []
        for file in files:
            self.data.append(ExtractDataFromFile(file[0], file[1]))
        self.normData = []
        self.normDataArray = []
        self.listOfColors = ["red", "green", "blue", "yellow"]
        self.colors = []

    def plot(self):
        axes = ["dis","dio", "dao", "version", "rank"]
        for label in axes:
            fig, ax = plt.subplots()
            for attack in self.data:
                ax.plot(attack.data["x"], attack.data[label], label=attack.data["file"])
            ax.legend()
            plt.title(label)

            plt.show()


    def normalizeData(self):
        mini = {}
        maxi = {}
        for param in ["dis", "dio", "dao", "version-changes", "rank-changes", "power"]:
            mini[param] = None
            maxi[param] = None
        for dataFile in self.data:
            for window in dataFile.packetSummary:
                for host in window:
                    for param in ["dis", "dio" , "dao", "version-changes", "rank-changes", "power"]:
                        if mini[param] == None or maxi[param] == None:
                            mini[param] = float(window[host][param])
                            maxi[param] = float(window[host][param])
                        else:
                            mini[param] = min(mini[param], float(window[host][param]))
                            a = maxi[param]
                            b = float(window[host][param])
                            maxi[param] = max(a,b)

        i = 0
        for dataFile in self.data:
            for window in dataFile.packetSummary:
                for host in window:
                    self.colors.append(self.listOfColors[i])
                    line = ""
                    self.normDataArray.append([])
                    for param in ["dis", "dio" , "dao", "version-changes", "rank-changes","power"]:
                        # if maxi[param] - mini[param] == 0:

                        window[host][param] = (((float(window[host][param]) - mini[param]) * (1 + 1)) / (maxi[param] - mini[param])) - 1
                        line += str(window[host][param]) + " "
                        self.normDataArray[-1].append(window[host][param])

                    self.normData.append(line)
            i += 1



# d = ExtractDataFromFile('/home/remi/Documents/internship/shared/flood-with.json')

p = ProcessFiles([("/home/remi/Documents/internship/shared/script-experiments/benign-udp/output.json", "/home/remi/Documents/internship/shared/script-experiments/benign-udp/powertracker.log"), ("/home/remi/Documents/internship/shared/script-experiments/decreased-rank-udp/output.json", "/home/remi/Documents/internship/shared/script-experiments/decreased-rank-udp/powertracker.log"), ("/home/remi/Documents/internship/shared/script-experiments/flooding-udp/output.json", "/home/remi/Documents/internship/shared/script-experiments/flooding-udp/powertracker.log"), ("/home/remi/Documents/internship/shared/script-experiments/increased-version-udp/output.json", "/home/remi/Documents/internship/shared/script-experiments/increased-version-udp/powertracker.log")])
p.plot();
p.normalizeData()
print(p.normData)

f = open("/home/remi/Documents/internship/shared/output.txt", "w")
for line in p.normData:
    f.write(line+"\n")
f.close()

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import somoclu

data = np.float32(p.normDataArray)
n_rows, n_columns = 100,160
som = somoclu.Somoclu(n_columns, n_rows, compactsupport=False)
som.train(data, scale0=0.1, epochs=10)
som.view_component_planes(bestmatches=True,bestmatchcolors=p.colors)

print(p.colors)
print(len(p.colors), len(p.normDataArray))
som.view_umatrix(bestmatches=True,bestmatchcolors=p.colors)
print("FINISH")