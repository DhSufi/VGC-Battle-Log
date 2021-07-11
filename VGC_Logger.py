import os
import device
import numpy as np
import cv2
import pytesseract
from multiprocessing import Process, Queue
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def choose_capturecard():
    # print OpenCV version
    print("OpenCV version: " + cv2.__version__)

    # Get camera list
    device_list = device.getDeviceList()
    etiqueta = 0

    for name in device_list:
        print(str(etiqueta) + ': ' + name)
        etiqueta += 1

    recuento = etiqueta - 1

    if recuento < 0:
        print("No device is connected")
        return

    mensaje = "Select a camera (0 to " + str(recuento) + "): "
    try:
        capture_number = int(input(mensaje))
    except Exception:
        print("It's not a number!")
        print()
        return choose_capturecard()

    if (capture_number > recuento) or capture_number < 0:
        print("Invalid number! Retry!")
        print()
        return choose_capturecard()

    return capture_number


def checkpoint(myframe, value):
    contornos, hierarchy = cv2.findContours(myframe, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contornos:
        area = cv2.contourArea(cnt)
        # print(area)
        if area > value:
            # cv2.drawContours(frame, cnt, -1, (255, 0, 0), 3)
            return True
        else:
            return False


def checktextlength(myframe):
    my_list = []

    x1 = 90
    x2 = 190
    for cuenta1 in range(10):
        px = myframe[610:620, x1:x2]
        my_list.append(checkpoint(px, 890))
        x1 += 110
        x2 += 110

    x3 = 90
    x4 = 190
    for cuenta2 in range(10):
        px = myframe[665:675, x3:x4]
        my_list.append(checkpoint(px, 890))
        x1 += 110
        x2 += 110

    return my_list


def frame_ocr(q):
    my_file = None
    while True:
        if not q.empty():
            img = q.get()
            if img == 'FINISH':
                break
            elif img == 'FILE':
                my_file = q.get()
            elif type(img) == str:
                with open(my_file, "a+") as file:
                    file.write(img + '\n')
                print(img)
            elif type(img) != str:
                texto = pytesseract.image_to_string(img)
                texto = texto.rstrip()
                # texto = texto.lstrip("j")

                with open(my_file, "a+") as file:
                    file.write(texto + '\n')
                print(texto)


def get_hp(myframe):
    contornos, hierarchy = cv2.findContours(myframe, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if contornos == []:
        return 100
    else:
        for cnt in contornos:
            perimetro = cv2.arcLength(cnt, True)
            vertices = cv2.approxPolyDP(cnt, 0.02 * perimetro, True)

            x, y, w, h = cv2.boundingRect(vertices)

            porcentaje = 100 * x / 265
            return round(porcentaje, 2)


def ventana(q, capturadora):

    i = 1
    while True:
        if os.path.exists("Logs/Log" + str(i) + '.txt'):
            i += 1
        else:
            with open("Logs/Log" + str(i) + '.txt', "w+") as file:
                file.write("THIS IS A BETA" + '\n')
            q.put('FILE')
            q.put("Logs/Log" + str(i) + '.txt')
            break

    # Colores
    black_min = np.array([0, 0, 0])         # BLACK CUADRO TEXTO
    black_max = np.array([60, 40, 120])     # BALCK CUADRO TEXTO
    black1_min = np.array([0, 0, 0])        # BLACK HP BAR
    black1_max = np.array([179, 255, 138])  # BALCK HP BAR
    white_min = np.array([0, 0, 145])       # WHITE CUADRO HP
    white_max = np.array([179, 69, 255])    # WHITE CUADRO HP

    # PROGRAMA
    capture = cv2.VideoCapture(capturadora, cv2.CAP_DSHOW)
    capture.set(3, 1280)
    capture.set(4, 720)

    # VARIABLES
    text_read = False
    current_length = None
    previous_length = None
    equal_length = 0

    current_hp1 = 0
    previous_hp1 = 0
    hp1_counter = 0
    were_different1 = False
    printed_hp1 = None

    current_hp2 = 0
    previous_hp2 = 0
    hp2_counter = 0
    were_different2 = False
    printed_hp2 = None

    current_hp3 = 0
    previous_hp3 = 0
    hp3_counter = 0
    were_different3 = False
    printed_hp3 = None

    current_hp4 = 0
    previous_hp4 = 0
    hp4_counter = 0
    were_different4 = False
    printed_hp4 = None

    while True:

        # Leer la capturadora
        success, frame = capture.read()

        FrameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Crear mascara de color
        mask_black = cv2.inRange(FrameHSV, black_min, black_max)
        mask_white = cv2.inRange(FrameHSV, white_min, white_max)

        # PUNTOS DETECTION CUADRO TEXTO NEGRO
        P1 = mask_black[610:620, 20:50]      # Pastilla negra top left
        P2 = mask_black[610:620, 1230:1260]  # Pastilla negra top right
        P3 = mask_black[670:680, 10:30]      # Pastilla negra bot left
        P4 = mask_black[610:620, 1230:1250]  # Pastilla negra bot right
        P5 = mask_black[150:160, 100:200]    # Punto negativo pastilla negra
        P6 = mask_black[150:160, 1100:1200]  # Punto negativo pastilla negra

        # PUNTOS DETECCION CUADRO HP1
        P7 = mask_white[620:693, 6:12]       # white HP1 left 438 (73x6)
        P8 = mask_white[620:693, 288:294]    # white HP1 right 438 (73x6)
        P9 = mask_white[600:610, 120:220]    # white HP1 Punto negativo 1000 (10x100)

        # PUNTOS DETECCION CUADRO HP2
        P10 = mask_white[644:693, 335:345]   # white HP2 left  490 (49*10)
        P11 = mask_white[620:693, 622:628]   # white HP2 right 438 (73x6)
        P12 = mask_white[600:610, 480:580]   # white HP2 punto negativo 1000 (10x100)

        # PUNTOS DETECCION CUADRO HP3
        P13 = mask_white[25:80, 627:633]     # white HP3 left 330
        P14 = mask_white[25:80, 915:921]     # white HP3 right 330
        P15 = mask_white[90:100, 750:850]    # white HP3 punto negativo 1000

        # PUNTOS DETECCION CUADRO HP4
        P16 = mask_white[25:80, 969:975]     # white HP4 left 330
        P17 = mask_white[25:80, 1260:1266]   # white HP4 right 330
        P18 = mask_white[90:100, 1100:1200]  # white HP4 punto negativo 1000

        if checkpoint(P1, 250) and checkpoint(P2, 250) and checkpoint(P3, 150) and checkpoint(P4, 150) and checkpoint(P5, 950) != True and checkpoint(P6, 950) != True:
            if text_read is False:
                current_length = checktextlength(mask_black)
                if previous_length == current_length:
                    equal_length += 1
                    if equal_length == 6:
                        textRegion = frame[585:685, 100:1150]
                        q.put(textRegion)
                        text_read = True
                else:
                    equal_length = 0
                    previous_length = current_length
        else:
            text_read = False
            current_length = None
            previous_length = None
            equal_length = 0
            # print("FINALIZADO LECTURA TEXTO")

        # GET HP1
        if checkpoint(P7, 350) and checkpoint(P8, 350) and checkpoint(P9, 590) != True:
            mask = cv2.inRange(FrameHSV, black1_min, black1_max)
            HP1 = mask[658:662, 16:281]
            current_hp1 = get_hp(HP1)
            if current_hp1 == previous_hp1 and were_different1 == True:
                hp1_counter += 1
            elif current_hp1 != previous_hp1:
                hp1_counter = 0
                were_different1 = True
                previous_hp1 = current_hp1

            if hp1_counter == 7:
                if printed_hp1 != current_hp1:
                    q.put("Slot 1 HP: " + str(round(current_hp1)) + "%")
                    # print("Slot 1 HP: " + str(current_hp1) + "%")
                    printed_hp1 = current_hp1
                    were_different1 = False
                    hp1_counter = 0

       # get HP2
        if checkpoint(P10, 350) and checkpoint(P11, 350) and checkpoint(P12, 590) != True:
            mask = cv2.inRange(FrameHSV, black1_min, black1_max)
            HP2 = mask[658:662, 350:615]
            current_hp2 = get_hp(HP2)
            if current_hp2 == previous_hp2 and were_different2 == True:
                hp2_counter += 1
            elif current_hp2 != previous_hp2:
                hp2_counter = 0
                were_different2 = True
                previous_hp2 = current_hp2

            if hp2_counter == 7:
                if printed_hp2 != current_hp2:
                    q.put("Slot 2 HP: " + str(round(current_hp2)) + "%")
                    # print("Slot 2 HP: " + str(current_hp2) + "%")
                    printed_hp2 = current_hp2
                    were_different2 = False
                    hp2_counter = 0

        # get HP3
        if checkpoint(P13, 265) and checkpoint(P14, 265) and checkpoint(P15, 590) != True:
            mask = cv2.inRange(FrameHSV, black1_min, black1_max)
            HP3 = mask[66:70, 638:903]
            current_hp3 = get_hp(HP3)
            if current_hp3 == previous_hp3 and were_different3 == True:
                hp3_counter += 1
            elif current_hp3 != previous_hp3:
                hp3_counter = 0
                were_different3 = True
                previous_hp3 = current_hp3

            if hp3_counter == 7:
                if printed_hp3 != current_hp3:
                    q.put("Slot 3 HP: " + str(round(current_hp3)) + "%")
                    # print("Slot 3 HP: " + str(current_hp3) + "%")
                    printed_hp3 = current_hp3
                    were_different3 = False
                    hp3_counter = 0

        # get HP4
        if checkpoint(P16, 265) and checkpoint(P17, 265) and checkpoint(P18, 590) != True:
            mask = cv2.inRange(FrameHSV, black1_min, black1_max)
            HP4 = mask[66:70, 980:1245]
            current_hp4 = get_hp(HP4)
            if current_hp4 == previous_hp4 and were_different4 == True:
                hp4_counter += 1
            elif current_hp4 != previous_hp4:
                hp4_counter = 0
                were_different4 = True
                previous_hp4 = current_hp4

            if hp4_counter == 7:
                if printed_hp4 != current_hp4:
                    q.put("Slot 4 HP: " + str(round(current_hp4)) + "%")
                    # print("Slot 4 HP: " + str(current_hp4) + "%")
                    printed_hp4 = current_hp4
                    were_different4 = False
                    hp4_counter = 0

        cv2.imshow("frame", frame)
        # cv2.imshow("frameHSV", textRegion)
        # cv2.imshow("mask black", mask_black)  # SHOW CLEANFEED window

        if cv2.waitKey(1) & 0xFF == ord('q'):
            capture.release()
            cv2.destroyAllWindows()
            q.put('FINISH')
            break


if __name__ == "__main__":
    capturadora = choose_capturecard()
    a = Queue()
    p = Process(target=ventana, args=(a, capturadora,))
    c = Process(target=frame_ocr, args=(a,))

    p.start()
    c.start()
    p.join()
    c.join()