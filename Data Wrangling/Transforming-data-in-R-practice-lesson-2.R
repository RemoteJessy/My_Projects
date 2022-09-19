####### PLEASE NOTE: FOR THIS, I USED ANIME DATASET BECAUSE CRUISE SHIP DATASET IS NOT FUNCTIONING AND NO DATA IS SHOWING UP. #######

### Install and import rcompanion.
library("rcompanion")
library("IDPmisc")

### Import Dataset
anime <- read.csv("C:/Users/lzela/Downloads/anime.csv")
View(anime)

### use the plotNormalHistogram function on the score variable:
plotNormalHistogram(anime$score)
# This looks normally distributed. Let's move on to positvely skewed data below)

### Transforming Positively Skewed Data
plotNormalHistogram(anime$scored_by)
### Using sqrt() to see if this helps.
anime$scored_bySQRT <- sqrt(anime$scored_by)
### let's try with log to see if it gets better
### Using log
anime$scored_byLOG <- log(anime$scored_by)
### Let's do histogram again to see
plotNormalHistogram(anime$scored_byLOG)
### Removing Infinite Values
library("IDPmisc")
anime2 <- NaRV.omit(anime)
### let's histogram again
plotNormalHistogram(anime2$scored_byLOG)


### trans. neg data
### Transforming Negatively Skewed Data
### let's try Squaring the Variable
anime$aired_from_yearSQ <- anime$aired_from_year * anime$aired_from_year
### let's plot the histogram
plotNormalHistogram(anime$aired_from_yearSQ)
### That looks a bit better, but not amazing. No where near normally distributed.
### Cubing the Variable
anime$aired_from_yearCUBE <- anime$aired_from_year ^ 3
#### histogram again to check
plotNormalHistogram(anime$aired_from_yearCUBE)
### Overall, that definitely looks like the best option, so you can settle for that. Even though it is not perfect, you are out of options.

#### Tukey's Ladder of Power Transformation
### histogram
plotNormalHistogram(anime$scored_by)
#### using tukey
anime$scored_byTUK <- transformTukey(anime$scored_by, plotit=FALSE)
#### histogram to see change
plotNormalHistogram(anime$scored_byTUK)
### remove the infinite values
anime2 <- NaRV.omit(anime)
### try again this time with inf. values 
plotNormalHistogram(anime$scored_byTUK)

