from .portefeuille.referencing import build_dataset, create_rebalancing_pf
import matplotlib.pyplot as plt
import numpy as np

values = {
    "1rTPTPXH": 1600.0,
    "1rTPUST": 2600.0,
    "1rTCW8": 1000,
    "1rTESEH": 900.0
}
sum = np.sum(values.values())
for k in values:
    values[k] = values[k] / sum

dataset = build_dataset(list(values.keys()))
d, v = create_rebalancing_pf(dataset, values, 30)
plt.plot(d, v)
plt.show()