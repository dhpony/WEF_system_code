import gurobipy as gp
from gurobipy import GRB
from tabulate import tabulate
from datetime import datetime
import numpy as np
import math
def elctricity_grain(**kwargs):
#electricity：kwh，hydrogen：ton，crop：ton
    elc_grain = gp.Model()
    crop = list(range(0, 3))# rice, cron, wheat
    t_horizon01 = list(range(0, 13))
    t_horizon = list(range(0, 12))
    p_buy = [0.3442, 0.3442, 0.3442, 0.3442, 0.3442, 0.3442, 0.3442, 0.3442, 0.3442, 0.3442, 0.3442, 0.3442]
    efficient_crop = [[0.00, 0.00, 15.56], [0.00, 0.00, 57.78], [0.00, 0.00, 80.00], [71.03, 65.26, 75.56], [100.62, 65.26, 48.89], [93.82, 64.94, 0.00],
                      [93.82, 64.94, 0.00], [122.29, 24.80, 0.00], [122.29, 24.80, 15.56], [66.13, 0.00, 15.56], [0.00, 0.00, 15.56], [0.00, 0.00, 15.56]] 
    p_crop = [3100, 3046, 2950] #crop price
    efficient_electricity=0.95
    
    W_crop_t = elc_grain.addVars(t_horizon01, crop, lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="Water needed by crops")
    q_crop = elc_grain.addVars(crop, lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="quantity of crops")
    W_electricity_t = elc_grain.addVars(t_horizon01, lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="Water from electricity")
    revenue_crop = elc_grain.addVar(lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="revenue_crop")  
    electricity_cost_total = elc_grain.addVar(lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="electricity_cost_total")
    electricity_cost_t = elc_grain.addVars(t_horizon01, lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="electricity_cost_t")
    electricity_buy = elc_grain.addVars(t_horizon01, lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="electricity_buy")
    
    elc_grain.setObjective(electricity_cost_total - revenue_crop, GRB.MINIMIZE)
    elc_grain.addConstr(revenue_crop == gp.quicksum(q_crop[crop_kind] * 1 * p_crop[crop_kind] for crop_kind in crop), 'revenue_crop')
    elc_grain.addConstr(electricity_cost_total == gp.quicksum(electricity_cost_t[t] for t in t_horizon))

    for t in t_horizon:
        for crop_kind in crop:
            elc_grain.addConstr(W_crop_t[t, crop_kind] == 1 * efficient_crop[t][crop_kind] * q_crop[crop_kind])
        

   
    for t in t_horizon:
        elc_grain.addConstr(W_electricity_t[t] == efficient_electricity * electricity_buy[t])
        elc_grain.addConstr(W_electricity_t[t] == gp.quicksum(W_crop_t[t, crop_kind] for crop_kind in crop) )
        elc_grain.addConstr(electricity_cost_t[t] == electricity_buy[t] * 1 * p_buy[t])

        
    #increased yield to reach 2021
    elc_grain.addConstr(q_crop[0] == 311000)
    elc_grain.addConstr(q_crop[1] == 385000)
    elc_grain.addConstr(q_crop[2] == 0)



    elc_grain.Params.TimeLimit = 36000 
    elc_grain.setParam('OutputFlag', 0)
    elc_grain.Params.Threads = 32  
    elc_grain.Params.Method = 2  
    elc_grain.Params.Heuristics = 0.8  
    elc_grain.write('elc_grain_optimization.lp')


    elc_grain.optimize()
    if elc_grain.status == gp.GRB.OPTIMAL:
        print(f'Optimal objective value: {elc_grain.ObjVal}')
    Obj=[]
    Obj=elc_grain.ObjVal
    print("electricity_cost_total",electricity_cost_total)


    np.set_printoptions(threshold=np.inf)

    schedule = []
    for t in t_horizon:
        temp_day = t
        temp_cost_electricity = round(electricity_cost_t[t].X, 2)
        temp_water = round(W_electricity_t[t].X, 2)
        temp_electricity_buy = round(electricity_buy[t].X, 2)
        if t == 9:
           temp_rice = round(q_crop[0].X, 2)   
        else:
           temp_rice = 0
        if t == 8:
               temp_corn = round(q_crop[1].X, 2)
        else:
           temp_corn = 0          
        if t == 5:
               temp_wheat = round(q_crop[2].X, 2)
        else:
           temp_wheat = 0             
             
        schedule.append(
            [temp_day, temp_electricity_buy, temp_water, temp_cost_electricity, temp_rice, temp_corn, temp_wheat])
    schedule.append(
            [electricity_cost_total.X, revenue_crop.X, -Obj])
    if schedule:
        header_schedule = ['Month', "Electricity_buy", "Needed water", "Cost_Electricity","Rice", "Corn", "Wheat"]
    return schedule
