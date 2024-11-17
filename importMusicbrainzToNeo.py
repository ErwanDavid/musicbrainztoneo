import psycopg2
from py2neo import Graph, Node, Relationship
from py2neo.bulk import create_nodes, create_relationships

# Connectioons
conn = psycopg2.connect(database = "musicbrainz_db", 
                        user = "musicbrainz", 
                        host= 'localhost',
                        password = "musicbrainz",
                        port = 5432)

neoDriver = Graph("neo4j://localhost:7687")
BATCH_S = 10000

def splice_array(bigArray, start, step):
    stop = start + step
    ret_array = bigArray[start:stop]
    return ret_array

def sqlToArr(sql):
    arr = []
    with conn.cursor() as PGcur:
        print(sql)
        PGcur.execute(sql)
        print("The number of parts: ", PGcur.rowcount)
        row = PGcur.fetchone()
        while row is not None:
            arr.append(row)
            row = PGcur.fetchone()
    return arr

def getGroups():
    return sqlToArr("""SELECT  a.grpid, a.grpname, a.grptype, grp_st,  ts.tag,  string_agg(a2.text, ',') FROM musicbrainz.v_grp_artist a
                    left join  musicbrainz.v_tag_artist_single ts on a.grpid = ts.artistid 
                    left join artist_annotation aa on a.grpid = aa.artist 
                    left join annotation a2 on aa.annotation = a2.id 
                    where grptype = 2 or grptype = 5 or grptype = 6 
                     group by a.grpid, a.grpname, a.grptype, grp_st, ts.tag""")
   
def getArtists():
    return sqlToArr("""select a.id, a."name", a.sort_name, a.begin_date_year, a."type", a.gender, a."comment", ts.tag , string_agg(a2.text, ',') as annotations from  musicbrainz.artist a  
                        left join  musicbrainz.v_tag_artist_single ts on a.id = ts.artistid 
                        left join artist_annotation aa on  a.id = aa.artist
                        left join annotation a2 on a2.id  = aa.annotation 
                        where a."type" = 4 or a."type" = 1 or a."type" is null
                        group by a.id, a."name", a.sort_name, a.begin_date_year, a."type", a.gender, a."comment", ts.tag
                    """)

def getRelations():
    ret_arr = []
    all_rel =  sqlToArr('SELECT distinct x.artistid, x.entity1_credit, x.grpid FROM musicbrainz.v_grp_artist x where x.grpid is not null order by x.artistid')
    for rel in all_rel:
        newrel = []
        newrel.append(rel[0])
        map = {'comment' : rel[1]}
        newrel.append(map)
        newrel.append(rel[2])
        ret_arr.append(newrel)
    return ret_arr

def createGroups(ListGrp):
    keys = ["iddb", "name", "type", "year", "style", "annotations"]
    tot_len = len(ListGrp)
    cur_pos = 0
    while tot_len > 0:
        cur_arr = splice_array(ListGrp, cur_pos, BATCH_S)
        print("Batch insert", cur_pos,tot_len)
        cur_pos = cur_pos + BATCH_S
        tot_len = tot_len - BATCH_S
        create_nodes(neoDriver.auto(), cur_arr, labels={"Band"}, keys=keys)

def createArtist(ListArtist):
    keys = ["iddb", "name", "sort_name", "begin_date_year", "type", "gender", "comment", "style", "annotations"]
    tot_len = len(ListArtist)
    cur_pos = 0
    while tot_len > 0:
        cur_arr = splice_array(ListArtist, cur_pos, BATCH_S)
        print("Batch insert", cur_pos,tot_len)
        cur_pos = cur_pos + BATCH_S
        tot_len = tot_len - BATCH_S
        create_nodes(neoDriver.auto(), cur_arr, labels={"Artist"}, keys=keys)

def createRelation(ListRel):
    tot_len = len(ListRel)
    cur_pos = 0
    rel_batch = int(BATCH_S / 10)
    while tot_len > 0:
        cur_arr = splice_array(ListRel, cur_pos, rel_batch)
        print("Batch insert", cur_pos,tot_len)
        cur_pos = cur_pos + rel_batch
        tot_len = tot_len - rel_batch
        create_relationships(neoDriver.auto(), cur_arr, "PART", start_node_key=("Artist", "iddb"), end_node_key=("Band", "iddb"))


createGroups(getGroups())
createArtist(getArtists())
createRelation(getRelations())





