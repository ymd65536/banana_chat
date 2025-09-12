from typing import Optional
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QLineEdit, QPushButton, QListWidgetItem, QFileDialog
)
from PySide6.QtCore import Slot

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

        # --- シグナルとスロットの接続 ---
        self.attach_button.clicked.connect(self.on_attach_button_clicked)
        self.send_button.clicked.connect(self.on_send_button_clicked)
        # Enterキーでも送信できるようにする
        self.message_line_edit.returnPressed.connect(
            self.on_send_button_clicked)

        # --- 初期メッセージの追加 ---
        self.add_message(text="こんにちは、GitHub Copilotです。", is_my_message=False)
        self.add_message(text="こんにちは！", is_my_message=True)

    def add_message(self, text: Optional[str] = None, image_path: Optional[str] = None, is_my_message: bool = False):
        """チャットリストに新しいメッセージ（テキストまたは画像）を追加する"""
        chat_message = ChatMessageWidget(
            text=text, image_path=image_path, is_my_message=is_my_message)
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
            self.add_message(image_path=file_path, is_my_message=True)

    @Slot()
    def on_send_button_clicked(self):
        """送信ボタンがクリックされたときに呼ばれる"""
        text = self.message_line_edit.text()
        if not text:
            return

        self.add_message(text=text, is_my_message=True)
        self.message_line_edit.clear()

        # ここで相手からの返信をシミュレートするなどのロジックを追加できます
        self.add_message(text="なるほど！", is_my_message=False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
