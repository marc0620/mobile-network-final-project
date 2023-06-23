import math
import sympy as s

# Parameters I
r = 11.8 * 10**6  # Data rate: 11.8 Mbps
T_T = 100 * 10 ** (-6)  # The time duration to transmit 1 trigger frame
T_B = 100 * 10 ** (-6)  # The time duration to transmit 1 beacon
T_M = 100 * 10 ** (-6)  # The time duration to transmit 1 multiuser block ACK
m = 8  # Number of RA-RUs
OCW_min = 7  # OFDMA contention window
OCW_max = 31

# Parameters II
W = OCW_min + 1
bs = math.log2((OCW_max + 1) / (OCW_min + 1))  # The max number of backoff stage


def calculation_of_throughput(avg_num_STA):
    p_sb = s.Symbol("x")  # The probability of successful backoff
    p_ru = s.Symbol("y")  # The probability of choosing an idle RA-RU

    p_ru = (1 - p_sb / m) ** (avg_num_STA - 1)

    temp = 0  # The complicated sum
    for i in range(int(bs)):
        temp += 2**i * (1 - p_ru) ** i

    fn = p_sb - 2 / (1 + W / m + (1 - p_ru) * W / m * temp)

    p_sb = s.nsolve(fn, p_sb, 0.8)
    p_ru = (1 - p_sb / m) ** (avg_num_STA - 1)
    sol = []
    sol.append(p_sb)
    sol.append(p_ru)
    #
    throughput = avg_num_STA * p_sb * p_ru * r * T_D / (T_T + T_D + T_M)
    return throughput


#### Assumption
T_D = 15 * 10 ** (-3)


def max_one(a, b, c):
    if a > b and a > c:
        return 0

    elif b >= a and b > c:
        return 1

    elif c > a and c > b:
        return 2

    else:
        print(f"a:{a}, b:{b}, c{c}")


def optimal_avg_num_STA(number_of_STAs):
    old_left = 0
    old_right = number_of_STAs
    mid = number_of_STAs / 2
    right = (mid + old_right) / 2
    left = (mid + old_left) / 2
    theta = -1
    c = 0
    while True:
        # print(f"left:{left}, mid:{mid}, right{right}")
        max_temp = max_one(
            calculation_of_throughput(left),
            calculation_of_throughput(mid),
            calculation_of_throughput(right),
        )

        if max_temp == 0:
            # print(f"left:{left} theta:{calculation_of_throughput(left)}")

            temp = left
            right = (left + mid) / 2
            left = (old_left + left) / 2
            old_right = mid
            mid = temp
            if abs(calculation_of_throughput(left) - theta) < 10:
                return left
            theta = calculation_of_throughput(left)

        elif max_temp == 1:
            # print(f"mid:{mid} theta:{calculation_of_throughput(mid)}")
            old_right = right
            old_left = left
            right = (right + mid) / 2
            left = (mid + left) / 2
            c += 1
            if c > 7:
                return mid
            theta = calculation_of_throughput(mid)

        elif max_temp == 2:
            # print(f"right:{right} theta:{calculation_of_throughput(right)}")

            temp = right
            left = (right + mid) / 2
            right = (old_right + right) / 2

            old_left = mid
            mid = temp
            if abs(calculation_of_throughput(right) - theta) < 10:
                return right
            theta = calculation_of_throughput(right)

        else:
            print("BBQ")
            raise


def optimal_LI(original_LIs, optimal_avg_num_STA):
    sum = 0
    for i in range(len(original_LIs)):
        sum += original_LIs[i] ** (-1)
    # print(f"original average number or STAs: {sum}")

    for i in range(len(original_LIs)):
        original_LIs[i] = max(round(original_LIs[i] * sum / optimal_avg_num_STA), 1)

    sum = 0
    for i in range(len(original_LIs)):
        sum += original_LIs[i] ** (-1)
    # print(f"new average number of STAs: {sum}")

    return original_LIs
