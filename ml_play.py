# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 15:18:03 2020

@author: user
"""

"""The template of the main script of the machine learning process
"""
import numpy as np
import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)
    # Return y by giving the lienar equaltion and the x
def getX(y, lineEQ):
    a = lineEQ[0]
    b = lineEQ[1]
    return (y-b)/a
    
    # Get the linear equalition from p1 and p2
def getLineEqu(p1, p2):
    # AX=B
    A = np.array([[p1[0], 1],[p2[0],1]])
    B = np.array([p1[1], p2[1]])   
    a, b = np.linalg.solve(A, B)
    return a, b

def ml_loop():
    """The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()
    ball_bef_y = 0
    cal_x = 0
    cal_x_2 = 0
    cal_y = 0
    cal_y_2 = 0
    pre_x = 0
    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information
        ball_x = scene_info.ball[0]
        ball_y = scene_info.ball[1]
        platform_x = scene_info.platform[0]
        if ball_y > ball_bef_y:
            if 158 < ball_y < 165:
                cal_x = ball_x
                cal_y = ball_y
            if 166 < ball_y < 173:
                cal_x_2 = ball_x
                cal_y_2 = ball_y
            if cal_y_2 != 0:
                p1 = [cal_x, cal_y]
                p2 = [cal_x_2, cal_y_2]
                
                pre_x = int(getX(400, getLineEqu(p1, p2)))
            if pre_x != 0:
                if 400 > pre_x > 200:
                    pre_x = 400 - pre_x
                elif 600 > pre_x > 400:
                    pre_x = pre_x - 400
                elif 0 > pre_x > -200:
                    pre_x = -pre_x
                elif -200 > pre_x > -400:
                    pre_x = pre_x + 400
                if platform_x+20 - pre_x < 0:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                if platform_x+20 - pre_x > 0:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
        if ball_y < ball_bef_y:
            if platform_x > 80:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            elif platform_x < 80:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            cal_x = 0
            cal_x_2 = 0
            cal_y = 0
            cal_y_2 = 0
        ball_bef_y = ball_y
        # 3.4. Send the instruction for this frame to the game process
