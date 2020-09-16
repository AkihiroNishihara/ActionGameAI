import os
import numpy as np
import datetime
import math
import sys
import shutil
from keras.models import Sequential
from keras.layers import Dense, Conv2D, MaxPool2D
from keras.optimizers import Adam
from keras.utils import plot_model
from collections import deque
from keras import backend as K  # Kerasは自身で行列計算とかしない，それをするためのやーつ
import tensorflow as tf
import pygame
from project.source import myenv, header as h

FUNC_REWARD = 1  # 強化学習における報酬の設定
LEARNING_RATE = 0.1  # Q-networkの学習係数
# LEARNING_RATE = 0.01  # Q-networkの学習係数
OBS_LEFT = 0
OBS_TOP = -1
OBS_RIGHT = 3
OBS_BOTTOM = 2
SIZE_STATE = (OBS_RIGHT - OBS_LEFT) * (OBS_BOTTOM - OBS_TOP) - 1 + 2  # 観測マス（キャラ位置除く）+マス内の座標
SIZE_ACTION = 8
SIZE_HIDDEN = 32
SEED = 1
NUM_EPISODES = 19  # 総試行回数
SIZE_LOOP = 1000
GAMMA = 0.99  # 割引係数
# memory_size = 10000  # バッファーメモリの大きさ
MEMORY_SIZE = 1000  # バッファーメモリの大きさ
BATCH_SIZE = 32  # Q-networkを更新するバッチの大記載

# MODE PARAMETER
OBSERVE_PLAYER = 'RIGHT'
DQN_MODE = 1  # 1がDQN、0がDDQNです
LENDER_MODE = 0  # 0は学習後も描画なし、1は学習終了後に描画する


# 損失関数の定義(huber関数)
def huberloss(_y_true, _y_pred):
    EPSILON = 1.0
    err = _y_true - _y_pred
    condition = K.abs(err) < EPSILON
    L2 = K.square(err) / 2
    L1 = EPSILON * (K.abs(err) - EPSILON / 2)
    loss = tf.where(condition, L2, L1)
    return K.mean(loss)


# Q関数をDLのネットワーククラスとして定義
class QNetwork:
    def __init__(self, _learning_rate=LEARNING_RATE, _state_size=SIZE_STATE, _action_size=SIZE_ACTION,
                 _hidden_size=SIZE_HIDDEN):
        self.model = Sequential()
        self.model.add(Dense(_hidden_size, activation='relu', input_dim=_state_size))
        self.model.add(Dense(_hidden_size, activation='relu'))
        self.model.add(Dense(_hidden_size, activation='relu'))
        self.model.add(Dense(_action_size, activation='linear'))
        self.optimizer = Adam(lr=_learning_rate)
        self.model.compile(loss=huberloss, optimizer=self.optimizer)
        # CNNの構造（未完成）
        # self.model = Sequential()
        # self.model.add(Conv2D(16, (3, 3), padding='same', input_shape=(5, 5), activation='relu'))
        # self.model.add(MaxPool2D(2, 2))
        # self.model.add(Flatten())
        # self.model.add(Dense(SIZE_HIDDEN, activation='relu'))
        # self.model.add(Dense(_action_size, activation='linear'))
        # self.optimizer = Adam(lr=_learning_rate)
        # self.model.compile(loss=huberloss, optimizer=self.optimizer)

    # 重みの学習 _memoryには（state, action, reward, next_state）群が格納
    def replay(self, _memory, _batch_size, _gamma, _targetQN):
        inputs = np.zeros((_batch_size, SIZE_STATE))
        targets = np.zeros((_batch_size, SIZE_ACTION))
        mini_batch = _memory.sample(_batch_size)

        # 学習用の入力および出力を獲得
        for i, (state_b, action_b, reward_b, next_state_b) in enumerate(mini_batch):
            inputs[i:i + 1] = state_b
            target = reward_b

            if not (next_state_b == np.zeros(state_b.shape)).all(axis=1):
                # 価値計算
                retmainQs = self.model.predict(next_state_b)[0]
                next_action = np.argmax(retmainQs)  # 配列内で最大要素のインデックスを返す
                target = reward_b + _gamma * _targetQN.model.predict(next_state_b)[0][next_action]

            targets[i] = self.model.predict(state_b)  # Qネットワークの出力
            int_action_b = 1 * action_b['right'] + 2 * action_b['left'] + 4 * action_b['space']
            targets[i][int_action_b] = target  # 教師信号

        self.model.fit(inputs, targets, epochs=1, verbose=0)

    def save_network(self, _path_dir, _name_network):
        string_json_model = self.model.to_json()
        fp_model = open(_path_dir + '/' + _name_network + '_model.json', 'w')
        fp_model.write(string_json_model)
        self.model.save_weights(_path_dir + '/' + _name_network + '_weights.hdf5')


# Experience replay と fixed target Q-networkを実現するためのメモリクラス
class Memory:
    def __init__(self, _max_size=1000):
        self.buffer = deque(maxlen=_max_size)

    def add(self, _experience):
        self.buffer.append(_experience)

    def sample(self, _batch_size):
        # buffer内のインデックスを復元抽出で取り出す
        idx = np.random.choice(np.arange(len(self.buffer)), size=_batch_size, replace=False)
        return [self.buffer[ii] for ii in idx]

    def len(self):
        return len(self.buffer)


