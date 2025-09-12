from google import genai

from typing import Optional
import sys
import os
import base64
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QLineEdit, QPushButton, QListWidgetItem, QFileDialog
)
from PySide6.QtCore import Slot, QTimer, QThread, QObject, Signal

# 上で作成したカスタムウィジェットをインポート
from chat_message_widget import ChatMessageWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat UI")
        self.resize(400, 600)

        # --- UIのセットアップ ---
        # チャット履歴を表示するリストウィジェット
        self.chat_list_widget = QListWidget()
        self.chat_list_widget.setStyleSheet(
            "background-color: #f0f0f0; border: none;")

        # メッセージ入力欄
        self.message_line_edit = QLineEdit()
        self.message_line_edit.setPlaceholderText("メッセージを入力...")

        # 画像添付ボタン
        self.attach_button = QPushButton("📎")
        self.attach_button.setFixedWidth(40)  # ボタンの幅を調整

        # 送信ボタン
        self.send_button = QPushButton("送信")

        # --- レイアウトの設定 ---
        # 下部の入力欄と送信ボタン用のレイアウト
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.attach_button)
        bottom_layout.addWidget(self.message_line_edit)
        bottom_layout.addWidget(self.send_button)

        # 全体のメインレイアウト
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.chat_list_widget)
        main_layout.addLayout(bottom_layout)

        # セントラルウィジェットにレイアウトを設定
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # --- 添付ファイルの状態 ---
        self.attached_image_path: Optional[str] = None

        # --- 状態管理フラグ ---
        self.is_processing = False
        # --- スレッド管理 ---
        self.gemini_thread: Optional[QThread] = None
        self.worker: Optional[GeminiWorker] = None

        # --- シグナルとスロットの接続 ---
        self.attach_button.clicked.connect(self.on_attach_button_clicked)
        self.send_button.clicked.connect(self.on_send_button_clicked)
        # Enterキーでも送信できるようにする
        self.message_line_edit.returnPressed.connect(
            self.on_send_button_clicked)

        # --- 初期メッセージの追加 ---
        self.add_message(text="こんにちは、GitHub Copilotです。", is_my_message=False)
        self.add_message(text="こんにちは！", is_my_message=True)

    def add_message(self, text: Optional[str] = None, image_data_base64: Optional[str] = None, is_my_message: bool = False):
        """チャットリストに新しいメッセージ（テキストまたは画像）を追加する"""
        if is_my_message:
            self._add_message_to_widget(text, image_data_base64, is_my_message)
        else:
            # is_my_messageがFalseの場合、1秒後にメッセージを追加
            QTimer.singleShot(1000, lambda: self._add_message_to_widget(
                text, image_data_base64, is_my_message))

    def _add_message_to_widget(self, text: Optional[str], image_data_base64: Optional[str], is_my_message: bool):
        """実際にウィジェットを追加する内部メソッド"""
        # テキストが空でも画像があればウィジェットを作成
        if not text and not image_data_base64:
            return

        chat_message = ChatMessageWidget(
            text=text, image_data_base64=image_data_base64, is_my_message=is_my_message)
        list_item = QListWidgetItem(self.chat_list_widget)

        # QListWidgetItemのサイズをカスタムウィジェットの推奨サイズに合わせる
        list_item.setSizeHint(chat_message.sizeHint())

        self.chat_list_widget.addItem(list_item)
        self.chat_list_widget.setItemWidget(list_item, chat_message)

        # 自動で一番下までスクロール
        self.chat_list_widget.scrollToBottom()

    @Slot()
    def on_attach_button_clicked(self):
        """添付ボタンがクリックされたときに呼ばれる"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "画像を選択",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.attached_image_path = file_path
            # 添付されたファイル名を表示
            file_name = os.path.basename(file_path)
            self.message_line_edit.setPlaceholderText(f"添付中: {file_name}")

    @Slot()
    def on_send_button_clicked(self):
        """送信ボタンがクリックされたときに呼ばれる"""
        text = self.message_line_edit.text()
        original_image_path = self.attached_image_path
        image_data_base64 = None

        # 画像が添付されている場合、Base64にエンコードする
        if original_image_path:
            with open(original_image_path, "rb") as image_file:
                image_data = image_file.read()
                image_data_base64 = base64.b64encode(
                    image_data).decode("utf-8")

        # テキストも画像もなければ何もしない
        if not text and not image_data_base64:
            return

        self.add_message(
            text=text, image_data_base64=image_data_base64, is_my_message=True)

        # 送信後にリセット
        self.message_line_edit.clear()
        self.attached_image_path = None
        self.message_line_edit.setPlaceholderText("メッセージを入力...")

        # ここで相手からの返信をシミュレートするなどのロジックを追加できます
        if text:
            self.get_gemini_response(text)
        elif image_data_base64:
            self.add_message(text="素敵な画像ですね！", is_my_message=False)

    def get_gemini_response(self, prompt: str):
        """Geminiからの応答を非同期で取得する"""
        # 処理中であれば、新しいリクエストは受け付けない
        if self.is_processing:
            return

        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if not GEMINI_API_KEY:
            self.add_message(text="GEMINI_API_KEYが設定されていません。",
                             is_my_message=False)
            return

        # 状態を「処理中」に更新し、UIを無効化
        self.is_processing = True
        self.send_button.setEnabled(False)
        self.message_line_edit.setEnabled(False)
        self.add_message(text="...", is_my_message=False)

        # スレッドとワーカーをインスタンス変数として作成
        self.gemini_thread = QThread()
        self.worker = GeminiWorker(api_key=GEMINI_API_KEY, prompt=prompt)
        self.worker.moveToThread(self.gemini_thread)

        # 完了後にオブジェクトが自動で削除され、参照がクリーンアップされるように接続
        self.gemini_thread.started.connect(self.worker.run)
        self.worker.response_ready.connect(self.on_gemini_response)
        self.worker.error_occurred.connect(self.on_gemini_error)
        self.worker.response_ready.connect(self.gemini_thread.quit)
        self.worker.error_occurred.connect(self.gemini_thread.quit)
        self.gemini_thread.finished.connect(self.on_thread_finished)

        self.gemini_thread.start()

    @Slot(str)
    def on_gemini_response(self, response_text: str):
        """Geminiからの応答をチャットに追加する"""
        self.add_message(text=response_text, is_my_message=False)
        # UIを有効化
        self.send_button.setEnabled(True)
        self.message_line_edit.setEnabled(True)

    @Slot()
    def on_thread_finished(self):
        """スレッド終了時にオブジェクトを安全に削除し、状態を更新する"""
        if self.worker:
            self.worker.deleteLater()
        if self.gemini_thread:
            self.gemini_thread.deleteLater()

        self.worker = None
        self.gemini_thread = None
        self.is_processing = False  # 状態を「待機中」に戻す

    @Slot(str)
    def on_gemini_error(self, error_text: str):
        """APIエラーをチャットに追加する"""
        self.add_message(text=error_text, is_my_message=False)
        # UIを有効化
        self.send_button.setEnabled(True)
        self.message_line_edit.setEnabled(True)


# バックグラウンドでGemini APIと通信するためのワーカー
class GeminiWorker(QObject):
    response_ready = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, api_key: str, prompt: str):
        super().__init__()
        self.api_key = api_key
        self.prompt = prompt

    @Slot()
    def run(self):
        """APIリクエストを実行する"""
        try:
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=self.prompt
            )
            self.response_ready.emit(response.text)
        except Exception as e:
            self.error_occurred.emit(f"APIエラー: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
