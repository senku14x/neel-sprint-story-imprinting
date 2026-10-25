import numpy as np, math
rng=np.random.default_rng(0)
N=2_000_000
# exact closed forms
t2=4.302652729911275; t4=2.7764451051977987
print('t2*sqrt2=%.3f t4*sqrt2=%.3f z*sqrt2=%.3f'%(t2*2**.5,t4*2**.5,1.959964*2**.5))
print('1 vs 3-seed mean: t2*sqrt(4/3)=%.3f t4*sqrt(4/3)=%.3f z=%.3f'%(t2*(4/3)**.5,t4*(4/3)**.5,1.959964*(4/3)**.5))
print('2 seeds vs 3-seed mean: t2*sqrt(1/2+1/3)=%.3f t4=%.3f'%(t2*(5/6)**.5,t4*(5/6)**.5))
# sigma CI, df=2 closed form chi2 quantiles
lo2=math.sqrt(2/(-2*math.log(0.025))); hi2=math.sqrt(2/(-2*math.log(0.975)))
print('sigma CI df2 [%.3f, %.3f]'%(lo2,hi2))
# df4 by MC
c4=rng.chisquare(4,N); q=np.quantile(c4,[0.025,0.975]); print('chi2_4 q',q,' sigma CI df4 [%.3f, %.3f]'%(math.sqrt(4/q[1]),math.sqrt(4/q[0])))
# MC FPR of the spec's rule "|d| > 2 s" where s from 3 seeds of one condition (true sigma=1), d = diff of two new single seeds under null
for k,lab in [(1,'1v1'),(3,'1 vs mean of 3 (incl. ref)')]:
    pass
sig=1.0
X=rng.normal(0,sig,(N,3)); s=X.std(axis=1,ddof=1)
d11=rng.normal(0,sig,N)-rng.normal(0,sig,N)
print('FPR |d|>2s, 1v1, s from 3 seeds (2df): %.3f'%np.mean(np.abs(d11)>2*s))
# 1 vs 3-seed mean where mean uses the same 3 seeds that give s
d13=rng.normal(0,sig,N)-X.mean(axis=1)
print('FPR |d|>2s, new single vs mean of the 3 seeds: %.3f'%np.mean(np.abs(d13)>2*s))
# pooled over A and B (4 df)
Y=rng.normal(0,sig,(N,3)); sp=np.sqrt((s**2+Y.std(axis=1,ddof=1)**2)/2)
print('FPR |d|>2 s_pooled, 1v1: %.3f'%np.mean(np.abs(d11)>2*sp))
print('FPR |d|>2 sigma known, 1v1: %.3f; 1 vs 3-mean: %.3f'%(np.mean(np.abs(d11)>2), np.mean(np.abs(d13)>2)))
# check proposed thresholds give 5%
print('FPR proposed 6.09 s: %.4f; 3.93 s_pooled: %.4f'%(np.mean(np.abs(d11)>t2*2**.5*s),np.mean(np.abs(d11)>t4*2**.5*sp)))
# power: true diff Delta in units of sigma
for D in (1,2,3,4):
    d=d11+D
    print('true Delta=%dσ: P(|d|>6.09s)=%.2f P(|d|>3.93sp)=%.2f P(|d|>2s)=%.2f'%(D,np.mean(np.abs(d)>t2*2**.5*s),np.mean(np.abs(d)>t4*2**.5*sp),np.mean(np.abs(d)>2*s)))
