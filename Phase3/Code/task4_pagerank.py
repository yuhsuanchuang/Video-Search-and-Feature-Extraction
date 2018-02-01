import numpy as np
import time
import networkx as nx
import operator
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

    personalize = {}
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

                if int(q_video_number) == first_seed_video and int(q_frame_number) == first_seed_frame:
                    personalize[(int(q_video_number), int(q_frame_number))] = 0.333
                elif int(q_video_number) == second_seed_video and int(q_frame_number) == second_seed_frame:
                    personalize[(int(q_video_number), int(q_frame_number))] = 0.333
                elif int(q_video_number) == third_seed_video and int(q_frame_number) == third_seed_frame:
                    personalize[(int(q_video_number), int(q_frame_number))] = 0.333
                else:
                    personalize[(int(q_video_number),int(q_frame_number))] = 0



    pr = nx.pagerank(G, alpha=0.9, personalization=personalize)
    global sorted_pr
    sorted_pr = sorted(pr.items(), key=operator.itemgetter(1), reverse=True)


def visualize(m):
    # visualization
    utils.visualizeTopRankFrames(sorted_pr, m, excluded_nodes_set)


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
    excluded_nodes_set = {(first_seed_video, first_seed_frame), (second_seed_video, second_seed_frame),
                          (third_seed_video, third_seed_frame)}

    preProcessing()
    start_time = time.time();
    creatGraph()
    end_time = time.time();
    utils.printTime(end_time - start_time)

    while 1:
        # Take k as an input
        m = int(input("Enter m, for the m most significant frames:"))
        if m > 0:
            # visulization
            utils.clearOutputFramesDirectory()
            utils.output_a_frame(first_seed_video, first_seed_frame, "Input");
            utils.output_a_frame(second_seed_video, second_seed_frame, "Input");
            utils.output_a_frame(third_seed_video, third_seed_frame, "Input");
            visualize(m)
        else:
            print 'm must be positive'

