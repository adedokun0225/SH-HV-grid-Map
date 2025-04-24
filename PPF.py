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
#print(df_bus.columns)
    
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
print(net.ext_grid)
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
print(net.line)
df_trafo = pd.read_excel("Substation\data_Pandapower.xlsx", sheet_name="trafo", index_col = 0)
for i in df_trafo.index:
    #pp.create_transformer(net, **df_trafo.loc[i, :])
    #pp.create_transformer(net, hv_bus=df_trafo.at[1, "hv_bus"], lv_bus=df_trafo.at[i, "lv_bus"], std_type=df_trafo.at[i, "std_type"])
    hv = df_trafo.at[i, "hv_bus"]
    lv = df_trafo.at[i, "lv_bus"]

    if hv in net.bus.index and lv in net.bus.index:
        try:
            pp.create_transformer(net, **df_trafo.loc[i].to_dict())
        except Exception as e:
            print(f" caution Error at row {i}: {e}")
    else:
        print(f"Skipping row {i}: Bus {hv} or {lv} not in net.bus")
#print(net.trafo)
 
