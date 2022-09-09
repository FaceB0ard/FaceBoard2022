# 技育展2022
Geek-Ten develop repository

## 環境
### pipenv
pipenvは

```
python3 -m pip install pipenv
```

でインストールできます。

Pipfileにしたがって依存をすべてインストールしたい場合は`pipenv install`、新規にパッケージをインストールしたい場合は`pipenv install <パッケージ名>`で追加してください。

開発環境でのみ使いたいパッケージをインストールしたい場合は`pipenv install --dev <パッケージ名>`でインストール可能です。

作られた環境には`pipenv shell`で入れます。

### Anaconda
Anaconda環境でインストールを行うには、`package_list.txt`を用います。

```
conda create --name faceboard --file package_list.txt
```

作成した環境には、`conda activate faceboard`で入ります。

### mpg123について
音声ライブラリである、mpg123を別途システムにインストール必要があります。

macOSの場合は`brew install mpg123`でインストールできます。

Windowsの場合は、以下の手順でシステムにインストールします。

1. [mpg123公式サイト](https://www.mpg123.de/download.shtml)からWindows用バイナリをダウンロードする。
このとき、システムにあったもの(32bitか64bitか)を選ぶ。
2. Zipファイルを任意のわかる場所に解答する。(Cドライブ直下やホームディレクトリ(`%HOMEPATH%`)など)
3. システム環境変数のPathに上記の解凍後のディレクトリを追加する。
ターミナルから利用できるよう、指定したフォルダの下に`mpg123.exe`が来るようにします。
4. システム環境変数に、変数名: `MPG123_MODDIR`、変数値: `<path/to/mpg123_directory/plugins>`のように設定します。
pluginsディレクトリを変数値に設定します。




# キーボードの実行

```
pipenv run faceboard
```

Pipfileにscriptsとして登録されています。他にもショートカットを設定したい場合はここを利用してください。
