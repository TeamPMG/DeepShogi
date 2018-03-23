import numpy as np
from keras.models import Sequential,Model
from keras.layers import Dense, Input
from keras.layers.core import Activation, Flatten,Dropout,Reshape
from keras.layers.normalization import BatchNormalization
from keras.layers.convolutional import Conv2D
from keras.optimizers import Adam
DIM = 30
POLICY = 2187
NUM_EPOCH = 1000
from shogi import board
import copy

"""
それぞれの駒(8+6 = 14)の位置(one-hot表現) * 2
持ち駒がどれがいくつあるか * 2（テッペンは空白）
= 30
"""


class DeepShogi:
    def __init__(self):
        self.network = self.model()
        #self.network2 = self.model()
        #print("sex")

    def model(self):
        board = Input(shape=(DIM,9,9,))
        x = Conv2D(128, (3, 3), padding='same')(board)
        x = Activation('relu')(x)
        x = Conv2D(128, (3, 3), padding='same')(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = Conv2D(128, (3, 3), padding='same')(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = Conv2D(128, (3, 3), padding='same')(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = Conv2D(128, (3, 3), padding='same')(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = Conv2D(128, (3, 3), padding='same')(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = Conv2D(128, (3, 3), padding='same')(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = Conv2D(128, (3, 3), padding='same')(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        print(x.shape)
        
        x = Conv2D(1, (1, 1), padding='same')(x)
        x = Activation('relu')(x)
        x = Reshape((9*9,))(x)
        
        policy = Dense(POLICY)(x)
        policy = Activation('softmax')(policy)
        
        value = Dense(1)(x)
        value = Activation('tanh')(value)
        
        model = Model(inputs=board, outputs=[policy,value])
        '''
        自分側（たった今指し終わった方)が勝ちなら1
        自分側が負けなら-1
        引き分けなら0
        '''
        return model
    
    def convert(self,board,P1_in_hand,P2_in_hand,turn):
        #ネットワークに入れれるように盤面を変換する
        converted = np.zeros((DIM,9,9))
        pieces = ["01","02","03","04","05","06","07","08","01+","02+","05+","06+","07+","08+",
                  "11","12","13","14","15","16","17","18","11+","12+","15+","16+","17+","18+"]
        in_hand_pieces = ["01","02","03","04","05","06","07","08",
                          "11","12","13","14","15","16","17","18"]  
        
        channel = 0
        for piece in pieces:
            for i in range(9):
                for j in range(9):
                    if piece == board[i][j]:
                        converted[channel][i][j] = 1
            channel = channel + 1
        for i in range(8):
            if P1_in_hand.count(in_hand_pieces[i]) <=9:
                converted[channel][i][0:P1_in_hand.count(in_hand_pieces[i])] = 1
            else:
                converted[channel][i][0:9] = 1
                converted[channel][i+1][0:P1_in_hand.count(in_hand_pieces[i])-9] = 1
        channel = channel + 1
        
        for i in range(8):
            if P2_in_hand.count(in_hand_pieces[i]) <=9:
                converted[channel][i][0:P2_in_hand.count(in_hand_pieces[i])] = 1
            else:
                converted[channel][i][0:9] = 1
                converted[channel][i+1][0:P2_in_hand.count(in_hand_pieces[i])-9] = 1
        
        if turn == 0:
            converted_black = np.zeros((DIM,9,9))
            #盤面の反転
            for channel in range(14):
                for i in range(9):
                    for j in range(9):
                        converted_black[channel][i][j] = converted[channel+14][8-i][8-j]
            for channel in range(14,28):
                for i in range(9):
                    for j in range(9):
                        converted_black[channel][i][j] = converted[channel-14][8-i][8-j]
            #持ち駒の交換
            sub_in_hand = copy.deepcopy(converted[28])
            converted_black[28] = converted[29]
            converted_black[29] = sub_in_hand
            
            return converted_black
        
            
        return converted
    def convert_hand(self,board,hand):
        #91の指して,91の指して,11の指して....91の指して,92の指して,
        position = (int(hand[3]) - 1) * 9 + (9 - int(hand[2])) 
        #左上から順に1から8、桂馬は左から9,10
        
        if hand[0:2] == "00":
            in_hand = int(hand[5])
            return 27 * position + 19 + (in_hand - 1)
        else:
            relative = (int(hand[2]) - int(hand[0]),int(hand[3]) - int(hand[1]))
            if relative[0] == 0:
                #縦
                if relative[1] > 0:
                    direction = 1
                else:
                    direction = 6
            
            elif relative[1] == 0:
                #横
                if relative[0] > 0:
                    direction = 4
                else:
                    direction = 3
            
            elif abs(relative[0]) == abs(relative[1]):
                #斜め
                if relative[0] > 0:
                    if relative[1] > 0:
                        direction = 2
                    else:
                        direction = 7
                else:
                    if relative[1] > 0:
                        direction = 0
                    else:
                        direction = 5
            else:
                #桂馬
                if relative[0] > 0:
                    direction = 9
                else:
                    direction = 8
            if hand[-1] == "+":
                if board[int(hand[1]) - 1][9 - int(hand[0])][-1] != "+":
                    return 27 * position + 10 + direction
            return 27 * position + direction

    
    def train(self):
        try:
            self.network.load_weights('model.h5')
            #self.network2.load_weights('model.h5')
        except:
            print("model couldn't load")
        opt = Adam(lr=1e-1)
        self.network.compile(loss='mean_squared_error', optimizer=opt)
        
        
        for epoch in range(NUM_EPOCH):
            randomness = 0.3
            while(100):
                #自己対局
                play_board = board()
                X_train = []
                move_count = 0
                while play_board.win_lose() == 2 and move_count < 512:
                    #sub_board = copy.deepcopy(play_board)
                    hands = play_board.generate_move()
                    #value = []
                    legal_policy = []
                    converted = self.convert(play_board.board,play_board.P1_in_hand,play_board.P2_in_hand,play_board.turn)
                    predicted = self.network.predict(converted.reshape(1,DIM,9,9))
                    p = predicted[0] #確率
                    print(p.shape)
                    legal_policy_p = []
                    for hand in hands:
                        legal_policy.append(self.convert_hand(play_board.board,hand))
                        legal_policy_p.append(p[0][legal_policy[-1]])
                        '''
                        play_board.move(hand)
                        converted = self.convert(play_board.board,play_board.P1_in_hand,play_board.P2_in_hand,play_board.turn)
                        converted = converted + np.random.normal(0,randomness,(DIM,9,9))
                        value.append(self.network.predict(converted.reshape(1,DIM,9,9)))
                        
                        if play_board.turn == 1:
                            value.append(self.network.predict(converted.reshape(1,DIM,9,9)))
                        else:
                            value.append(self.network2.predict(converted.reshape(1,DIM,9,9)))
                        
                        play_board = copy.deepcopy(sub_board)
                        '''
                    legal_policy_p = np.array(legal_policy_p)
                    print(legal_policy_p.shape)
                    legal_policy_p = np.exp(legal_policy_p) / np.sum(np.exp(legal_policy_p))
                    play_board.move(np.random.choice(hands,p=legal_policy_p))
                    converted = self.convert(play_board.board,play_board.P1_in_hand,play_board.P2_in_hand,play_board.turn)
                    X_train.append(converted)
                    play_board.print_board()
                    move_count = move_count + 1 
                return (play_board.win_lose(),move_count)
                #訓練データ用意
                X_train = np.array(X_train)
                y_train = np.zeros(len(X_train))
                if play_board.win_lose() == 0 or not(move_count < 512):
                    y_train = np.zeros(len(X_train))
                else:
                    y_train = np.ones(len(X_train))
                    if len(y_train) % 2 == 0:
                        y_train[np.arange(0,len(y_train)-1,2)] = -1
                    else:
                        y_train[np.arange(1,len(y_train)-1,2)] = -1
                    
                y_train = y_train.reshape(len(y_train),1)
                    
                #訓練
                print(y_train[-1])
                print(move_count)
                loss = self.network.train_on_batch(X_train,y_train)
                print("epoch: %d,loss: %f" % (epoch,loss))
                self.network.save_weights('model.h5')
            
            #self.network2.load_weights('model.h5')
"""       
if __name__ == '__main__':
    ds = DeepShogi()
    ds.train()        
        
"""      
        
