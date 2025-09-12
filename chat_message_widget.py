from typing import Optional
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImageReader


class ChatMessageWidget(QWidget):
    """各チャットメッセージを表示するためのカスタムウィジェット"""

    def __init__(self, text: Optional[str] = None, image_path: Optional[str] = None, is_my_message: bool = False, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        self.message_label = QLabel()

        # スタイルシートの基本設定
        bg_color_me = "#7de64a"  # 明るい緑
        bg_color_other = "white"
        padding = "8px"
        border_radius = "10px"

        if text:
            self.message_label.setText(text)
            self.message_label.setWordWrap(True)
            style_sheet = f"""
                background-color: {bg_color_me if is_my_message else bg_color_other};
                color: black;
                border-radius: {border_radius};
                padding: {padding};
            """
            if not is_my_message:
                style_sheet += "border: 1px solid #ddd;"
            self.message_label.setStyleSheet(style_sheet)

        elif image_path:
            reader = QImageReader(image_path)
            reader.setAutoTransform(True)
            pixmap = QPixmap.fromImage(reader.read())

            # 画像が大きすぎる場合に備えて、幅を200pxに制限してリサイズ
            if pixmap.width() > 200:
                pixmap = pixmap.scaledToWidth(200, Qt.TransformationMode.SmoothTransformation)
            self.message_label.setPixmap(pixmap)
            # 画像の場合はパディングや背景を調整
            self.message_label.setStyleSheet(f"""
                border-radius: {border_radius};
                padding: 5px;
                border: 1px solid #ddd;
            """)

        # メッセージの寄せ方を設定
        if is_my_message:
            # 自分のメッセージ (右寄せ)
            layout.addSpacerItem(QSpacerItem(
                40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
            layout.addWidget(self.message_label)
            layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        else:
            # 相手のメッセージ (左寄せ)
            layout.addWidget(self.message_label)
            layout.addSpacerItem(QSpacerItem(
                40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
            layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.setLayout(layout)
