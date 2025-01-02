# Music Brainz to Neo4j

![example01](images/shortest_gojira-metallica.png "How Gojira and Metallica relates ?")
How Gojira and Metallica relates ?

See other data exploration at the end ! 

## Goals
https://musicbrainz.org/ is an open music encyclopedia that collects music metadata and makes it available to the public. The goal of this repo is to make available some of its data into a neo4j database abd then ask typical graph questions (shortest path ,...)


## Pre requesites

* Docker
* Python
* Git
* 70 GB (40GB database + few GB for neo4j graph)

### Brainz Docker

You need to make available the database. The musicbrainz propose multiple ways. I think the simpler is to use the docker way.

https://musicbrainz.org/doc/MusicBrainz_Database/Download

#### Clone the repo

```bash
 git clone https://github.com/metabrainz/musicbrainz-docker
 cd musicbrainz-docker
 admin/configure with alt-db-only-mirror
 ```
 The last line set up the docker to start only database related service (no web server)

#### Edit the compose file to publish the port to the host

We will use the database from the host server so you may replace the *expose* keyword by the *port*

See https://stackoverflow.com/questions/40801772/what-is-the-difference-between-ports-and-expose-in-docker-compose

    expose:             -->    port:
      - "5432"          -->        - "5432"

#### Build

```bash
docker-compose build
```

### Neo4j server

Using the default latest and no auth 
This binds two ports (7474 and 7687) for HTTP and Bolt access to the Neo4j API. 
A volume is bound to /data to allow the database to be persisted outside the container.


```bash
docker run -d --env=NEO4J_AUTH=none    --publish=7474:7474 --publish=7687:7687     --volume=$HOME/neo4j/data:/data     neo4j
```

### Testings

Either you may work on your local machine or using a remote server, the example below will use the 'localhost' as target for services. If you are runing the server on a remote machine, you may set up an *ssh tunnel* to make the services ports reachable locally. eg :

```bash
ssh -L 5432:localhost:5432  -L 7687:localhost:7687  -L 7474:localhost:7474  192.168.1.3
```

#### Postgresql
Use a database browser to chack database access. You can use an equivalent of the following jdbc url : 

jdbc:postgresql://localhost:5432/musicbrainz_db

The default password is 'musicbrainz'
![database](images/database01.png "Example of the schema in DBeaver")

#### Neo4j

Test the access using for example 
http://localhost:7474/browser/


## Importer

### Venv and module

```bash
python -m venv ./venv
. ./venv/bin/activate
pip install neo4j
pip install py2neopy2neo
pip install psycopg2-binary
```

### Neo4j indexes


CREATE INDEX IDXartiddb
FOR (n:Artist)
ON (n.iddb)

CREATE INDEX IDXbandiddb
FOR (n:Band)
ON (n.iddb)

CREATE INDEX IDXReliddb
FOR (n:Release)
ON (n.iddb)


### Runing the code

Note you may clean up the neo4j database first if it has been use for previsou testings 

MATCH (n)
WITH n LIMIT 100000
DETACH DELETE n
RETURN count(*);

Once the venv activated, you can run : 

```bash
time python -u ./importMusicbrainzToNeo.py
SELECT  a.grpid, a.grpname, a.grptype, grp_st,  ts.tag,  string_agg(a2.text, ',') FROM musicbrainz.v_grp_artist a
                    left join  musicbrainz.v_tag_artist_single ts on a.grpid = ts.artistid
                    left join artist_annotation aa on a.grpid = aa.artist
                    left join annotation a2 on aa.annotation = a2.id
                    where grptype = 2 or grptype = 5 or grptype = 6
                     group by a.grpid, a.grpname, a.grptype, grp_st, ts.tag
The number of parts:  171800
Batch insert 0 171800
Batch insert 10000 161800
....
Batch insert 160000 11800
Batch insert 170000 1800
select a.id, a."name", a.sort_name, a.begin_date_year, a."type", a.gender, a."comment", ts.tag , string_agg(a2.text, ',') as annotations from  musicbrainz.artist a
                        left join  musicbrainz.v_tag_artist_single ts on a.id = ts.artistid
                        left join artist_annotation aa on  a.id = aa.artist
                        left join annotation a2 on a2.id  = aa.annotation
                        where a."type" = 4 or a."type" = 1 or a."type" is null
                        group by a.id, a."name", a.sort_name, a.begin_date_year, a."type", a.gender, a."comment", ts.tag

The number of parts:  1893896
Batch insert 0 1893896
Batch insert 10000 1883896
....
Batch insert 1880000 13896
Batch insert 1890000 3896
SELECT distinct x.artistid, x.entity1_credit, x.grpid FROM musicbrainz.v_grp_artist x where x.grpid is not null order by x.artistid
The number of parts:  668822
Batch insert 0 668822
Batch insert 1000 667822
....
Batch insert 667000 1822
Batch insert 668000 822

real    1m30,029s
user    0m13,866s
sys     0m1,105s

```
### Testing



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



## Adding spotify release 

-- select count(1) from r_track_artist;  --11 840 402 
-- select count(distinct track_id) from r_track_artist;  -- 8 741 672