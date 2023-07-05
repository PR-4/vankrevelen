#======== COMANDOS INICIAIS ===========#

# Packages
library(ggplot2)
library(cowplot)

#Importação das planilhas
ALS2AL <- read.csv("~/Desktop/PR4/Achilles/Gráficos e Estatística/Poços_BR/csv/ALS2AL.csv", dec=",")

# Gráfico

Theme = theme_bw()+theme(axis.title.y=element_text(size=rel(1.0)), axis.text=element_text(size=rel(0.75)),axis.title.x=element_text(size=rel(1.0)), axis.text.x=element_text(vjust=0.75), plot.title=element_text(hjust=0.5)) 

A = ggplot(ALS2AL, aes(TR, Prof, group=Eq))
I= A+geom_point()+
  Theme+scale_y_reverse()+
  geom_path(aes(colour=Eq))+
  geom_point(aes(colour=Eq))+
  scale_colour_manual(values=c("royalblue4","darkslategray","tomato4","black"), breaks=c("a","b","c","z"), labels=c("Média", "Mínimo", "Mediana","Ro/Tmax"))+
  scale_x_continuous(limits=c(0.0,1.0))+
  labs(y="") +
  labs(x=expression(""))
I
