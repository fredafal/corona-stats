# corona-stats
script to pull current format of RIVM covid-19 testing,hospitalizations, and mortality data.
info at https://www.rivm.nl/en
location of data is:
'https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_cumulatief.csv'

data is a full csv of all days since collection started of these numbers in the Netherlands, updated daily.
Numbers are daily totals on each metric by Municipality, so finding daily numbers requires subtracting them
from pervious day to compare the increase to.  

I've writen this to be able to change Municipality to get sub counts for, and to specify a difference window
to get counts or graphs for.
