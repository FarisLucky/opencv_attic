import numpy as np
import cv2, cv
import os
from common import splitfn

USAGE = '''
USAGE: calib.py [--save <filename>] [--debug <output path>] [<image mask>] 
'''



if __name__ == '__main__':
    import sys, getopt
    from glob import glob

    args, img_mask = getopt.getopt(sys.argv[1:], '', ['save=', 'debug='])
    args = dict(args)
    try: img_mask = img_mask[0]
    except: img_mask = '../cpp/left*.jpg'
    img_names = glob(img_mask)
    debug_dir = args.get('--debug')

    pattern_size = (9, 6)
    pattern_points = np.zeros( (np.prod(pattern_size), 3), np.float32 )
    pattern_points[:,:2] = np.indices(pattern_size).T.reshape(-1, 2)

    obj_points = []
    img_points = []
    h, w = 0, 0
    for fn in img_names:
        print 'processing %s...' % fn,
        img = cv2.imread(fn, 0)
        h, w = img.shape[:2]
        found, corners = cv2.findChessboardCorners(img, pattern_size)
        if found:
            term = ( cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1 )
            cv2.cornerSubPix(img, corners, (5, 5), (-1, -1), term)
        if debug_dir:
            vis = cv2.cvtColor(img, cv.CV_GRAY2BGR)
            cv2.drawChessboardCorners(vis, pattern_size, corners, found)
            path, name, ext = splitfn(fn)
            cv2.imwrite('%s/%s_chess.bmp' % (debug_dir, name), vis)
        if not found:
            print 'chessboard not found'
            continue
        img_points.append(corners.reshape(-1, 2))
        obj_points.append(pattern_points)
        
        print 'ok'

    camera_matrix = np.zeros((3, 3))
    dist_coefs = np.zeros(4)
    img_n = len(img_points)
    rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, (w, h), camera_matrix, dist_coefs)
    print "RMS:", rms
    print "camera matrix: ", camera_matrix
    print "distortion coefficients: ", dist_coefs

