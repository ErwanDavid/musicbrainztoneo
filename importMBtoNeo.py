import psycopg2
from py2neo import Graph, Node, Relationship
from py2neo.bulk import create_nodes, create_relationships
import json
import logging


CONFIG = {}
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

with open("config.json", "r") as jsonfile:
    CONFIG = json.load(jsonfile)
CONFIG_PG = CONFIG['PG']

logging.warning("Config loaded")

conn = psycopg2.connect(database = CONFIG_PG['database'], 
                        user     = CONFIG_PG['user'],
                        host     = CONFIG_PG['host'],
                        password = CONFIG_PG['password'],
                        port     = CONFIG_PG['port'],)

neoDriver = Graph(CONFIG['Neo4j']['url'])
BATCH_S = CONFIG['Neo4j']['batch']

def splice_array(bigArray, start, step):
    stop = start + step
    ret_array = bigArray[start:stop]
    return ret_array

def getNodeData(sql):
    ret_arr = []
    with conn.cursor() as PGcur:
        PGcur.execute(sql)
        logging.warning('Number of objects fetched %s', PGcur.rowcount)
        row = PGcur.fetchone()
        while row is not None:
            ret_arr.append(row)
            row = PGcur.fetchone()
    return ret_arr


def getRelationsData(sql):
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

def createNode(ListNode, keyArrray, NodeLabel):
    tot_len = len(ListNode)
    cur_pos = 0
    while tot_len > 0:
        cur_arr = splice_array(ListNode, cur_pos, BATCH_S)
        logging.info('Batch insert node %s remaining %s', cur_pos, tot_len)
        cur_pos = cur_pos + BATCH_S
        tot_len = tot_len - BATCH_S
        create_nodes(neoDriver.auto(), cur_arr, labels={NodeLabel}, keys=keyArrray)

def createRelation(ListRel, RelLabel, srcLabel, srcField, dstLabel, dstField):
    tot_len = len(ListRel)
    cur_pos = 0
    rel_batch = int(BATCH_S / 10)
    while tot_len > 0:
        cur_arr = splice_array(ListRel, cur_pos, rel_batch)
        logging.info('Batch insert relation %s remaining %s', cur_pos, tot_len)
        cur_pos = cur_pos + rel_batch
        tot_len = tot_len - rel_batch
        start_k = (srcLabel, srcField)
        end_k = (dstLabel, dstField)
        create_relationships(neoDriver.auto(), cur_arr, RelLabel, start_node_key=start_k, end_node_key=end_k)



# Creating nodes
for node_data in CONFIG['nodes']:
    logging.warning('Working on %s', node_data['label'])
    logging.info('SQL %s', node_data['sql'])
    createNode(getNodeData(node_data['sql']), node_data['metadata'],node_data['label'])


# Creating relations
for rel_data in CONFIG['relations']:
    logging.warning('Working on %s - %s -> %s', rel_data['srcNode'], rel_data['label'], rel_data['dstNode'])
    logging.info('SQL %s', rel_data['sql'])
    createRelation(getRelationsData(rel_data['sql']), rel_data['label'], rel_data['srcNode'], rel_data['srcField'], rel_data['dstNode'], rel_data['dstField'])