import numpy as np
from scipy.spatial.distance import cdist
from sklearn import preprocessing as pp
import math

# SIFT desc Information
global START_COL, VIDEO_NUM_COL, FRAME_NUM_COL, CELL_NUM_COL, SIFT_DES_START, MAX_DIST
START_COL = 0
VIDEO_NUM_COL = 0
FRAME_NUM_COL = 1
CELL_NUM_COL = 2
SIFT_DES_START = 5
MAX_DIST = 0


# SIFT I/O Information
INPUT_PREFIX = "../Input/"
INPUT_FILE = "in_file_d.spc"
OUTPUT_PREFIX = "../Output/"
OUTPUT_FILE = "in_file_d_k.gspc"

# Function : genDict
# Description: This function generates all the nodes for the graph
def genNodes(k):
    # Get total number of videos
    total_number_videos = database[-1, VIDEO_NUM_COL]

    # Iter over all the frames in the query video
    for query_video_number in range(1, int(total_number_videos + 1)):

        # Get the whole video
        query_video = database[database[:, VIDEO_NUM_COL] == query_video_number, VIDEO_NUM_COL:]

        # Get the number of frames for the video
        query_frameNos = np.transpose(np.unique(query_video[:, FRAME_NUM_COL]))

        for query_frame_number in np.nditer(query_frameNos):

            # Get the query frame using query_frame_number
            query_frame = query_video[query_video[:, FRAME_NUM_COL] == query_frame_number, SIFT_DES_START:]

            # List of the most similar frames
            query_frame_k_values = list()

            # Iter over all the frames in the object video
            for object_video_number in range(1, int(total_number_videos + 1)):

                # Don't find similarities in the same video
                if query_video_number != object_video_number:

                    # Get the object video and the unique number of frames
                    object_video = database[database[:, VIDEO_NUM_COL] == object_video_number, VIDEO_NUM_COL:]
                    object_frameNos = np.transpose(np.unique(object_video[:, FRAME_NUM_COL]))

                    # Iter through all the frames in the object video
                    for object_frame_number in np.nditer(object_frameNos):

                        # Get the object frame
                        object_frame = object_video[object_video[:, FRAME_NUM_COL] == object_frame_number,
                                       SIFT_DES_START:]

                        # Compute the similarities values for the object frame and query video
                        sim_value = 1 - computeDistance(query_frame, object_frame)

                        # add to list
                        query_frame_k_values.append(
                            ((object_video_number, int(object_frame_number.item(0))), sim_value))

                        # Remove if there are too many items
                        if len(query_frame_k_values) > k:
                            query_frame_k_values = sorted(query_frame_k_values, key=lambda t: t[1], reverse=True)
                            del query_frame_k_values[-1]

            # sort before printing
            query_frame_k_values = sorted(query_frame_k_values, key=lambda t: t[1], reverse=True)

            # print to the file
            printInfo(query_video_number, int(query_frame_number.item(0)), query_frame_k_values)

# Function : printInfo
# Description: Prints each node in the graph
def printInfo(query_video_number, query_frame_number, query_frame_k_values):

    # Open the file to Edit
    printerFile = open(OUTPUT_FILE, "ab")

    # pint to the file
    for object_video_info, similarity in query_frame_k_values:
        object_video_number, object_frame_number = object_video_info

        printerFile.write(str(query_video_number) + "," + str(query_frame_number) + "," + str(
            object_video_number) + "," + str(object_frame_number) + "," + str(similarity) + "\n")

    # Close the file
    printerFile.close()

# Function : preProcessing
# Description: This function computes the distance between two frames
def computeDistance(qframe, oframe):
    frameD = cdist(qframe, oframe, 'euclidean')
    minD = np.amin(frameD, axis=1)
    meanD = np.mean(minD)
    meanD = meanD / MAX_DIST
    return meanD

# Function : preProcessing
# Description: This function loads the database and clears the input file
def preProcessing(fileName, k):

    global database, MAX_DIST, OUTPUT_FILE
    # Clear the file
    OUTPUT_FILE = OUTPUT_PREFIX + fileName + "_" + str(k) + ".gspc"
    printerFile = open(OUTPUT_FILE, "wb")
    printerFile.close()

    # Load the database
    print 'Loading database......'

    database = np.loadtxt(INPUT_FILE, delimiter=",")
    scaler = pp.MinMaxScaler().fit(database[:, SIFT_DES_START:])
    database = np.column_stack((database[:, 0:SIFT_DES_START], scaler.transform(database[:, SIFT_DES_START:])))
    MAX_DIST = math.sqrt(database.shape[1] - SIFT_DES_START)
    print 'Database loaded......'


# Function : Main
# Description: Run the main program
if __name__ == '__main__':
    INPUT_FILE = raw_input("Enter the input file name(File should exist in Input directory): ")
    fileName = INPUT_FILE.split(".")[0]
    INPUT_FILE = INPUT_PREFIX + INPUT_FILE
    # Take k as an input
    flag = 1
    while flag :
        k = int(input("Enter k, for the k most similar frames: "))
        if k <=0 :
            print 'K must be positive.'
        else : flag = 0

    # Pre-processing
    preProcessing(fileName, k)

    # generate the Nodes for the graph
    genNodes(k)

