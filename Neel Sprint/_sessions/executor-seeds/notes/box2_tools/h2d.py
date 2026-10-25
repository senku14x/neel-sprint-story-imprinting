import torch, time, os
x = torch.empty(256*1024*1024, dtype=torch.float32).pin_memory(); y = torch.empty_like(x, device="cuda")
torch.cuda.synchronize()
best = 0
for _ in range(3):
    t=time.time(); y.copy_(x, non_blocking=True); torch.cuda.synchronize(); best=max(best, 1/(time.time()-t))
t=time.time()
for _ in range(2000): torch.cuda._sleep(1)
torch.cuda.synchronize(); lat=(time.time()-t)/2000*1e6
print(f"cpus {sorted(os.sched_getaffinity(0))[:2]}..: H2D pinned 1 GiB best {best:.1f} GiB/s; tiny-kernel launch+run {lat:.0f} us each")
