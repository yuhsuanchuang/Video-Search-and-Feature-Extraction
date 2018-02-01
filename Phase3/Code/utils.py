import imageio
import numpy as np
import os

INPUT_VIDEO_PATH = '../Input/Videos/'
INPUT_INDEX = '../Input/in_file.index'
OUTPUT_PATH = '../Output/Frames/'

def output_frame(video_index, frame_index, output_name):
    if not os.path.isdir(INPUT_VIDEO_PATH):
        print "No file path: " + INPUT_VIDEO_PATH + ". Can't visualize frames."
        return
    if not os.path.isfile(INPUT_INDEX):
        print "No file: " + INPUT_INDEX + ". Can't visualize frames."
        return

    #Creating video name to video num index and reverse index
    fileIndex = np.genfromtxt(INPUT_INDEX, delimiter="=", dtype=None, skip_header=1)
    fileIndex = dict(fileIndex)
    revIndex = {v: k for k, v in fileIndex.iteritems()}

    # Creating output path if not exist
    if not os.path.isdir(OUTPUT_PATH):
        os.mkdir(OUTPUT_PATH)

    video_name = revIndex[int(video_index)];
    objectFile = imageio.get_reader(INPUT_VIDEO_PATH + video_name, 'ffmpeg')
    oimage = objectFile.get_data(int(frame_index))
    imageio.imwrite(OUTPUT_PATH + output_name, oimage)


def output_a_frame(vi, fi, prefix, rank=None):
    vi_fi = str(vi) + "_"+ str(fi)
    if rank is not None:
        output_name = str(prefix) + '_rank' + str(rank) + '_index_' + vi_fi  + '.png';
    else:
        output_name = prefix + '_' + vi_fi + '.png';
    print output_name
    output_frame(vi, fi, output_name);

def visualizeTopRankFrames(sorted_dic, m, excluded_nodes_set=None):
    count = 0;
    i = 0;
    while count < m:
        node, score = sorted_dic[i]
        if (excluded_nodes_set is None) or ((excluded_nodes_set is not None) and (node not in excluded_nodes_set)):
            (vi,fi) = node;
            output_a_frame(vi, fi, "Output", count)
            count += 1
        i += 1

def clearOutputFramesDirectory():
    if os.path.isdir(OUTPUT_PATH):
         filelist = [f for f in os.listdir(OUTPUT_PATH)]
         for file in filelist:
             os.remove(OUTPUT_PATH + file)

def printTime(seconds):
    if seconds < 300:
        print "Time consumed: " + str(seconds) + " seconds."
    else:
        print "Time consumed: " + str(seconds / 60) + " minutes."
