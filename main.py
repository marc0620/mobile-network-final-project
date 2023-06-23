import sympy as s
import math
import LI
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import device
import copy
import random
from signal_source import signal_source

matplotlib.use("TkAgg")

# Parameters
SP = device.SP  ## 30ms
POWER = {"tx": 1, "rx": 1, "idle": 0.3, "doze": 0}
packet_size = 0.1 * 10**3
capacity = device.capacity
busy = device.busy
data_rate = device.data_rate
# num_station = [100]
num_station = [(i + 1) * 10 for i in range(50)]
iteration = 1000  # unit: 1 beacon (100 ms)
comparison_busy = [2]

np.random.seed(2023)
random.seed(2023)
# Recoding different properties of different # of STAs
twt_energy_consumption = []
twt_throughput = []
twt_latency = []
twt_ee = []
beacon_energy_consumption = []
beacon_throughput = []
beacon_latency = []
beacon_ee = []
twt1_energy_consumption = []
twt1_throughput = []
twt1_latency = []
twt1_ee = []
for ith in range(len(comparison_busy)):
    twt_energy_consumption.append([])
    twt_throughput.append([])
    twt_latency.append([])
    twt_ee.append([])
    beacon_energy_consumption.append([])
    beacon_throughput.append([])
    beacon_latency.append([])
    beacon_ee.append([])
    twt1_energy_consumption.append([])
    twt1_throughput.append([])
    twt1_latency.append([])
    twt1_ee.append([])

    LI.busy = comparison_busy[ith]
    for STA_num in num_station:
        LI.m = 8
        # Recoding different properties of each # of STAs
        twt_each_LIs = []
        twt_each_latency = []
        twt_each_energy_consumption = []
        twt1_each_LIs = []
        twt1_each_latency = []
        twt1_each_energy_consumption = []
        beacon_each_LIs = []
        beacon_each_latency = []
        beacon_each_energy_consumption = []
        lamb_avg = capacity / packet_size / busy / STA_num
        disp = lamb_avg * 2 / 3
        lambs = np.random.uniform(lamb_avg - disp, lamb_avg + disp, (STA_num))
        STAs = []
        original_TBTTs = []
        optimized_TBTTs = []

        for i in range(STA_num):
            STAs.append(device.STA(i, lambs[i], STA_num))
            original_TBTTs.append(STAs[i].first_TBTT)

        STAs_1 = copy.deepcopy(STAs)
        STAs_2 = copy.deepcopy(STAs)
        beacon_AP = device.Beacon_AP(sta_num=STA_num, stas=STAs_2)
        twtt_ap = device.TWTT_AP1(STAs, STA_num)
        twtt1_ap = device.TWTT_AP(STAs_1, STA_num)

        for i in range(STA_num):
            optimized_TBTTs.append(STAs[i].first_TBTT)

        for i in range(iteration):
            twtt_ap.tick()
            twtt1_ap.tick()

        for i in range(STA_num):
            twt_each_energy_consumption.append(twtt_ap.STAs[i].total_power_consumption)
            twt_each_LIs.append(twtt_ap.STAs[i].LI)
            twt_each_latency.append(twtt_ap.STAs[i].latency)
            twt1_each_energy_consumption.append(
                twtt1_ap.STAs[i].total_power_consumption
            )
            twt1_each_LIs.append(twtt1_ap.STAs[i].LI)
            twt1_each_latency.append(twtt1_ap.STAs[i].latency)
            # beacon_each_LIs.append(beacon_AP.stas[i].LI)
            # beacon_each_latency.append(beacon_AP.stas[i].latency)
            # beacon_each_energy_consumption.append(
            #    beacon_AP.stas[i].total_power_consumption
            # )

        twt_energy_consumption[ith].append(sum(twt_each_energy_consumption))
        twt_throughput[ith].append(
            twtt_ap.total_data_transmitted * packet_size / (iteration * 0.1) / 1e6
        )
        twt_latency[ith].append(
            sum(twt_each_latency) / twtt_ap.total_data_transmitted * 0.1
        )
        twt_ee[ith].append(twt_throughput[ith][-1] / twt_energy_consumption[ith][-1])

        twt1_energy_consumption[ith].append(sum(twt1_each_energy_consumption))
        twt1_throughput[ith].append(
            twtt1_ap.total_data_transmitted * packet_size / (iteration * 0.1) / 1e6
        )
        twt1_latency[ith].append(
            sum(twt1_each_latency) / twtt1_ap.total_data_transmitted * 0.1
        )
        twt1_ee[ith].append(twt1_throughput[ith][-1] / twt1_energy_consumption[ith][-1])

        # beacon_energy_consumption[ith].append(sum(beacon_each_energy_consumption))
        # beacon_throughput[ith].append(
        #    beacon_AP.total_transmitted * packet_size / (iteration * 0.1) / 1e6
        # )
        # beacon_latency[ith].append(
        #    sum(beacon_each_latency) / beacon_AP.total_transmitted * 0.1
        # )
        # beacon_ee[ith].append(
        #    beacon_throughput[ith][-1] / beacon_energy_consumption[ith][-1]
        # )


