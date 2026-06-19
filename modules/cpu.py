import psutil

def get_cpu():
    return {
        "physical": psutil.cpu_count(logical=False),
        "logical": psutil.cpu_count(logical=True),
        "freq": psutil.cpu_freq()._asdict(),
        "percent": psutil.cpu_percent(interval=0.5),
        "per_core_percent": psutil.cpu_percent(interval=0.5, percpu=True),
    }
