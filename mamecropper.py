import cv2 as cv
import numpy as np
import os

def GarbageRemover(img_path):
    img = cv.imread(img_path)
    assert img is not None, "file could not be read, check with os.path.exists()"
    i = 0
    '''Looking for the GUI'''
    while any(img[i, i] != (0, 0, 255)):
        i += 1
    j = i
    '''Looking for the top left corner of the window'''
    while all(img[j, i - 1] == (0, 0, 255)):
        i -= 1
    while all(img[j - 1, i] == (0, 0, 255)):
        j -= 1
    TopLeftX = j
    TopLeftY = i
    '''Looking for the bottom right corner of the window'''
    j = img.shape[0] - 1
    i = img.shape[1] - 1
    while any(img[j, i] != (0, 0, 255)):
        j -= 1
        i -= 1
    while all(img[j, i + 1] == (0, 0, 255)):
        i += 1
    while all(img[j + 1, i] == (0, 0, 255)):
        j += 1
    BottomRightX = j
    BottomRightY = i
    '''Searching for top left tile sheet pivot point'''
    j = TopLeftX
    i = TopLeftY
    NoBaseColorPixels = False
    NoBaseColorPixelsCounter = 0
    while NoBaseColorPixels == False:
        for k in range(i, i + 4, 1):
            for m in range(j, j + 4, 1):
                if any(img[m, k] != (0, 0, 255)):
                    NoBaseColorPixelsCounter += 1
        if NoBaseColorPixelsCounter >= 16:
            NoBaseColorPixels = True
        else:
            i += 4
            j += 4
            NoBaseColorPixelsCounter = 0
    TLPivotX = j
    TLPivotY = i
    j = BottomRightX
    i = BottomRightY
    '''Searching for bottom right tile sheet pivot point'''
    NoBaseColorPixels = False
    NoBaseColorPixelsCounter = 0
    while NoBaseColorPixels == False:
        for k in range(i - 3, i + 1, 1):
            for m in range (j - 3, j + 1, 1):
                if any(img[m, k] != (0, 0, 255)):
                    NoBaseColorPixelsCounter += 1
        if NoBaseColorPixelsCounter >= 16:
            NoBaseColorPixels = True
        else:
            i -= 4
            j -= 4
            NoBaseColorPixelsCounter = 0
    BRPivotX = j
    BRPivotY = i
    '''Shifting TL and BR pivot points to the edges'''
    while not (all(img[TLPivotX - 3, TLPivotY] == (0, 0, 255)) and
               all(img[TLPivotX - 2, TLPivotY] == (0, 0, 255)) and
               all(img[TLPivotX - 1, TLPivotY] == (0, 0, 255))):
        TLPivotX -= 1
    while not (all(img[TLPivotX, TLPivotY - 3] == (0, 0, 255)) and
               all(img[TLPivotX, TLPivotY - 2] == (0, 0, 255)) and
               all(img[TLPivotX, TLPivotY - 1] == (0, 0, 255))):
        TLPivotY -= 1
    while not (all(img[BRPivotX + 3, TLPivotY] == (0, 0, 255)) and
               all(img[BRPivotX + 2, BRPivotY] == (0, 0, 255)) and
               all(img[BRPivotX + 1, BRPivotY] == (0, 0, 255))):
        BRPivotX += 1
    while not (all(img[BRPivotX, BRPivotY + 3] == (0, 0, 255)) and
               all(img[BRPivotX, BRPivotY + 2] == (0, 0, 255)) and
               all(img[BRPivotX, BRPivotY + 1] == (0, 0, 255))):
        BRPivotY += 1
    '''Cropping the result'''
    crop = img[TLPivotX:BRPivotX, TLPivotY:BRPivotY]
    '''Getting the tile and padding sizes and tiles per row/column amounts'''
    k = 0
    m = 0
    while any(crop[0, k] != (0, 0, 255)):
        k += 1
    while all(crop[0, m + k] == (0, 0, 255)):
        m += 1
    TileSize = k
    Padding = m
    crop = cv.copyMakeBorder(crop, 0, Padding, 0, Padding, cv.BORDER_CONSTANT, value = [0, 0, 255])
    k = 0
    TilesPerRow = int((crop.shape[1] + 1) / (TileSize + 1))
    TilesPerColumn = int((crop.shape[0] + 1) / (TileSize + 1))
    '''Removing the padding'''
    for k in range(0, TilesPerRow, 1):
        crop[0:crop.shape[0], (k * TileSize):(k * TileSize + TileSize)] = crop[0:crop.shape[0], k * (TileSize + Padding):(k * (TileSize + Padding) + TileSize)]
    for k in range(0, TilesPerColumn, 1):
        crop[(k * TileSize):(k * TileSize + TileSize), 0:crop.shape[1]] = crop[k * (TileSize + Padding):(k * (TileSize + Padding) + TileSize), 0:crop.shape[1]]
    nopadding = crop[0:(TilesPerColumn * TileSize - Padding),
                     0:(TilesPerRow * TileSize - Padding)]
    return nopadding
    
def ImageLoad(FolderPath):
    try:
        os.chdir(FolderPath)
    except NotADirectoryError:
        print('Folder not found')
    except PermissionError:
        print('Access denied')
    else:
        print('Folder loaded successfully')
    return os.listdir(FolderPath)

def ImageCropper(ImagePaths, load_path):
    CroppedImages = []
    CroppedImages.extend(ImagePaths)
    height = 0
    width = 0
    i = 0
    for image_path in ImagePaths:
            image_path = load_path + '/' + image_path
            print('Image '+ image_path + ' loaded successfully')
            CroppedImages[i] = GarbageRemover(image_path)
            i += 1
    for image in CroppedImages:
        height += (image.shape[0])
        width = image.shape[1]
    ResultingImage = np.zeros((height, width, 3), np.uint8)
    j = 0
    for image in CroppedImages:
        ResultingImage[j: (j + image.shape[0]), 0:image.shape[1]] = image
        j += (image.shape[0])
    return ResultingImage

def ImageProcessor(load_path, save_name):
    path_array = ImageLoad(load_path)
    processed_image = ImageCropper(path_array, load_path)
    cv.imwrite(save_name, processed_image)
    return 0