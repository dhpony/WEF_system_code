import numpy as np
import os
import shutil
import datetime
from Electricity_Grain_buy import elctricity_grain  
import pandas as pd

start = datetime.datetime.now()


print("\n------------------------------------------")
print("\tOPTIMIZATION BEGINS")
print("------------------------------------------")


schedule = elctricity_grain()


df = pd.DataFrame(schedule, columns=['Month', "Electricity_buy", "Needed water", "Cost_Electricity","Rice", "Corn", "Wheat"])
current_year = 2022
excel_file_path = f"results/Gurobi_results/{current_year}_Sichuan_buy.xlsx"
save_result_dir = "results/Gurobi_results"
if os.path.isfile(excel_file_path):
    os.remove(excel_file_path)

if not os.path.exists(save_result_dir):
    os.makedirs(save_result_dir)


df.to_excel(excel_file_path, index=False)
print(f"Schedule data has been saved to {excel_file_path}")
print("\n------------------------------------------")
print("\tOPTIMIZATION FINISHES")
print("------------------------------------------")
end = datetime.datetime.now()
print('耗时{}'.format(end - start))
