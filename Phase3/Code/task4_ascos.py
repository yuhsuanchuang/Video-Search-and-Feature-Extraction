#    Copyright (C) 2004-2010 by
#    Yu-hsuan Chuang <ychuang8@asu.edu>
#    Hung-Hsuan Chen <hhchen@psu.edu>
#    All rights reserved.
#    BSD license.
#    NetworkX:http://networkx.lanl.gov/.
import numpy as np
import time
import networkx as nx
import operator
import copy
import math
import utils

# graph file
global INPUT_FILE, INPUT_PATH
INPUT_PATH = "../Input/"
INPUT_FILE = "in_file.gspc"

global excluded_nodes_set

global first_seed_video, first_seed_frame, \
    second_seed_video, second_seed_frame, \
    third_seed_video, third_seed_frame

def creatGraph():
    #creat a new graph
    G = nx.DiGraph()
    #get the database size
    (row, column) = database.shape

    for r in range(row):
        #add edge weight(similarity) btw query node and object nodes
        for c in range(column):
            if (c % 5) == 4:
                q_video_number = database[r, c - 4]
                q_frame_number = database[r, c - 3]
                o_video_number = database[r, c - 2]
                o_frame_number = database[r, c - 1]
                weight = database[r, c]
                # add nodes
                #G.add_node((int(q_video_number), int(q_frame_number)))
                # add edge weight
                G.add_edge((int(q_video_number),int(q_frame_number)), (int(o_video_number),int(o_frame_number)), weight=weight)

    ASCOS = ascos(G, is_weighted=True)
    global sorted_ASCOS
    sorted_ASCOS = sorted(ASCOS.items(), key=operator.itemgetter(1), reverse=True)

def ascos(G, c=0.9, alpha= 0.85, max_iter=100, is_weighted=False, remove_neighbors=False, remove_self=False, dump_process=False):

    if type(G) == nx.MultiGraph or type(G) == nx.MultiDiGraph:
        raise Exception("ascos() not defined for graphs with multiedges.")

    node_ids = G.nodes()

    node_id_lookup_tbl = { }
    for i, n in enumerate(node_ids):
        node_id_lookup_tbl[n] = i

    nb_ids = [G.successors(n) for n in node_ids]

    nbs = [ ]
    for nb_id in nb_ids:
        nbs.append([node_id_lookup_tbl[n] for n in nb_id])
    del(node_id_lookup_tbl)

    n = G.number_of_nodes()
    sim = np.eye(n)

    sim_old = np.zeros(shape = (n, n))
    for iter_ctr in range(max_iter):
        print iter_ctr
        if _is_converge(sim, sim_old, n, n):
            break
        sim_old = copy.deepcopy(sim)
        for i in range(n):
            if dump_process:
                print iter_ctr, ':', i, '/', n
            w_i = G.out_degree(weight='weight')[node_ids[i]]
            for j in range(n):
                if not is_weighted:
                    if i == j:
                        continue
                    s_ij = 0.0
                    for n_i in nbs[i]:
                        s_ij += sim_old[n_i, j]
                    sim[i, j] = c * s_ij / len(nbs[i]) if len(nbs[i]) > 0 else 0
                else:
                    if i == j:
                        continue
                    s_ij = 0.0
                    for n_i in nbs[i]:
                        w_ik = G[node_ids[i]][node_ids[n_i]]['weight'] if 'weight' in G[node_ids[i]][node_ids[n_i]] else 1
                        s_ij += float(w_ik) * (1 - math.exp(-w_ik)) * sim_old[n_i, j]

                    sim[i, j] = alpha * (c * s_ij / w_i) if w_i > 0 else 0
                    if node_ids[j] == (first_seed_video, first_seed_frame) or \
                                    node_ids[j] == (second_seed_video, second_seed_frame) or \
                                    node_ids[j] == (third_seed_video, third_seed_frame):
                        if not sim[i, j] == 0:
                            sim[i, j] += (1 - alpha) * 0.33

    if remove_self:
        for i in range(n):
            sim[i,i] = 0

    if remove_neighbors:
        for i in range(n):
            for j in nbs[i]:
                sim[i,j] = 0

    ASCOS = {}
    for nodej in range(len(node_ids)):
        totalsum = 0;
        for nodei in range(len(node_ids)):
            if nodei != nodej:
                totalsum += sim[nodei, nodej]
        totalsum = totalsum / (len(node_ids) - 1)
        ASCOS[node_ids[nodej]] = totalsum

    return ASCOS

def _is_converge(sim, sim_old, nrow, ncol, eps=1e-4):
    for i in range(nrow):
        for j in range(ncol):
            if abs(sim[i,j] - sim_old[i,j]) >= eps:
                return False
    return True


def visualize(m):
    # visualization
    utils.visualizeTopRankFrames(sorted_ASCOS, m, excluded_nodes_set)

def calculate_k():
    column1 = ''
    column2 = ''
    count = 0;
    with open(INPUT_FILE) as f:
        for line in f:
            a = line.split(',');
            if column1 == '' and column2 == '':
                column1 = a[0]
                column2 = a[1]
            elif column1 != a[0] or column2 != a[1]:
                break
            count += 1
    return count;

def preProcessing():

    # Clear the file
    transfile = open("../Input/" + "trans_output_t2.gspc", "wb")
    # Load the database
    print 'Loading database......'

    k = calculate_k()

    count = 0
    with open(INPUT_FILE) as f:
        for line in f:
            line = line.strip('\n')
            transfile.write(line)
            count += 1
            if count == k:
                transfile.write("\n")
                count = 0
            else:
                transfile.write(",")

    transfile.write("\n")
    transfile.close()

    global database
    database = np.loadtxt("../Input/" + "trans_output_t2.gspc", delimiter=",")
    print 'Database loaded......'

# Function : Main
# Description: Run the main program
if __name__ == '__main__':
    
    INPUT_FILE = raw_input("Enter file name (default: in_file.gspc), the path is 'Input/', don't contain path:")
    INPUT_FILE = INPUT_PATH + INPUT_FILE

    # Take k as an input
    first_seed_video, first_seed_frame = input("Enter first seed pair VIDEO_NUMBER,FRAME_NUMBER:")
    second_seed_video, second_seed_frame = input("Enter second seed pair VIDEO_NUMBER,FRAME_NUMBER:")
    third_seed_video, third_seed_frame = input("Enter third seed pair VIDEO_NUMBER,FRAME_NUMBER:")

    global excluded_nodes_set
    excluded_nodes_set = {(first_seed_video, first_seed_frame),(second_seed_video, second_seed_frame),(third_seed_video, third_seed_frame)}

    preProcessing()
    start_time = time.time();
    creatGraph()
    end_time = time.time();
    utils.printTime(end_time - start_time)

    while 1 :
        # Take k as an input
        m = int(input("Enter m, for the m most significant frames:"))
        if m > 0:
            # visulization
            utils.clearOutputFramesDirectory()
            utils.output_a_frame(first_seed_video, first_seed_frame, "Input");
            utils.output_a_frame(second_seed_video, second_seed_frame, "Input");
            utils.output_a_frame(third_seed_video, third_seed_frame, "Input");
            visualize(m)
        else :
            print 'm must be positive'
