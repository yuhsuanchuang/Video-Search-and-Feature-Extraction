import numpy as np
from nearpy import Engine
from nearpy.hashes import RandomBinaryProjections
from nearpy.distances import CosineDistance

# SIFT desc Information
global START_COL, VIDEO_NUM_COL, FRAME_NUM_COL, CELL_NUM_COL, SIFT_DES_START
START_COL = 0
VIDEO_NUM_COL = 0
FRAME_NUM_COL = 1
LSH_VECT_START_COL = 5
CELL_NUM_COL = 2
SIFT_DES_START = 7


# SIFT I/O Information
INPUT_PREFIX = "../Input/"
INPUT_FILE = "in_file_d.spc"
OUTPUT_PREFIX = "../Output/"
OUTPUT_FILE = "in_file_d.lsh"

# Function : LSH
# Description: This function hashes the SIFT vectors
# Arguments: layers = number of hash forests/layers, K = 2^K buckets in each layer
def LSH(Layers, K):

    lsh_vectors = database[:, LSH_VECT_START_COL:]
    video_data = database[:, 0:5]

    num_rows, num_cols = lsh_vectors.shape
    dimension = num_cols

    rbp = list()
    for i in range(Layers):
        rbp.append(RandomBinaryProjections(str(i), K))

    # Create engine with pipeline configuration
    engine = Engine(dimension, lshashes=rbp)

    # Index 1000000 random vectors (set their data zo a unique string)
    for index in range(num_rows):
        v = lsh_vectors[index, :]

        meta_data = str(index)+',' + str(int(video_data[index, 0])) + ', ' + str(int(video_data[index, 1])) + ', ' + str(int(video_data[index, 2])) \
                    + ', ' + str(video_data[index, 3]) + ', ' + str(video_data[index, 4])

        engine.store_vector(v, meta_data)

    printOutput(engine.storage.buckets)

    print 'stop'

def printOutput(buckets):
    # Open the file to Edit
    printerFile = open(OUTPUT_FILE, "wb")

    for layers in buckets.keys():
        current_layer= buckets[layers]
        for new_buckets in current_layer.keys():
            current_bucket = current_layer[new_buckets]
            for current_point in current_bucket:
                printerFile.write( layers + ', ' + str(int(new_buckets,2)) + ', ' + current_point[1])
                printerFile.write("\n")

    printerFile.close()

# Function : preProcessing
# Description: This function loads the database and clears the input file
def preProcessing(fileName):

    global OUTPUT_FILE
    # Clear the file
    OUTPUT_FILE = OUTPUT_PREFIX + fileName + ".lsh"
    printerFile = open(OUTPUT_FILE, "wb")
    printerFile.close()

    # Load the database
    print 'Loading database......'

    global database
    database = np.loadtxt(INPUT_FILE, delimiter=",")

    print 'Database loaded......'


# Function : Main
# Description: Run the main program
if __name__ == '__main__':
    INPUT_FILE = raw_input("Enter the input file name(File should exist in Input directory): ")
    fileName = INPUT_FILE.split(".")[0]
    INPUT_FILE = INPUT_PREFIX + INPUT_FILE
    # Take L, k as an input
    flag = 1
    while flag:
        L = int(input("Enter L, for L layers of LSH: "))
        if L <= 0:
            print 'L must be positive.'
        else:
            flag = 0

    flag = 1
    while flag:
        K = int(input("Enter K, for 2^K buckets in each hash layer: "))
        if K <= 0:
            print 'K must be positive.'
        else:
            flag = 0
    # Pre-processing
    preProcessing(fileName)

    # Hash the vectors
    LSH(L,K)