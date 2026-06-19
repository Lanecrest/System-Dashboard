import psutil, heapq

def get_memory():
    vm = psutil.virtual_memory()

    def iter_procs():
            for proc in psutil.process_iter(attrs=['name', 'memory_info', 'memory_percent']):
                try:
                    if proc.info['memory_info'] is not None:
                        payload = proc.info.copy()
                        payload['memory_info'] = proc.info['memory_info']._asdict()
                        yield payload
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

    top_10 = heapq.nlargest(
        10, 
        iter_procs(), 
        key=lambda p: p['memory_percent'] if p['memory_percent'] is not None else 0
    )

    return {
        "total": vm.total,
        "available": vm.available,
        "used": vm.total - vm.available,
        "percent": vm.percent,
        "per_process": top_10
    }
