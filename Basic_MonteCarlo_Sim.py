"""
Actvity: 10k investment, with growth by a random annual return ¬Norm(0.07,0.15). 
Simulate what happens over 10 years across 1,000 different futures.
"""
import numpy as np

# Simulate one path 


def simulate_one_path():
    current_value = 10000.0
    Portfolio_values = [current_value]
    for i in range(10):
        random_return = np.random.normal(0.07,0.15)
        current_value = current_value * (1 + random_return )
        Portfolio_values.append(current_value)

    return Portfolio_values

# Run it 1,000 times
final_values = []
for i in range(1000):
    final = simulate_one_path()[-1]
    final_values.append(final)

# or final_values = [simulate_one_path()[-1] for _ in range(1000)]

# Summary stats

median = np.median(final_values)
tenth_percentile = np.percentile(final_values , 10)
ninetieth_percentile = np.percentile(final_values , 90)
count = sum(value > 20000 for value in final_values)
percentage = count / len(final_values) *100
print(f"Median final value: £{median:,.0f}")
print(f"10th percentile:    £{tenth_percentile:,.0f}")
print(f"90th percentile:    £{ninetieth_percentile:,.0f}")
print(f"Chance of > £20,000: {percentage:.2f}%")




