from typing import Tuple

from settings import ANIMALS, SCORES

class Piece:
    '''棋子类'''
    def __init__(self,name: str, color: Tuple[int,int,int]) -> None:
        # 动物的名字
        self.name = name
        # 动物的颜色，用它来区分是哪一队的棋子
        self.color = color
        # 动物的权重
        self.score = SCORES[name]

        # 设置动物的天敌和食物
        # 大象和老鼠比较特殊，其他都是按照列表里的顺序排列的
        if name == 'elephant':
            self.enemy = {'mouse'}
            self.food = { a for a in ANIMALS[1:-1]}
        elif name == 'mouse':
            self.enemy = {a for a in ANIMALS[1:-1]}
            self.food = {'elephant'}
        else:
            index = ANIMALS.index(name)
            self.enemy = {a for a in ANIMALS[:index]}
            self.food = {a for a in ANIMALS[index+1:]}
