import numpy as np

# class STA:
#     def __init__(self, n, li) -> None:
#         self.ID = n

#         # TBTT Scheduling
#         self.LI = li
#         while self.LI <= 0:
#             self.LI = np.floor(np.random.normal(8, 3))
#         self.first_TBTT = 0

#         # Power Parameters
#         self.total_power_consumption = 0.0


#     def LI_optimization(self):
#         pass


def inter_grouping(STAs):
    # Sorting
    STAs_sorted = sorted(STAs, key=lambda STA: STA.LI)
    u = 0
    subsets = []
    while len(STAs_sorted) != 0:
        t = STAs_sorted[0]
        temp_subset = []
        i_terminate = 0
        find = False
        if u >= 1:
            for i in range(u):
                i_terminate = i
                if len(subsets) > i:
                    temp = subsets[i][-1]
                    if t.LI % temp.LI == 0:
                        temp_subset = subsets[i]
                        find = True
                        break
                else:
                    break
        if len(temp_subset) == 0:
            u = u + 1
        temp_subset.append(t)
        if find:
            subsets[i_terminate] = temp_subset
        else:
            subsets.append(temp_subset)

        STAs_sorted.pop(0)

    return subsets


def intra_grouping(subset):
    max_t = 0
    for STA in subset:
        if STA.LI > max_t:
            max_t = STA.LI
    lists = [[]]
    row = 0
    for i in range(max_t):
        lists[0].append(-1)
    for STA in subset:
        for i in range(max_t):
            if lists[row][i] == -1:
                j = i
                STA.first_TBTT = i
                while j < max_t:
                    lists[row][j] = STA.ID
                    j = j + STA.LI
                break
        full = True
        for i in range(max_t):
            if lists[row][i] == -1:
                full = False
        if full:
            row = row + 1
            lists.append([])
            for i in range(max_t):
                lists[row].append(-1)
    return lists


def drift_grouping(listss):
    drift_offsets = [0]
    for i in range(1, len(listss)):
        k = round(np.random.uniform(0, len(listss[i - 1][-1])))
        j = 0
        while j < len(listss[i - 1][-1]):
            if listss[i - 1][-1][(k + j) % len(listss[i - 1][-1])] == -1:
                break
            j = j + 1
        drift_offsets.append(j)
    return drift_offsets


# STAs = []
# STAs.append(STA(1, 3))
# STAs.append(STA(2, 2))
# STAs.append(STA(3, 2))
# STAs.append(STA(4, 10))
# STAs.append(STA(5, 9))
# STAs.append(STA(6, 3))
# STAs.append(STA(7, 2))
# STAs.append(STA(8, 3))
# STAs.append(STA(9, 3))
# STAs.append(STA(10, 6))


# subsets = inter_grouping(STAs)
# for subset in subsets:
#     list_a = intra_grouping(subset)
#     for i in list_a:
#         for j in i:
#             print(j)
#         print('x')
#     print('y')

# subsets = inter_grouping(STAs)
# intra_subsetss = []
# for subset in subsets:
#     list_a = intra_grouping(subset)
#     intra_subsetss.append(list_a)
# drift_offsets = drift_grouping(intra_subsetss)
# print(drift_offsets)
# for STA in STAs:
#     print(STA.first_TBTT)
