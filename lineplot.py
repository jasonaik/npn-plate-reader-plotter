import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
import datetime
import os

construct_names=[
            "Empty Vector Control", 
            "Pore Only Control",
            "ICR211+192",
            "ICR212+192",
            "ICR213+192",
            "ICR214+192",
            "ICR215+192",
            "ICR216+192",
            "ICR235+196",
            "ICR236+196",
            "ICR237+196",
            "ICR238+196",
            "ICR239+196",
            "ICR240+196",
        ]

df = pd.read_csv("restructured_light_AF_mapping.csv")