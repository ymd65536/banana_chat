from typing import Optional
import base64
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt, QBuffer, QByteArray
from PySide6.QtGui import QPixmap, QImageReader


class ChatMessageWidget(QWidget):
    """各チャットメッセージを表示するためのカスタムウィジェット"""

    def __init__(self, text: Optional[str] = None, image_data_base64: Optional[str] = None, is_my_message: bool = False, parent=None):
        super().__init__(parent)

        # メインレイアウト（左右の寄せを担当）
        main_layout = QHBoxLayout(self)

        # コンテンツ用ウィジェットとレイアウト（画像とテキストを縦に並べる）
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(5)

        # スタイルシートの基本設定
        bg_color_me = "#7de64a"  # 明るい緑
        bg_color_other = "white"
        padding = "8px"
        border_radius = "10px"

        style_sheet = f"""
            background-color: {bg_color_me if is_my_message else bg_color_other};
            color: black;
            border-radius: {border_radius};
            padding: {padding};
        """
        if not is_my_message:
            style_sheet += "border: 1px solid #ddd;"
        content_widget.setStyleSheet(style_sheet)

        # 画像がある場合の処理
        if image_data_base64:
            image_label = QLabel()
            # Base64データをデコードしてQPixmapに読み込む
            image_data = base64.b64decode(image_data_base64)
            byte_array = QByteArray(image_data)
            buffer = QBuffer(byte_array)
            buffer.open(QBuffer.OpenModeFlag.ReadOnly)

            reader = QImageReader(buffer)
            reader.setAutoTransform(True)
            pixmap = QPixmap.fromImage(reader.read())

            # 画像が大きすぎる場合に備えて、幅を200pxに制限してリサイズ
            if pixmap.width() > 200:
                pixmap = pixmap.scaledToWidth(
                    200, Qt.TransformationMode.SmoothTransformation)
            image_label.setPixmap(pixmap)
            # 画像の場合は背景を透明にし、パディングをなくす
            image_label.setStyleSheet(
                "background-color: transparent; padding: 0px;")
            content_layout.addWidget(image_label)

        # テキストがある場合の処理
        if text:
            text_label = QLabel(text)
            text_label.setWordWrap(True)
            # テキストの場合は背景を透明にし、パディングをなくす
            text_label.setStyleSheet(
                "background-color: transparent; padding: 4px;font-size: 16px;")
            content_layout.addWidget(text_label)

        # メッセージの寄せ方を設定
        if is_my_message:
            # 自分のメッセージ (右寄せ)
            main_layout.addSpacerItem(QSpacerItem(
                40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
            main_layout.addWidget(content_widget)
            main_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        else:
            # 相手のメッセージ (左寄せ)
            main_layout.addWidget(content_widget)
            main_layout.addSpacerItem(QSpacerItem(
                40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
            main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.setLayout(main_layout)
