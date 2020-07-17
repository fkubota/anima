# i-sed-pyqt5

## このアプリはなに？
[このアプリ](https://interactiveaudiolab.github.io/project/ised.html)を参考につくりました。
音データをラベリングするツールです。あるターゲット音1種類を探す時に使います。例えば音声ファイルの中にクシャミが含まれていてその音をラベリングしたいなどです。  
また、このツールにはラベルレコメンド機能がついています。ラベリングしたデータに似たデータを自動で抽出しレコメンドしてくれます。レコメンドされたラベルに対し正否を判断しフィードバックすることでレコメンド性能は徐々に向上していきます。

## Installation
- めっちゃ簡単に動かしたい人向けの説明
    - 実行ファイルがビルドされているのでそれを動かすだけです
    - 手順
        1. リポジトリをクローンする
        2. `chmod u+x i-sed-pyqt5/app/dist/main/main`

- developer 向けの説明


## build
- build command
    - `cd app`
    - `pyinstaller main.spec`
- sklearnとscipyのビルドをするのはちょっとむずかしい。
- app/main.spec ファイルに以下を書き足したら動いた。
```
hiddenimports=['scipy.special.cython_special', 'sklearn.utils._cython_blas', 'sklearn.neighbors._typedefs', 'sklearn.neighbors._quad_tree', 'sklearn.tree', 'sklearn.tree._utils'],
```
