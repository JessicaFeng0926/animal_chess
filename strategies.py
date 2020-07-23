from typing import Tuple
import random
from copy import deepcopy
from cell import Cell
import settings


def get_random_move(valid_moves) -> Tuple[Cell,...]:
    '''随机返回一个可以走的棋步'''
    return random.choice(valid_moves)

def get_eat_move(valid_moves) -> Tuple[Cell,...]:
    '''优先返回能吃对方棋子的一步'''
    random.shuffle(valid_moves)
    for move in valid_moves:
        if len(move) == 2:
            start_cell, end_cell = move
            start_piece = start_cell.get_piece()
            end_piece = end_cell.get_piece()
            if start_cell.meet_food(end_cell):
                return move
    return random.choice(valid_moves)

def get_best_move(valid_moves,board):
    '''返回分数最高的棋步'''
    random.shuffle(valid_moves)
    reverse_moves = []
    best_move = None
    best_score = -100
    for move in valid_moves:
        
        if len(move) == 1:
            reverse_moves.append(move)
        else:
            board_copy = deepcopy(board)
            score = 0
            start_cell, end_cell = move
            
            # 先计算走这一步本身能得到多少分
            score += get_move_score(start_cell, end_cell)
            start_row = (start_cell.get_rect().top-settings.TOP_OF_BOARD)//settings.CELL_SIZE
            start_col = (start_cell.get_rect().left-settings.LEFT_OF_BOARD)//settings.CELL_SIZE
            end_row = (end_cell.get_rect().top-settings.TOP_OF_BOARD)//settings.CELL_SIZE
            end_col = (end_cell.get_rect().left-settings.LEFT_OF_BOARD)//settings.CELL_SIZE
            # 在棋盘副本上模拟出这步棋
            board_copy.make_move_by_cell(
                board_copy.get_cell_by_row_col(start_row,start_col),
                board_copy.get_cell_by_row_col(end_row,end_col))
            # 再计算走完了之后的整盘棋对自己来说的价值是多少
            score += get_board_score(board_copy, board.turn) 
            if score > best_score:
                best_score = score
                best_move = move
    # 返回最好的棋步
    if best_score >= 10 or not reverse_moves:
        return best_move
    return random.choice(reverse_moves)
    
def get_best_move2(valid_moves, board):
    '''根据差值的变化选出最好的棋步'''
    random.shuffle(valid_moves)
    computer_color = board.turn
    player_color = 'red' if computer_color == 'blue' else 'blue'
    # 走棋之前，自己的分数
    pre_computer_score = get_board_score(board,computer_color)
    pre_player_score =  get_board_score(board,player_color)
    # 走棋之前的差值
    best_diff = pre_computer_score - pre_player_score
    best_move = None
    for move in valid_moves:
        board_copy = deepcopy(board)
        move_score = 0
        if len(move) == 1:
            cell_rect = move[0].get_rect()
            row = (cell_rect.top - settings.TOP_OF_BOARD)//settings.CELL_SIZE
            col = (cell_rect.left - settings.LEFT_OF_BOARD)//settings.CELL_SIZE
            cell = board_copy.get_cell_by_row_col(row,col)
            cell.reverse_piece()
        else:
            start_cell, end_cell = move
            move_score = get_move_score(start_cell,end_cell)
            start_row = (start_cell.get_rect().top-settings.TOP_OF_BOARD)//settings.CELL_SIZE
            start_col = (start_cell.get_rect().left-settings.LEFT_OF_BOARD)//settings.CELL_SIZE
            end_row = (end_cell.get_rect().top-settings.TOP_OF_BOARD)//settings.CELL_SIZE
            end_col = (end_cell.get_rect().left-settings.LEFT_OF_BOARD)//settings.CELL_SIZE
            board_copy.make_move_by_cell(
                board_copy.get_cell_by_row_col(start_row,start_col),
                board_copy.get_cell_by_row_col(end_row,end_col)
            )
        player_score, computer_score = board_copy.get_result()
        if player_score == 0 and computer_score>0:
            return move
        after_player_score = get_board_score(board_copy,player_color)
        after_computer_score = get_board_score(board_copy,computer_color)
        diff = after_computer_score - after_player_score + move_score
        if diff > best_diff:
            best_diff = diff
            best_move = move
    if best_move:
        return best_move
    return random.choice(valid_moves)

