# https://medium.com/critical-powers/comparison-of-wbalance-algorithms-8838173e2c15
# original code fom pizero as for the logic
import numpy as np


def tau_w_prime_balance(delta_cp):
    return 546 * np.exp(-0.01 * delta_cp) + 316


def init_w_prime_balance(cp, w_prime, algorithm="WATERWORTH"):
    initial = {"w_prime_balance": w_prime}

    if algorithm == "WATERWORTH":
        initial.update(
            {
                "w_prime_power_sum": 0,
                "w_prime_power_count": 0,
                "w_prime_t": 0,
                "w_prime_sum": 0,
                "tau": tau_w_prime_balance(cp),
            }
        )
    return initial


def w_prime_balance_differential(power, cp, w_prime, prev_w_prime_balance):
    if power < cp:
        # recovery
        return prev_w_prime_balance + (
            (cp - power) * (w_prime - prev_w_prime_balance) / w_prime
        )
    else:
        # consume
        return prev_w_prime_balance + cp - power


def w_prime_balance_waterworth(power, cp, w_prime, interval, values):
    power_cp_diff = power - cp

    power_sum = values["w_prime_power_sum"]
    power_count = values["w_prime_power_count"]
    w_prime_sum = values["w_prime_sum"]
    w_prime_t = values["w_prime_t"] + interval
    tau = values["tau"]

    if power_cp_diff < 0:
        power_sum = power_sum + power
        power_count = power_count + 1
        power_mean_under_cp = power_sum / power_count
        tau = tau_w_prime_balance(cp - power_mean_under_cp)

    w_prime_sum = w_prime_sum + max(0, power_cp_diff) * np.exp(w_prime_t / tau)

    w_prime_balance = w_prime - w_prime_sum * np.exp(-w_prime_t / tau)

    return {
        "w_prime_balance": w_prime_balance,
        # values for running sum logic
        "w_prime_power_sum": power_sum,
        "w_prime_power_count": power_count,
        "w_prime_sum": w_prime_sum,
        "w_prime_t": w_prime_t,
        "tau": tau,
    }


def calc_w_prime_balance(
    power, cp, w_prime, values, algorithm="WATERWORTH", invertal=1
):
    if algorithm == "WATERWORTH":
        data = w_prime_balance_waterworth(power, cp, w_prime, invertal, values)
    # Differential algorithm
    elif algorithm == "DIFFERENTIAL":
        prev_w_prime_balance = values["w_prime_balance"]
        w_prime_balance = w_prime_balance_differential(
            power, cp, w_prime, prev_w_prime_balance
        )

        data = {"w_prime_balance": w_prime_balance}
    else:
        raise ValueError(f"Unsupported algorithm {algorithm}")

    data.update(
        {
            "w_prime_balance_normalized": round(
                data["w_prime_balance"] / w_prime * 100, 1
            )
        }
    )

    return data
