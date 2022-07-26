P_k<-0.5
P_d<-0.6
lamM <-
lamT <- 
XE<-1/((P_k/lamT)*(lamM + lamT)*(1/P_d + 2)+1)
XS<-P_k*(lamM+lamT)*XE/(P_d*lamT)
XC<-P_k*(lamM+lamT)*XE/(lamT)
XI<-XC
E <- (XS/lamT + XC*20 + XI*20 + XE*11)/XE