import dlib
import cv2
import time
import pyzed.sl as sl

# 储存截图的目录
path_screenshots = "data/images/screenshots/"

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

#zed摄像头参数
camera_settings = sl.CAMERA_SETTINGS.CAMERA_SETTINGS_BRIGHTNESS
str_camera_settings = "BRIGHTNESS"
step_camera_settings = 1

def main():
    print("Running...")
    init = sl.InitParameters()
    cam = sl.Camera()
    if not cam.is_opened():
        print("Opening ZED Camera...")
    status = cam.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit()

    runtime = sl.RuntimeParameters()
    #截取帧图
    mat_zed = sl.Mat()

    print_camera_information(cam)
    print_help()

    key = ''
    while key != 113: #for 'q' key
        err = cam.grab(runtime)
        if err == sl.ERROR_CODE.SUCCESS:
            cam.retrieve_image(mat_zed, sl.VIEW.VIEW_LEFT)
            mat_cv = mat_zed.get_data()

            #取灰度
            img_gray = cv2.cvtColor(mat_cv, cv2.COLOR_RGB2GRAY)

            #人脸数
            faces = detector(img_gray, 0)

            # 待会要写的字体
            font = cv2.FONT_HERSHEY_SIMPLEX

            # 检测到人脸
            if len(faces) != 0:
                # 记录每次开始写入人脸像素的宽度位置
                faces_start_width = 0

                for face in faces:
                    # 绘制矩形框
                    cv2.rectangle(mat_cv, tuple([face.left(), face.top()]), tuple([face.right(), face.bottom()]),
                                  (0, 255, 255), 2)

                    height = face.bottom() - face.top()
                    width = face.right() - face.left()

                    # ### 进行人脸裁减 ###
                    # # 如果没有超出摄像头边界
                    # if (face.bottom() < 480) and (face.right() < 640) and \
                    #         ((face.top() + height) < 480) and ((face.left() + width) < 640):
                    #     # 填充
                    #     for i in range(height):
                    #         for j in range(width):
                    #             img_rd[i][faces_start_width + j] = \
                    #                 img_rd[face.top() + i][face.left() + j]

                    # 更新 faces_start_width 的坐标
                    faces_start_width += width

                cv2.putText(mat_cv, "Faces in all: " + str(len(faces)), (20, 350), font, 0.8, (0, 0, 0), 1, cv2.LINE_AA)

            else:
                # 没有检测到人脸
                cv2.putText(mat_cv, "no face", (20, 350), font, 0.8, (0, 0, 0), 1, cv2.LINE_AA)

            # 添加说明
            mat_cv = cv2.putText(mat_cv, "Press 'S': Screen shot", (20, 400), font, 0.8, (255, 255, 255), 1, cv2.LINE_AA)
            mat_cv = cv2.putText(mat_cv, "Press 'Q': Quit", (20, 450), font, 0.8, (255, 255, 255), 1, cv2.LINE_AA)

            cv2.namedWindow("camera", 1)
            cv2.imshow("ZED", mat_cv)
            key = cv2.waitKey(5)
            settings(key, cam, runtime, mat_zed)
        else:
            key = cv2.waitKey(5)
    cv2.destroyAllWindows()

    cam.close()
    print("\nFINISH")

def print_camera_information(cam):
    print("Resolution: {0}, {1}.".format(round(cam.get_resolution().width, 2), cam.get_resolution().height))
    print("Camera FPS: {0}.".format(cam.get_camera_fps()))
    print("Firmware: {0}.".format(cam.get_camera_information().firmware_version))
    print("Serial number: {0}.\n".format(cam.get_camera_information().serial_number))


def print_help():
    print("Help for camera setting controls")
    print("  Increase camera settings value:     +")
    print("  Decrease camera settings value:     -")
    print("  Switch camera settings:             s")
    print("  Reset all parameters:               r")
    print("  Record a video:                     z")
    print("  Quit:                               q\n")


