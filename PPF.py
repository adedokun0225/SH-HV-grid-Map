import pandapower as pp
import pandas as pd

net = pp.create_empty_network()

df_bus = pd.read_excel("Substation\data_Pandapower.xlsx", sheet_name="bus", index_col = 0)
#strip column name to avoid issues with spaces
df_bus.columns = df_bus.columns.str.strip()
for i, row in df_bus.iterrows():
    bus_index = pp.create_bus(net,
                              vn_kv=row["vn_kv"],
                              name=row["name"],
                              type=row.get("type", "b"),
                              zone=row.get("zone", None),
                              in_service=row.get("in_service", True)
                              )
print(net.bus)
    
df_load = pd.read_excel("Substation\data_Pandapower.xlsx", sheet_name="load", index_col = 0)
for i in df_load.index:
    pp.create_load(net, **df_load.loc[i, :].to_dict())


df_sgen = pd.read_excel("Substation\data_Pandapower.xlsx", sheet_name="sgen", index_col = 0)
for i in df_sgen.index:
    pp.create_sgen(net, **df_sgen.loc[i, :].to_dict())
print(net.sgen)

df_ext_grid = pd.read_excel("Substation\data_Pandapower.xlsx", sheet_name="ext_grid", index_col = 0)
for i in df_ext_grid.index:
    pp.create_ext_grid(net, **df_ext_grid.loc[i, :].to_dict())

df_lines = pd.read_excel("Substation\data_Pandapower.xlsx", sheet_name="line", index_col = 0)
#strip column name to avoid issues with spaces
df_lines.columns = df_lines.columns.str.strip()
#create powerlines
for i, row in df_lines.iterrows():
    #clean lenght_km column
    df_lines["length_km"] = df_lines["length_km"].astype(str).str.replace(",",".").astype(float)
    length = float(str(row["length_km"]).replace(".", "").strip())

    pp.create_line_from_parameters(net, 
                                   from_bus=int(row["from_bus"]), 
                                   to_bus=int(row["to_bus"]),
                                   length_km=length, 
                                   r_ohm_per_km=row["r_ohm_per_km"], 
                                   x_ohm_per_km=row["x_ohm_per_km"], 
                                   c_nf_per_km=row["c_nf_per_km"],
                                   g_us_per_km=row["g_us_per_km"],
                                   max_i_ka=row["max_i_ka"], 
                                   name = row["name"],
                                   type=row["type"],
                                   df=row.get("df", 1),
                                   parallel=row.get("parallel", 1),
                                   in_service=row.get("in_service", True)
                                   )
'''df_trafo = pd.read_excel("Substation\data_Pandapower.xlsx", sheet_name="trafo", index_col = 0)
for i,row in df_trafo.iterrows():
    pp.create_transformer_from_parameters(net, 
                                          hv_bus=int(row["hv_bus"]),
                                          lv_bus=int(row["lv_bus"]),
                                          sn_mva=row["sn_mva"],
                                          vn_hv_kv=row["vn_hv_kv"],
                                          vn_lv_kv=row["vn_lv_kv"],
                                          vk_percent=row["vk_percent"],
                                          vkr_percent=row["vkr_percent"],
                                          pfe_kw=row["pfe_kw"],
                                          i0_percent=row["i0_percent"],
                                          shift_degree=row["shift_degree"],
                                          tap_side=row["tap_side"],
                                          tap_neutral=row["tap_neutral"],
                                          tap_min=row["tap_min"],
                                          tap_max=row["tap_max"],
                                          tap_step_percent=row["tap_step_percent"],
                                          tap_step_degree=row["tap_step_degree"],
                                          tap_pos=row["tap_pos"],
                                          tap_phase_shifter=row["tap_phase_shifter"],
                                          parallel=row["parallel"],
                                          df=row["df"],
                                          in_service=row["in_service"],
                                          name=row["name"]
                                          )'''
pp.runpp(net)
pp.diagnostic(net)

try:
    pp.runpp(net)
except pp.LoadflowNotConverged:
    print("Power flow did not converge. Running diagnostic:")
    pp.diagnostic(net)