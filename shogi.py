import random
import copy
import hashlib
PIECE_DIC = {"2": "ー ",
             "01":"玉 ",
             "02":"飛 ","02+":"竜 ",
             "03":"角 ","03+":"馬 ",
             "04":"金 ",
             "05":"銀 ","05+":"全 ",
             "06":"桂 ","06+":"圭 ",
             "07":"香 ","07+":"杏 ",
             "08":"歩 ","08+":"と ",
             "11":"玉v",
             "12":"飛v","12+":"竜v",
             "13":"角v","13+":"馬v",
             "14":"金v",
             "15":"銀v","15+":"全v",
             "16":"桂v","16+":"圭v",
             "17":"香v","17+":"杏v",
             "18":"歩v","18+":"とv"}

class board:
    def __init__(self):
        self.board = [
         ["17","16","15","14","11","14","15","16","17"],
         ["2" ,"12","2" ,"2" ,"2" ,"2" ,"2" ,"13","2"],
         ["18","18","18","18","18","18","18","18","18"],
         ["2" ,"2" ,"2" ,"2" ,"2" ,"2" ,"2" ,"2" ,"2" ],
         ["2" ,"2" ,"2" ,"2" ,"2" ,"2" ,"2" ,"2" ,"2" ],
         ["2" ,"2" ,"2" ,"2" ,"2" ,"2" ,"2" ,"2" ,"2" ],
         ["08","08","08","08","08","08","08","08","08"],
         ["2" ,"03","2" ,"2" ,"2" ,"2" ,"2" ,"02","2" ],
         ["07","06","05","04","01","04","05","06","07"]]
    
        self.P1_in_hand = []
        self.P2_in_hand = []
        self.turn = 0
        
        self.pre_board = []
        self.pre_board.append(self.board_to_hash())
        self.check_log = [0]
        
        """
        先手0
        後手1
        成駒は最後に+
        例　先手の飛車は02、後手の角は13。
        玉 1
        飛 2
        角 3
        金 4
        銀 5
        桂 6
        香 7
        歩 8
        
        """
    def print_board(self):
        #後手持ち駒
        line = "後手持ち駒:"
        for i in range(len(self.P2_in_hand)):
            line = line + PIECE_DIC[self.P2_in_hand[i]]
        print(line)
        print("")
        
        #盤面
        for i in range(9):
            line = ""
            for j in range(9):
                line = line + PIECE_DIC[self.board[i][j]]
            print(line)
            
        #先手持ち駒
        print("")
        line = "先手持ち駒:"
        for i in range(len(self.P1_in_hand)):
            line = line + PIECE_DIC[self.P1_in_hand[i]]
        print(line)
    
    def move(self,hand,make_hash = True):
        """
        handの形式
        最初の2桁は元の位置(持ち駒なら00)
        次の2桁は動かす位置
        最後の2桁は動かす駒
        （駒が成る時は次に+）
        例えば初手７六歩なら、777608 
        角道を開けあった後の２二角成なら、882203+
        """
        
        first_position = (9 - int(hand[0]),int(hand[1]) - 1)
        second_position = (9 - int(hand[2]),int(hand[3]) - 1)
        piece = hand[4:]
        
        if (int(hand[0]),int(hand[1])) == (0,0):
            if piece[0] == "0":
                self.P1_in_hand.remove(piece)
            else:
                self.P2_in_hand.remove(piece)
            self.board[second_position[1]][second_position[0]] = piece
        else:
            #元いた場所を空に
            self.board[first_position[1]][first_position[0]] = "2" 
            
            #駒を取る時の処理
            if self.board[second_position[1]][second_position[0]] != "2":
                got_piece = self.board[second_position[1]][second_position[0]]
                if piece[0] == "0":
                    self.P1_in_hand.append("0" + got_piece[1])
                else:
                    self.P2_in_hand.append("1" + got_piece[1])
             
            #駒を置く処理
            self.board[second_position[1]][second_position[0]] = piece
        #手番の置き換え
        if self.turn == 0:
            self.turn = 1
        else:
            self.turn = 0
            
        if make_hash:
            self.pre_board.append(self.board_to_hash())
            self.check_log.append(self.is_check())
            
    def generate_move(self,delete = True):
        #盤面の駒を動かす
        hand = []
        for i in range(9):
            for j in range(9):
                hand.extend(self.generate_move_piece(i,j))
        
        hand = self.generate_promote(hand)
                
        #駒を打つ

        if self.turn == 0:
            in_hand = self.P1_in_hand
        else:
            in_hand = self.P2_in_hand
            
        for piece in in_hand:
            for i in range(9):
                for j in range(9):
                    if self.board[i][j] == "2":        
                        hand.append("00" + str(9 - j) + str(i + 1) + piece)
                        #二歩の判定
                        count = 0
                        if piece[1:] == "8":
                            for k in range(9):
                                if self.board[k][j] == str(self.turn)+"8":
                                    count = count + 1
                        
                        #動けないところ&二歩を除外
                        if piece[1:] == "8" or piece[1:] == "7" or piece[1:] == "6":
                            if count > 0:
                                hand.pop()
                            elif self.turn == 0:
                                if i == 0 or (i == 1 and piece[1:] == "6"):
                                    hand.pop()
                            else:
                                if i == 8 or (i == 7 and piece[1:] == "6"):
                                    hand.pop()
                        if hand.count(hand[-1]) > 1:
                            hand.pop()

        #禁じ手を消す
        
        if delete:
            legal_hand = []
            board_sub = copy.deepcopy(self.board)
            turn_sub = copy.deepcopy(self.turn)
            P1_in_hand_sub = copy.deepcopy(self.P1_in_hand)
            P2_in_hand_sub = copy.deepcopy(self.P2_in_hand)
         
            for try_hand in hand:
                self.move(try_hand,False)

                if not self.is_illegal():
                    legal_hand.append(try_hand)
                    if try_hand[0:2] == "00" and try_hand[5:] == "8":
                        #打ち歩詰め
                        #print(try_hand)
                        if turn_sub == 0:
                            if board_sub[int(try_hand[3]) - 1 - 1][9 - int(try_hand[2])] == "11":
                                if self.checkmate() == 1:
                                    legal_hand.pop()
                        else:
                            if board_sub[int(try_hand[3]) - 1 + 1][9 - int(try_hand[2])] == "01":
                                if self.checkmate() == -1:
                                    legal_hand.pop()

                self.board = copy.deepcopy(board_sub)
                self.turn = copy.deepcopy(turn_sub)
                self.P1_in_hand = copy.deepcopy(P1_in_hand_sub)
                self.P2_in_hand = copy.deepcopy(P2_in_hand_sub)
                

                    
            return legal_hand

        
        return hand
    
    def generate_move_piece(self,i_input,j_input):
        #一つのコマを対象に、動けるところを返す
        hand = []
        if self.board[i_input][j_input][0] == str(self.turn):
            if self.board[i_input][j_input][1] == "1":
                hand = self.generate_move_king(i_input,j_input)
            elif self.board[i_input][j_input][1] == "2":
                hand = self.generate_move_rook(i_input,j_input)
            elif self.board[i_input][j_input][1] == "3":
                hand = self.generate_move_bishop(i_input,j_input)
            elif self.board[i_input][j_input][1] == "4":
                hand = self.generate_move_gold(i_input,j_input)
            elif self.board[i_input][j_input][1] == "5":
                hand = self.generate_move_silver(i_input,j_input)
            elif self.board[i_input][j_input][1] == "6":
                hand = self.generate_move_knight(i_input,j_input)
            elif self.board[i_input][j_input][1] == "7":
                hand = self.generate_move_lance(i_input,j_input)
            elif self.board[i_input][j_input][1] == "8":
                hand = self.generate_move_pawn(i_input,j_input)
    
        return hand
    
    def in_board(self,i_input,j_input):
        if i_input >= 0 and i_input < 9:
            if j_input >= 0 and j_input < 9:
                return True
        return False
                            
    def generate_move_king(self,i_input,j_input):
        hand = []
        directions = [(1,1),(1,0),(1,-1),(0,1),(0,-1),(-1,1),(-1,0),(-1,-1)]
        hand.extend(self.generate_move_walk(i_input,j_input,directions))       
        return hand
    
    def generate_move_rook(self,i_input,j_input):
        hand = []
        directions = [(1,0),(-1,0),(0,1),(0,-1)]
        for direction in directions:
            hand.extend(self.generate_move_jump(i_input,j_input,direction))
            
        if "+" in self.board[i_input][j_input]:
            directions = [(1,1),(-1,1),(1,-1),(-1,-1)]
            hand.extend(self.generate_move_walk(i_input,j_input,directions))

        return hand

    def generate_move_bishop(self,i_input,j_input):
        hand = []
        directions = [(1,1),(-1,1),(1,-1),(-1,-1)]
        for direction in directions:
            hand.extend(self.generate_move_jump(i_input,j_input,direction))
            
        if "+" in self.board[i_input][j_input]:
            directions = [(1,0),(-1,0),(0,1),(0,-1)]
            hand.extend(self.generate_move_walk(i_input,j_input,directions))
        return hand
    
    def generate_move_gold(self,i_input,j_input):
        hand = []
        if self.board[i_input][j_input][0] == "0":
            directions = [(1,0),(0,1),(0,-1),(-1,1),(-1,0),(-1,-1)]
        else:
            directions = [(1,1),(1,0),(1,-1),(0,1),(0,-1),(-1,0)]
        hand.extend(self.generate_move_walk(i_input,j_input,directions))       
        return hand
    
        
    def generate_move_silver(self,i_input,j_input):
        hand = []
        if "+" in self.board[i_input][j_input]:
            hand = self.generate_move_gold(i_input,j_input)
        else:
            if self.board[i_input][j_input][0] == "0":
                directions = [(1,1),(1,-1),(-1,1),(-1,0),(-1,-1)]
            else:
                directions = [(1,1),(1,0),(1,-1),(-1,1),(-1,-1)]
            hand.extend(self.generate_move_walk(i_input,j_input,directions)) 
        return hand
    
    def generate_move_knight(self,i_input,j_input):
        if "+" in self.board[i_input][j_input]:
            hand = self.generate_move_gold(i_input,j_input)
        else:
            hand = []
            if self.board[i_input][j_input][0] == "0":
                directions = [(-2,-1),(-2,1)]
            else:
                directions = [(2,-1),(2,1)]
            hand.extend(self.generate_move_walk(i_input,j_input,directions))       
        return hand
    
    def generate_move_lance(self,i_input,j_input):
        if "+" in self.board[i_input][j_input]:
            hand = self.generate_move_gold(i_input,j_input)
        else:
            hand = []
            if self.board[i_input][j_input][0] == "0":
                directions = [(-1,0)]
            else:
                directions = [(1,0)]
            for direction in directions:
                hand.extend(self.generate_move_jump(i_input,j_input,direction))
        return hand
    
    def generate_move_pawn(self,i_input,j_input):
        if "+" in self.board[i_input][j_input]:
            hand = self.generate_move_gold(i_input,j_input)
        else:
            hand = []
            if self.board[i_input][j_input][0] == "0":
                directions = [(-1,0)]
            else:
                directions = [(1,0)]
            hand.extend(self.generate_move_walk(i_input,j_input,directions))       
        return hand
    
    def generate_move_jump(self,i_input,j_input,direction):
        #俗にいう飛び道具のこと。directionで方向を指定する。
        hand = []
        i = 0
        j = 0
        i = i + direction[0]
        j = j + direction[1]
        if self.in_board(i_input + i,j_input + j):
            while self.board[i_input + i][j_input + j][0] != str(self.turn):
                if self.in_board(i_input + i,j_input + j):
                    if self.board[i_input + i][j_input + j] == "2" \
                    or self.board[i_input + i][j_input + j][0] != str(self.turn):
                        hand.append(str(9 - j_input)+str(i_input + 1) + \
                                    str(9 - (j_input + j))+str(i_input + i + 1) + \
                                    self.board[i_input][j_input])
                        if self.board[i_input + i][j_input + j] != "2" \
                        and self.board[i_input + i][j_input + j][0] != str(self.turn): 
                            break
                else:
                    break
                i = i + direction[0]
                j = j + direction[1]
                if not self.in_board(i_input + i,j_input + j):
                    break
            
        return hand
    def generate_move_walk(self,i_input,j_input,directions):
        #飛び道具ではない駒用
        hand = []
        for direction in directions:
            i = direction[0]
            j = direction[1]
            if self.in_board(i_input + i,j_input + j):
                if self.board[i_input + i][j_input + j] == "2" \
                    or self.board[i_input + i][j_input + j][0] != str(self.turn):
                        hand.append(str(9 - j_input)+str(i_input + 1) + \
                                    str(9 - (j_input + j))+str(i_input + i + 1) + \
                                    self.board[i_input][j_input])
        return hand
    
    def is_illegal (self):
        hands = self.generate_move(False)
        #王手がかかっているか
        for hand in hands:
            position = (9 - int(hand[2]),int(hand[3]) - 1)
            if self.board[position[1]][position[0]] != "2":
                if self.board[position[1]][position[0]][1] == "1":
                    return True
        return False
    
    def generate_promote(self,hands):
        hand = copy.deepcopy(hands)
        able_to_promote = ["2","3","5","6","7","8"]
        for i in range(len(hands)):
            if hands[i][5:] in able_to_promote:
                if hands[i][4] == "0":
                    line = min(int(hands[i][1]),int(hands[i][3]))
                    in_enemy = line <= 3
                    deep_place = (1,2)
                    
                else:
                    line = max(int(hands[i][1]),int(hands[i][3]))
                    in_enemy = line >= 7
                    deep_place = (9,8)
                             
                if in_enemy:
                    if hands[i][5:] == "8" or hands[i][5:]== "7" or hands[i][5:] == "6":
                        if line == deep_place[0] or (line == deep_place[1] and hands[i][5:] == "6"):
                            hand[i] = hands[i] + "+"
                    else:
                        hand.append(hands[i] + "+")        
        return hand
            
    def win_lose(self):
        """
        先手勝ちなら1
        後手勝ちなら-1
        引き分けなら0を返す
        また、まだ勝敗が決まってないなら2を返す。
        """
        is_checkmate = self.checkmate()
        if is_checkmate == 0:
            #千日手判定
            if self.pre_board.count(self.pre_board[-1]) == 4:
                first_index = self.pre_board.index(self.pre_board[-1])
                check_in_repetition = self.check_log[first_index:]
                if check_in_repetition.count(1) >= len(check_in_repetition) / 2:
                    return -1
                elif check_in_repetition.count(-1) >= len(check_in_repetition) / 2:
                    return 1
                    
                return 0
            
            return 2
            
        else:
            return is_checkmate
        
    def checkmate(self):
        """
        先手勝ち(後手玉が詰んでる)なら1
        後手勝ち(先手玉が詰んでる)なら-1
        引き分け(どちらの玉も詰んでない）なら0を返す
        """
        turn_sub = copy.deepcopy(self.turn)
        
        self.turn = 0
        hand = self.generate_move()
        if len(hand) == 0:
            self.turn = turn_sub
            return -1
        
        self.turn = 1
        hand = self.generate_move()
        if len(hand) == 0:
            self.turn = turn_sub
            return 1
        self.turn = turn_sub
        return 0

    def board_to_hash(self):
        string = str(self.board) + str(self.P1_in_hand) + str(self.P2_in_hand) + str(self.turn)
        return hashlib.sha256(string.encode('utf-8')).hexdigest()

    def is_check(self):
        """
        先手が王手を掛けているなら1
        後手が王手を掛けているなら-1
        どちらも掛けていないなら0
        """
        turn_sub = copy.deepcopy(self.turn)
        self.turn = 0
        hands = self.generate_move(False)
        #王手がかかっているか
        for hand in hands:
            position = (9 - int(hand[2]),int(hand[3]) - 1)
            if self.board[position[1]][position[0]] != "2":
                if self.board[position[1]][position[0]][1] == "1":
                    self.turn = turn_sub
                    return 1
                
        self.turn = 1
        hands = self.generate_move(False)
        #王手がかかっているか
        for hand in hands:
            position = (9 - int(hand[2]),int(hand[3]) - 1)
            if self.board[position[1]][position[0]] != "2":
                if self.board[position[1]][position[0]][1] == "1":
                    self.turn = turn_sub
                    return -1
        self.turn = turn_sub
        return 0
        

        
    

        
def random_play():
    random_board = board()
    count = 0
    while random_board.win_lose() == 2:
        hand = random_board.generate_move()
        random_board.move(hand[random.randint(0,len(hand)-1)])
        count = count + 1
        if count % 1 == 0:
            random_board.print_board()
    random_board.print_board()
    #random_board.print_board()
        
