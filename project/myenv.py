import sys

import gym
import numpy as np
import gym.spaces
import io

from project import mode_gamestage


class MyEnv(gym.Env):
    # metadata = {'render.modes': ['human', 'ansi']}
    MAX_STEPS = 100

    def __init__(self, _path_file_stage):
        super().__init__()
        self.path_file_stage = _path_file_stage
        # action_space, observation_space, reward_range を設定する
        # 行動空間：離散値（right, left, jumpの各キーのON,OFF）
        self.action_space = gym.spaces.MultiBinary(3)
        # 状態空間：離散値（0:無し, 1：ブロック, 2：ゴール, 3:壁），上右下左の4方向を観測
        self.observation_space = gym.spaces.Discrete(4)
        # 報酬の範囲（正規化する）
        self.reward_range = [0.0, 1.0]
        self._reset()

    # ---------------------------------------- function required -------------------------------------------------------
    # ゲームを呼び出すことで初期化
    def _reset(self):
        self.game_stage = mode_gamestage.GameStage(self.path_file_stage, _is_training=True)

    # _actionは（right, left, jump）の各キーのON,OFFで獲得
    def _step(self, _action):
        self.game_stage.step_training(_action)
        # 1ステップ進める処理を記述。戻り値は observation, reward, done(ゲーム終了したか), info(追加の情報の辞書)
        if _action == 0:
            next_pos = self.pos + [0, 1]
        elif _action == 1:
            next_pos = self.pos + [0, -1]
        elif _action == 2:
            next_pos = self.pos + [1, 0]
        elif _action == 3:
            next_pos = self.pos + [-1, 0]

        if self._is_movable(next_pos):
            self.pos = next_pos
            moved = True
        else:
            moved = False

        observation = self._observe()
        reward = self._get_reward(self.pos, moved)
        self.damage += self._get_damage(self.pos)
        self.done = self._is_done()
        return observation, reward, self.done, {}

    def _render(self, mode='human', close=False):
        # human の場合はコンソールに出力。ansiの場合は StringIO を返す
        outfile = io.StringIO() if mode == 'ansi' else sys.stdout
        outfile.write('\n'.join(' '.join(self.FIELD_TYPES[elem] for elem in row) for row in self._observe()) + '\n')
        return outfile

    # ---------------------------------------- function better to implement --------------------------------------------
    def _close(self):
        pass

    def _seed(self, seed=None):
        pass

    # ---------------------------------------- function specified for this class ---------------------------------------
    def _get_reward(self, pos, moved):
        # 報酬を返す。報酬の与え方が難しいが、ここでは
        # - ゴールにたどり着くと 100 ポイント
        # - ダメージはゴール時にまとめて計算
        # - 1ステップごとに-1ポイント(できるだけ短いステップでゴールにたどり着きたい)
        # とした
        if moved and (self.goal == pos).all():
            return max(100 - self.damage, 0)
        else:
            return -1

    def _get_damage(self, pos):
        # ダメージの計算
        field_type = self.FIELD_TYPES[self.MAP[tuple(pos)]]
        if field_type == 'S':
            return 0
        elif field_type == 'G':
            return 0
        elif field_type == '~':
            return 10 if np.random.random() < 1 / 10. else 0
        elif field_type == 'w':
            return 10 if np.random.random() < 1 / 2. else 0
        elif field_type == '=':
            return 11 if np.random.random() < 1 / 2. else 1

    def _is_movable(self, pos):
        # マップの中にいるか、歩けない場所にいないか
        return (
                0 <= pos[0] < self.MAP.shape[0]
                and 0 <= pos[1] < self.MAP.shape[1]
                and self.FIELD_TYPES[self.MAP[tuple(pos)]] != 'A'
        )

    def _observe(self):
        # マップに勇者の位置を重ねて返す
        observation = self.MAP.copy()
        observation[tuple(self.pos)] = self.FIELD_TYPES.index('Y')
        return observation

    def _is_done(self):
        # 今回は最大で self.MAX_STEPS までとした
        if (self.pos == self.goal).all():
            return True
        elif self.steps > self.MAX_STEPS:
            return True
        else:
            return False

    def _find_pos(self, field_type):
        return np.array(list(zip(*np.where(
            self.MAP == self.FIELD_TYPES.index(field_type)
        ))))
