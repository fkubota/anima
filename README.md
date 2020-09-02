<img src='data/design/logo.png' width='800'>


## このアプリはなに？
[このアプリ](https://interactiveaudiolab.github.io/project/ised.html)を参考につくりました。
ヒューマンインザループ思想で作られた音データをラベリングするツールです。あるターゲット音1種類を探す時に使います。例えば音声ファイルの中にクシャミが含まれていてその音をラベリングしたいなどです。  
また、このツールにはラベルレコメンド機能がついています。ラベリングしたデータに似たデータを自動で抽出しレコメンドしてくれます。レコメンドされたラベルに対し正否を判断しフィードバックすることでレコメンド性能は徐々に向上していきます。

![Not Found](https://raw.github.com/wiki/fkubota/anima/gif/example01.gif)


## 使い方
- また今度書くやで

## Installation
- めっちゃ簡単に動かしたい人向けの説明
    - 実行ファイルがビルドされているのでそれを動かすだけです
    - 手順
        1. リポジトリをクローンする
        1. `chmod u+x anima/app/dist/anima/anima`  <--- 実行権限付与
        1. `./anima/app/dist/anima/anima`  <--- 実行

- developer 向けの説明
    - また今度書くやで


## build
- build command
    - `cd app`
    - `pyinstaller main.spec`
- sklearnとscipyのビルドをするのはちょっとむずかしい。
- app/main.spec ファイルに以下を書き足したら動いた。
```
hiddenimports=['scipy.special.cython_special', 'sklearn.utils._cython_blas', 'sklearn.neighbors._typedefs', 'sklearn.neighbors._quad_tree', 'sklearn.tree', 'sklearn.tree._utils'],
```