def settings(key, cam, runtime, mat):
    if key == 115:  # for 's' key
        switch_camera_settings()
    elif key == 43:  # for '+' key
        current_value = cam.get_camera_settings(camera_settings)
        cam.set_camera_settings(camera_settings, current_value + step_camera_settings)
        print(str_camera_settings + ": " + str(current_value + step_camera_settings))
    elif key == 45:  # for '-' key
        current_value = cam.get_camera_settings(camera_settings)
        if current_value >= 1:
            cam.set_camera_settings(camera_settings, current_value - step_camera_settings)
            print(str_camera_settings + ": " + str(current_value - step_camera_settings))
    elif key == 114:  # for 'r' key
        cam.set_camera_settings(sl.CAMERA_SETTINGS.CAMERA_SETTINGS_BRIGHTNESS, -1, True)
        cam.set_camera_settings(sl.CAMERA_SETTINGS.CAMERA_SETTINGS_CONTRAST, -1, True)
        cam.set_camera_settings(sl.CAMERA_SETTINGS.CAMERA_SETTINGS_HUE, -1, True)
        cam.set_camera_settings(sl.CAMERA_SETTINGS.CAMERA_SETTINGS_SATURATION, -1, True)
        cam.set_camera_settings(sl.CAMERA_SETTINGS.CAMERA_SETTINGS_GAIN, -1, True)
        cam.set_camera_settings(sl.CAMERA_SETTINGS.CAMERA_SETTINGS_EXPOSURE, -1, True)
        cam.set_camera_settings(sl.CAMERA_SETTINGS.CAMERA_SETTINGS_WHITEBALANCE, -1, True)
        print("Camera settings: reset")
    elif key == 122:  # for 'z' key
        record(cam, runtime, mat)


def switch_camera_settings():
    global camera_settings
    global str_camera_settings
    if camera_settings == sl.CAMERA_SETTINGS.CAMERA_SETTINGS_BRIGHTNESS:
        camera_settings = sl.CAMERA_SETTINGS.CAMERA_SETTINGS_CONTRAST
        str_camera_settings = "Contrast"
        print("Camera settings: CONTRAST")
    elif camera_settings == sl.CAMERA_SETTINGS.CAMERA_SETTINGS_CONTRAST:
        camera_settings = sl.CAMERA_SETTINGS.CAMERA_SETTINGS_HUE
        str_camera_settings = "Hue"
        print("Camera settings: HUE")
    elif camera_settings == sl.CAMERA_SETTINGS.CAMERA_SETTINGS_HUE:
        camera_settings = sl.CAMERA_SETTINGS.CAMERA_SETTINGS_SATURATION
        str_camera_settings = "Saturation"
        print("Camera settings: SATURATION")
    elif camera_settings == sl.CAMERA_SETTINGS.CAMERA_SETTINGS_SATURATION:
        camera_settings = sl.CAMERA_SETTINGS.CAMERA_SETTINGS_GAIN
        str_camera_settings = "Gain"
        print("Camera settings: GAIN")
    elif camera_settings == sl.CAMERA_SETTINGS.CAMERA_SETTINGS_GAIN:
        camera_settings = sl.CAMERA_SETTINGS.CAMERA_SETTINGS_EXPOSURE
        str_camera_settings = "Exposure"
        print("Camera settings: EXPOSURE")
    elif camera_settings == sl.CAMERA_SETTINGS.CAMERA_SETTINGS_EXPOSURE:
        camera_settings = sl.CAMERA_SETTINGS.CAMERA_SETTINGS_WHITEBALANCE
        str_camera_settings = "White Balance"
        print("Camera settings: WHITEBALANCE")
    elif camera_settings == sl.CAMERA_SETTINGS.CAMERA_SETTINGS_WHITEBALANCE:
        camera_settings = sl.CAMERA_SETTINGS.CAMERA_SETTINGS_BRIGHTNESS
        str_camera_settings = "Brightness"
        print("Camera settings: BRIGHTNESS")


def record(cam, runtime, mat):
    vid = sl.ERROR_CODE.ERROR_CODE_FAILURE
    out = False
    while vid != sl.ERROR_CODE.SUCCESS and not out:
        filepath = input("Enter filepath name: ")
        vid = cam.enable_recording(filepath)
        print(repr(vid))
        if vid == sl.ERROR_CODE.SUCCESS:
            print("Recording started...")
            out = True
            print("Hit spacebar to stop recording: ")
            key = False
            while key != 32:  # for spacebar
                err = cam.grab(runtime)
                if err == sl.ERROR_CODE.SUCCESS:
                    cam.retrieve_image(mat)
                    cv2.imshow("ZED", mat.get_data())
                    key = cv2.waitKey(5)
                    cam.record()
        else:
            print("Help: you must enter the filepath + filename + SVO extension.")
            print("Recording not started.")
    cam.disable_recording()
    print("Recording finished.")
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()