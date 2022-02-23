import cv2
import numpy as np

# カメラのキャプチャ
capture = cv2.VideoCapture(0)

# グローバル変数
drawing = False
complete_region = False
ix,iy,width,height,kx,ky = -1,-1,0,0,-1,-1
box = [ix, iy, width, height]
img_thresh = []
img_thresh_max_bn = []
roi_max = []
correction = 1
box_list =[]
tempcopy = False
thresh_flag = False

# OpenCVのバージョン
version = cv2.__version__.split(".")
CVversion = int(version[0])

# マウスコールバック関数
def my_mouse_callback(event,x,y,flags,param):
    global ix,iy,width,height,box,drawing,complete_region,kx,ky

    if event == cv2.EVENT_MOUSEMOVE: # マウスが動いた時
        if(drawing == True):
            width = x - ix
            height = y - iy
    elif event == cv2.EVENT_LBUTTONDOWN: # マウス左押された時
        drawing = True
        ix = x
        iy = y
        width = 0
        height = 0
    elif event == cv2.EVENT_LBUTTONUP:  # マウス左離された時
        drawing = False
        complete_region = True
        kx = x
        ky = y

    box = [ix, iy, kx, ky, width, height] # 選択範囲

# 二値化画像表示
def thresh(im_gray,threshold):
    global img_thresh, thresh_flag
    ret, img_thresh = cv2.threshold(im_gray, threshold, 255, cv2.THRESH_BINARY)
    cv2.imshow('img_thresh', img_thresh)
    cv2.moveWindow('img_thresh', 400, 730)
    thresh_flag = True
    
