import numpy as np
import os
import shutil
import datetime
from Electricity_Grain_hydropower import elctricity_grain  # Electricity_Grain 更改来测试不同的买电场景
import pandas as pd

start = datetime.datetime.now()


print("\n------------------------------------------")
print("\tOPTIMIZATION BEGINS")
print("------------------------------------------")

# 调用模型优化函数
schedule = elctricity_grain()

# 将结果保存为DataFrame
df = pd.DataFrame(schedule, columns=['Month', 'Hydrogen Storage','Electricity to Hydrogen', 'Hydrogen to Electricity', 'Hydrogen from Electricity', 
                           "Electricity from Hydrogen", "Cost_Electricity","Variable Cost","Rice", "Corn", "Wheat"])
current_year = 2022
excel_file_path = f"results/Gurobi_results/{current_year}_Sichuan_hydrogen.xlsx"
save_result_dir = "results/Gurobi_results"
if os.path.isfile(excel_file_path):
    os.remove(excel_file_path)

# 如果目录不存在，则创建
if not os.path.exists(save_result_dir):
    os.makedirs(save_result_dir)

# Save the DataFrame to the Excel file
df.to_excel(excel_file_path, index=False)
print(f"Schedule data has been saved to {excel_file_path}")
print("\n------------------------------------------")
print("\tOPTIMIZATION FINISHES")
print("------------------------------------------")
end = datetime.datetime.now()
print('耗时{}'.format(end - start))
