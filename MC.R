n_samples <- 1000
x <- runif(n_samples, min = 0, max = 1)
y <- runif(n_samples, min = 0, max = 1)

xx <- seq(0,1,by = 0.0001)
yy <- function(z) {
	out <- sqrt(1 - z^2)
}


i <- 1
x1 <- rep(0, length(x))
y1 <- rep(0, length(x))
xplot <- rep(0, length(x))
yplot <- rep(0, length(x))
while (i < length(x)){
	test <- sqrt(x[i]^2 + y[i]^2)
	if (test<=1) {
		x1[i] <- 1
		y1[i] <- 1

		xplot[i] <- x[i]
		yplot[i] <- y[i]
	}
	i  <- i + 1 

}
lapply(xplot, function(x) {x[x!=0]})
lapply(yplot, function(x) {x[x!=0]})
calc1 <- (sum(x1) + sum(y1))/(2*length(x))
calc2 <- abs((4*calc1 - pi)/pi)


error <- paste("Estimated pi = ", toString(round(4*calc1,2))," Error = ",toString(round(calc2*100,3)),"%")
nsam <- paste("Number of Samples = ", n_samples)
title <- paste("Approximating pi Using Monte Carlo Methods",nsam,error,sep = "\n") 
plot(xx,yy(xx),xlim = c(0,1), ylim = c(0,1), main = title, xlab = "X", ylab = "Y")
points(x,y)
points(xplot,yplot,col = "red")