def get_move_score(start_cell, end_cell) -> int:
    '''计算这一步本身会带来多少得分'''
    start_piece = start_cell.get_piece()
    end_piece = end_cell.get_piece()
    if end_piece:
        # 如果撞在天敌身上了，得到负分，绝对值是自身的价值
        if end_piece.name in start_piece.enemy:
            return - 2*start_piece.score
        # 如果吃掉了对方，得到正分，绝对值是对方的价值
        elif end_piece.name in start_piece.food:
            return 2*end_piece.score
        # 如果和对方同归于尽了，得到正分，绝对值是自身价值的四分之一
        elif end_piece.name == start_piece.name:
            return 0.25*start_piece.score
    # 其他情况都得0分
    return 0

def get_environment_score(board,end_row,end_col):
    '''计算这个格子周围的八个格子能给它多少分'''
    score = 0
    cell = board.get_cell_by_row_col(end_row,end_col)
    piece = board.get_cell_by_row_col(end_row,end_col).get_piece()
    if piece:
        # 先看相邻的
        for r, c in [(0,1),(1,0),(-1,0),(0,-1)]:
            row = end_row + r
            col = end_col + c
            if row>=0 and row<=3 and col>=0 and col<=3:
                neighbor_cell = board.get_cell_by_row_col(row,col)
                if neighbor_cell.visible:
                    neighbor_piece = board.get_cell_by_row_col(row,col).get_piece()
                    if neighbor_piece and neighbor_piece.color != piece.color:
                        # 和天敌相邻，减去自身价值的1.5倍
                        if neighbor_piece.name in piece.enemy:
                            #score -= 2*piece.score
                            score -= 1.5*piece.score
                        # 和食物相邻，加上食物价值的一半
                        elif neighbor_piece.name in piece.food:
                            score += neighbor_piece.score / 2
                        # 和一样的动物相邻，减去自身价值的一半
                        elif neighbor_piece.name == piece.name:
                            score -= 0.5*piece.score
        # 再看对角线
        for r, c in [(1,1),(1,-1),(-1,1),(-1,-1)]:
            row = end_row + r
            col = end_col + c
            if row>=0 and row<=3 and col>=0 and col<=3:
                neighbor_cell = board.get_cell_by_row_col(row,col)
                if neighbor_cell.visible:
                    neighbor_piece = board.get_cell_by_row_col(row,col).get_piece()
                    if neighbor_piece and neighbor_piece.color != piece.color:
                        block1 = board.get_cell_by_row_col(end_row+r,end_col)
                        block2 = board.get_cell_by_row_col(end_row,end_col+c)

                        # 和天敌对角线，减去自身价值的一半
                        if neighbor_piece.name in piece.enemy:
                            # 天敌能吃到自己
                            if block1.is_empty() or block2.is_empty() or neighbor_cell.meet_food(block1) or neighbor_cell.meet_food(block2):
                                score -= piece.score/2
                        # 和食物对角线，加上食物的价值
                        elif neighbor_piece.name in piece.food:
                            # 可以到达食物
                            if cell.meet_food(block1) or cell.meet_food(block2) or block1.is_empty() or block2.is_empty():
                                score += neighbor_piece.score
                        elif neighbor_piece.name == piece.name:
                            if cell.meet_food(block1) or cell.meet_food(block2) or block1.is_empty() or block2.is_empty():
                                score += 0.25*piece.score
    return score

def get_board_score(board,computer_color):
    '''计算并返回电脑方在整个棋盘的分数'''
    score = 0
    for row in range(4):
        for col in range(4):
            cell = board.get_cell_by_row_col(row,col)
            if cell.visible:
                piece = cell.get_piece()
                if piece and piece.color == computer_color:
                    score += get_environment_score(board,row,col)
                    score += piece.score
    return score

    


            
if __name__ == '__main__':
    from board import Board
    board = Board()
    for row in range(4):
        for col in range(4):
            cell = board.get_cell_by_row_col(row,col)
            cell.reverse_piece()
            if cell.get_piece().color == 'red':
                cell.set_piece()
    print(get_board_score(board,'red'))