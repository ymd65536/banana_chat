# 1. 仮想環境を作成 (プロジェクトごとに環境を分離するため推奨)

```bash
python -m venv test
```

※Python3.9.6を前提にしています。

# 2. 仮想環境を有効化

## Windowsの場合

```bash
.venv\Scripts\activate
```

## macOS/Linuxの場合

```bash
source .venv/bin/activate
```

# 3. PySide6ライブラリをインストール

```bash
pip install pyside6
```

# pyside6-designer

```bash
pyside6-designer
```

# UIファイルをPythonコードに変換

```bash
pyside6-uic main_window.ui -o ui_main_window.py
```

# GenaI SDKとGemini APIキーの設定

```bash
pip install google-genai
pip install pillow
```

変更前のGoogle GenAI SDK（Vertex AI SDK）

```bash
pip install google-generativeai
```

コード

```python
import google.generativeai as genai

genai.configure(api_key=self.api_key)
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content(self.prompt)
```

## まとめ

この「UIデザイン(Designer)とロジック(Pythonコード)を分離する」方法が、PythonでQtアプリを開発する際の王道です。
見た目の修正が簡単になり、コードもすっきりと保つことができます。
ぜひこの手順をベースに、色々なウィジェットを配置したり、複雑な動作を実装したりして、オリジナルのアプリケーションを作成してみてください。

# references

[Qt for Python](https://wiki.qt.io/Qt_for_Python)
