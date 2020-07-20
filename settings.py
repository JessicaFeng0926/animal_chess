import os 

# 从大到小排列的动物
ANIMALS = ['elephant','lion','tiger','leopard','wolf','dog','cat','mouse']
# 不同动物的基础权重
SCORES = {'elephant':8,'lion':7,'tiger':5,'leopard':4,'wolf':3,'dog':2,'cat':1,'mouse':6}


# 窗口大小
WINDOW_WIDTH = 580
WINDOW_HEIGHT = 680

# 棋盘左上角坐标
LEFT_OF_BOARD = 50
TOP_OF_BOARD = 50

# 棋盘大小
BOARD_SIZE = 480

# 格子大小
CELL_SIZE = 120


# 颜色
SEA_GREEN = (78, 238, 148)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 191, 255)
RED = (255, 20, 147)
YELLOW = (255, 255, 0)

# 文件夹路径
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IMAGE_DIR = os.path.join(BASE_DIR,'images')

# 帧速率
FPS = 40