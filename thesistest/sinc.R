x <- seq(-10,10,by = 0.01)
index <- 10
multi <- 1.9
sensy <- 25
y <- function(xx) {abs(sin(multi*xx)/xx) + abs(sin(multi*xx + index)/(xx + index)) + abs(sin(multi*xx - index)/(xx - index))}
z<-log(y(x))
z[1001] <- 0
z[1000 - index*100 + 1]<-0
z[1000 + index*100 + 1] <- 0
z<-z[sensy:(2000-sensy)]
polar.plot(z)