# ActionGameAI
##必要なパッケージ
Pythonをインストールした後に，下記のパッケージをコンソールからpyhtonのpipを用いてインストールして下さい．
その他にも，ご自身の環境によっては必要なパッケージが無い場合もあるので，その都度必要なパッケージをインストールして下さい．
コマンド例：`python -m pip install pygame`
* pygame
* keras
* numpy
* tensorflow
* gym


## play方法:
### ゲームのプレイ
任意の画面において，ESCキーで強制終了が可能
* メイン画面： 下記のキーを入力すると，各ステージをAIまたはユーザがプレイ

|ステージ番号|1|2|3|4|5|6|7|8|9|
|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|
|入力キー(ユーザプレイ)|1|2|3|4|5|6|7|8|9|
|入力キー(AIプレイ)|Q|W|E|R|T|Y|U|I|O|

* ステージ画面: Rightキーで右に進み，離すと止まります．Spaceキーでジャンプします． 左へは進みません．<br>黒い星があなたです，ハートの所まで移動しましょう．画面下に落ちるとゲームオーバーです．<br>クリア時，またはゲームオーバー時はエンターキーでゲーム終了画面へ移動します．
* ゲーム終了画面: エンターキーでメイン画面に移動します．

### ステージの作成および学習
* ステージの作成: source/stage_sample.txtがステージ情報です，これを書き換えることで任意のステージが構築できます．各数字は，0:空中，1:ブロック，2:ゴール，4:プレイヤー初期位置になります．なお3は内部でゲーム画面端に使っているので入力しないで下さい．
* ステージの作成後はsource/DQN.pyを実行すると，作成したステージを学習します．


## referenced URL
### Pygame:
[【Pygame入門】ゲームプログラミング【Python】 | 西住工房](https://algorithm.joho.info/programming/python/pygame/)<br>
[ブロックとの衝突判定 - 人工知能に関する断創録](http://aidiary.hatenablog.com/entry/20081129/1281614716)

### DQN，Gym:
[OpenAI Gym で自前の環境をつくる - Qiita](https://qiita.com/ohtaman/items/edcb3b0a2ff9d48a7def)
[【強化学習】OpenAI Gym×Keras-rlで強化学習アルゴリズムを実装していくぞ（準備編） - Qiita](https://qiita.com/pocokhc/items/a8120b0abd5941dd7a9f)
[CartPoleでDQN（deep Q-learning）、DDQNを実装・解説【Phythonで強化学習：第2回】](http://neuro-educator.com/rl2/)