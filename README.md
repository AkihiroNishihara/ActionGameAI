# ActionGameAI
この作品およびreadmeはWindowsPCでの実行を想定しています．
##必要なパッケージ
Pythonをインストールした後に，下記のパッケージをコンソールからpyhtonのpipを用いてインストールして下さい．
その他にも，ご自身の環境によっては必要なパッケージが無い場合もあるので，その都度必要なパッケージをインストールして下さい．
コマンド例：`python -m pip install pygame`
* pygame
* keras
* numpy
* tensorflow
* gym


## play方法
### ゲームのプレイ
"play_game.bat"より実行してください．実行後は任意の画面において，ESCキーで強制終了が可能
* メイン画面： 下記のキーを入力すると，各ステージをAIまたはユーザがプレイします．
ステージ1~7はそれぞれ学習済みのAI(クリアできるとは限らない)，ステージ0はステージ1と同じステージですが，AIは全くの未学習です．
ステージ8,9は下の自作ステージ用の空きファイルです，自作ステージをここに登録していないとエラーが出ます．

|ステージ番号|1|2|3|4|5|6|7|8|9|0|
|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|
|入力キー(ユーザプレイ)|1|2|3|4|5|6|7|8|9|0|
|入力キー(AIプレイ)|Q|W|E|R|T|Y|U|I|O|P|

* ステージ画面: Rightキーで右に進み，離すと止まります．Spaceキーでジャンプします． 左へは進みません．<br>黒い星があなたです，ハートの所まで移動しましょう．画面下に落ちるとゲームオーバーです．<br>クリア時，またはゲームオーバー時はエンターキーでゲーム終了画面へ移動します．
* ゲーム終了画面: エンターキーでメイン画面に移動します．

### ステージの作成および学習
* ステージの作成: source/stageX.txtがステージ情報です，これを書き換えることで任意のステージが構築できます．Xには0~9の数字を入れると，上記のステージとモデルを上書きします．8,9は空きステージなのでここに自作ステージを登録すると良いです．<br>
ステージファイル内の各数字は，0:空中，1:ブロック，2:ゴール，4:プレイヤー初期位置になります．なお3は内部でゲーム画面端に使っているので入力しないで下さい．
* ステージの学習: 同梱の"learn_DQN.bat"を実行してください．コンソールにはAIの入力（20ステップごと）および平均の報酬，クリア状況などが出力されます．


## referenced URL
### Pygame:
[【Pygame入門】ゲームプログラミング【Python】 | 西住工房](https://algorithm.joho.info/programming/python/pygame/)<br>
[ブロックとの衝突判定 - 人工知能に関する断創録](http://aidiary.hatenablog.com/entry/20081129/1281614716)

### DQN，Gym:
[OpenAI Gym で自前の環境をつくる - Qiita](https://qiita.com/ohtaman/items/edcb3b0a2ff9d48a7def)<br>
[【強化学習】OpenAI Gym×Keras-rlで強化学習アルゴリズムを実装していくぞ（準備編） - Qiita](https://qiita.com/pocokhc/items/a8120b0abd5941dd7a9f)<br>
[CartPoleでDQN（deep Q-learning）、DDQNを実装・解説【Phythonで強化学習：第2回】](http://neuro-educator.com/rl2/)