from PIL import Image
import requests
import base64
import cv2 as cv
import numpy as np
import math
import time

def getA(P,q,n):
    for i in range(len(P)):
        for j in range(len(P[0])):
            P[i][j]=q*P[i][j]+(1-q)/n
    return P

def MatrixMul(A,B):
    rowA=len(A)
    columnA=len(A[0])
    columnB=len(B[0])
    C=[]
    for i in range(rowA):
        row=[]
        for j in range(columnB):
            m=0
            e=0
            while(m<columnA):
                e+=A[i][m]*B[m][j]
                m+=1
            row.append(e)
        C.append(row)
    return C

def Iteration(A,R,n):
    for i in range(n):
       R=MatrixMul(A,R)
    return R

def getNum(path):
    img = cv.imread(path, 0)
    (h, w) = img.shape
    with open("D:/token.txt", 'r', encoding='utf-8') as f:
        token = f.readline()
    url = "https://ocr.cn-north-4.myhuaweicloud.com/v1.0/ocr/handwriting"
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': token}

    imagepath = path
    with open(imagepath, "rb") as bin_data:
        image_data = bin_data.read()
    # 使用图片的base64编码
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    payload = {"image": image_base64,"quick_mode":True,"char_set":'general'}
    response = requests.post(url, headers=headers, json=payload)
    list=response.text.split('\n')
    elementHasRes=''
    for e in list:
        if 'words' in e:
            elementHasRes=e
    elementHasRes=elementHasRes.replace(' ','')
    res=elementHasRes.replace("\"words\":\"","").split("\"")[0]
    if '/' in res:
        res=int(res[0])/int(res[2])
    else:
        res=int(res)
    time.sleep(0.1)
    return res

def getCoordinate(list,h,w):
    border = []
    ave=sum(list)/len(list)

    for i in range(len(list)):
        if list[i]>ave:
            border.append(i)

    test=[]
    for i in range(1,len(border)):
        if(border[i]-border[i-1]>30):
            test.append(border[i-1])
            test.append(border[i])
    res=[0]
    print(test)
    for i in range(len(test)):
        if i%2==1:
            res.append(int((test[i]+test[i-1])/2))
    print(res)
    return res

def getLittleImgList(source):
    img = cv.imread(source, 0)
    ret, img1 = cv.threshold(img, 80, 255, cv.THRESH_BINARY)
    # 获得图像的宽高
    (h, w) = img1.shape
    # 初始化一个跟图像宽一样长的数组，用于记录每一列的黑点个数
    width = [0 for e in range(0, w)]
    # 初始化一个跟图像高一样长的数组，用于记录每一行的黑点个数
    height = [0 for e in range(0, h)]
    #统计每一行的黑点个数
    for i in range(0, h):
        for j in range(0, w):
            if img1[i, j] == 0:
                height[i] += 1
    #统计每一列的黑点个数
    for i in range(0, w):
        for j in range(0, h):
            if img1[j][i] == 0:
                width[i] += 1
    #新建空白图片
    img2 = np.zeros((h, w, 3), np.uint8)
    img3 = np.zeros((h, w, 3), np.uint8)
    img2.fill(255)
    img3.fill(255)
    #描绘峰值图
    for i in range(0, h):
        for j in range(0,height[i]):
            img2[i, j] = 0
    for i in range(0, w):
        for j in range(h - width[i], h):
            img3[j, i] = 0
    #保存图片
    cv.imwrite("D:/h.jpg", img2)
    cv.imwrite("D:/w.jpg", img3)
    #获取坐标
    column=getCoordinate(width,h,w)
    column.append(w)
    row=getCoordinate(height,h,w)
    row.append(h)
    #按坐标进行切割
    res=[]
    x=1
    y=1
    for i in range(len(row)-1):
        for j in range(len(column)-1):
            cutImg=img[row[i]:row[i+1],column[j]:column[j+1]]
            #cv.imshow("img",cutImg)
            imgName="D:/"+str(x)+str(y)+".png"
            res.append(imgName)
            cv.imwrite(imgName,cutImg)
            y+=1
        x+=1
        y=1
    return res

def handleImg(path):
    image = Image.open(path)
    imageL = image.convert('L')
    threshold=200
    table=[]
    for i in range(256):
        if i<threshold:
            table.append(1)
        else:
            table.append(0)
    Img=imageL.point(table,'1')
    Img.save('D:/temp.png')
    return getLittleImgList('D:/temp.png')

def main(source):
    imgList = handleImg(source)
    P = []
    count = 0
    temp = []
    pageNum = math.sqrt(len(imgList))

    for img in imgList:
        num = getNum(img)
        temp.append(num)
        count += 1
        if count % pageNum == 0:
            count = 0
            P.append(temp)
            temp = []

    A = getA(P, 0.85, len(P))
    R = [[0.25], [0.25], [0.25], [0.25]]
    R_10 = Iteration(A,R,10)
    for e in R_10:
      print(e[0])

main("D:/T.png")