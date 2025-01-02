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
BATCH_S = 20000

def splice_array(bigArray, start, step):
    stop = start + step
    ret_array = bigArray[start:stop]
    return ret_array

def getNodeData(sql):
    ret_arr = []
    with conn.cursor() as PGcur:
        print(sql)
        PGcur.execute(sql)
        print("The number of parts: ", PGcur.rowcount)
        row = PGcur.fetchone()
        while row is not None:
            ret_arr.append(row)
            row = PGcur.fetchone()
    return ret_arr


def getRelationsPART(sql):
    ret_arr = []
    all_rel =  getNodeData(sql)
    for rel in all_rel:
        newrel = []
        newrel.append(rel[0])
        map = {'comment' : rel[1]}
        newrel.append(map)
        newrel.append(rel[2])
        ret_arr.append(newrel)
    return ret_arr