import psutil

def get_disk():
    return {
        part.mountpoint: {
            "fs": part.fstype,
            **psutil.disk_usage(part.mountpoint)._asdict()
        }
        for part in psutil.disk_partitions(all=False)
        if part.fstype
    }
