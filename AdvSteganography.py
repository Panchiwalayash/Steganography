import cv2
import sys
from warnings import filterwarnings
import numpy as np
from time import sleep, time
import copy
import vigenere as Cryptography
import random
import os

filterwarnings('ignore')

sourcePath = "original.jpg"
destinationPath = "stagneography.png"

enType = {'raw':0, 'rq':1, 'dq':2, 'b':10}

def encryptPixel(char, image, row, col):
    num = bin(ord(char)+1024)
    HSg, MSg, LSg = num[-9:-6], num[-6:-3], num[-3:]

    b,g,r = image[row][col]
    b,g,r = (b//8)*8, (g//8)*8, (r//8)*8
    b += int(HSg,2)
    g += int(MSg,2)
    r += int(LSg,2)
    return b,g,r


def decryptPixel(image, row, col):
    EOM = 0
    b,g,r = image[row][col]
    b,g,r = b%8, g%8, r%8
    if b > 3:
        EOM = 1
    b += 8
    g += 8
    r += 8
    char = "".join([bin(b)[-3:], bin(g)[-3:], bin(r)[-3:]])
    char = chr(int(char,2))
    return char, EOM

def rawEncoding(originalImg, text):
    newImg =  copy.deepcopy(originalImg)
    row = 0
    col = 0

    # hiding the message in the image
    for i in text:
        if row == originalImg.shape[0]:
            print("ERROR: Message too large!")
            break

        b,g,r = encryptPixel(i, originalImg, row, col)
        
        newImg[row][col] = (b,g,r)

        col += 1
        if col == originalImg.shape[1]:
            row+=1
            col=0

    if row != originalImg.shape[0]:
        b,g,r = originalImg[row][col]
        b = (b//8)*8+7
        newImg[row][col] = (b,g,r)
    
    return newImg

def hideMessage(originalImg= None, encoding=enType['raw'], ret=False, text=None, encryption=False, sl=False):
    if type(originalImg) == type(None):
        originalImg= cv2.imread(sourcePath)
    if text == None:
        text=input("write message: ")
    # initialization of required variables:
    newImg = copy.deepcopy(originalImg)

    if encryption:
        key = int(input("Enter Secret Key (number):"))
        text = Cryptography.encrypt(text, key)

    if encoding == enType['raw']:
        newImg = rawEncoding(originalImg, text)

    elif encoding == enType['rq']:
        H, W ,n = originalImg.shape
        p1 = originalImg[:H//2,:W//2]
        p2 = originalImg[:H//2,W//2:]
        p3 = originalImg[H//2:,:W//2]
        p4 = originalImg[H//2:,W//2:]
        newImg[:H//2,:W//2] = rawEncoding(p1, text)
        newImg[:H//2,W//2:] = rawEncoding(p2, text)
        newImg[H//2:,:W//2] = rawEncoding(p3, text)
        newImg[H//2:,W//2:] = rawEncoding(p4, text)

    elif encoding == enType['dq']:
        H, W ,n = originalImg.shape
        p1 = originalImg[:H//2,:W//2]
        p2 = originalImg[:H//2,W//2:]
        p3 = originalImg[H//2:,:W//2]
        p4 = originalImg[H//2:,W//2:]

        ind = 0
        msg = ["","","",""]
        for i in text:
            msg[ind] += i
            ind = (ind+1)%4

        newImg[:H//2,:W//2] = rawEncoding(p1, msg[0])
        newImg[:H//2,W//2:] = rawEncoding(p2, msg[1])
        newImg[H//2:,:W//2] = rawEncoding(p3, msg[2])
        newImg[H//2:,W//2:] = rawEncoding(p4, msg[3])

    else:
        print("Error occured! Invalid encoding technique")
    

    if sl:
        path = "en"+str(random.randrange(1e9, 1e15)) + 'stg.png'
        destinationPath =  os.getcwd() + "/" + path
        
    cv2.imwrite(destinationPath, newImg)

    if ret:
        if sl:
            return path
        return newImg
    else:
        cv2.destroyAllWindows()


def rawDecoding(image):
    msg = ""
    char = ""
    EOM = 0
    row = 0
    col = 0

    while EOM == 0 and ( row < image.shape[0]):
        char, EOM = decryptPixel(image, row, col)
        msg += char
        
        col += 1
        if col == image.shape[1]:
            row+=1
            col=0

    # print("Hidden Message:",msg[:-1])
    return msg[:-1]


def readMessage(image = None, encoding=enType['raw'], ret=False, encryption=False):
    if type(image) == type(None):
        image = cv2.imread(sourcePath)
    msg = ""

    if encoding == enType['raw']:
        msg = rawDecoding(image)

    elif encoding == enType['rq']:
        H, W ,n = image.shape
        p1 = image[:H//2,:W//2]
        p2 = image[:H//2,W//2:]
        p3 = image[H//2:,:W//2]
        p4 = image[H//2:,W//2:]

        msg1 = rawDecoding(p1)
        msg2 = rawDecoding(p2)
        msg3 = rawDecoding(p3)
        msg4 = rawDecoding(p4)

        for i in range(max(len(msg1),len(msg2),len(msg3),len(msg4))):
            try:
                oc = {}
                oc[msg1[i]] = msg1[i] if msg1 in oc.keys() else 1
                oc[msg2[i]] = msg2[i] if msg2 in oc.keys() else 1
                oc[msg3[i]] = msg3[i] if msg3 in oc.keys() else 1
                oc[msg4[i]] = msg4[i] if msg4 in oc.keys() else 1

                # print(max(oc), oc)
                msg += max(oc)

            except IndexError:
                print("Error Occured! Message may have been corupted or Wrong encoding is used")
                return

    elif encoding == enType['dq']:
        H, W ,n = image.shape
        p1 = image[:H//2,:W//2]
        p2 = image[:H//2,W//2:]
        p3 = image[H//2:,:W//2]
        p4 = image[H//2:,W//2:]

        msg1 = rawDecoding(p1)
        msg2 = rawDecoding(p2)
        msg3 = rawDecoding(p3)
        msg4 = rawDecoding(p4)

        msg = ''
        for i in range(len(msg1)):
            try:
                msg += msg1[i]
                msg += msg2[i]
                msg += msg3[i]
                msg += msg4[i]
            except IndexError:
                break

    else:
        print("Error occured! Invalid encoding technique")

    if encryption:
        key = int(input("Enter Secret Key (number):"))
        msg = Cryptography.decrypt(msg, key)

    if ret:
        return msg
    else:
        print("final:",msg)
        cv2.destroyAllWindows()
        open("/".join(destinationPath.split("/")[:-1])+"Message.txt",'wb').write(bytes(msg, 'utf-8'))


def hideMessageInVideo(cap=None, encoding=enType['b'], encryption=False, text=None, sl=False):

    if type(cap) == type(None):
        cap= cv2.VideoCapture(sourcePath)

    # initialization of required variables:
    if text == None:
        text = input("write message: ")

    if encryption:
        key = int(input("Enter Secret Key (number):"))
        text = Cryptography.encrypt(text, key)
    
    text += 'Ǹ'
    row = 0
    col = 0

    windowName = "source video"
    cv2.namedWindow(windowName)

    codec = cv2.VideoWriter_fourcc(*'HFYU') # HFYU for faster but more uncompressed video output
    resolution = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    # Find OpenCV version
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

    if int(major_ver)  < 3 :
        framerate = cap.get(cv2.cv.CV_CAP_PROP_FPS)
        totalFrames = cap.get(cv2.cv.CAP_PROP_FRAME_COUNT)
    else :
        framerate = cap.get(cv2.CAP_PROP_FPS)
        totalFrames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    destinationPath = ""

    if sl:
        path = "en" + str(random.randrange(1e9, 1e15)) + 'stg.avi'
        destinationPath =  path

    VideoOutput = cv2.VideoWriter(destinationPath, codec, framerate, resolution)

    if cap.isOpened():
        ret, frame = cap.read()
    else:
        ret = False

    f = 0
    index = 0

    partition= 500
    pn = 0
    
    while totalFrames > f:
        print("\rProcessing: {:.2f}%".format((f*100)/totalFrames), end="")
        f+=1

        newFrame = frame

        if encoding == enType['b']:
            if index < len(text):
                for x in range(frame.shape[0]):
                    if x == 0 or x == frame.shape[0]-1:
                        for y in range(frame.shape[1]):

                            og = frame[x][y]
                            
                            b,g,r = encryptPixel(text[index], frame, x, y)
                            newFrame[x][y] = (b,g,r)

                            #print(og, frame[x][y], newFrame[x][y], (b,g,r), text[index], decryptPixel(newFrame, x, y), x, y)

                            index += 1
                            if index == len(text):
                                break
                    else:
                        b,g,r = encryptPixel(text[index], frame, x, 0)
                        newFrame[x][0] = (b,g,r)
                        index += 1
                        #print(frame[x][y], newFrame[x][y], (b,g,r), text[index], decryptPixel(newFrame, x, y), x, y)

                        if index < len(text):
                            b,g,r = encryptPixel(text[index], frame, x, frame.shape[1]-1)
                            newFrame[x][0] = (b,g,r)
                            index += 1
                            #print(frame[x][y], newFrame[x][y], (b,g,r), text[index], decryptPixel(newFrame, x, y), x, y)

                    if index == len(text):        
                        break
        else:
            part = text[pn*partition:(pn+1)*partition]
            newFrame = hideMessage(encoding, ret=True, text=part)
            pn+=1
    
        
        VideoOutput.write( newFrame if index < len(text) else frame)
        ret, frame = cap.read()
    # print("\rProcessing: {:.5}%".format((f*100)/totalFrames))
    cv2.destroyAllWindows()

    if sl:
        return path


def readMessageInVideo(encoding= enType['b'], encryption=False, cap= None, ret=False):    
    if type(cap) == type(None):
        cap = cv2.VideoCapture(sourcePath)
    msg = ""
    char = ""
    EOM = 0

    resolution = (cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Find OpenCV version
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

    if int(major_ver)  < 3 :
        framerate = cap.get(cv2.cv.CV_CAP_PROP_FPS)
        totalFrames = cap.get(cv2.cv.CAP_PROP_FRAME_COUNT)
    else :
        framerate = cap.get(cv2.CAP_PROP_FPS)
        totalFrames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    if cap.isOpened() == False:
        print("Error opening file")
        return
    
    f = 0
    
    while totalFrames > f and EOM == 0:
        print("\rProcessing: {:.2f}%".format((f*100)/totalFrames), end="")
        f+=1
        row = 0
        col = 0 
        ret, frame = cap.read()

        if encoding == enType['b']:
            for x in range(frame.shape[0]):
                if (x == 0) or (x == frame.shape[0]-1):
                    for y in range(frame.shape[1]):
                        char, EOM = decryptPixel(frame, x, y)
                        msg += char
                        if EOM == 1:
                            break
                else:
                    char, EOM = decryptPixel(frame, x, 0)
                    msg += char
                    if EOM == 0:
                        char, EOM = decryptPixel(frame, x, frame.shape[1]-1)
                        msg += char
                if EOM == 1:
                    break
        else:
                msg += readMessage(image=frame, encoding=encoding, ret=True)
    cv2.destroyAllWindows()

    if encryption:
        key = int(input("Enter Secret Key (number):"))
        msg = Cryptography.encrypt(msg, key)
    
    if ret:
        return msg[:-1]
    
    print("\rProcessing: 100%  ")
    print("Hidden Message:",msg[:-1])
    open("/".join(destinationPath.split("/")[:-1])+"Message.txt",'wb').write(bytes(msg[:-1], 'utf-8'))


def play():
    cap = cv2.VideoCapture(sourcePath)
    ret = True
    framerate = cap.get(cv2.CAP_PROP_FPS)
    totalFrames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    print(totalFrames,framerate)
    f=0
    t0 = time()

    while totalFrames > f:
        ret, frame = cap.read()
        if (cv2.waitKey(1) & 0xFF == ord('s')) or ret == False:
            break

        resolution = (int(frame.shape[1]/2), int(frame.shape[0]/2))
        frame = cv2.resize(frame, resolution, interpolation = cv2.INTER_AREA)
        sleep(0.5/framerate)
        cv2.imshow(sourcePath, frame)
        f+=1
        print("\r{:.2f}".format(time()-t0), end='')

    cap.release()
    cv2.destroyAllWindows()


def main():
    '''
stagneography.py ops src dest

arguments: Takes 3 arguments

1.ops   the operation you want to perform
<VALUES>
    --help  to read documentation

    play    plays the source video
    <REQUIRE>
        'src'
    <ALTERNATE>
    -p

    H   -   to hide message in image passed in 'src' argument and generated stagneography image name passed in 'dest' argument
    <REQUIRE>
        'src'
        'dest'
    <OUTPUTS>
        Generates stagneography image stored on 'dest' path.
        Extension: PNG

    R   -   to read the message hidden in the image. image path is passed as 'src' argument
    <REQUIRE>
        'src'
    <OUTPUTS>
        Message.txt file containing the message extracted from the image
    
    VH   -   to hide message in video passed in 'src' argument and generated stagneography video name passed in 'dest' argument
    <REQUIRE>
        'src'
        'dest'
    <OUTPUTS>
        Generates stagneography video stored on 'dest' path.
        Extension: AVI

    VR   -   to read the message hidden in the video. video path is passed as 'src' argument
    <REQUIRE>
        src
    <OUTPUTS>
        Message.txt file containing the message extracted from the video

2.src   source image path with extension that is to be read

3.dest  destination image name for generated stagneography image


VALID COMMANDS:
stagneography.py --help
stagneography.py play src
stagneography.py -p src
stagneography.py R src enType
stagneography.py H src dest enType
stagneography.py VR src enType
stagneography.py VH src dest enType
    '''

    global sourcePath, destinationPath

    try:
        if len(sys.argv) == 1:
            print("What operation you want to perform?")
            print("1. Read message hidden in Image")
            print("2. Hide message in a Image")
            print("3. Read message hidden in Video")
            print("4. Hide message in a Video")
            ops = int(input("Enter your choice: "))
            sourcePath = input("Enter source file path: ")
            open(sourcePath,'r').close()
                
            if ops%2 == 0:
                destinationPath = input("Enter destination file path (without extension): ")
            
            # Read hidden message command
            if ops == 1:
                encoding = input("Enter Encoding: ")
                readMessage(encoding= enType[encoding])

            # Hide message in image command
            elif ops ==2:
                destinationPath = destinationPath + ".png"
                open(destinationPath,'w').close()
                encoding = input("Enter Encoding: ")
                hideMessage(encoding= enType[encoding])
                print("Generated image name:", destinationPath)

            # Read hidden message in Vide command
            elif ops == 3:
                encoding = input("Enter Encoding: ")
                readMessageInVideo(encoding= enType[encoding])

            # Hide message in Video command
            elif ops == 4:
                destinationPath = destinationPath + ".avi"
                open(destinationPath,'w').close()
                encoding = input("Enter Encoding: ")
                hideMessageInVideo(encoding= enType[encoding])
                print("Generated video name:", destinationPath)

            else:
                print("Error: Invalid choice")
                print("Try: stagneography --help command")
                return

        # help command
        elif sys.argv[1] == '--help':
            print(main.__doc__)
            return

        # play source video
        elif sys.argv[1] == 'play' or sys.argv[1] == '-p':
            sourcePath = sys.argv[2]
            open(sourcePath,'r').close()
            play()
            return

        # Read hidden message command
        elif sys.argv[1] == 'R':
            sourcePath = sys.argv[2]
            encoding = sys.argv[3]
            open(sourcePath,'r').close()
            readMessage(encoding= enType[encoding])

        # Hide message in image command
        elif sys.argv[1] == 'H':
            sourcePath = sys.argv[2]
            destinationPath = sys.argv[3]+".png"
            encoding = sys.argv[4]
            open(sourcePath,'r').close()
            open(destinationPath,'w').close()
            hideMessage(encoding= enType[encoding])
            print("Generated image name:", destinationPath)

        # Read hidden message in Vide command
        elif sys.argv[1] == 'VR':
            sourcePath = sys.argv[2]
            encoding = sys.argv[3]
            open(sourcePath,'r').close()
            readMessageInVideo(encoding= enType[encoding])

        # Hide message in Video command
        elif sys.argv[1] == 'VH':
            sourcePath = sys.argv[2]
            destinationPath = sys.argv[3]+".avi"
            encoding = sys.argv[4]
            open(sourcePath,'r').close()
            open(destinationPath,'w').close()
            hideMessageInVideo(encoding= enType[encoding])
            print("Generated Video name:", destinationPath)

        # Invalid command
        else:
            print("Invalid command. Try --help")

    # Missing Arguments
    except IndexError:
        print("Missing arguments")
        print(main.__doc__)
    
    except FileNotFoundError as e:
        print(f"No such file exist\n" f"{e}")


if __name__ == "__main__":
    main()