# 状態に応じて行動を決定するクラス
class Actor:
    # 確率epsilonに応じて報酬を最高にする行動を返す関数
    def get_action(self, _state, _episode, _mainQN):
        # 徐々に最適な行動をとるΕ-greedy法
        # Eが徐々に小さくなることで，最適行動をとる確率が高まる．
        # epsilon = 0.001 + 0.9 / (1.0 + _episode)
        epsilon = 1.0 - (_episode / NUM_EPISODES)
        if epsilon <= np.random.uniform(0, 1):
            list_return_target_Qs = _mainQN.model.predict(_state)[0]  # 各行動への報酬のリストを返す
            action = np.argmax(list_return_target_Qs)
        else:
            action = np.random.choice(list(range(0, SIZE_ACTION)))

        dict_action = get_dict_action(action)
        return dict_action


def get_dict_action(_int_act):
    if _int_act not in range(0, SIZE_ACTION):
        print('Error: _int_act in get_list_bin_action is out of range', file=sys.stderr)
        os.system('PAUSE')
        exit(-1)
    # actoin をバイナリの文字列で表現
    str_bin_action = format(_int_act, 'b')
    for i in range(int(math.log2(SIZE_ACTION)) - len(str_bin_action)):
        str_bin_action = '0' + str_bin_action
    list_str_bin_action = list(str_bin_action)
    key_right = int(list_str_bin_action[2])
    key_left = int(list_str_bin_action[1])
    key_space = int(list_str_bin_action[0])
    dict_pressed_key = {'right': key_right, 'left': key_left, 'space': key_space}
    return dict_pressed_key


