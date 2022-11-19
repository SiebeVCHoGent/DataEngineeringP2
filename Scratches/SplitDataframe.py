import numpy as np
import pandas as pd

AANTAL_DELEN = 5

def split_dataframe_in_x(df, x):
    # split dataframe in x parts
    if x == 0 or x == None:
        raise ValueError("x moet groter zijn dan 0")
    if type(x) != int and type(x) != float:
        raise ValueError("x moet een integer of float zijn")

    if df is None:
        raise ValueError("df mag niet None zijn")

    df_split = np.array_split(df, x)
    return df_split

def save_dataframe_as_csv(name, df):
    # save dataframe as csv
    if df is None:
        raise ValueError("df mag niet None zijn")
    if name is None or name == "":
        raise ValueError("name mag niet None of empty zijn")
    



    df.to_csv(name, index=False)

#read kmos.csv
df = pd.read_csv("kmos.csv", sep=",")
#shuffle dataframe
df = df.sample(frac=1).reset_index(drop=True)
df = split_dataframe_in_x(df, AANTAL_DELEN)

i = 1
for df_part in df:
    save_dataframe_as_csv(f"kmos_{i}.csv", df_part)
    i += 1
