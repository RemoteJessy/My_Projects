# Part 3 in R

#importing library
library("ggplot2")

#import data
L3Part3 <- read.csv("C:/Users/lzela/Desktop/data_wrangling/Lesson 4 files/L3Part3.csv")

#view data
View(L3Part3)

#Question: Create a stacked bar chart using either Python or R.
ggplot(data=L3Part3) +
  geom_bar(mapping = aes(x =Car, fill=Location)) + 
  ggtitle("Car Brands by Location") +
  xlab("Car Brands") +
  ylab("Frequency") 

#Answer: More Jaguars overall and most cars in sample from Southwest
