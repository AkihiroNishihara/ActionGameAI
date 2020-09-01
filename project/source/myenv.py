import gym
import gym.spaces
import numpy as np

from project.source import mode_gamestage, DQN, header as h


class MyEnv(gym.Env):
    def __init__(self, _path_file_stage, _screen):
        super().__init__()
        self.path_file_stage = _path_file_stage

        '''
        <override attribution>
            action_space, observation_space, reward_range を設定する
            行動空間：マルチバイナリ（right, left, jumpの各キーのON,OFF）
            状態空間：離散値（0:無し, 1：ブロック, 2：ゴール, 3:壁），上右下左の4方向を観測
            報酬の範囲：0以上
        '''
        self.action_space = gym.spaces.MultiBinary(3)
        # self.observation_space = gym.spaces.Discrete(DQN.SIZE_STATE)
        self.observation_space = gym.spaces.Box(low=0.0, high=h.SIZE_IMAGE_UNIT, shape=(1, DQN.SIZE_STATE),
                                                dtype=np.float32)
        self.reward_range = (0.0, float('inf'))

        self.screen = _screen
        self.reset()

    # ---------------------------------------- function required -------------------------------------------------------
    # ゲームを呼び出すことで初期化
    def reset(self):
        self.game_stage = mode_gamestage.GameStage(_screen_class_arg=self.screen, _path_file_stage=self.path_file_stage,
                                                   _actor='AGENT')

    # _actionは（right, left, jump）の各キーのON,OFFで獲得
    def step(self, _action):
        self.game_stage.step_training(_action)

        # 状態，報酬，終了条件の取得
        observation = self.game_stage.get_observation_around()
        reward = self.game_stage.get_reward
        is_done = self.game_stage.get_is_done()
        info = {'GAMEOVER': self.game_stage.is_game_over, 'CLEAR': self.game_stage.is_game_clear,
                'TIME': self.game_stage.time_remain}

        return observation, reward, is_done, info

    def render(self, mode='human', close=False):
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
