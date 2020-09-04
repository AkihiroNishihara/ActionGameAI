import pygame
from pygame.locals import *
import itertools
import numpy as np
import os
import sys
import header as h, class_generate_rect, DQN
from keras.models import model_from_json
from keras.optimizers import Adam

TIME_STAGE = 99
PARAM_ACCEL = 1
DIST_BASE_MOVE = 10
SCREEN = Rect(0, 0, h.SCREEN_WIDTH, h.SCREEN_HEIGHT)


# _player = {'USER': 人間のユーザ，'AI': ニューラルネットワークのモデル，'AGENT': DQNの学習エージェント}
class GameStage:
    def __init__(self, _screen_class_arg, _num_stage, _actor):
        self.mode_next = "END"
        self.screen = _screen_class_arg
        self.is_continue_playing = True
        self.is_game_over = False
        self.is_game_clear = False
        self.is_training = True if (_actor is 'AGENT') else False
        self.actor = _actor
        self.time_remain = TIME_STAGE
        self.time_elapsed = 0
        # フォントの定義
        self.font = pygame.font.Font(None, 60)
        # ステージ情報のロード(0:空，1:ブロック，2:ゴール，3:壁，4:player)
        self.list_info_stage, _list_pos_player_ini, _list_pos_goal_ini = self._load_info_gamestage(_num_stage)

        # テキストオブジェクトの生成
        self.rect_gameover = class_generate_rect.Rectangle("Game Over", _is_alpha=True, is_centering=True,
                                                           _color=(50, 50, 50), _size_font=60)
        self.rect_gameclear = class_generate_rect.Rectangle("Game Clear", _is_alpha=True, is_centering=True,
                                                            _color=(50, 50, 50), _size_font=60)
        self.rect_ope = class_generate_rect.Rectangle("press Enter", _is_alpha=True, is_centering=True,
                                                      _color=(0, 255, 0), _size_font=60)

        # テキストオブジェクトの初期位置更新
        self.rect_gameover.update_pos_rect(0, -50)
        self.rect_ope.update_pos_rect(0, 100)

        # 画像のロード
        Player.left_image = pygame.image.load("./project/image/player.png").convert_alpha()  # 左向き
        Player.right_image = pygame.transform.flip(Player.left_image, 1, 0)  # 右向き
        Block.image = pygame.image.load("./project/image/brick.png").convert_alpha()
        Goal.image = pygame.image.load("./project/image/goal.png").convert_alpha()

        # スプライトグループの作成
        self.all = pygame.sprite.RenderUpdates()
        self.blocks = pygame.sprite.Group()
        Block.containers = self.all, self.blocks
        Goal.containers = self.all
        Player.containers = self.all

        # 各スプライトの生成
        self._create_blocks()
        self.player = Player(self._get_pos_topleft(_list_pos_player_ini), self.blocks, _is_training=self.is_training)
        self.goal = Goal(self._get_pos_topleft(_list_pos_goal_ini))

        # モデルのロード
        self.model = None
        if not self.is_training and not (self.player == 'USER'):
            self._load_model(_num_stage)

        # DQN用の値の初期化
        self.dist_old = self.player.get_dist()
        self.x_old = self.player.rect.centerx
        self.index_width_old = int(self.player.rect.centerx / h.SIZE_IMAGE_UNIT)
        self.weight_take_off = 0
        # メインループ
        self.time_start = pygame.time.get_ticks()
        if not self.is_training:
            # 背景描写
            self.bg = pygame.Surface(SCREEN.size)
            self.bg.fill((200, 255, 255))
            self.screen.blit(self.bg, (0, 0))
            pygame.display.update()

            self._run_playing()

    # ステージのブロックの配置およびプレイヤーの初期位置の取得
    def _load_info_gamestage(self, _num_stage):
        list_info_gamestage = []
        list_pos_player_ini = []
        list_pos_goal_ini = []
        if self.is_training:
            _path_file_stage = './project/source/stage_sample.txt'
        else:
            _path_file_stage = './project/network/model_stage{0}/stage{0}.txt'.format(_num_stage)
        fp = open(_path_file_stage, 'r')
        list_lines = fp.readlines()
        for line in list_lines:
            line = line.replace('\n', '')
            list_temp = [int(s) for s in list(line)]
            list_info_gamestage.append(list_temp)

        for i, j in itertools.product(range(len(list_info_gamestage)), range(len(list_info_gamestage[0]))):
            if list_info_gamestage[i][j] == 2:
                list_pos_goal_ini = [i, j]
            elif list_info_gamestage[i][j] == 4:
                list_pos_player_ini = [i, j]
                list_info_gamestage[i][j] = 0

        return list_info_gamestage, list_pos_player_ini, list_pos_goal_ini

    def _load_model(self, _num_stage):
        path_dir = './project/network/model_stage{0}'.format(_num_stage)
        str_model = open(path_dir + '/mainQN_model.json', 'r').read()
        self.model = model_from_json(str_model)
        self.model.compile(loss=DQN.huberloss, optimizer=Adam(lr=DQN.LEARNING_RATE))
        self.model.load_weights(path_dir + '/mainQN_weights.hdf5')

    # 経過時間あるいはプレイヤーの位置によるゲームオーバー判定
    def _check_is_gameover(self, _player):
        is_gameover = _player.get_is_on_ground()
        if self.time_remain <= 0:
            is_gameover = True
        return is_gameover

    def _process_end_game(self):
        keys = pygame.key.get_pressed()
        if keys[K_RETURN]:
            self.is_continue_playing = False
        #
        # for event in _list_event:
        #     if event.key == K_RETURN:
        #         self.is_loop = False

    def _get_pos_topleft(self, xy):
        return tuple([h.SIZE_IMAGE_UNIT * xy[1], h.SIZE_IMAGE_UNIT * xy[0]])

    def _create_blocks(self):
        for i, j in itertools.product(range(1, int(h.SCREEN_HEIGHT / h.SIZE_IMAGE_UNIT)),
                                      range(int(h.SCREEN_WIDTH / h.SIZE_IMAGE_UNIT))):
            if self.list_info_stage[i][j] == 1:
                Block(self._get_pos_topleft([i, j]))

    def _update_time_remain(self):
        if not self.is_game_over and not self.is_game_clear:
            param_time_accel = 1
            if self.is_training:
                param_time_accel = PARAM_ACCEL
            self.time_elapsed = param_time_accel * int((pygame.time.get_ticks() - self.time_start) / 1000)
            self.time_remain = TIME_STAGE - self.time_elapsed

    def _update_sprite(self, _is_training=False, _input_action=()):
        # スプライトの更新
        self.all.update(_is_training, _input_action)

    def _update_display(self):
        # 背景の描写
        self.all.clear(self.screen, self.bg)
        pygame.draw.rect(self.screen, (200, 200, 200), Rect(0, 0, h.SCREEN_WIDTH, h.SIZE_IMAGE_UNIT))  # 画面上部の四角形の描写

        # 経過時間の描写
        self._update_time_remain()
        text_time_remain = self.font.render(str(max(0, self.time_remain)), True, (255, 0, 0))  # テキストの作成
        self.screen.blit(text_time_remain, [0, 0])

        # 更新されたスプライトの取得
        dirty_rect = self.all.draw(self.screen)

        if self.is_game_over:
            self.screen.blit(self.rect_gameover.get_obj(), self.rect_gameover.get_pos())
            self.screen.blit(self.rect_ope.get_obj(), self.rect_ope.get_pos())

        if self.is_game_clear:
            self.screen.blit(self.rect_gameclear.get_obj(), self.rect_gameover.get_pos())
            self.screen.blit(self.rect_ope.get_obj(), self.rect_ope.get_pos())

        pygame.display.update()

    def _run_playing(self):
        clock = pygame.time.Clock()
        while self.is_continue_playing:
            clock.tick(60)  # 60fps
            self._update_time_remain()

            dict_pressed_key = {}
            if self.actor == 'USER':
                # ユーザの操作からキー入力を受け取る
                pressed_keys = pygame.key.get_pressed()
                dict_pressed_key = {'right': pressed_keys[K_RIGHT], 'left': pressed_keys[K_LEFT],
                                    'space': pressed_keys[K_SPACE]}
            else:
                # 現在の周囲の状態からキー入力を受け取る
                state_current = self.get_observation_around()
                state_current = np.array(state_current).reshape([1, len(state_current)])
                list_reward = self.model.predict(np.array(state_current))[0]
                action_int = np.argmax(list_reward)
                dict_pressed_key = DQN.get_dict_action(_int_act=action_int)
            self._update_sprite(_input_action=dict_pressed_key)

            # 強制終了のイベント獲得
            self.list_event = pygame.event.get()
            for event in self.list_event:
                if event.type == QUIT:
                    h.operation_finish()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        h.operation_finish()

            # ゲームの状態判定
            self._check_status()

            # 画面の更新
            self._update_display()

            # プレイヤー操作時の処理
            if not self.is_training:
                if self.is_game_over or self.is_game_clear:
                    self._process_end_game()

    def _check_status(self):
        self.player.update_status(self.goal)
        self.is_game_over = self._check_is_gameover(self.player)
        self.is_game_clear = self.player.get_is_touch_goal()

    def get_mode_next(self):
        return self.mode_next

    def try_function(self):
        x = self.get_observation_around()
        print("x\n")

    # ---------------------------------------- function for DQN --------------------------------------------------------
    def _get_observation_each(self, _index):
        is_state_wall = False

        if _index[0] < 0 or int(h.SCREEN_HEIGHT / h.SIZE_IMAGE_UNIT) <= _index[0]:
            is_state_wall = True
        elif _index[1] < 0 or int(h.SCREEN_WIDTH / h.SIZE_IMAGE_UNIT) <= _index[1]:
            is_state_wall = True

        if is_state_wall:
            state = 3
        else:
            state = self.list_info_stage[_index[0]][_index[1]]
        return state

    def step_training(self, _input_act_agent):
        self._update_time_remain()

        # エージェントからの入力を受け取り，スプライトの更新
        self._update_sprite(_is_training=True, _input_action=_input_act_agent)

        # ゲームの状態判定
        self._check_status()

    # 上，右上，右，右下，下の5マス，およびマス内の現在位置(x, y)を観測
    def get_observation_around(self, _num_around=DQN.SIZE_STATE):
        observation = []
        # キャラが所属するマスの周囲5マス観測
        rect_player = None
        if DQN.OBSERVE_PLAYER is 'CENTER':
            rect_player = self.player.rect.center
        elif DQN.OBSERVE_PLAYER is 'LEFT':
            # rect_player = (self.player.rect.left, self.player.rect.centery)
            rect_player = self.player.rect.bottomleft
        elif DQN.OBSERVE_PLAYER is 'RIGHT':
            # rect_player = (self.player.rect.right, self.player.rect.centery)
            rect_player = self.player.rect.bottomright
        else:
            print('Error: wrong OBSERVE_PLAYER', file=sys.stderr)
            os.system('PAUSE')
            exit(-1)
        # index_height, index_width: 現在プレイヤーの中心が所属する格子点の番号
        index_height = int(rect_player[1] / h.SIZE_IMAGE_UNIT)
        index_width = int(rect_player[0] / h.SIZE_IMAGE_UNIT)
        for index_h, index_w in itertools.product(range(index_height + DQN.OBS_TOP, index_height + DQN.OBS_BOTTOM),
                                                  range(index_width + DQN.OBS_LEFT, index_width + DQN.OBS_RIGHT)):
            observation.append(self._get_observation_each((index_h, index_w)))
        # for index_h in range(index_height - 2, index_height + 3):
        #     temp_list = []
        #     for index_w in range(index_width, index_width + 5):
        #         # キャラがいる場所は無視
        #         temp_list.append(self._get_observation_each((index_h, index_w)))
        #     observation.append(temp_list)

        # マス内のキャラ（の左中心）が所属する座標を観測
        index_in_square = (rect_player[0] % h.SIZE_IMAGE_UNIT, rect_player[1] % h.SIZE_IMAGE_UNIT)
        observation.append(index_in_square[0])
        observation.append(index_in_square[1])
        return observation

    # 報酬を設定して返す
    @property
    def get_reward(self):
        # param_state_game = 0  # 0:continue, 1:clear, -1:gameover
        # if self.is_game_clear:
        #     param_state_game = 10
        # elif self.is_game_over and self.time_remain != 0.0:
        #     # 時間切れ以外でゲームオーバー，すなわち地面に落ちた場合はマイナス評価
        #     param_state_game = -1
        # dist_cur = self.player.get_dist()
        '''
        reward = (40 / dist_cur) ** 2 * 1000 ** param_state_game
        reward = (self.time_remain + 0.001)**2 * 1.0 / dist_cur * 1000 ** param_state_game
        reward = 100 / dist + (self.time_remain + 0.001) ** param_state_game - 1
        reward = 1000 ** param_state_game
        reward = (40 / dist) ** 3 * 1000 ** param_state_game
        reward = param_state_game * 40 / dist        
        reward = self.dist_old - dist_cur
        reward = (self.time_remain / dist_cur) ** param_state_game
        self.dist_old = dist_cur
        '''
        # reward = 1 if self.dist_old - dist_cur > 0 else -1
        '''
        1. 停止にマイナス評価を付与
        2. ジャンプにプラス評価を付与(ブロックから離れている状態)
        '''

        # 周囲の状態を獲得
        observation_around = self.get_observation_around()

        # 移動による報酬: 移動距離(右方向でプラス): ブロックのジャンプを積極的に行える
        x_cur = self.player.rect.centerx
        dif_x = x_cur - self.x_old
        reward = 0
        if dif_x > 0:
            reward = 1

        # 隣のセルに移動した際の追加報酬
        # index_width_cur = int(self.player.rect.centerx / h.SIZE_IMAGE_UNIT)
        # dif_index_width = index_width_cur - self.index_width_old
        # reward += dif_index_width * 100

        # ジャンプ時の報酬調整（正面にブロック，または右下が空きの場合に）
        """
        is_jump = self.player.get_is_jump()
        is_air = not self.player.get_is_on_block()
        weight_jump = 1
        # if is_jump:
        #     # 正面がブロックでない場合のジャンプ
        #     if observation_around[2] != 1:
        #         if observation_around[4] == 0:
        #             # 右下が空中: キャラ左端が崖ギリギリに近いほど重みが増える => キャラがギリギリで飛ぼうとする
        #             self.weight_take_off = observation_around[5] / h.SIZE_IMAGE_UNIT
        #             # self.weight_take_off = observation_around[5] / h.SIZE_IMAGE_UNIT
        #         else:
        #             # 右下が空中でない: 不要なジャンプ
        #             weight_reward_jump = 0
        #     else:
        #         weight_reward_jump = 2
        #     reward *= weight_reward_jump
        # if not is_air:
        #     self.weight_take_off = 1
        # reward *= self.weight_take_off
        if is_jump:
            # 正面がブロックでない，または右下が空中でない: 不要なジャンプ
            if observation_around[2] != 1 and observation_around[4] != 0:
                weight_jump = -1
            else:
                # 必要なジャンプ: 踏切位置に応じて重みを算出 => ブロックの端ギリギリで飛ぶ方が高スコア
                weight_jump = observation_around[5] ** 2
        if not is_air:
            self.weight_take_off = 1
        reward *= self.weight_take_off

        # 空中，移動に大きな重み
        weight_air = 1
        if is_air:
            weight_air = 10

        reward *= weight_jump * weight_air
"""
        # ゲームの状態による追加報酬
        # if self.is_game_over and self.time_remain != 0:
        #     # 地面に落下時： 報酬マイナス
        #     reward -= 10

        if DQN.FUNC_REWARD == 1:
            # 追加の報酬調整
            # index_width_cur = int(self.player.rect.centerx / h.SIZE_IMAGE_UNIT)
            # dif_index_width = index_width_cur - self.index_width_old
            # if dif_index_width>0:
            #     reward += index_width_cur * 100

            is_jump = self.player.get_is_jump()
            is_air = not self.player.get_is_on_block()
            weight_jump = 1
            if is_jump:
                # 正面がブロックでない，または右下が空中でない: 不要なジャンプ
                if observation_around[1] != 1 and observation_around[2] != 0:
                    weight_jump = -1
            # else:
            #     # 必要なジャンプ: 踏切位置に応じて重みを算出 => ブロックの端ギリギリで飛ぶ方が高スコア
            #     # weight_jump = (observation_around[5] / h.SIZE_IMAGE_UNIT) ** 2
            #     weight_jump = 1 - (1 - observation_around[3] / h.SIZE_IMAGE_UNIT) ** 4

            # if not is_air:
            #     self.weight_take_off = 1
            # reward *= self.weight_take_off

            # 空中，移動に大きな重み
            # weight_air = 1
            # if is_air:
            #     weight_air = 10

            reward *= weight_jump
            # 実質ゲームオーバー
            if self.player.rect.bottom > h.SCREEN_HEIGHT - h.SIZE_IMAGE_UNIT:
                reward = -1

        if self.is_game_clear:
            reward = 1
        if self.is_game_over and self.time_remain != 0:
            # 地面に落下時： 報酬マイナス
            reward = -1
        # if self.is_game_clear:
        #     reward += self.time_remain * 10
        # if self.is_game_over and self.time_remain != 0:
        #     # 地面に落下時： 報酬マイナス
        #     reward = -1
        index_width_cur = self.player.rect.centerx / h.SIZE_IMAGE_UNIT
        # reward = index_width_cur - self.index_width_old
        # if self.is_game_over:
        #     reward = -1

        # パラメータの更新
        self.x_old = x_cur
        self.index_width_old = index_width_cur

        return reward

    # 終了状態か否かを返す
    def get_is_done(self):
        is_done = False
        if self.is_game_over or self.is_game_clear:
            is_done = True
        return is_done


