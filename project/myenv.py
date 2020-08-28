import sys

import gym
import gym.spaces
import io
import pygame

from project import mode_gamestage


class MyEnv(gym.Env):
    # metadata = {'render.modes': ['human', 'ansi']}
    MAX_STEPS = 100

    def __init__(self, _path_file_stage, _screen):
        super().__init__()
        self.path_file_stage = _path_file_stage

        # action_space, observation_space, reward_range を設定する
        # 行動空間：離散値（right, left, jumpの各キーのON,OFF）
        self.action_space = gym.spaces.MultiBinary(3)

        # 状態空間：離散値（0:無し, 1：ブロック, 2：ゴール, 3:壁），上右下左の4方向を観測
        self.observation_space = gym.spaces.Discrete(4)

        # # 報酬の範囲
        # self.reward_range = [0.0, inf)
        self._reset(_screen)

    # ---------------------------------------- function required -------------------------------------------------------
    # ゲームを呼び出すことで初期化
    def _reset(self, _screen):
        self.game_stage = mode_gamestage.GameStage(_screen_class_arg=_screen, _path_file_stage=self.path_file_stage,
                                                   _is_training=True)

    # _actionは（right, left, jump）の各キーのON,OFFで獲得
    def _step(self, _action):
        self.game_stage.step_training(_action)

        # 状態，報酬，終了条件の取得
        observation = self.game_stage.get_state_around()
        reward = self.game_stage.get_reward()
        self.done = self.game_stage.get_is_done()
        info = {}

        return observation, reward, self.done, info

    def _render(self, mode='human', close=False):
        pass
        # human の場合はコンソールに出力。ansiの場合は StringIO を返す
        # outfile = io.StringIO() if mode == 'ansi' else sys.stdout
        # outfile.write('\n'.join(' '.join(self.FIELD_TYPES[elem] for elem in row) for row in self._observe()) + '\n')
        # return outfile

    # ---------------------------------------- function better to implement --------------------------------------------
    def _close(self):
        pass

    def _seed(self, seed=None):
        pass

    # ---------------------------------------- function specified for this class ---------------------------------------

    # def _get_damage(self, pos):
    #     # ダメージの計算
    #     field_type = self.FIELD_TYPES[self.MAP[tuple(pos)]]
    #     if field_type == 'S':
    #         return 0
    #     elif field_type == 'G':
    #         return 0
    #     elif field_type == '~':
    #         return 10 if np.random.random() < 1 / 10. else 0
    #     elif field_type == 'w':
    #         return 10 if np.random.random() < 1 / 2. else 0
    #     elif field_type == '=':
    #         return 11 if np.random.random() < 1 / 2. else 1
    #
    # def _is_movable(self, pos):
    #     # マップの中にいるか、歩けない場所にいないか
    #     return (
    #             0 <= pos[0] < self.MAP.shape[0]
    #             and 0 <= pos[1] < self.MAP.shape[1]
    #             and self.FIELD_TYPES[self.MAP[tuple(pos)]] != 'A'
    #     )
    #
    # def _observe(self):
    #     # マップに勇者の位置を重ねて返す
    #     observation = self.MAP.copy()
    #     observation[tuple(self.pos)] = self.FIELD_TYPES.index('Y')
    #     return observation
    #
    # def _is_done(self):
    #     # 今回は最大で self.MAX_STEPS までとした
    #     if (self.pos == self.goal).all():
    #         return True
    #     elif self.steps > self.MAX_STEPS:
    #         return True
    #     else:
    #         return False
    #
    # def _find_pos(self, field_type):
    #     return np.array(list(zip(*np.where(
    #         self.MAP == self.FIELD_TYPES.index(field_type)
    #     ))))
