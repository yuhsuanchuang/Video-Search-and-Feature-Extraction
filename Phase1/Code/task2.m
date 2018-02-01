clear, close all
list = dir('*.mp4');
for W=1:length(list)
    v = VideoReader(list(W).name);
    if strcmp(list(W).name,'1R.mp4')
        filename = '1';
    elseif strcmp(list(W).name, '2R.mp4')
        filename = '2';
    elseif strcmp(list(W).name, '3R.mp4')
        filename = '3';
    elseif strcmp(list(W).name, '4R.mp4')
        filename = '4';
    elseif strcmp(list(W).name, '5R.mp4')
        filename = '5';
    elseif strcmp(list(W).name, '6R.mp4')
        filename = '6';
    elseif strcmp(list(W).name, '7R.mp4')
        filename = '7';
    elseif strcmp(list(W).name, '8R.mp4')
        filename = '8';
    elseif strcmp(list(W).name, '9R.mp4')
        filename = '9';
    elseif strcmp(list(W).name, '10R.mp4')
        filename = '10';
    end

    r=2;
    fid = fopen('task2-siftoutput.txt', 'a');
    for index = 1:v.NumberOfFrames;
        frame = read(v,index);
        greyframe = rgb2gray(frame);
        [row column]=size(greyframe);
        cutframe=mat2cell(greyframe,(row/r)*ones(1,r),(column/r)*ones(1,r));
        for ROW = 1:r
            for COLUMN = 1:r
                [frames,descr] = sift(cutframe{ROW,COLUMN}, 'Verbosity', 1 ) ;
                [m,n] = size(descr);
                fprintf(fid, '<%s, %d, %d, {', filename, index, COLUMN+(ROW-1)*r);
                for q = 1:n
                    fprintf(fid, '[');
                    for w = 1:4
                        fprintf(fid, '%f, ', frames(w, q));
                    end
                    fprintf(fid, '%f', descr(1, q));
                    for e = 2:128
                        fprintf(fid, ', %f', descr(e, q));
                    end
                    fprintf(fid, ']');
                end
                fprintf(fid, '}>\n\n');
            end
        end
    end
end
