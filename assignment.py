import cv2 as cv
import numpy as np
from PIL import Image

img = cv.imread("./coins.jpg", cv.IMREAD_UNCHANGED)
img2 = cv.imread("./input.jpg", cv.IMREAD_UNCHANGED)

# resize image
def resize_img(input_path,output_path,new_size):
    with Image.open(input_path) as img:
        new_img=img.resize(new_size)
        new_img.save(output_path)
        new_img.show("Modified Image")
            
input_path="sample.jpg"
output_path="output_task1.jpg"
new_size= (256,256)




class coinCounter():
        
    def __init__(self,Image,wHeight,wWidth):


        self.Image = Image
        self.wWidth =wWidth
        self.wHeight =wHeight
        self.totalObjects = 0
        # self.Image = cv.resize(self.Image, (256,256), interpolation = cv.INTER_AREA)

        self.rgb2gray()
        self.gray2bin(165)
        self.show("Binary Image ",self.Image)



    def show(self,prompt, img):
        cv.namedWindow(prompt, cv.WINDOW_NORMAL)
        cv.imshow(prompt, img)
        cv.waitKey(0)


    def setChannels(self):
        # arranging channels to rgb from bgr but that is no longer required i suppose

        blue = self.Image[:, :, 0]
        green = self.Image[:, :, 1]
        red = self.Image[:, :, 2]
        self.Image[:, :, 0] = red
        self.Image[:, :, 1] = green
        self.Image[:, :, 2] = blue
        return self.Image


    def showChannel(image, idx, prompt,self):
        temp = np.array(image)
        temp[:, :, (idx+1) % 3] = 0
        temp[:, :, (idx+2) % 3] = 0

        self.show(prompt=prompt, img=temp)


    # converts rgb to grayscale image by taking maximum intensity values
    
    def rgb2gray(self):
        blue = self.Image[:, :, 0]
        green = self.Image[:, :, 1]
        red = self.Image[:, :, 2]
        self.Image = np.maximum(blue, green, red)
        self.show("Gray Scale Image", self.Image)
        return self.Image


    def gray2bin(self,threshold):
        self.Image = np.where(self.Image < threshold, 0, 255).astype(np.uint8)
        return self.Image

    # the size of window should be such that it must be less than the space between two objects
    # not every zero  is object and not every non zero is boundary

    # a window is assigned to the object if it is all dark or maxDark and
    # the pixels in its neighbour (in our traversal we will always move from left to right and then from top to bottom)
    # so our concerned condition will be (top is object || left pixel is object)
    # final label will be logical or of above condition applied on (every element of left most coloumn and top most row)
    # have been assigned to some object
    # if it is start than we shall assign it the object value

    # check the condition where window moves out of the image

    # areas that are object are assigned number between 10 and 10 + n


    # if we find more thatn 50% dark in some area but there is no neighbour then
    # we assign it a speecial value of 10 (that means it has potential to
    # be an object but no neighbour is found yet)


    def checkWindow(self, startRow, startCol):
        dark = 0
        white = 0
        

        for i in range(self.wWidth):
            for j in range(self.wHeight):
                if ((i+startRow) >= np.shape(self.Image)[0] or (j+startCol) >= np.shape(self.Image)[1]):
                    continue
                if (self.Image[i+startRow][j+startCol] == 0):
                    dark += 1
                else:
                    white += 1

        isDark = dark >= white

        if (isDark == True ):
            isNibrObj = self.isNeighbourObj(startRow, startCol)

            if(isNibrObj[0] == True):
                if (isNibrObj[1] == 10):
                    self.totalObjects += 1

                    self.labelWindow(startRow, startCol, 128 + self.totalObjects * 8)

                    # this condition can be improved
                    self.Image = np.where(self.Image==10,128 + self.totalObjects * 8,self.Image)

                else:
                    self.labelWindow( startRow, startCol,isNibrObj[1] )
                    self.Image = np.where(self.Image==10,isNibrObj[1],self.Image)


            else:
                self.labelWindow( startRow, startCol, 10)


            return

            #  that means this window is undoubtedly the part of a object

            #  that means this window is undoubtedly the part of a boundary


    def isNeighbourObj(self, startRow, startCol):
        # tells wheather their is any object in the neighbours or not
        if (startRow - 1 < 0 and startCol-1 < 0):
            # that means we are at start
            return False, 0
        
        searchStartRow = startRow - 1
        searchStartCol = startCol - 1
        isObj = False


        neighboursAtTop = []
        neighboursAtLeft = []



        for i in range(self.wWidth):

            if ((searchStartRow) >= np.shape(self.Image)[0] or (startCol + i) >= np.shape(self.Image)[1] or len(neighboursAtTop) > 0):
                continue

            isObj = self.Image[searchStartRow][startCol + i] != 0 and self.Image[searchStartRow][startCol + i] != 255

            if (isObj == True):
                neighboursAtTop.append(self.Image[searchStartRow][startCol + i])

               
        for i in range(self.wHeight):
            if ((startRow + i) >= np.shape(self.Image)[0] or (searchStartCol) >= np.shape(self.Image)[1] or len(neighboursAtLeft) > 0):
                continue
            isObj = self.Image[startRow + i][searchStartCol] != 0 and  self.Image[startRow + i][searchStartCol] != 255
            if (isObj == True):
                neighboursAtLeft.append(self.Image[startRow + i][searchStartCol])
              
        

        topNeiSet = list(set(neighboursAtTop))
        leftNeiSet=list(set(neighboursAtLeft))
        if(len(neighboursAtLeft)==0 or len(neighboursAtTop)==0):
            if(len(neighboursAtLeft)!=0):

                return True, neighboursAtLeft[0]
            if(len(neighboursAtTop)!=0):

                return True, neighboursAtTop[0]

            return False,0
        
        
        # lines below will only execute if both of the lists are non zero

        # code below is based on the assumption that the window will encounter at most 1 distinct neighbour at top and one at left




        if(topNeiSet[0] != leftNeiSet[0] and topNeiSet[0] !=10 and leftNeiSet[0]!=10):
            #that means we have two different neighbours assigned so
            # print("reducing total objects by 1")
            self.totalObjects -= 1
            
            # assigning window at left, the label of window at top

            
            self.Image = np.where(self.Image == leftNeiSet[0],topNeiSet[0],self.Image)
          
            return True,topNeiSet[0]

       # if window has same neighbours then  
        return True,topNeiSet[0] 




    def labelWindow(self, startRow, startCol, label):
        # marks whole window with some label decided by search
        for i in range(self.wHeight):
            for j in range(self.wWidth):
                if ((i+startRow) >= np.shape(self.Image)[0] or (j+startCol) >= np.shape(self.Image)[1]):
                    continue
                self.Image[i+startRow][j+startCol] = label


    def countObjects(self):
        # stride is automically set here
        # i, j means the next startRow and startCol
    
        i = 0
        rows, cols = np.shape(self.Image)
        while (i < rows):
            rows, cols = np.shape(self.Image)
            j = 0
            while(j<cols):
            # for j in range(cols):
                self.checkWindow(i,j)
                j += self.wWidth
            i += self.wHeight
            
        print("total objects ", self.totalObjects)
        self.show((f"Segmented Image with {self.totalObjects} coins"),self.Image)

# counter = coinCounter(img,10,10)

# counter.countObjects()

resize_img(input_path,output_path,new_size)
counter = coinCounter(img2,10,10)

counter.countObjects()


