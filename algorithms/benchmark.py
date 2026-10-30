"""Consistent lightweight performance measurements."""
import time, tracemalloc
def measure(fn,*args,**kwargs):
    tracemalloc.start(); start=time.perf_counter()
    try: result=fn(*args,**kwargs)
    finally:
        elapsed=(time.perf_counter()-start)*1000
        current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    return {"result":result,"time_ms":round(elapsed,4),"memory_kb":round(peak/1024,2),
            "operations":result.get("operations",result.get("comparisons",0)),
            "nodes_visited":result.get("nodes_visited",None)}
