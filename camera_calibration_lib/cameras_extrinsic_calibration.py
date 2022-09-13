import numpy as np
from scipy.spatial.transform import Rotation as R

from camera_calibration_lib.chessboard_pose_estimation import chessboard_pose_estimation

def extrinsic_calibration(cameras, chess_size, chess_square_size, loops = 1, display_frame = False):
    '''
    @brief: this function perform the extrinsic calibration between a list of cameras.

    @param cameras [mandatory]: [list] is a list of Camera type. see camera_utils.camera_init for more info.

    @param chessboard_size [mandatory]: [tuple(int)] is the number of chessboard corners in tuple form i.e. (length, width).

    @param chess_square_size [mandatory]: [int] is the length of a chessboard square in mm.

    @param loops: [int] number of samples for computing average poses

    @param display_frame: [boolean] flag to allow display of image and frame

    @return: cam1_H_camX [list(np.array(4x4))] is a list of homogeneous transformation of all the cameras in the cameras list with respect to the first camera of the list. 
    '''
    assert(len(cameras) >= 2 and "You must pass at least two cameras in the cameras list")

    # discard first frames because they are not good
    for camera in cameras:
        for i in range(10):
            camera.get_rgb()
    
    homogeneous_matrices = []
    cam_number = 1
    for camera in cameras:
        print("Chessboard pose estimation for camera %d" % cam_number)
        if loops == 1:
            rot_mat, trasl_vec = chessboard_pose_estimation(camera, chess_size, chess_square_size, display_frame)
        else:
            rots = []
            trasls = []
            for k in range(loops):
                rot_k, trasl_k = chessboard_pose_estimation(camera, chess_size, chess_square_size, display_frame)
                trasls.append(trasl_k)
                rots.append(rot_k)
            rots = np.array(rots)
            trasls = np.array(trasls)
            rot_mat = np.mean(rots, 0)
            trasl_vec = np.mean(trasls, 0)

        print("rot_mat", rot_mat)
        print("det(rot_mat)", np.linalg.det(rot_mat))
        hom_mat = np.eye(4)
        hom_mat[:3, :3] = rot_mat
        hom_mat[:3, 3:] = trasl_vec
        homogeneous_matrices.append(hom_mat)
        cam_number += 1
    print()
    
    cam1_H_camX = [] # is a list of homogeneous transforamtion between cam1 and all the other cam in cameras list
    H_ref = homogeneous_matrices[0]
    for hom_mat in homogeneous_matrices:
        H_inv = np.linalg.inv(hom_mat)
        cam1_H_currentCam = np.matmul(H_ref, H_inv)
        cam1_H_camX.append(cam1_H_currentCam)
    
    return cam1_H_camX[1:]
        