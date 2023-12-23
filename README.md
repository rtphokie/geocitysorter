# geocitysorter

Selecting the right set of cities to include on a map can be challenging. The ideal map should have enough cities
labeled to provide sufficient context to the reader to get across the overall purpose of the map, but not so many to
create visual clutter and lose all meaning.

Picking just the most populated cities to include can create a mess too. Metropolitan areas are usually made up of many
cities, often large themselves. Desert or mountainous areas also tend to have smaller
populations creating large gaps

<img src="https://raw.githubusercontent.com/rtphokie/geocitysorter/main/images/Texas_pop.png" alt="drawing" width="300"/>
<img src="https://raw.githubusercontent.com/rtphokie/geocitysorter/main/images/West Virginia_pop.png" alt="drawing" width="300"/>

The most meaningful maps are labeled with a set of recognizable cities while avoiding
large gaps between them.

<img src="https://raw.githubusercontent.com/rtphokie/geocitysorter/main/images/Texas_geopop.png" alt="drawing" width="300"/>
<img src="https://raw.githubusercontent.com/rtphokie/geocitysorter/main/images/West Virginia_geopop.png" alt="drawing" width="300"/>

This package tries to create that balance by ordering a dataframe with (at minimum) columns
with the city, state, longitude, latitude and a column for the weighted value of that 
city (population by default)

Options allow you to force the most populous city, capital, or an arbitrary list of cities
to be at the top of the resulting dataframe.

It orders whatever points you give it, including across multiple states

<img src="https://raw.githubusercontent.com/rtphokie/geocitysorter/main/images/Texas_Oklahoma_geopop.png" alt="drawing" width="300"/>

## How it works

The algorithm sorts a passed (GeoPandas or Pandas) dataframe sorted by column which
indicates the row's weight (e.g. population). Any cities that must be at the top
(largest city, capital cities, or an arbitrary list) are moved to the resulting
dataframe.

The most relevant (largest population) city in the gaps between cities are 
iteratively added to the bottom of the resulting dataframe until all cities have 
been ordered.

This is done by finding the smallest distance between cities that yet to be included
in the resulting dataframe to those that have. Cities are grouped by those distances
by creating logical rings and the largest city in the outer most (or inner, see options
below) set of rings is selected and moved to the bottom of the resulting dataframe.

The result dataframe is ordered by a balance of population and geographic relevant.

Labeling a map with cities at the top of the list should produce more "I get it"
reactions while cities at the bottom produce "I've never heard of that city" or "why
did thy pick that city?"


### Syntax

```
def order_geo_dataframe(df_orig, rings=5, order='furthest', 
                        valuecolumn='population', 
                        starting_lat=None, starting_lng=None, 
                        verbose=False, first='both', citylist=[]):
```

#### Options

df
: Pandas (or GeoPandas) dataframe containing at minimum: city, state, latitude, longitude columns
  and a weighted value column

starting_lat, starting_lng
: coordinates to start from, most useful in finding the largest city near a set
of coordinates.  Defaults to 0,0


rings
: number of rings to logically draw around each city when generalizing distance between a given city and
                    the others that have already been ordered as more "relevant".  (default: 5)
                    fewer rings favor larger cities.  Default: 3

order
:how the next point is selected, default: furthest:
* _furthest_: the most populous city in the furthest ring, useful for intelligently ordering
                              points on a map by population 
* _nearest_: the most populous city in the nearest ring, useful for finding the most relevant
                             point "near" a given point such as the largest city nearby

citylist
: list of city names to force to order first

first 
: include the _largest_ city, _capital_ city, or _both_ first
: _capito    :param first:   capital: order state capitals first
                    largest: order the largest city first (default)
