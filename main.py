import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.layers.core import Activation, Flatten
from keras.layers.normalization import BatchNormalization
from keras.layers.convolutional import Conv2D
from keras.optimizers import Adam
DIM = 30
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
        #print("sex")

    def model(self):
        model = Sequential()
        model.add(Conv2D(256, (5, 5), padding='same', input_shape=(DIM,9, 9, )))
        #model.add(BatchNormalization())
        model.add(Activation('relu'))
        model.add(Conv2D(256, (3, 3), padding='same'))
        model.add(BatchNormalization())
        model.add(Activation('relu'))
        model.add(Conv2D(128, (3, 3), padding='same'))
        model.add(BatchNormalization())
        model.add(Activation('relu'))
        model.add(Conv2D(64, (3, 3), padding='same'))
        model.add(BatchNormalization())
        model.add(Activation('relu'))
        model.add(Conv2D(32, (3, 3), padding='same'))
        model.add(BatchNormalization())
        model.add(Activation('relu'))
        model.add(Conv2D(16, (3, 3), padding='same'))
        model.add(BatchNormalization())
        model.add(Activation('relu'))
        model.add(Conv2D(8, (3, 3), padding='same'))
        model.add(BatchNormalization())
        model.add(Activation('relu'))
        
        model.add(Flatten())
        
        model.add(Dense(1))
        model.add(Activation('tanh'))
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
    
    def train(self):
        try:
            self.network.load_weights('model.h5')
        except:
            print("model couldn't load")
        opt = Adam(lr=1e-3)
        self.network.compile(loss='mean_squared_error', optimizer=opt)
        
        
        for epoch in range(NUM_EPOCH):
            #自己対局
            play_board = board()
            X_train = []
            while play_board.win_lose() == 2:
                sub_board = copy.deepcopy(play_board)
                hands = play_board.generate_move()
                value = []
                for hand in hands:
                    play_board.move(hand)
                    converted = self.convert(play_board.board,play_board.P1_in_hand,play_board.P2_in_hand,play_board.turn)
                    value.append(self.network.predict(converted.reshape(1,DIM,9,9)))
                    play_board = copy.deepcopy(sub_board)
                index = max(enumerate(value), key=lambda value: value[1])[0]
                play_board.move(hands[index])
                converted = self.convert(play_board.board,play_board.P1_in_hand,play_board.P2_in_hand,play_board.turn)
                X_train.append(converted)
                play_board.print_board()
            
            #訓練データ用意
            X_train = np.array(X_train)
            y_train = np.zeros(len(X_train))
            y_train[0:] = play_board.win_lose()
            if len(y_train) % 2 == 0:
                y_train[np.arange(0,len(y_train)-1,2)] = y_train[-1] * -1
            else:
                y_train[np.arange(1,len(y_train)-1,2)] = y_train[-1] * -1
            
            y_train = y_train.reshape(len(y_train),1)
                
            #訓練
            print(X_train.shape)
            print(y_train.shape)
            loss = self.network.train_on_batch(X_train,y_train)
            print("epoch: %d,loss: %f" % (epoch,loss))
            self.network.save_weights('model.h5')
        
        
        
        
        
        
