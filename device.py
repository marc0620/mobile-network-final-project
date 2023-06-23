import numpy as np
import algorithm
import LI
import random
from signal_source import signal_source


# Parameters
SP = 0.03  ## 30ms
POWER = {"tx": 1, "rx": 1, "idle": 0.3, "doze": 0}
capacity = 28.32 * 10**5
busy = 2
packet_size = 0.1 * 10**3
data_rate = 11.8 * 10**6

# average_capacity = capacity / num_STA / 2
# lamb_avg = average_capacity / packet_size
# packet_threshold = lamb_avg * 2
threshold = 1.5


class STA:
    def __init__(self, n, lamb, num_STA) -> None:
        self.ID = n

        # TBTT Scheduling
        self.first_TBTT = 0
        # Power Parameters
        self.lamb = lamb
        self.total_power_consumption = 0.0
        self.packet_buffer = 0
        self.latency = 0
        self.LI = round(
            (capacity / busy / num_STA * 4) * (lamb * packet_size) ** (-1)
        )  # scale_LI = average_capacity * 4
        # print(self.LI)
        if self.LI <= 0:
            self.LI = 1


class Beacon_AP:
    def __init__(self, sta_num, stas):
        self.sta_num = sta_num
        self.stas = stas
        lamb = list(map(lambda sta: sta.lamb, stas))
        self.source_signal = signal_source(lamb, sta_num)
        self.total_transmitted = 0
        self.latency = 0

    def transmit(self):
        total = 0
        ready = []
        for idx, sta in enumerate(self.stas):
            if (
                sta.packet_buffer
                > (capacity / busy / self.sta_num / packet_size) * threshold
            ):  # packet_threshold=lamb_avg*2
                ready.append(idx)
        selected = random.sample(ready, k=min(LI.m, len(ready)))

        for s in selected:
            total += self.stas[s].packet_buffer
            ready.remove(s)

        for s in selected:
            transmitted = min(self.stas[s].packet_buffer * packet_size, SP * data_rate)
            tx_duration = transmitted / data_rate
            self.stas[s].total_power_consumption += tx_duration * POWER["rx"]
            self.stas[s].total_power_consumption += (
                max(SP - tx_duration, 0) * POWER["idle"]
            )
            self.stas[s].packet_buffer -= transmitted / packet_size
            self.total_transmitted += transmitted / packet_size

            # print(self.stas[s].packet_buffer)
        for r in ready:
            self.stas[r].total_power_consumption += SP * POWER["idle"]

    def tick(self):
        packets = self.source_signal.generate()
        for idx, sta in enumerate(self.stas):
            sta.packet_buffer += packets[idx]
        self.transmit()
        for sta in self.stas:
            sta.latency += sta.packet_buffer


class TWTT_AP:
    def __init__(self, STAs, sta_num) -> None:
        self.STAs = STAs
        self.schedule = []
        self.time = 0
        lamb = list(map(lambda sta: sta.lamb, STAs))
        self.source_signal = signal_source(lamb, sta_num)
        self.total_data_transmitted = 0
        # self.optimizing_LI()
        # self.scheduling()

    def optimizing_LI(self):
        original_LI = []

        for i in range(len(self.STAs)):
            original_LI.append(self.STAs[i].LI)

        best = LI.optimal_avg_num_STA(len(self.STAs))
        optimized_LI = []

        optimized_LI = LI.optimal_LI(original_LI, best)

        for i in range(len(self.STAs)):
            self.STAs[i].LI = optimized_LI[i]

    def scheduling(self):
        subsets = algorithm.inter_grouping(self.STAs)
        for subset in subsets:
            self.schedule.append(algorithm.intra_grouping(subset))
        drift_offsets = algorithm.drift_grouping(self.schedule)
        shifted = []
        for i in range(len(self.STAs)):
            shifted.append(False)
        for i in range(len(subsets)):
            for slot in self.schedule[i][-1]:
                if slot != -1 and shifted[slot] == False:
                    self.STAs[slot].first_TBTT += drift_offsets[i]
                    shifted[slot] = True

    def transmit(self, sta):
        transmission_duration = min(sta.packet_buffer * packet_size / data_rate, SP)
        idle_time = SP - transmission_duration
        sta.total_power_consumption += (
            transmission_duration * POWER["tx"] + idle_time * POWER["idle"]
        )
        # print(transmission_duration)
        transmitted = min(SP * data_rate / packet_size, sta.packet_buffer)
        self.total_data_transmitted += transmitted
        sta.packet_buffer = sta.packet_buffer - transmitted

    def tick(self):
        packets = self.source_signal.generate()
        for idx, sta in enumerate(self.STAs):
            sta.packet_buffer += packets[idx]
        ready = []
        for sta in self.STAs:
            if (self.time - sta.first_TBTT) % sta.LI == 0:
                ready.append(sta.ID)
        selected = random.sample(ready, k=min(LI.m, len(ready)))
        for s in selected:
            self.transmit(self.STAs[s])
            ready.remove(s)
        for r in ready:
            self.STAs[r].total_power_consumption += SP * POWER["idle"]
        for sta in self.STAs:
            sta.latency += sta.packet_buffer
        self.time += 1


class TWTT_AP1:
    def __init__(self, STAs, sta_num) -> None:
        self.STAs = STAs
        self.schedule = []
        self.time = 0
        lamb = list(map(lambda sta: sta.lamb, STAs))
        self.source_signal = signal_source(lamb, sta_num)
        self.total_data_transmitted = 0
        self.optimizing_LI()
        self.scheduling()

    def optimizing_LI(self):
        original_LI = []

        for i in range(len(self.STAs)):
            original_LI.append(self.STAs[i].LI)

        best = LI.optimal_avg_num_STA(len(self.STAs))
        optimized_LI = []

        optimized_LI = LI.optimal_LI(original_LI, best)

        for i in range(len(self.STAs)):
            self.STAs[i].LI = optimized_LI[i]

    def scheduling(self):
        subsets = algorithm.inter_grouping(self.STAs)
        for subset in subsets:
            self.schedule.append(algorithm.intra_grouping(subset))
        drift_offsets = algorithm.drift_grouping(self.schedule)
        shifted = []
        for i in range(len(self.STAs)):
            shifted.append(False)
        for i in range(len(subsets)):
            for slot in self.schedule[i][-1]:
                if slot != -1 and shifted[slot] == False:
                    self.STAs[slot].first_TBTT += drift_offsets[i]
                    shifted[slot] = True

    def transmit(self, sta):
        transmission_duration = min(sta.packet_buffer * packet_size / data_rate, SP)
        idle_time = SP - transmission_duration
        sta.total_power_consumption += (
            transmission_duration * POWER["tx"] + idle_time * POWER["idle"]
        )
        # print(transmission_duration)
        transmitted = min(SP * data_rate / packet_size, sta.packet_buffer)
        self.total_data_transmitted += transmitted
        sta.packet_buffer = sta.packet_buffer - transmitted

    def tick(self):
        packets = self.source_signal.generate()
        for idx, sta in enumerate(self.STAs):
            sta.packet_buffer += packets[idx]
        ready = []
        for sta in self.STAs:
            if (self.time - sta.first_TBTT) % sta.LI == 0:
                ready.append(sta.ID)
        selected = random.sample(ready, k=min(LI.m, len(ready)))
        for s in selected:
            self.transmit(self.STAs[s])
            ready.remove(s)
        for r in ready:
            self.STAs[r].total_power_consumption += SP * POWER["idle"]
        for sta in self.STAs:
            sta.latency += sta.packet_buffer
        self.time += 1
