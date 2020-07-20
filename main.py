import os
import sys
import pygame
import pygame.locals as pl

import settings
from board import Board

if __name__ == "__main__":
    # 初始化
    pygame.init()
    main_clock = pygame.time.Clock()

    # 创建窗口
    window_surface = pygame.display.set_mode((settings.WINDOW_WIDTH,settings.WINDOW_HEIGHT))
    pygame.display.set_caption('斗兽棋')
    
    # 创建字体
    big_font = pygame.font.SysFont(None,64)

    # 加载各种图片并且保存
    back_image = pygame.image.load(os.path.join(settings.IMAGE_DIR,'问号.jpg'))
    back_stretched_image = pygame.transform.scale(back_image,(settings.CELL_SIZE,settings.CELL_SIZE))
    stretched_images = {'back':back_stretched_image}
    for color in ('red','blue'):
        for animal in settings.ANIMALS:
            filename = f'{color}_{animal}'
            original_image = pygame.image.load(os.path.join(settings.IMAGE_DIR,filename+'.jpg'))
            stretched_image = pygame.transform.scale(original_image,(settings.CELL_SIZE,settings.CELL_SIZE))
            stretched_images[filename] = stretched_image
    

    # 创建棋盘
    board = Board()
    

    # 监听用户键鼠事件
    while True:
        if board.not_eat == 10:
            pygame.quit()
            sys.exit()
        for event in pygame.event.get():
            if event.type == pl.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pl.MOUSEBUTTONUP:
                x,y = event.pos[0],event.pos[1]
                board.collect_coordinates_and_make_move(x,y)

        window_surface.fill(settings.WHITE)
        board.draw_board(window_surface,stretched_images)
        turn = board.turn
        if turn == 'red':
            color = settings.RED
        else:
            color = settings.BLUE
        text = big_font.render(turn,True,color)
        text_rect = text.get_rect()
        text_rect.centerx = window_surface.get_rect().centerx
        text_rect.centery = window_surface.get_rect().centery + 250
        window_surface.blit(text,text_rect)
        pygame.display.update()
        main_clock.tick(settings.FPS)