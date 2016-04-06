import pylab as pl
import numpy as np

F = []
for filename in ['tau1.txt', 'tau2.txt', 'tau5.txt', 'tau50.txt']:
	f = open(filename)
	lines = f.readlines()
	f.close()
	taulines = filter(lambda s: 'tau' in s, lines)
	tau = [line.split()[1:] for line in taulines]
	tau = np.array(tau).astype('float')
	F.append( np.exp(-tau[-1,:]) )

#pl.imshow(np.log10(tau), aspect='auto', interpolation='nearest')
pl.figure()
pl.subplot(411)
pl.plot(F[0])
pl.text(100,0.6,'step=cellsize')
pl.subplot(412)
pl.plot(F[1])
pl.text(100,0.6,'step=cellsize/2')
pl.subplot(413)
pl.plot(F[2])
pl.text(100,0.6,'step=cellsize/5')
pl.subplot(414)
pl.plot(F[3])
pl.text(100,0.6,'step=cellsize/50')
pl.show()


