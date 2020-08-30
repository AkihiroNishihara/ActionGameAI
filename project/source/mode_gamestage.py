import pygame
from pygame.locals import *
import itertools
import numpy as np
from project.source import header as h, class_generate_rect

TIME_STAGE = 30
PARAM_ACCEL = 10
DIST_BASE_MOVE = 10
SCREEN = Rect(0, 0, h.SCREEN_WIDTH, h.SCREEN_HEIGHT)


class GameStage:
    def __init__(self, _screen_class_arg, _path_file_stage, _is_training=False):
        self.mode_next = "END"
        self.screen = _screen_class_arg
        self.is_loop = True
        self.is_game_over = False
        self.is_game_clear = False
        self.is_training = _is_training
        self.time_start = pygame.time.get_ticks()
        self.time_remain = TIME_STAGE
        self.time_elapsed = 0
        # フォントの定義
        self.font = pygame.font.Font(None, 60)
        # ステージ情報のロード(0:空，1:ブロック，2:player，3:ゴール)
        self.list_info_stage, _list_pos_player_ini, _list_pos_goal_ini = self._load_info_gamestage(_path_file_stage)

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
        Player.left_image = pygame.image.load("../image/player.png").convert_alpha()  # 左向き
        Player.right_image = pygame.transform.flip(Player.left_image, 1, 0)  # 右向き
        Block.image = pygame.image.load("../image/brick.png").convert_alpha()
        Goal.image = pygame.image.load("../image/goal.png").convert_alpha()

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

        # メインループ
        if not _is_training:
            # 背景描写
            self.bg = pygame.Surface(SCREEN.size)
            self.bg.fill((200, 255, 255))
            self.screen.blit(self.bg, (0, 0))
            pygame.display.update()

            self._run_playing()

        # clock = pygame.time.Clock()
        # while self.is_loop:
        #     if not _is_training:
        #         clock.tick(60)
        #     self._get_time_remain()
        #     self._update_sprite()
        #     self._draw()
        #     pygame.display.update()
        #
        #     # イベント獲得
        #     self.list_event = pygame.event.get()
        #     for event in self.list_event:
        #         if event.type == QUIT:
        #             h.operation_finish()
        #         if event.type == KEYDOWN:
        #             if event.key == K_ESCAPE:
        #                 h.operation_finish()
        #
        #     self.player.check_status(goal)
        #     self.is_game_over = self._check_is_gameover(self.player)
        #     if self.is_game_over:
        #         self._process_gameover()
        #     if not self.is_game_over:
        #         self.is_game_clear = self.player.get_is_touch_goal()
        #         if self.is_game_clear:
        #             self._process_gameclear()
        #     self._key_handler()

        # 関数テスト用
        # self.try_function()

    # ステージのブロックの配置およびプレイヤーの初期位置の取得
    def _load_info_gamestage(self, _path_file_stage):
        list_info_gamestage = []
        list_pos_player_ini = []
        list_pos_goal_ini = []
        fp = open(_path_file_stage, 'r')
        list_lines = fp.readlines()
        for line in list_lines:
            line = line.replace('\n', '')
            list_temp = [int(s) for s in list(line)]
            list_info_gamestage.append(list_temp)

        for i, j in itertools.product(range(len(list_info_gamestage)), range(len(list_info_gamestage[0]))):
            if list_info_gamestage[i][j] == 2:
                list_pos_goal_ini = [i, j]
            elif list_info_gamestage[i][j] == 3:
                list_pos_player_ini = [i, j]
                list_info_gamestage[i][j] = 0

        return list_info_gamestage, list_pos_player_ini, list_pos_goal_ini

    # 経過時間あるいはプレイヤーの位置によるゲームオーバー判定
    def _check_is_gameover(self, _player):
        is_gameover = _player.get_is_on_ground()
        if self.time_remain <= 0:
            is_gameover = True
        return is_gameover

    def _process_gameover(self):
        for event in self.list_event:
            if event.key == K_RETURN:
                self.is_loop = False

    def _process_gameclear(self):
        for event in self.list_event:
            if event.key == K_RETURN:
                self.is_loop = False

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

    # def _key_handler(self):
    #     """キー入力処理"""
    #     for event in pygame.event.get():
    #         if event.type == QUIT:
    #             h.operation_finish()
    #         elif event.type == KEYDOWN and event.key == K_ESCAPE:
    #             h.operation_finish()

    def _run_playing(self):
        clock = pygame.time.Clock()
        while self.is_loop:
            clock.tick(60)  # 60fps
            self._update_time_remain()

            # ユーザからのキー入力を受け取り，スプライトを更新
            pressed_keys = pygame.key.get_pressed()
            tuple_pressed_key = (pressed_keys[K_RIGHT], pressed_keys[K_LEFT], pressed_keys[K_SPACE])
            self._update_sprite(_input_action=tuple_pressed_key)

            # 画面の更新
            self._update_display()

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

            # self.player.check_status(self.goal)
            # self.is_game_over = self._check_is_gameover(self.player)
            # if self.is_game_over:
            #     self._process_gameover()
            # if not self.is_game_over:
            #     self.is_game_clear = self.player.get_is_touch_goal()
            #     if self.is_game_clear:
            #         self._process_gameclear()
            # self._key_handler()

    def _check_status(self):
        self.player.update_status(self.goal)
        self.is_game_over = self._check_is_gameover(self.player)

        # プレイヤー操作時の処理
        if not self.is_training:
            if self.is_game_over:
                self._process_gameover()
            if not self.is_game_over:
                self.is_game_clear = self.player.get_is_touch_goal()
                if self.is_game_clear:
                    self._process_gameclear()

    def get_mode_next(self):
        return self.mode_next

    def try_function(self):
        x = self.get_state_around()
        print("x\n")

    # ---------------------------------------- function for DQN --------------------------------------------------------
    def _get_state_each(self, _index):
        is_state_wall = False

        if _index[0] < 0 or int(h.SCREEN_WIDTH / h.SIZE_IMAGE_UNIT) <= _index[0]:
            is_state_wall = True
        elif _index[1] < 0 or int(h.SCREEN_HEIGHT / h.SIZE_IMAGE_UNIT) <= _index[1]:
            is_state_wall = True

        if is_state_wall:
            state = 3
        else:
            state = self.list_info_stage[_index[1]][_index[0]]
        return state

    def step_training(self, _input_act_agent):
        self._update_time_remain()

        # エージェントからの入力を受け取り，スプライトの更新
        self._update_sprite(_is_training=True, _input_action=_input_act_agent)

        # ゲームの状態判定
        self._check_status()

        # self.player.check_status(self.goal)
        # self.is_game_over = self._check_is_gameover(self.player)
        # if self.is_game_over:
        #     self._process_gameover()
        # if not self.is_game_over:
        #     self.is_game_clear = self.player.get_is_touch_goal()
        #     if self.is_game_clear:
        #         self._process_gameclear()

    def get_state_around(self, _num_around=4):
        tuple_state_around = ()
        # index_x, index_y: 現在プレイヤーの中心が所属する格子点の番号
        index_x = int(self.player.rect.center[0] / h.SIZE_IMAGE_UNIT)
        index_y = int(self.player.rect.center[1] / h.SIZE_IMAGE_UNIT)

        # 上下左右の座標
        index_right = (index_x + 1, index_y)
        index_left = (index_x - 1, index_y)
        index_up = (index_x, index_y - 1)
        index_down = (index_x, index_y + 1)

        # 上下左右の状態
        state_up = self._get_state_each(index_up)
        state_right = self._get_state_each(index_right)
        state_down = self._get_state_each(index_down)
        state_left = self._get_state_each(index_left)

        # 上下左右の状態を返す
        if _num_around == 4:
            tuple_state_around = (state_up, state_right, state_down, state_left)
        return tuple_state_around

    # 報酬を設定して返す
    def get_reward(self):
        param_state_game = 0  # 0:continue, 1:clear, -1:gameover
        if self.is_game_clear:
            param_state_game = 1
        elif self.is_game_over:
            param_state_game = -1
        dist = self.player.get_dist()
        reward = (self.time_remain + 0.001) * dist * 10 ** param_state_game
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

        # 位置のフラグ
        self.is_on_block = False
        self.is_on_ground = False
        self.is_touch_goal = False

        self.coef_speed = 1
        if _is_training:
            self.coef_speed = PARAM_ACCEL

    # スプライトの更新(Spriteクラスのoverride)
    def update(self, _is_training=False, _input_action=()):
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
            self.dist = np.linalg.norm(xy_player - xy_goal)
            if self.dist <= h.SIZE_IMAGE_UNIT:
                self.is_touch_goal = True

    def get_is_on_ground(self):
        return self.is_on_ground

    def get_is_touch_goal(self):
        return self.is_touch_goal

    def get_dist(self):
        return self.dist

    # _tuple_pressed_key = (right, left, space)
    def action(self, _tuple_pressed_key):
        if _tuple_pressed_key[0]:
            self.image = self.right_image
            self.fpvx = self.MOVE_SPEED * self.coef_speed
        elif _tuple_pressed_key[1]:
            self.image = self.left_image
            self.fpvx = -self.MOVE_SPEED * self.coef_speed
        else:
            self.fpvx = 0.0

        # ジャンプ
        if _tuple_pressed_key[2]:
            if self.is_on_block:
                self.fpvy = - self.JUMP_SPEED * self.coef_speed  # 上向きに初速度を与える
                self.is_on_block = False

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