# 最大領域の抽出
def max_area(img_thresh,roi):
    global img_thresh_max_bn, roi_max
    img_thresh02 = cv2.bitwise_not(img_thresh)
    if CVversion == 3:
        img,contours,hierarchy = cv2.findContours(img_thresh02, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    else:
        contours,hierarchy = cv2.findContours(img_thresh02, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours != []:
        max_cnt = max(contours, key=lambda x: cv2.contourArea(x))
        img_thresh_max = np.zeros_like(img_thresh02)
        cv2.drawContours(img_thresh_max, [max_cnt], -1, color=255, thickness=-1)
        img_thresh_max_bn = cv2.bitwise_not(img_thresh_max)
        cv2.imshow('img_thresh_max', img_thresh_max_bn)
        cv2.moveWindow('img_thresh_max', 800, 730)

        # 最大領域の輪郭
        if CVversion == 3:
            img,contours_max,hierarchy = cv2.findContours(img_thresh_max, 1, 2)
        else:
            contours_max,hierarchy = cv2.findContours(img_thresh_max, 1, 2)
        cnt = contours_max[0]
        xm,ym,wm,hm = cv2.boundingRect(cnt)
        roi_max = roi.copy()
        roi_max = cv2.rectangle(roi_max,(xm,ym),(xm+wm,ym+hm),(255,100,0),1)
        wh_hm = str(int(hm*correction)) + '-' + str(int(wm*correction))
        roi_max = cv2.putText(roi_max, wh_hm, (xm+2,ym+20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255,100,0), 1, cv2.LINE_AA) # 大きさを描写
        cv2.imshow('roi_max', roi_max)
        cv2.moveWindow('roi_max', 1200, 730)

# メイン関数
def main():
    global ix,iy,width,height,box,drawing,complete_region,correction,kx,ky,tempcopy

    source_window = "draw_window"
    cv2.namedWindow(source_window)
    cv2.setMouseCallback(source_window, my_mouse_callback)

    # 初期値
    mode = 'Line'
    linecolour = (0,255,0)
    threshold = 100

    while(True):

        ret, frame = capture.read()
        windowsize = (800, 600)
        frame = cv2.resize(frame, windowsize)
        cv2.imshow('frame',frame)
        cv2.moveWindow('frame', 10, 10)
        if (tempcopy):
            cv2.imshow(source_window, temp)
            cv2.moveWindow(source_window, 820, 10)

        # ステータスウインドウ
        frame_config = np.full((250, 250, 3), 255, dtype=np.uint8)
        mode_text =  'Mode = '  + mode
        correction_text = 'Correction = ' + str(round(correction,2))
        threshold_text = 'Threshold = ' + str(threshold)
        frame_config = cv2.putText(frame_config, mode_text, (10,40), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0,0,200), 1, cv2.LINE_AA)
        frame_config = cv2.putText(frame_config, correction_text, (10,60), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0,0,200), 1, cv2.LINE_AA)
        frame_config = cv2.putText(frame_config, threshold_text, (10,80), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0,0,200), 1, cv2.LINE_AA)
        frame_config = cv2.putText(frame_config, 'Line colour', (10,100), cv2.FONT_HERSHEY_DUPLEX, 0.5, linecolour, 1, cv2.LINE_AA)

        frame_config = cv2.putText(frame_config, 'Temporarily saved : t', (10,120), cv2.FONT_HERSHEY_DUPLEX, 0.5, (100,0,0), 1, cv2.LINE_AA)
        frame_config = cv2.putText(frame_config, 'Correction : c', (10,140), cv2.FONT_HERSHEY_DUPLEX, 0.5, (100,0,0), 1, cv2.LINE_AA)
        frame_config = cv2.putText(frame_config, 'Threshold +: x -: y', (10,160), cv2.FONT_HERSHEY_DUPLEX, 0.5, (100,0,0), 1, cv2.LINE_AA)
        frame_config = cv2.putText(frame_config, 'Save : s', (10,180), cv2.FONT_HERSHEY_DUPLEX, 0.5, (100,0,0), 1, cv2.LINE_AA)
        frame_config = cv2.putText(frame_config, 'Quit : q', (10,200), cv2.FONT_HERSHEY_DUPLEX, 0.5, (100,0,0), 1, cv2.LINE_AA)
        cv2.imshow('config', frame_config)
        cv2.moveWindow('config', 10, 730)
        
        if(drawing): # 左クリック押されてたら
            temp = temp00.copy()
            if mode == 'Line':
                temp = cv2.line(temp,(ix,iy),(ix + width, iy+ height),linecolour,1) # 直線を描画
                width_height = str(int((height**2 + width**2)**0.5*correction))
                temp = cv2.putText(temp, width_height, (ix,iy-10), cv2.FONT_HERSHEY_DUPLEX, 0.5, linecolour, 1, cv2.LINE_AA) # 長さを描写
            else:
                cv2.rectangle(temp,(ix,iy),(ix + width, iy+ height),linecolour,1) # 矩形を描画
                width_height = str(int(height * correction)) + '-' + str(int(width * correction))
                temp = cv2.putText(temp, width_height, (ix,iy-10), cv2.FONT_HERSHEY_DUPLEX, 0.5, linecolour, 1, cv2.LINE_AA) # 大きさを描写

        if(complete_region): # 矩形の選択が終了したら
            complete_region = False
            if (height != 0 and width != 0):
                box_list.append(box)
                if mode == 'Line':
                    temp00 = temp.copy()
                else:
                    roi = orign[iy+1:iy+height-1, ix+1:ix+width-1] # 元画像から選択範囲を切り取り
                    im_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                    thresh(im_gray,threshold)
                    max_area(img_thresh,roi)

        # キー操作
        key = cv2.waitKey(1) & 0xFF
        if key ==ord('q'):
            break
        elif key ==ord('m'):
            if mode == 'Line':
                mode = 'Binarization'
            else:
                mode = 'Line'
        elif key ==ord('t'):
            tempcopy = True
            temp = frame.copy()
            temp00 = frame.copy()
            orign = frame.copy()
        elif key ==ord('c'):
            if width > 0:
                correction = 10 / width
            elif width < 0:
                correction = 10 / (width*-1)
        elif key ==ord('l'):
            if linecolour == (0,255,0):
                linecolour = (0,0,255)
            elif linecolour == (0,0,255):
                linecolour = (255,0,0)
            else:
                linecolour = (0,255,0)
        elif key ==ord('x'):
            threshold = threshold + 1
            if width != 0:
                thresh(im_gray,threshold)
                max_area(img_thresh,roi)
        elif key ==ord('z'):
            threshold = threshold - 1
            if width != 0:
                thresh(im_gray,threshold)
                max_area(img_thresh,roi)
        elif key ==ord('s'):
            if (tempcopy):
                cv2.imwrite('01_original.png', orign)
                cv2.imwrite('02_draw.png', temp)
                if (thresh_flag):
                    cv2.imwrite('03_img_thresh.png', img_thresh)
                    cv2.imwrite('04_mg_thresh_max.png', img_thresh_max_bn)
                    cv2.imwrite('05_roi_max.png', roi_max)
                print('save files')

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()