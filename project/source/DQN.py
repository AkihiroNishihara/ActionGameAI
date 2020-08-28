import os
import numpy as np
import time
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from keras.utils import plot_model
from collections import deque
from keras import backend as K  # Kerasは自身で行列計算とかしない，それをするためのやーつ
import tensorflow as tf
import pygame
from tqdm import tqdm
from project.source import myenv, header as h

LEARNING_RATE = 0.01
SIZE_STATE = 4
SIZE_ACTION = 8


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
    def __init__(self, _learning_rate=LEARNING_RATE, _state_size=SIZE_STATE, _action_size=SIZE_ACTION, _hidden_size=10):
        self.model = Sequential()
        self.model.add(Dense(_hidden_size, activation='relu', input_dim=_state_size))
        self.model.add(Dense(_hidden_size, activation='relu'))
        self.model.add(Dense(_action_size, activation='linear'))
        self.optimizer = Adam(lr=_learning_rate)
        self.model.compile(loss=huberloss, optimizer=self.optimizer)

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
            targets[i][action_b] = target  # 教師信号

        self.model.fit(inputs, targets, epochs=1, verbose=0)

    def save_network(self, _name_network):
        string_json_model = self.model.to_json()
        path_dirs = '../AI/network'
        os.makedirs(path_dirs, exist_ok=True)
        fp_model = open(path_dirs + '/' + _name_network + '_model.json', 'w')
        fp_model.write(string_json_model)
        self.model.save_weights(path_dirs + '/' + _name_network + '_weights.hdf5')


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
        epsilon = 0.001 + 0.9 / (1.0 + _episode)
        if epsilon <= np.random.uniform(0, 1):
            list_return_target_Qs = _mainQN.model.predict(_state)[0]  # 各行動への報酬のリストを返す
            action = np.argmax(list_return_target_Qs)
        else:
            action = np.random.choice(list(range(0, SIZE_ACTION)))

        str_bin_action = format(action, 'b')
        for i in range(3 - len(str_bin_action)):
            str_bin_action = '0' + str_bin_action
        list_bin_action = [int(c) for c in list(str_bin_action)]

        return list_bin_action


DQN_MODE = 1  # 1がDQN、0がDDQNです
LENDER_MODE = 0  # 0は学習後も描画なし、1は学習終了後に描画する

