from typing import List, Dict, Tuple
import random
import os

import pygame

from piece import Piece
from cell import Cell
import settings

class Board:
    '''棋盘类'''
    def __init__(self) -> None:
        # 用于存放16颗棋子
        pieces: List[Piece] = []
        # 添加红方的8颗棋子
        for name in settings.ANIMALS:
            pieces.append(Piece(name,'red'))
        # 添加蓝方的8颗棋子
        for name in settings.ANIMALS:
            pieces.append(Piece(name,'blue'))
        # 随机打乱棋子的顺序
        random.shuffle(pieces)
        # 用于存放棋盘上的16个格子
        # 这些格子是4行4列
        self._container: List[List[Cell]] = []
        # 把16颗棋子放到16个格子上
        i = 0
        for row in range(4):
            row_of_board = []
            for col in range(4):
                row_of_board.append(
                    Cell(pieces[i], 
                         settings.LEFT_OF_BOARD + col*settings.CELL_SIZE,
                         settings.TOP_OF_BOARD + row*settings.CELL_SIZE,
                         settings.CELL_SIZE)
                    )
                i += 1
            self._container.append(row_of_board)
        self._turn = random.choice(['red','blue'])
        # 保存的用户第一次点击的坐标
        self.user_coordinates = None
        # 10次没有互相吃，就平局
        self.not_eat = 0
    
    @property
    def turn(self) -> str:
        return self._turn
    
        
    def change_turn(self) -> None:
        '''交出出牌权'''
        if self._turn == 'red':
            self._turn = 'blue'
        else:
            self._turn = 'red'
    
    def get_turn_color(self) -> Tuple[int,int,int]:
        '''获取这一轮对应的颜色'''
        return settings.RED if self._turn == 'red' else settings.BLUE

    def draw_board(self, surface: pygame.Surface, images: Dict[str,pygame.Surface] ) -> None:
        '''展示棋盘'''
        for row in range(4):
            for col in range(4):
                cell = self._container[row][col]
                cell_rect = cell.get_rect()
                # 不可见就绘制问号图片
                if not cell.visible:
                    cell_stretched_image = images['back']
                    surface.blit(cell_stretched_image, cell_rect)
                # 有棋子就绘制棋子图片
                elif cell.get_piece():
                    piece = cell.get_piece()
                    color = piece.color
                    name = piece.name
                    cell_stretched_image = images[f'{color}_{name}']
                    surface.blit(cell_stretched_image,cell_rect)
                # 没有棋子就绘制绿色正方形
                else:
                    pygame.draw.rect(surface,settings.SEA_GREEN,cell_rect)
                    pygame.draw.rect(surface,settings.BLACK,cell_rect,1)
        if self.user_coordinates:
            cell = self.get_cell_by_coordinates(*self.user_coordinates)
            cell_rect = cell.get_rect()
            pygame.draw.rect(surface,settings.YELLOW,cell_rect,2)
    
    def is_on_board(self, x, y):
        '''判断一个坐标是否在棋盘上'''
        return x >= settings.LEFT_OF_BOARD and x < settings.LEFT_OF_BOARD + settings.BOARD_SIZE \
            and y >= settings.TOP_OF_BOARD and y < settings.TOP_OF_BOARD + settings.BOARD_SIZE
    
    def is_neighbor(self,start,end) -> bool:
        '''检查两个格子是否是相邻的'''
        # 只有四个方向可以相邻
        for r,c in [(1,0),(-1,0),(0,1),(0,-1)]:
            if (start[0]+r,start[1]+c) == end:
                return True
        return False

    def get_row_col_by_coordinates(self, x, y):
        '''根据坐标，获取格子的行和列'''
        for row in range(4):
            for col in range(4):
                cell = self._container[row][col]
                cell_rect = cell.get_rect()
                if x>=cell_rect.left and x<cell_rect.right and y>=cell_rect.top and y<cell_rect.bottom:
                    return row,col
    
    def get_cell_by_coordinates(self,x,y) -> Cell:
        '''根据用户点击的坐标获取格子'''
        for row in range(4):
            for col in range(4):
                cell = self._container[row][col]
                cell_rect = cell.get_rect()
                if x>=cell_rect.left and x<cell_rect.right and y>=cell_rect.top and y<cell_rect.bottom:
                    return cell
    
    def get_cell_by_row_col(self,row,col) -> Cell:
        '''根据行和列获取格子'''
        return self._container[row][col]

    def is_valid_end(self,end_cell):
        '''判断是否是有效的终点'''
        # 必须是可见的相邻的对方格子或者空格子
        # 相邻不需要判断，因为在搜索的时候就会只搜索邻居
        return end_cell.visible and (not end_cell.get_piece() or end_cell.get_piece().color != self.turn) 
        

    def collect_coordinates_and_make_move(self,x,y):
        '''收集用户点击的坐标并根据情况来下棋'''
        # 这一切的前提是x,y是棋盘上的坐标
        if self.is_on_board(x,y):
            cell = self.get_cell_by_coordinates(x,y)
            # 第一次点击
            if not self.user_coordinates:
                # 遇到没翻的棋就翻棋，并且交出出牌权
                if not cell.visible:
                    cell.reverse_piece()
                    self.change_turn()
                # 如果是自己的棋，就保存起来
                elif cell.get_piece() and cell.get_piece().color == self._turn:
                    self.user_coordinates = (x,y)
                # 其他的棋情况有：对方的棋，空格子。这些都不需要处理。
            # 第二次点击
            else:
                start_row_col = self.get_row_col_by_coordinates(*self.user_coordinates)
                end_row_col = self.get_row_col_by_coordinates(x,y)
                # 如果是对方的棋或者空格子并且两个格子是邻居，都是有效的，可以走棋了
                if cell.visible and (not cell.get_piece() or cell.get_piece().color != self._turn) and self.is_neighbor(start_row_col,end_row_col):
                    self.make_move_by_coordinates(self.user_coordinates,(x,y))
                    self.change_turn()
                # 不管有没有效，连续点击两次后都应该清空保存的坐标
                self.user_coordinates = None

    def make_computer_move(self,move: Tuple[Cell,...],surface) -> None:
        '''根据电脑给出的格子走棋'''
        if len(move) == 1:
            cell = move[0]
            cell.reverse_piece()
            self.change_turn()
        else:
            start_cell, end_cell = move
            start_rect = start_cell.get_rect()
            pygame.draw.rect(surface,settings.YELLOW,start_rect,2)
            pygame.display.update()
            pygame.time.delay(400)
            self.make_move_by_cell(start_cell,end_cell)
            self.change_turn()

    def make_move_by_coordinates(self, start, end):
        '''根据坐标来走棋，其实就是把坐标转化为格子再走'''
        start_cell = self.get_cell_by_coordinates(*start)
        end_cell = self.get_cell_by_coordinates(*end)
        self.make_move_by_cell(start_cell, end_cell)
    
    def make_move_by_cell(self,start_cell,end_cell) -> None:
        '''根据给定的起点和终点格子来走棋'''
        start_piece = start_cell.get_piece()
        end_piece = end_cell.get_piece()
        # 往空格子走，起点清空，终点落子
        if not end_piece:
            start_cell.set_piece()
            end_cell.set_piece(start_piece)
            self.not_eat += 1
        # 分值一样，同归于尽
        elif start_piece.name == end_piece.name:
            # 如果是两个大象同归于尽，两方的老鼠都贬值
            if start_piece.name == 'elephant':
                for row_of_board in self._container:
                    for cell in row_of_board:
                        if cell.get_piece() and cell.get_piece().name == 'mouse':
                            cell.get_piece().score = 0.5
            start_cell.set_piece()
            end_cell.set_piece()
            self.not_eat = 0
        # 往天敌身上走，自杀
        elif start_piece.name in end_piece.food:
            # 如果是大象往老鼠身上撞，老鼠贬值
            if end_piece.name == 'mouse':
                end_piece.score = 0.5
            start_cell.set_piece()
            self.not_eat = 0
        # 往食物身上走，吃掉对方
        elif start_piece.name in end_piece.enemy:
            # 如果是老鼠吃掉了大象，老鼠贬值
            if start_piece.name == 'mouse':
                start_piece.score = 0.5
            start_cell.set_piece()
            end_cell.set_piece(start_piece)
            self.not_eat = 0
        

    def run_out_of_chances(self) -> bool:
        '''判断当前是否已经磨棋磨到极限了'''
        return self.not_eat >= 10

    def game_over(self) -> bool:
        '''判断是否有一方的动物死绝了'''
        red_num = 0
        blue_num = 0
        for row_of_board in self._container:
            for cell in row_of_board:
                piece = cell.get_piece()
                if piece:
                    if piece.color == 'red':
                        red_num += 1
                    else:
                        blue_num += 1
        return (red_num == 0 or blue_num == 0)

    def get_result(self) -> Tuple[int, int]:
        '''返回游戏的结果'''
        player_score = 0
        computer_score = 0
        for row_of_board in self._container:
            for cell in row_of_board:
                piece = cell.get_piece()
                if piece:
                    if piece.color == 'red':
                        player_score += 1
                    else:
                        computer_score += 1
        return (player_score, computer_score)

    def get_valid_moves(self) -> List[Tuple[Cell,...]]:
        '''获取所有有效的棋步'''
        valid_moves = []
        for row in range(4):
            for col in range(4):
                start_cell = self._container[row][col]
                if not start_cell.visible:
                    valid_moves.append((start_cell,))
                else:
                    piece = start_cell.get_piece()
                    if piece and piece.color == self._turn:
                        for r, c in [(0,1),(0,-1),(1,0),(-1,0)]:
                            if row+r >= 0 and row+r <=3 and col+c>=0 and col+c<=3:
                                end_cell = self._container[row+r][col+c]
                                if self.is_valid_end(end_cell):
                                    valid_moves.append((start_cell,end_cell))
        return valid_moves
            
        

        

