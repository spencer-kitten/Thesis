#100
a = c(38,21,14,4,2,6,0,1,3,3)
#200
b = c(88,45,30,14,6,6,4,2,1,0)

xx = seq(1,10)
P = 0.7*0.6310111
# can .631 be calculated?
c = sum(b)*(1-(1-P)^xx)

#plot(c)
plot(cumsum(b),xlim = c(0,10),ylim = c(0,200))
lines(c)