for i in range(len(comparison_busy)):
    fig0 = plt.figure()
    plt.xlabel("number of stations", fontsize="10")
    plt.ylabel("energy (W)", fontsize="10")
    plt.title(f"energy_consumption, busy =  {comparison_busy[i]**(-1)}", fontsize="18")
    plt.plot(num_station, twt_energy_consumption[i], label="with offset scheduling")
    plt.plot(num_station, twt1_energy_consumption[i], label="without offset scheduling")
    plt.legend()

    fig1 = plt.figure()
    plt.xlabel("number of stations", fontsize="10")
    plt.title(f"throughput (Mbps), busy =  {comparison_busy[i]**(-1)}", fontsize="18")
    plt.plot(num_station, twt_throughput[i], label="with offset scheduling")
    plt.plot(num_station, twt1_throughput[i], label="without offset scheduling")
    plt.legend()

    fig2 = plt.figure()
    plt.xlabel("number of stations", fontsize="10")
    plt.ylabel("latency (s)", fontsize="10")
    plt.title(f"latency, busy =  {comparison_busy[i]**(-1)}", fontsize="18")
    plt.plot(num_station, twt_latency[i], label="with offset scheduling")
    plt.plot(num_station, twt1_latency[i], label="without offset scheduling")
    plt.legend()

    fig3 = plt.figure()
    plt.xlabel("number of stations", fontsize="10")
    plt.ylabel("energy_efficiency", fontsize="10")
    plt.title(f"EE, busy =  {comparison_busy[i]**(-1)}", fontsize="18")
    plt.plot(num_station, twt_ee[i], label="with offset scheduling")
    plt.plot(num_station, twt1_ee[i], label="without offset scheduling")
    plt.legend()
plt.show()


###################


# fig0 = plt.figure()
# plt.xlabel('number of stations', fontsize="10")
# plt.ylabel('energy (W)', fontsize="10")
# plt.title('twt_energy_consumption', fontsize="18")
# plt.plot(num_station, twt_energy_consumption[i])


# fig1 = plt.figure()
# plt.xlabel('number of stations', fontsize="10")
# plt.title('twt_throughput (Mbps)', fontsize="18")
# plt.plot(num_station, twt_throughput[i])


# fig2 = plt.figure()
# plt.xlabel('number of stations', fontsize="10")
# plt.ylabel('twt_latency (s)', fontsize="10")
# plt.title('twt_latency', fontsize="18")
# plt.plot(num_station, twt_latency[i])


# fig3 = plt.figure()
# plt.xlabel('number of stations', fontsize="10")
# plt.ylabel('energy_efficiency', fontsize="10")
# plt.title('twt_EE = throughput / energy_consumed (Mbps / J)', fontsize="18")
# plt.plot(num_station, twt_ee[i])


# fig4 = plt.figure()
# plt.xlabel('number of stations', fontsize="10")
# plt.ylabel('energy (W)', fontsize="10")
# plt.title('beacon_energy_consumption', fontsize="18")
# plt.plot(num_station, beacon_energy_consumption[i])


# fig5 = plt.figure()
# plt.xlabel('number of stations', fontsize="10")
# plt.title('beacon_throughput (Mbps)', fontsize="18")
# plt.plot(num_station, beacon_throughput[i])

# fig6 = plt.figure()
# plt.xlabel('number of stations', fontsize="10")
# plt.ylabel('beacon_latency (s)', fontsize="10")
# plt.title('beacon_latency', fontsize="18")
# plt.plot(num_station, beacon_latency[i])

# fig7 = plt.figure()
# plt.xlabel('number of stations', fontsize="10")
# plt.ylabel('energy_efficiency', fontsize="10")
# plt.title('beacon_EE', fontsize="18")
# plt.plot(num_station, beacon_ee[i])
