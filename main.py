import os
import sys
from typing import Tuple

import pygame
import pygame.locals as pl

import settings
from board import Board
from strategies import get_random_move, get_eat_move,get_best_move


def terminate() -> None:
    '''退出游戏'''
    pygame.quit()
    sys.exit()

def write_text(font: pygame.font.Font, 
               text: str, 
               color: Tuple[int,int,int],
               centerx: int, 
               centery: int,
               surface: pygame.Surface,
               bg_color = None) -> None:
    ''''写文字'''
    text_obj = font.render(text,True,color,bg_color)
    text_rect = text_obj.get_rect()
    text_rect.centerx = centerx
    text_rect.centery = centery
    surface.blit(text_obj,text_rect)

def play_game() -> Tuple[int,int]:
    '''玩一局游戏，返回游戏最终比分'''
    # 创建棋盘
    board = Board()
    

    # 监听用户键鼠事件
    while True:
        
        if board.not_eat >= 20:
            return (0, 0)
        if board.game_over():
            return board.get_result()

        for event in pygame.event.get():
            if event.type == pl.QUIT:
                terminate()
            if event.type == pl.MOUSEBUTTONUP:
                if board.turn == 'red':
                    x,y = event.pos[0],event.pos[1]
                    board.collect_coordinates_and_make_move(x,y)
        
        window_surface.fill(settings.WHITE)
        # 绘制棋盘
        board.draw_board(window_surface,stretched_images)
        # 绘制轮到谁出牌的提示
        color = board.get_turn_color()
        text = 'Your turn' if board.turn == 'red' else "Computer turn"
        write_text(big_font,
                text,
                color,
                window_rect.centerx,
                window_rect.centery+250,
                window_surface)
        
        pygame.display.update()
        
        if board.turn == 'blue':
            valid_moves = board.get_valid_moves()
            if valid_moves:
                pygame.time.delay(400)
                move = get_best_move(valid_moves, board)
                board.make_computer_move(move, window_surface)

        
        main_clock.tick(settings.FPS)
    




def show_result(player_score, computer_score) -> None:
    '''把游戏结果显示在屏幕上'''
    if player_score > computer_score:
        result = 'You Win'
        bg_color = settings.SEA_GREEN
    elif player_score < computer_score:
        result = 'You Lose'
        bg_color = settings.RED
    else:
        result = 'Tie'
        bg_color = settings.BLUE
    window_surface.fill(settings.WHITE)
    # 显示结论
    write_text(big_font,
               result,
               settings.BLACK,
               window_rect.centerx,
               window_rect.centery-50,
               window_surface,
               bg_color
               )    
    # 提示按任意键可以再玩一局
    write_text(small_font,
               'Press any key to play again',
               settings.BLACK,
               window_rect.centerx,
               window_rect.centery+50,
               window_surface,
               )
    pygame.display.update()

def play_again() -> bool:
    '''玩家决定是否再玩一盘'''
    while True:
        for event in pygame.event.get():
            if event.type == pl.QUIT:
                return False
            if event.type == pl.KEYUP:
                if event.key == pl.K_ESCAPE:
                    return False
                else:
                    return True


if __name__ == "__main__":
    # 初始化
    pygame.init()
    main_clock = pygame.time.Clock()

    # 创建窗口
    window_surface = pygame.display.set_mode((settings.WINDOW_WIDTH,settings.WINDOW_HEIGHT))
    window_rect = window_surface.get_rect()
    pygame.display.set_caption('斗兽棋')
    
    # 创建字体
    big_font = pygame.font.SysFont(None,64)
    small_font = pygame.font.SysFont(None,32)

    # 加载各种图片并且保存到一个字典里面
    back_image = pygame.image.load(os.path.join(settings.IMAGE_DIR,'问号.jpg'))
    back_stretched_image = pygame.transform.scale(back_image,(settings.CELL_SIZE,settings.CELL_SIZE))
    stretched_images = {'back':back_stretched_image}
    for color in ('red','blue'):
        for animal in settings.ANIMALS:
            filename = f'{color}_{animal}'
            original_image = pygame.image.load(os.path.join(settings.IMAGE_DIR,filename+'.jpg'))
            stretched_image = pygame.transform.scale(original_image,(settings.CELL_SIZE,settings.CELL_SIZE))
            stretched_images[filename] = stretched_image
    
    while True:
        # 玩一局游戏，获得最终比分
        player_score , computer_score = play_game()
        # 显示比分
        show_result(player_score, computer_score)
        # 要不要再玩一局
        if not play_again():
            terminate()
    