﻿'''
start : 21.07.20
updated : 21.07.21
minku koo

점선 감지 후, 연결 작업
Camelot Github Issue
https://github.com/atlanhq/camelot/issues/370

원인
점선은 line_scale 보다 작은 길이의 선의 경우에만 감지되지 않음
보다 큰 길이의 점선의 경우 > iterations를 증가함으로써 부분적으로 해결 가능함

목적
동일한 길이와 패턴으로 이어진 점선의 감지
ex) __ __ __ __ or _ _ _ _

이슈
동일하지 않은 길이의 점선은 어떻게 감지할 것인가
ex) ___ _ ___ _ 

'''

import numpy as np
import cv2

# 이미지의 한 줄에서 점선이 감지되는지의 여부
def __check_dotted_line(line, repetition = 5, erosion_size=10):
    '''
    Parameters
        line <nd.array> : Line on Image
        repetitionn <int> : Constant number of pattern iterations (default = 5)
    returns
        dotted_line <list in list> : Index of dotted line start and end
    '''
    
    line = [1 if x>0 else 0 for x in line]
    
    # line_meta_data : 간단하게 정리된 라인의 메타데이터들
    # count_pixel : 라인 사이즈 측정을 위한 변수
    line_meta_data, count_pixel = [], 0
    # temp_pixel : 이전 픽셀이 0인지 1인지 확인하기 위한 변수
    # start_point : 라인 또는 공백의 시작점 인덱스 저장 변수
    temp_pixel, start_point = int( line[0] ), 0
    for index, pixel in enumerate(line):
        # 현재 픽셀과 이전 픽셀의 값이 동일한 경우
        if temp_pixel == pixel : 
            count_pixel += 1 # 사이즈만 추가
            
        else: # 다른 경우
            # 기존 라인 또는 공백 정보를 메타 데이터에 추가
            line_meta_data.append( {
                                    "start": start_point,
                                    "pixel": temp_pixel,
                                    "size": count_pixel
                                    } )
            # 변수 초기화
            count_pixel = 1
            temp_pixel = pixel
            start_point = index
    
    line_meta_data.append( {
                            "start": start_point,
                            "pixel": temp_pixel,
                            "size": count_pixel
                            } )
    
    '''
    # Example
    >> print( line_meta_data )
    [{'start': 0, 'pixel': 0, 'size': 1}, {'start': 1, 'pixel': 1, 'size': 4}, ...]
    '''
    
    '''
    여기에 조건 걸기
    - 만약 line meta data 길이가 몇개 이하라면 패스
    - 
    '''
    
    # print(line_meta_data)
    
    dotted_line_section, dotted_line_stack = [], []
    line_size, space_size = 0, 0
    isDotted = False
    for pixel in line_meta_data:
        this_size = pixel["size"]
        if pixel["pixel"] == 1: # line
            if this_size == line_size:
                if this_size < erosion_size :
                    dotted_line_stack.append( pixel["start"] )
                    isDotted = True
            else:
                if isDotted:
                    dotted_line_stack.append( pixel["start"] )
                    if len(dotted_line_stack) >= repetition:
                        # dotted_line_stack.append( pixel["start"] )
                        dotted_line_section.append( dotted_line_stack )
                
                dotted_line_stack = [ pixel["start"] ]
                isDotted = False
            line_size = this_size
            
        else: # space
            if this_size == space_size:
                if len(dotted_line_stack) == 1:
                    dotted_line_stack.append( pixel["start"] )
                if this_size >= erosion_size :
                    line_size = 0
                    dotted_line_stack = []
            else:
                if isDotted :
                    if len(dotted_line_stack) >= repetition:
                        # 초기화
                        # line_size = 0
                        # dotted_line_stack = []
                    # else:
                        dotted_line_section.append( dotted_line_stack )
                    
                    line_size = 0
                    dotted_line_stack = []
                else:
                    dotted_line_stack = [ pixel["start"] ]
            space_size = this_size
    
    # print("=="*20)
    # print(dotted_line_section)
    
    
    return dotted_line_section

# 점선을 실선으로 만들어서 반환
def __dotted2solid(threshold, sections, direction, index):
    if direction == "h" :
        for sec in sections:
            start, end = sec[0], sec[-1]
            threshold[index][start: end+1] = 255
            
    elif direction == "v" :
        for sec in sections:
            start, end = sec[0], sec[-1]
            threshold[ start:end+1 , index:index+1 ] = 255
            # print("start", start, "end", end, "index", index)
    return threshold


def detect_dotted_line(threshold, direction="v", line_scale=15, rep = 5):
    '''
    Parameters
    
    returns
    
    '''
    size = threshold.shape[0] // line_scale
    board = threshold.copy()
    
    if direction.lower() == "v":
        for index in range( len(threshold[0]) ):
            row = threshold[:,index]
            # if index> 340 and index<350:
                # print("index", index, row[170:210])
            dotted_section = __check_dotted_line(row, 
                                                repetition = rep, 
                                                erosion_size=size)
            # if dotted_section: print(index, ":",dotted_section)
            board = __dotted2solid(board, dotted_section, "v", index)
            
    elif direction.lower() == "h":
        for index, col in enumerate(threshold):
            dotted_section = __check_dotted_line(col, 
                                                repetition = rep, 
                                                erosion_size=size)
            board = __dotted2solid(board, dotted_section, "h", index)
    return board


if __name__ == "__main__":
    line = [0,1,1,1,1,0,0,1,1,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,1,1,1,1,1,0,0,0]
    line2 = [0,0,0,0,0,1,1,0,1,1,0,1,1,0,1,1,0,1,1,0,1,1,0,1,1,0,0,0,0,0,0,1,1,0,0,0,1,1,0,0,0]
    line = [0,0,1,0,1,0,1,0,1,0,1,0,0,0,0,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,0,0,0,1]
    
    __check_dotted_line(line, repetition = 5)
    pass