class Player(pygame.sprite.Sprite):
    MOVE_SPEED = 2.5  # 移動速度
    JUMP_SPEED = 6.0  # ジャンプの初速度
    GRAVITY = 0.2  # 重力加速度

    def __init__(self, pos, blocks, _is_training=False):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.right_image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos[0], pos[1]  # 座標設定
        self.blocks = blocks  # 衝突判定用
        self.dist = 1.0e14  # ゴールまでの距離（初期値）

        # 浮動小数点の位置と速度
        self.fpx = float(self.rect.x)
        self.fpy = float(self.rect.y)
        self.fpvx = 0.0
        self.fpvy = 0.0

        # 各フラグ
        self.is_on_block = False
        self.is_on_ground = False
        self.is_touch_goal = False
        self.is_jump = False

        self.coef_speed = 1
        if _is_training:
            self.coef_speed = PARAM_ACCEL

    # スプライトの更新(Spriteクラスのoverride)
    def update(self, _is_training=False, _input_action={}):
        if not self.is_on_ground and not self.is_touch_goal:
            self.action(_input_action)

    def _collision_x(self):
        """X方向の衝突判定処理"""
        # パイソンのサイズ
        width = self.rect.width
        height = self.rect.height

        # X方向の移動先の座標と矩形を求める
        newx = self.fpx + self.fpvx
        newrect = Rect(newx, self.fpy, width, height)

        # ブロックとの衝突判定
        for block in self.blocks:
            collide = newrect.colliderect(block.rect)
            if collide:  # 衝突するブロックあり
                if self.fpvx > 0:  # 右に移動中に衝突
                    # めり込まないように調整して速度を0に
                    self.fpx = block.rect.left - width
                    self.fpvx = 0
                elif self.fpvx < 0:  # 左に移動中に衝突
                    self.fpx = block.rect.right
                    self.fpvx = 0
                break  # 衝突ブロックは1個調べれば十分
            else:
                # 衝突ブロックがない場合、位置を更新
                self.fpx = newx

        # 壁との衝突判定
        if self.rect.left <= 0 and self.fpvx <= 0:
            self.fpx = 0
            self.fpvx = 0
        elif self.rect.right >= h.SCREEN_WIDTH and self.fpvx > 0:
            self.fpx = self.rect.right - width
            self.fpvx = 0

    def _collision_y(self):
        """Y方向の衝突判定処理"""
        # パイソンのサイズ
        width = self.rect.width
        height = self.rect.height

        # Y方向の移動先の座標と矩形を求める
        newy = self.fpy + self.fpvy
        newrect = Rect(self.fpx, newy, width, height)

        # ブロックとの衝突判定
        for block in self.blocks:
            collide = newrect.colliderect(block.rect)
            if collide:  # 衝突するブロックあり
                if self.fpvy > 0:  # 下に移動中に衝突
                    # めり込まないように調整して速度を0に
                    self.fpy = block.rect.top - height
                    self.fpvy = 0
                    # 下に移動中に衝突したならブロックの上にいる
                    self.is_on_block = True
                elif self.fpvy < 0:  # 上に移動中に衝突
                    self.fpy = block.rect.bottom
                    self.fpvy = 0
                break  # 衝突ブロックは1個調べれば十分
            else:
                # 衝突ブロックがない場合、位置を更新
                self.fpy = newy
                # 衝突ブロックがないならブロックの上にいない
                self.is_on_block = False

        # 床との接触判定
        if self.rect.bottom >= h.SCREEN_HEIGHT:
            self.fpy = h.SCREEN_HEIGHT - height
            self.fpvy = 0

    # プレイヤーの現在位置からの状態判定（接地によるgame-over，ゴール接触によるgame-clear）
    def update_status(self, _goal):
        if self.rect.bottom == h.SCREEN_HEIGHT:
            self.is_on_ground = True
        else:
            xy_player = np.array(self.rect.center)
            xy_goal = np.array(_goal.rect.center)
            # xy_player = np.array(self.rect.bottomright)
            # xy_goal = np.array(_goal.rect.topleft)
            self.dist = np.linalg.norm(xy_player - xy_goal)
            if self.dist <= h.SIZE_IMAGE_UNIT:
                self.is_touch_goal = True

    def get_is_on_ground(self):
        return self.is_on_ground

    def get_is_on_block(self):
        return self.is_on_block

    def get_is_touch_goal(self):
        return self.is_touch_goal

    def get_dist(self):
        return self.dist

    # _tuple_pressed_key = (right, left, space)
    def action(self, _dict_input):
        if _dict_input['right']:
            self.image = self.right_image
            self.fpvx = self.MOVE_SPEED * self.coef_speed
        else:
            self.fpvx = 0.0

        # ジャンプ
        self.is_jump = False
        if _dict_input['space']:
            if self.is_on_block:
                self.fpvy = - self.JUMP_SPEED * self.coef_speed  # 上向きに初速度を与える
                self.is_on_block = False
                self.is_jump = True

        # 速度を更新
        if not self.is_on_block:
            self.fpvy += self.GRAVITY * self.coef_speed  # 下向きに重力をかける

        # X方向の衝突判定処理
        self._collision_x()

        # この時点でX方向に関しては衝突がないことが保証されてる

        # Y方向の衝突判定処理
        self._collision_y()

        # 浮動小数点の位置を整数座標に戻す
        # スプライトを動かすにはself.rectの更新が必要！
        self.rect.x = int(self.fpx)
        self.rect.y = int(self.fpy)

    def get_is_jump(self):
        return self.is_jump


class Block(pygame.sprite.Sprite):
    def __init__(self, _pos):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.topleft = _pos


class Goal(pygame.sprite.Sprite):
    def __init__(self, _pos):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.topleft = _pos
