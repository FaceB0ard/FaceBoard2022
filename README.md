# 技育展2022
Geek-Ten develop repository

## 環境
### Anaconda
Anaconda環境でインストールを行うには、`Anaconda_FaceBoard_Environment.yaml`を用います。

```
conda env create -f Anaconda_FaceBoard_Environment.yaml
```

作成した環境には、`conda activate faceboard`で入ります。

### mpg123について
音声ライブラリである、mpg123を別途システムにインストール必要があります。

macOSの場合は`brew install mpg123`でインストールできます。

Windowsの場合は、以下の手順でシステムにインストールします。

1. [mpg123公式サイト](https://www.mpg123.de/download.shtml)からWindows用バイナリをダウンロードする。
このとき、システムにあったもの(32bitか64bitか)を選ぶ。
2. Zipファイルを任意の分かる場所に解凍する。(Cドライブ直下やホームディレクトリ(`%HOMEPATH%`)など)
3. システム環境変数のPathに上記の解凍後のディレクトリを追加する。
ターミナルから利用できるよう、指定したフォルダの下に`mpg123.exe`が来るようにします。
4. システム環境変数に、変数名: `MPG123_MODDIR`、変数値: `path/to/mpg123_directory/plugins`のように設定します。
pluginsディレクトリを変数値に設定します。




# キーボードの実行

```
python entry.py
```

# その他
詳細情報は[Notion](https://honey-transport-7a7.notion.site/FaceBoard-2022-0185dc2042b042689565e6c11101b620)を確認してください。
