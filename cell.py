from typing import Optional
import pygame
from piece import Piece

class Cell:
    '''棋盘上的一个格子'''
    def __init__(self,piece: Piece, left, top, size) -> None:
        # 这个格子上的棋子，初始化的时候必须有棋子
        self._piece = piece
        # 表示是否可以看到这个格子上的棋子是什么
        # 因为一开始棋子都是背过去的，所以默认是False
        self._visible = False
        # 这个格子的矩形
        self._rect = pygame.Rect(left, top, size, size)

    @property
    def visible(self) -> bool:
        '''是否可以看到棋子是什么'''
        return self._visible

    def is_empty(self) -> bool:
        '''这个格子是否是空的'''
        return self._visible and not self._piece

    def meet_enemy(self, cell) -> bool:
        '''参数中的格子是否是本格子的天敌'''
        return cell.visible and cell._piece and cell._piece.name in self._piece.enemy

    def meet_food(self, cell) -> bool:
        '''参数中的格子是否是本格子的食物'''
        return cell.visible and cell._piece and cell._piece.name in self._piece.food


    
    def get_rect(self) -> pygame.Rect:
        return self._rect

    def reverse_piece(self) -> None:
        '''把这个格子上的棋子翻过来'''
        self._visible = True
    
    def set_piece(self, piece : Optional[Piece] = None) -> None:
        '''清空这个格子上的棋子或者往上面放一颗棋子'''
        self._piece = piece
    
    def get_piece(self) -> Optional[Piece]:
        '''返回当前格子上的棋子，它也可能返回None'''
        return self._piece