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
    p_out = [0.395, 0.395, 0.395, 0.395, 0.395, 0.14, 0.14, 0.14, 0.14, 0.14, 0.395, 0.395]
    pw_t = [156.1e8, 248.7e8, 196.4e8, 232e8, 291.7e8, 426.4e8, 468.5e8, 408.2e8, 333e8, 381.9e8, 287e8, 255e8]
    eta_e = 2.12e-5
    eta_f = 1.55e4  
    delta_t = 1
    efficient_crop = [[0.00, 0.00, 15.56], [0.00, 0.00, 57.78], [0.00, 0.00, 80.00], [71.03, 65.26, 75.56], [100.62, 65.26, 48.89], [93.82, 64.94, 0.00],
                      [93.82, 64.94, 0.00], [122.29, 24.80, 0.00], [122.29, 24.80, 15.56], [66.13, 0.00, 15.56], [0.00, 0.00, 15.56], [0.00, 0.00, 15.56]] 
    p_crop = [3100, 3046, 2950] # crop price
    
    efficient_electricity=0.95
    p_el =  0.41 #fixed cost of unit capacity
    p_fc = 1.5e4
    p_es = 5000
    pHes = 2000
    pel_t = elc_grain.addVars(t_horizon01, lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="Electricity to hydrogen")
    Hfc_t = elc_grain.addVars(t_horizon01, lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="Hydrogen to electricity")
    Hes_t = elc_grain.addVars(t_horizon01, lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="Hydrogen storage")
    Hh_t = elc_grain.addVars(t_horizon01, lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="Hydrogen from electricity")
    pfc_t = elc_grain.addVars(t_horizon01, lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="Electricity from hydrogen")
    W_crop_t = elc_grain.addVars(t_horizon01, crop, lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="Water needed by crops")
    q_crop = elc_grain.addVars(crop, lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="quantity of crops")
    W_electricity_t = elc_grain.addVars(t_horizon01, lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="Water from electricity")
    x_el = elc_grain.addVar(lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="Electricity to hydrogen capacity")
    x_fc = elc_grain.addVar(lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="Hydrogen to electricity capacity")
    x_es = elc_grain.addVar(lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="Hydrogen storage capacity") 
    revenue_crop = elc_grain.addVar(lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="revenue_crop") 
    variable_cost = elc_grain.addVar(lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="variable_cost")
    fix_cost_el = elc_grain.addVar(lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="Fix cost of electricity to hydrogen subsystem") 
    fix_cost_fc = elc_grain.addVar(lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="Fix cost of hydrogen to electricity subsystem")  
    fix_cost_es = elc_grain.addVar(lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="Fix cost of hydrogen storage subsystem")  
    fix_cost = elc_grain.addVar(lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="Total fix cost")    
    cost_electricity = elc_grain.addVars(t_horizon01, lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="Electricity cost") 
    variable_cost_t = elc_grain.addVars(t_horizon01, lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="Variable_cost") 
    electricity_cost_total = elc_grain.addVar(lb=0, ub=float("inf"), vtype=GRB.CONTINUOUS, name="Total electricity Cost")
    elc_grain.setObjective(electricity_cost_total - revenue_crop, GRB.MINIMIZE)
    elc_grain.addConstr(fix_cost == fix_cost_el + fix_cost_fc + fix_cost_es)
    elc_grain.addConstr(fix_cost_el == 1 * p_el * x_el)
    elc_grain.addConstr(fix_cost_fc == 1 * p_fc * x_fc)
    elc_grain.addConstr(fix_cost_es == 1 * p_es * x_es)
    elc_grain.addConstr(revenue_crop == gp.quicksum(q_crop[crop_kind] * 1 * p_crop[crop_kind] for crop_kind in crop), 'revenue_crop')
    elc_grain.addConstr(variable_cost == gp.quicksum(variable_cost_t[t] for t in t_horizon))
    elc_grain.addConstr(electricity_cost_total == gp.quicksum(cost_electricity[t] for t in t_horizon))
    for t in t_horizon:    
        elc_grain.addConstr(cost_electricity[t] == pel_t[t] * p_out[t])
        elc_grain.addConstr(variable_cost_t[t] == Hes_t[t] * 1 * pHes )
    for t in t_horizon:
        elc_grain.addConstr(pel_t[t] <= x_el)
        elc_grain.addConstr(pel_t[t] <= pw_t[t]) 

    for t in t_horizon:
        elc_grain.addConstr(pfc_t[t] == 1 * eta_f * Hfc_t[t] * delta_t)
        elc_grain.addConstr(Hfc_t[t] <= x_fc)

   

    for t in t_horizon:
        if t == 0:
            elc_grain.addConstr(Hh_t[t] == Hes_t[t] +  Hfc_t[t])
        else:
            elc_grain.addConstr(Hh_t[t] + Hes_t[t - 1] - Hfc_t[t] == Hes_t[t])

    for t in t_horizon:
        elc_grain.addConstr(Hh_t[t] == (1.45 * eta_e * pel_t[t]) * delta_t)

    for t in t_horizon:
        if t == 0:
            elc_grain.addConstr(Hfc_t[t] <= Hh_t[t])
        else:
            elc_grain.addConstr(Hfc_t[t] <= Hes_t[t - 1] + Hh_t[t])
    
    for t in t_horizon:
        elc_grain.addConstr(Hes_t[t] <= x_es)

    for t in t_horizon:
        for crop_kind in crop:
            elc_grain.addConstr(W_crop_t[t, crop_kind] == 1 * efficient_crop[t][crop_kind] * q_crop[crop_kind])
        

   
    for t in t_horizon:
        elc_grain.addConstr(W_electricity_t[t] == efficient_electricity * pfc_t[t])
        elc_grain.addConstr(W_electricity_t[t] == gp.quicksum( W_crop_t[t, crop_kind] for crop_kind in crop))
        
   

        
    #increased yield to reach 2021
    elc_grain.addConstr(q_crop[0] == 311000)
    elc_grain.addConstr(q_crop[1] == 385000)
    elc_grain.addConstr(q_crop[2] == 0)


   



    elc_grain.Params.TimeLimit = 36000  
       # elc_grain.resetParams()
    elc_grain.setParam('OutputFlag', 0)
    elc_grain.Params.Threads = 32  
    elc_grain.Params.Method = 2  
    elc_grain.Params.Heuristics = 0.8  
    # elc_grain.feasRelaxS(0, False, False, True)
    elc_grain.write('elc_grain_optimization.lp')
    # elc_grain.read('elc_grain_optimization.lp') 

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
        temp_Hes_t = round(Hes_t[t].X, 2)
        temp_pel_t = round(pel_t[t].X, 2)
        temp_Hfc_t = round(Hfc_t[t].X, 2)
        temp_Hh_t = round(Hh_t[t].X, 2)
        temp_pfc_t = round(pfc_t[t].X, 2)
        temp_cost_electricity = round(cost_electricity[t].X, 2)
        temp_variable_cost_t = round(variable_cost_t[t].X, 2)
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
            [temp_day, temp_Hes_t, temp_pel_t, temp_Hfc_t,
            temp_Hh_t, temp_pfc_t, temp_cost_electricity, temp_variable_cost_t, temp_rice, temp_corn, temp_wheat])

    schedule.append(
            [x_el.X, x_fc.X, x_es.X,fix_cost_el.X, fix_cost_fc.X, fix_cost_es.X,fix_cost.X, variable_cost.X, electricity_cost_total.X, revenue_crop.X, -Obj])

    if schedule:
        header_schedule = ['Month', 'Hydrogen Storage','Electricity to Hydrogen', 'Hydrogen to Electricity', 'Hydrogen from Electricity', 
                           "Electricity from Hydrogen", "Cost_Electricity","Variable Cost","Rice", "Corn", "Wheat"]
    return schedule
