# Part 3 in R
# Create Stacked Bar Chart
#importing library
library("ggplot2")
#import data
L3Part3 <- read.csv("C:/Users/lzela/Desktop/data_wrangling/Lesson 4 files/L3Part3.csv")
#view data
View(L3Part3)
#create a stacked bar chart using either Python or R.
#using R to create stacked bar chart.
ggplot(data=L3Part3) +
  +     geom_bar(mapping = aes(x = Car, fill=Location)) + 
  +     ggtitle("Car Brands by Location") +
  +     xlab("Car Brands") +
  +     ylab("Frequency") 
