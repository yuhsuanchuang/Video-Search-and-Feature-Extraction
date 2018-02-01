import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
import imageio

# SIFT desc Information
global START_COL, VIDEO_NUM_COL, FRAME_NUM_COL, CELL_NUM_COL, SIFT_DES_START, LSH_HASH_COL, LSH_BUCKET_COL, DATA_INDEX_COL, X_COL, Y_COL
START_COL = 0
VIDEO_NUM_COL = 3
FRAME_NUM_COL = 4
CELL_NUM_COL = 5
LSH_HASH_COL = 1
LSH_BUCKET_COL = 0
DATA_INDEX_COL = 2
X_COL = 6
Y_COL = 7


#SIFT I/O Information
global INPUT_FILE, INPUT_DB_INDEX, INPUT_VIDEO_PREFIX, OUTPUT_FRAMES_PREFIX,INPUT_PREFIX
INPUT_FILE = "../Output/filename_d.lsh"
INPUT_PREFIX = "../Input/"
INPUT_DB_INDEX = "in_file.index"
INPUT_VIDEO_PREFIX = "../Input/Videos/"
OUTPUT_FRAMES_PREFIX = "../Output/n_frames/"

# Function : preProcessing
# Description: This function loads the database and clears the input file
def preProcessing(fileName):

    global fileIndex, revIndex, database

    # Load the database
    print 'Loading database......'

    global database, databasePD
    database = np.loadtxt(INPUT_PREFIX + fileName + ".spc", delimiter=",")
    databasePD = pd.read_csv(INPUT_FILE,header=None,names=['b','h','i','v','f','c','x','y'])
    print 'Database loaded......'

    # Creating file index
    fileIndex = np.genfromtxt(INPUT_PREFIX + INPUT_DB_INDEX, delimiter="=", dtype=None, skip_header=1)
    fileIndex = dict(fileIndex)
    revIndex = {v: k for k, v in fileIndex.iteritems()}


def search(N,V,F,X1,Y1,X2,Y2):
    totalDataAccessSize = 0
    totalIndexAccessSize = 0
    samples = databasePD[(databasePD.v == V) & (databasePD.f == F) & (databasePD.x>=X1) & (databasePD.x<=X2) & (databasePD.y>=Y1) & (databasePD.y<=Y2)]
    totalIndexAccessSize += samples.memory_usage().sum()
    selIndexes = samples['i']
    selIndexes = selIndexes.drop_duplicates()
    sampleArray = database[selIndexes,:]
    totalDataAccessSize += sampleArray.nbytes
    samples = samples[['b', 'h']]
    result = pd.merge(samples, databasePD, how='inner', on=['b', 'h'])
    result = result[(result.v != V)]
    overallSiftVectors = result.shape[0]
    print 'Overall Sift Vectors Considered from all buckets: %s' % str(overallSiftVectors)
    result = result.drop_duplicates('i')
    totalIndexAccessSize += result.memory_usage().sum()
    result = result.sort_values('i')
    uniqueSiftVectors = result.shape[0]
    print 'Unique Sift Vectors Considered from all buckets: %s' % str(uniqueSiftVectors)
    prunedData = database[result['i'],:]
    totalDataAccessSize += prunedData.nbytes
    print 'Original Database access Size: %s' % str(totalDataAccessSize)

    videoNos = np.transpose(np.unique(prunedData[:, 0]))
    frameSim = np.array([]).reshape(0, 3)
    for videoNo in np.nditer(videoNos):
        videoData = prunedData[prunedData[:, 0] == videoNo, :]
        frameNos = np.transpose(np.unique(videoData[:, 1]))
        for frameNo in np.nditer(frameNos):
            frameD = cdist(videoData[videoData[:, 1] == frameNo, 5:], sampleArray[:, 5:], 'euclidean')
            # Most similar vectors
            minD = np.amin(frameD, axis=1)
            meanD = np.mean(minD)
            frameSim = np.vstack([frameSim, [videoNo, frameNo, meanD]])
    frameSim = frameSim[np.argsort(frameSim[:, 2])]

    for i in range(0,N):
        print 'Video No: %s Frame No: %s' % (str(int(frameSim[i,0])), str(int(frameSim[i,1])))
        outputFrame(frameSim[i,0],frameSim[i,1])
    print 'done'

def outputFrame(videoIndex, frameIndex):

    video = imageio.get_reader(INPUT_VIDEO_PREFIX + revIndex[int(videoIndex)], 'ffmpeg')
    frame = video.get_data(int(frameIndex))
    imageio.imwrite(OUTPUT_FRAMES_PREFIX + "v"+ str(int(videoIndex)) + "_f"+str(int(frameIndex)) + '.jpg', frame)

# Function : Main
# Description: Run the main program
if __name__ == '__main__':
    INPUT_FILE = raw_input("Enter the input file name(File should exist in Input directory): ")
    fileName = INPUT_FILE.split(".")[0]
    INPUT_FILE = INPUT_PREFIX + INPUT_FILE
    # Pre-processing
    preProcessing(fileName)
    while 1:
        # Take k as an input
        N = int(input("Enter n, for number of frames: "))
        (V,F,X1,Y1,X2,Y2) = map(int, raw_input("Enter Video, Frame No and 2 points seperated by space (V F X1 Y1 X2 Y2): ").split())
        search(N, V, F, X1, Y1, X2, Y2)
