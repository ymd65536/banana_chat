import asyncio

from google import genai
from PySide6.QtCore import Slot, QObject, Signal


# バックグラウンドでGemini APIと通信するためのワーカー
class GeminiWorker(QObject):
    response_ready = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, api_key: str, prompt: str, image_data_base64: str = None):
        super().__init__()
        self.api_key = api_key
        self.prompt = prompt
        self.image_data_base64 = image_data_base64

    @Slot()
    def run(self):
        """APIリクエストを実行する"""
        loop = None  # finallyブロックで参照できるようにするため
        try:
            # このスレッド用の新しいイベントループを作成して設定
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            if self.prompt and self.image_data_base64:
                # 画像付きのプロンプト処理（必要に応じて実装）
                pass
            else:
                self.response_ready.emit(self._text_to_text())

        except Exception as e:
            self.error_occurred.emit(f"APIエラー: {e}")
        finally:
            # イベントループを閉じる
            if loop:
                loop.close()

    def _text_to_text(self) -> str:
        """同期的にGemini APIを呼び出すヘルパー関数"""
        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=self.prompt
        )
        return response.text