# メイン関数
if __name__ == '__main__':
    # env = gym.make('CartPole-v0')
    # env = wrappers.Monitor(env, './movie/cartpoleDDQN', video_callable=(lambda ep: ep % 100 == 0))  # 動画保存する場合

    # original environment
    pygame.init()
    pygame.display.set_caption("Action Game AI")
    screen = pygame.display.set_mode((h.SCREEN_WIDTH, h.SCREEN_HEIGHT))
    env = myenv.MyEnv(_path_file_stage='../stage_sample.txt', _screen=screen)

    num_episodes = 9  # 総試行回数
    max_number_of_steps = 200  # 1試行のstep数
    # goal_average_reward = 195  # この報酬を超えると学習終了
    num_consecutive_iterations = 10  # 学習完了評価の平均計算を行う試行回数
    total_reward_vec = np.zeros(num_consecutive_iterations)  # 各試行の報酬を格納
    gamma = 0.99  # 割引係数
    islearned = 0  # 学習が終わったフラグ
    isrender = 0  # 描画フラグ
    # ---
    hidden_size = 16  # Q-networkの隠れ層のニューロンの数
    learning_rate = 0.00001  # Q-networkの学習係数
    memory_size = 10000  # バッファーメモリの大きさ
    batch_size = 32  # Q-networkを更新するバッチの大記載

    # ネットワーク・メモリ・Actorの生成
    mainQN = QNetwork(_hidden_size=hidden_size, _learning_rate=learning_rate)
    targetQN = QNetwork(_hidden_size=hidden_size, _learning_rate=learning_rate)
    plot_model(mainQN.model, to_file='../AI/Qnetwork.png', show_shapes=True)  # Qネットワークの可視化
    memory = Memory(_max_size=memory_size)
    actor = Actor()

    # メインルーチン
    for episode in tqdm(range(num_episodes)):
        env.reset()
        state, reward, is_done, _ = env.step(env.action_space.sample())  # 行動a_tの実行による行動後の観測データ・報酬・ゲーム終了フラグ・詳細情報
        state = np.reshape(state, [1, 4])
        episode_reward = 0

        targetQN.model.set_weights(mainQN.model.get_weights())

        count = 0
        while not is_done:  # 1試行のループ
            print(str(count))
            count += 1
            if (islearned == 1) and LENDER_MODE:  # 学習終了時にcart-pole描画
                env.render()
                time.sleep(0.1)
                print(state[0, 0])

            action = actor.get_action(state, episode, mainQN)  # 時刻tでの行動を決定
            next_state, reward, is_done, info = env.step(action)  # 行動a_tの実行による行動後の観測データ・報酬・ゲーム終了フラグ・詳細情報
            next_state = np.reshape(next_state, [1, SIZE_STATE])

            # 報酬を設定し、与える
            if is_done:
                next_state = np.zeros(state.shape)
            #     # 195ステップまで立てていたか判定
            #     if t < 195:
            #         reward = -1  #
            #     else:
            #         reward = 1
            # else:
            #     reward = 0
            #
            # episode_reward += 1  # 合計報酬を更新
            episode_reward += reward

            memory.add((state, action, reward, next_state))  # memory update
            state = next_state  # state update

            # learning and update the weights of Q-network
            if (memory.len() > batch_size) and not islearned:
                mainQN.replay(memory, batch_size, gamma, targetQN)

            if DQN_MODE:
                targetQN.model.set_weights(mainQN.model.get_weights())

            # process in finishing one trial
            if is_done:
                # total_reward_vec = np.hstack((total_reward_vec[1:], episode_reward))  # record rewards
                # print(
                #     '{0} Episode finished after {1} time steps / mean {2}'.format(episode, t + 1,
                #                                                                   total_reward_vec.mean()))
                break

        # for t in range(max_number_of_steps + 1):  # 1試行のループ
        #     if (islearned == 1) and LENDER_MODE:  # 学習終了時にcart-pole描画
        #         env.render()
        #         time.sleep(0.1)
        #         print(state[0, 0])
        #
        #     action = actor.get_action(state, episode, mainQN)  # 時刻tでの行動を決定
        #     next_state, reward, is_done, info = env.step(action)  # 行動a_tの実行による行動後の観測データ・報酬・ゲーム終了フラグ・詳細情報
        #     next_state = np.reshape(next_state, [1, SIZE_STATE])
        #
        #     # 報酬を設定し、与える
        #     if is_done:
        #         next_state = np.zeros(state.shape)
        #     #     # 195ステップまで立てていたか判定
        #     #     if t < 195:
        #     #         reward = -1  #
        #     #     else:
        #     #         reward = 1
        #     # else:
        #     #     reward = 0
        #     #
        #     # episode_reward += 1  # 合計報酬を更新
        #     episode_reward += reward
        #
        #     memory.add((state, action, reward, next_state))  # memory update
        #     state = next_state  # state update
        #
        #     # learning and update the weights of Q-network
        #     if (memory.len() > batch_size) and not islearned:
        #         mainQN.replay(memory, batch_size, gamma, targetQN)
        #
        #     if DQN_MODE:
        #         targetQN.model.set_weights(mainQN.model.get_weights())
        #
        #     # process in finishing one trial
        #     if is_done:
        #         total_reward_vec = np.hstack((total_reward_vec[1:], episode_reward))  # record rewards
        #         print(
        #             '{0} Episode finished after {1} time steps / mean {2}'.format(episode, t + 1,
        #                                                                           total_reward_vec.mean()))
        #         break

        # 複数試行の平均報酬で終了を判断
        # if total_reward_vec.mean() > goal_average_reward:
        #     print('Episode {0} train agent successfully!'.format(episode))
        #     islearned = 1
        #     if isrender == 0:
        #         isrender = 1
        #
        # env = wrappers.Monitor(env, './movie/cartpoleDDQN')  # 動画保存する場合
        # 10エピソードだけでどんな挙動になるのか見たかったら、以下のコメントを外す
        # if episode > 10:
        #     if isrender == 0:
        #         env = wrappers.Monitor(env, './movie/cartpole-experiment-1')  # 動画保存する場合
        #         isrender = 1
        #     islearned = 1

    mainQN.save_network('mainQN')
