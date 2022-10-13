import numpy as np
import pandas as pd

AANTAL_DELEN = 5

def split_dataframe_in_x(df, x):
    # split dataframe in x parts
    df_split = np.array_split(df, x)
    return df_split

def save_dataframe_as_csv(name, df):
    # save dataframe as csv
    df.to_csv(name, index=False)

#read kmos.csv
df = pd.read_csv("kmos.csv", sep=",")
#shuffle dataframe
df = df.sample(frac=1).reset_index(drop=True)
df = split_dataframe_in_x(df, AANTAL_DELEN)

i = 1
for df_part in df:
    save_dataframe_as_csv(f"dataframes/kmos_{i}.csv", df_part)
    i += 1
