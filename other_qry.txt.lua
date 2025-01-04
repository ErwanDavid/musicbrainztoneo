MATCH (metal_band:Band) <-[d]-> (p)
WHERE  metal_band.style contains 'metal'
and metal_band.year < 1990
RETURN metal_band, d, p
limit 50



MATCH (myArtist:Artist) <-[d]-> (p)
WHERE  myArtist.name contains 'Gaga'
RETURN myArtist, d, p
limit 50


MATCH (people:Artist)
RETURN people
LIMIT 5


MATCH (starrtInEighties:Artist)
WHERE starrtInEighties.begin_date_year >= 1980 AND starrtInEighties.begin_date_year < 1990
RETURN starrtInEighties.name as name, starrtInEighties.begin_date_year as begin_date_year
ORDER BY begin_date_year DESC

MATCH (starrtInEighties:Artist) -[d]-> (p:Band)
WHERE starrtInEighties.begin_date_year >= 1980 AND starrtInEighties.begin_date_year < 1990
RETURN starrtInEighties, d, p
limit 50


MATCH (myBand:Band) <-[d]- (p:Artist)
WHERE myBand.name = 'Gojira'
RETURN myBand, d, p
limit 50


MATCH (myBand:Band) <-[d]- (p:Artist)
WHERE myBand.name = 'Ultra Vomit'
RETURN myBand, d, p
limit 50

MATCH (myBand:Band) <-[d]- (p:Artist)
WHERE myBand.name = 'Metallica'
RETURN myBand, d, p
limit 50


MATCH (metal_band:Band) <-[d]- (p:Artist)
WHERE  metal_band.style contains 'metal'
RETURN metal_band, d, p
limit 500



MATCH (m:Group {name: 'In Flames'})<-[d]-(p:Artist)
RETURN m,d,p


MATCH  (source:Band {name: 'Ultra Vomit'}), (target:Band {name: 'Metallica'}),
p = shortestPath((source)-[*..15]-(target)) 
RETURN p

MATCH  (source:Band {name: 'Dark Tranquillity'}), (target:Band {name: 'In Flames'}),
p = shortestPath((source)-[*..25]-(target)) 
RETURN p


MATCH  (source:Artist {name: 'Madonna'}), (target:Artist {name: 'Elton John'}),
p = shortestPath((source)-[*..15]-(target)) 
RETURN p




MATCH  (source:Band {name: '$Judas Priest'}), (target:Band {name: 'name: Motörhead'}),
p = shortestPath((source)-[*..6]-(target)) 
RETURN p



MATCH  (source:Artist {name: 'Lady Gaga'}), (target:Artist {name: 'Ozzy Osbourne'}),
p = shortestPath((source)-[*..6]-(target)) 
RETURN p


MATCH  (source:Artist {name: 'Lady Gaga'}), (target:Band )
WHERE  target.style contains 'metal' ,
p = shortestPath((source)-[*..6]-(target)) 
RETURN p



## Adding spotify release 

-- select count(1) from r_track_artist;  --11 840 402 
-- select count(distinct track_id) from r_track_artist;  -- 8 741 672