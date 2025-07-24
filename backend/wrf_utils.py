def extract_variable(nc, var_name: str, time_idx: int, level: int):
    if var_name == "Rainfall":
        return nc.RAINC[time_idx] + nc.RAINNC[time_idx]
    elif var_name == "Temperature":
        return nc.T[time_idx, level, :, :]
    elif var_name =="Humidity":
        return nc.RH[time_idx, level, :, :]
    else:
        raise ValueError("Unsupported variable")