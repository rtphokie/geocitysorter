# geocitysorter

Assists in preparing a geodataframe containing points for plotting on a map by 
sorting them geographic relevance.

Finding the right set of cities to label on a map to make it meaningful can be 
challenging. While this package doesn't address finding the right balance  
between geographically relevant and overcrowded, that's more of an aesthetic 
decision, it does sort geopandas data frame by population and 

## Methodology

The algorithm sorts a passed geopandas dataframe sorted by column which 
indicates the row's weight (e.g. city or region population), moving the row
with the greatest weight to a new dataframe.

Distances to that point are calculated for each of the remaining rows and
the point with the largest weight that is the furthest away is added to the bottom
of the new dataframe.

This continues until all rows have been moved to the new dataframe, now
sorted by geographic relevance.