# メイン関数
def main():
    # env = gym.make('CartPole-v0')
    # env = wrappers.Monitor(env, './movie/cartpoleDDQN', video_callable=(lambda ep: ep % 100 == 0))  # 動画保存する場合

    # original environment
    os.environ['PYTHONHASHSEED'] = str(SEED)
    np.random.seed(SEED)
    tf.random.set_seed(SEED)
    # rn.seed(SEED)
    pygame.init()
    pygame.display.set_caption("Action Game AI")
    screen = pygame.display.set_mode((h.SCREEN_WIDTH, h.SCREEN_HEIGHT))
    screen_sub1 = pygame.display.set_mode((h.SCREEN_WIDTH, h.SCREEN_HEIGHT))
    screen_sub2 = pygame.display.set_mode((h.SCREEN_WIDTH, h.SCREEN_HEIGHT))
    # env = myenv.MyEnv(_path_file_stage='./stage_sample.txt', _screen=screen)
    env = myenv.MyEnv(_path_file_stage='./stage_sample.txt', _screen=screen)
    env_sub1 = myenv.MyEnv(_path_file_stage='./stage_sub1.txt', _screen=screen_sub1)
    env_sub2 = myenv.MyEnv(_path_file_stage='./stage_sub2.txt', _screen=screen_sub2)

    islearned = 0  # 学習が終わったフラグ
    isrender = 0  # 描画フラグ
    # ---

    # ネットワーク・メモリ・Actorの生成
    mainQN = QNetwork(_hidden_size=SIZE_HIDDEN, _learning_rate=LEARNING_RATE)
    targetQN = QNetwork(_hidden_size=SIZE_HIDDEN, _learning_rate=LEARNING_RATE)
    memory = Memory(_max_size=MEMORY_SIZE)
    actor = Actor()

    # メインルーチン
    for episode in range(NUM_EPISODES):
        env.reset()
        act_ini = env.action_space.sample()
        action = {'right': act_ini[0], 'left': act_ini[1], 'space': act_ini[2]}
        state, reward, is_done, _ = env.step(action)  # 行動a_tの実行による行動後の観測データ・報酬・ゲーム終了フラグ・詳細情報
        state = np.reshape(state, [1, SIZE_STATE])

        env_sub1.reset()
        state_sub1, reward_sub1, is_done_sub1, _ = env_sub1.step(action)  # 行動a_tの実行による行動後の観測データ・報酬・ゲーム終了フラグ・詳細情報
        state_sub1 = np.reshape(state_sub1, [1, SIZE_STATE])
        env_sub2.reset()
        state_sub2, reward_sub2, is_done_sub2, _ = env_sub2.step(action)  # 行動a_tの実行による行動後の観測データ・報酬・ゲーム終了フラグ・詳細情報
        state_sub2 = np.reshape(state_sub2, [1, SIZE_STATE])

        targetQN.model.set_weights(mainQN.model.get_weights())

        # 1試行のループ
        list_reward = []
        count_loop = 0
        is_train_sub1 = False
        is_train_sub2 = False
        # for count_loop in range(SIZE_LOOP):
        # print(str(count))
        while not is_done:
            count_loop += 1
            # if (islearned == 1) and LENDER_MODE:  # 学習終了時にcart-pole描画
            #     env.render()
            #     time.sleep(0.1)
            #     print(state[0, 0])

            action = actor.get_action(state, episode, mainQN)  # 時刻tでの行動を決定
            if count_loop % 20 == 0:
                print(action)

            # (メインゲーム)行動a_tの実行による行動後の観測データ・報酬・ゲーム終了フラグ・詳細情報
            next_state, reward, is_done, info = env.step(action)
            next_state = np.reshape(next_state, [1, SIZE_STATE])
            memory.add((state, action, reward, next_state))  # memory update
            state = next_state  # state update
            list_reward.append(reward)

            # 終了判定
            if is_done:
                if info['GAMEOVER']:
                    if info['TIME'] == 0:
                        print('MAIN {0}/{1}: TIME OVER'.format(episode + 1, NUM_EPISODES))
                    else:
                        print('MAIN {0}/{1}: FALL GROUND'.format(episode + 1, NUM_EPISODES))
                elif info['CLEAR']:
                    print('MAIN {0}/{1}: CLEAR!'.format(episode + 1, NUM_EPISODES))
                else:
                    print('Error: Wrong information of main stage', file=sys.stderr)
                    os.system('PAUSE')
                    exit(-1)
                next_state = np.zeros(state.shape)
                next_state_sub1 = np.zeros(state_sub1.shape)
                next_state_sub2 = np.zeros(state_sub2.shape)
                break

            if is_train_sub1:
                action_sub1 = actor.get_action(state_sub1, episode, mainQN)  # 時刻tでの行動を決定
                # (サブゲーム)行動a_tの実行による行動後の観測データ・報酬・ゲーム終了フラグ・詳細情報
                next_state_sub1, reward_sub1, is_done_sub1, info_sub1 = env_sub1.step(action_sub1)
                next_state_sub1 = np.reshape(next_state_sub1, [1, SIZE_STATE])
                memory.add((state_sub1, action_sub1, reward_sub1, next_state_sub1))  # memory update
                state_sub1 = next_state_sub1

                # サブステージがゴールまで到着したら，メインの基礎学習を十分と判断し，このエピソード内では学習終了．
                if is_done_sub1:
                    if info_sub1['GAMEOVER']:
                        if info_sub1['TIME'] == 0:
                            print('sub1 {0}/{1}: TIME OVER'.format(episode + 1, NUM_EPISODES))
                        else:
                            print('sub1 {0}/{1}: FALL GROUND'.format(episode + 1, NUM_EPISODES))
                    elif info_sub1['CLEAR']:
                        print('sub1 {0}/{1}: CLEAR!'.format(episode + 1, NUM_EPISODES))
                    else:
                        print('Error: Wrong information of sub1 stage', file=sys.stderr)
                        os.system('PAUSE')
                        exit(-1)
                    is_train_sub1 = False

            if is_train_sub2:
                action_sub2 = actor.get_action(state_sub2, episode, mainQN)  # 時刻tでの行動を決定
                # (サブゲーム)行動a_tの実行による行動後の観測データ・報酬・ゲーム終了フラグ・詳細情報
                next_state_sub2, reward_sub2, is_done_sub2, info_sub2 = env_sub2.step(action_sub2)
                next_state_sub2 = np.reshape(next_state_sub2, [1, SIZE_STATE])
                memory.add((state_sub2, action_sub2, reward_sub2, next_state_sub2))  # memory update
                state_sub2 = next_state_sub2

                # サブステージがゴールまで到着したら，メインの基礎学習を十分と判断し，このエピソード内では学習終了．
                if is_done_sub2:
                    if info_sub2['GAMEOVER']:
                        if info_sub2['TIME'] == 0:
                            print('sub2 {0}/{1}: TIME OVER'.format(episode + 1, NUM_EPISODES))
                        else:
                            print('sub2 {0}/{1}: FALL GROUND'.format(episode + 1, NUM_EPISODES))
                    elif info_sub2['CLEAR']:
                        print('sub2 {0}/{1}: CLEAR!'.format(episode + 1, NUM_EPISODES))
                    else:
                        print('Error: Wrong information of sub2 stage', file=sys.stderr)
                        os.system('PAUSE')
                        exit(-1)
                    is_train_sub2 = False

            # Q-networkの重みの学習と更新
            if (memory.len() > BATCH_SIZE) and not is_done:
                mainQN.replay(memory, BATCH_SIZE, GAMMA, targetQN)

            if DQN_MODE:
                targetQN.model.set_weights(mainQN.model.get_weights())

        print('{0}/{1}: {2}'.format(episode + 1, NUM_EPISODES, sum(list_reward) / len(list_reward)))
        # print(count_loop)

    dt_now = datetime.datetime.now()
    str_time = dt_now.strftime('%Y-%m-%d_%H-%M-%S')
    path_dirs = '../network/model_{0}'.format(str_time)
    os.makedirs(path_dirs, exist_ok=True)
    mainQN.save_network(_path_dir=path_dirs, _name_network='mainQN')
    plot_model(mainQN.model, to_file=path_dirs + '/Qnetwork.png', show_shapes=True)  # Qネットワークの可視化
    shutil.copy('./stage_sample.txt', path_dirs)


if __name__ == '__main__':
    main()
