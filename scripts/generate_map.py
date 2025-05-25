import random
import pandas as pd
import numpy as np
import os

def generate_unique_pairs(n, rows, cols):
    all_coords = [(i, j) for i in range(rows) for j in range(cols)]
    return random.sample(all_coords, n)

def generate_map(n_terminating: int, n_amplifying: int, size: int):
    df = pd.DataFrame([['E'] * size for _ in range(size)])
    coords = generate_unique_pairs(n_terminating + n_amplifying, size, size)

    term_coords = coords[:n_terminating]
    amp_coords = coords[n_terminating:]

    for i, j in term_coords:
        df.iat[i, j] = 'T'

    for i, j in amp_coords:
        df.iat[i, j] = 'A'

    return df

dir_path = "./maps"
count = 0
# Iterate directory
for path in os.listdir(dir_path):
    # check if current path is a file
    if os.path.isfile(os.path.join(dir_path, path)):
        count += 1
size = int(input("Size: "))
n_terminating = int(input("Number of chain terminating tiles: "))
n_amplifying = int(input("Number of chain amplifying tiles: "))
if n_amplifying + n_terminating > size*size:
    raise Exception("Invalid input, number of tiles are insufficient")
generate_map(n_terminating,n_amplifying,size).to_csv(f'./maps/map{count+1}.csv', index=False)
