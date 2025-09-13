
from typing import Optional
import sys
import os

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QLineEdit, QPushButton, QListWidgetItem, QFileDialog,
    QDialog, QLabel, QDialogButtonBox
)
from PySide6.QtCore import Slot, QTimer, QThread, QSettings

# 上で作成したカスタムウィジェットをインポート
from ui.chat_message_widget import ChatMessageWidget
from google.gemini_worker import GeminiWorker
from media.image_base64 import pil_image_base64

class SettingsDialog(QDialog):
    def _q_settings(self) -> QSettings:
        """QSettingsのインスタンスを返す"""
        return QSettings("GeminiApp", "Chat")

    def get_gemini_api_key(self) -> Optional[str]:
        """設定からGEMINI_API_KEYを取得する"""
        settings = self._q_settings()
        return settings.value("GEMINI_API_KEY", None)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GEMINI_API_KEYの設定")
        self.settings = self._q_settings()

        layout = QVBoxLayout(self)

        # APIキー入力
        api_key_layout = QHBoxLayout()
        self.api_key_label = QLabel("GEMINI_API_KEY:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setText(self.settings.value("GEMINI_API_KEY", ""))
        api_key_layout.addWidget(self.api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        layout.addLayout(api_key_layout)

        # OK/キャンセルボタン
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def accept(self):
        """OKボタンが押されたときに設定を保存する"""
        self.settings.setValue("GEMINI_API_KEY", self.api_key_input.text())
        super().accept()


class MainWindow(QMainWindow):
    def _q_settings(self) -> QSettings:
        """QSettingsのインスタンスを返す"""
        return QSettings("GeminiApp", "Chat")

    def get_gemini_api_key(self) -> Optional[str]:
        """設定からGEMINI_API_KEYを取得する"""
        settings = self._q_settings()
        return settings.value("GEMINI_API_KEY", None)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Banana Chat")

        # 画面サイズに合わせてウィンドウをリサイズ
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            self.resize(screen_geometry.width(), screen_geometry.height())
        else:
            # フォールバックサイズ
            self.resize(800, 600)

        # --- メニューバーの作成 ---
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("設定")
        settings_action = file_menu.addAction("GEMINI_API_KEYの設定")
        settings_action.triggered.connect(self.open_settings_dialog)

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
        self.add_message(text="こんにちは、bananaです。", is_my_message=False)
        self.add_message(text="こんにちは！", is_my_message=True)

        # --- 設定ダイアログ ---
        self.settings_dialog = SettingsDialog(self)

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
        image_data_base64 = pil_image_base64(self.attached_image_path)

        # テキストも画像もなければ何もしない
        if not text and not image_data_base64:
            return

        self.add_message(
            text=text, image_data_base64=image_data_base64, is_my_message=True)

        # 送信後にリセット
        self.message_line_edit.clear()
        self.attached_image_path = None
        self.message_line_edit.setPlaceholderText("メッセージを入力...")

        GEMINI_API_KEY = self.get_gemini_api_key()
        if not GEMINI_API_KEY:
            self.add_message(text="GEMINI_API_KEYが設定されていません。メニューから設定してください。",
                             is_my_message=False)
            return

        self.worker = GeminiWorker(api_key=GEMINI_API_KEY, prompt=text)

        # ここで相手からの返信をシミュレートするなどのロジックを追加できます
        if text and image_data_base64:
            self.add_message(text="banana!!", is_my_message=False)
        elif text:
            self._get_gemini_response()

    def _status_change(self, processing: bool):
        """状態を変更し、UIの有効/無効を切り替える"""
        self.is_processing = processing
        self.send_button.setEnabled(not processing)
        self.message_line_edit.setEnabled(not processing)
    
    def _start_thread(self):
        """Gemini API呼び出し用のスレッドを開始する"""
        # スレッドとワーカーをインスタンス変数として作成
        self.gemini_thread = QThread()
        self.worker.moveToThread(self.gemini_thread)

        # 完了後にオブジェクトが自動で削除され、参照がクリーンアップされるように接続
        self.gemini_thread.started.connect(self.worker.run)
        self.worker.response_ready.connect(self.on_gemini_response)
        self.worker.error_occurred.connect(self.on_gemini_error)
        self.worker.response_ready.connect(self.gemini_thread.quit)
        self.worker.error_occurred.connect(self.gemini_thread.quit)
        self.gemini_thread.finished.connect(self.on_thread_finished)

        self.gemini_thread.start()

    def _get_gemini_response(self):
        """Geminiからの応答を非同期で取得する"""
        # 処理中であれば、新しいリクエストは受け付けない
        if self.is_processing:
            return

        # 状態を「処理中」に更新し、UIを無効化
        self._status_change(processing=True)
        self.add_message(text="...", is_my_message=False)
        self._start_thread()

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

    def closeEvent(self, event):
        """ウィンドウが閉じられるときに呼ばれる"""
        # 設定ダイアログも閉じる
        self.settings_dialog.close()
        event.accept()

    @Slot()
    def open_settings_dialog(self):
        """設定ダイアログを開く"""
        dialog = SettingsDialog(self)
        dialog.exec()

    def open_settings_dialog(self):
        """設定ダイアログを表示する"""
        self.settings_dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
