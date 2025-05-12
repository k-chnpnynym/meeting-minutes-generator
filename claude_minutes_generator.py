"""Claude APIを活用した議事録作成ツール
1. MP3ファイルをテキストに変換
2. Claude APIに渡して議事録を作成
3. 結果を保存
"""

import os
import json
import datetime
from pathlib import Path
from typing import Dict, Any

import anthropic
from dotenv import load_dotenv
# 以下の2行をコメントアウト
# from google.api_core.client_options import ClientOptions
# from google.cloud import speech_v1 as speech

# 以下の1行を追加
import whisper

# 環境変数の読み込み
load_dotenv()
# google_api_key = os.getenv("GOOGLE_CLOUD_PROJECT_API_KEY")  # この行をコメントアウト
claude_api_key = os.getenv("ANTHROPIC_API_KEY")


class EnhancedMinutesGenerator:
    def __init__(self, input_dir: Path, output_dir: Path):
        """議事録生成ツールの初期化

        Args:
            input_dir (Path): MP3ファイルが格納されているディレクトリ
            output_dir (Path): 生成された議事録を保存するディレクトリ
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)

        # Google Cloud Speech-to-Text APIクライアントの初期化をコメントアウト
        # client_options = ClientOptions(api_key=google_api_key)
        # self.speech_client = speech.SpeechClient(client_options=client_options)

        # Whisperモデルの初期化を追加
        print("Whisperモデルを読み込み中...")
        self.whisper_model = whisper.load_model("base")

        # Claude APIクライアントの初期化
        self.claude_client = anthropic.Anthropic(api_key=claude_api_key)

        # モデル設定
        self.claude_model = "claude-3-5-sonnet-20241022"  # または利用可能な最新モデル

    def transcribe_audio(self, audio_path: Path) -> str:
        """音声ファイルをテキストに変換する（Whisper使用）

        Args:
            audio_path (Path): 音声ファイルのパス

        Returns:
            str: 変換されたテキスト
        """
        print(f"音声ファイル「{audio_path.name}」をWhisperで認識中...")

        # 以下の元の処理を全てコメントアウト
        """
        # 音声ファイルの読み込み
        with open(audio_path, "rb") as audio_file:
            content = audio_file.read()

        # 音声認識リクエストの設定
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.MP3,
            language_code="ja-JP",
            enable_automatic_punctuation=True,
            # audio_channel_count=2,  # ステレオ対応が必要なら有効化
        )

        try:
            # 非同期音声認識の実行
            operation = self.speech_client.long_running_recognize(config=config, audio=audio)

            print("Google Cloud による非同期処理を待機中（最大600秒）...")
            response = operation.result(timeout=600)

            # レスポンスの処理
            transcription = ""
            for result in response.results:
                transcription += result.alternatives[0].transcript + "\n"

            return transcription

        except Exception as e:
            print(f"音声認識エラー（非同期）: {str(e)}")
            return f"音声認識エラー（非同期）: {str(e)}"
        """

        # Whisperの処理を追加
        try:
            result = self.whisper_model.transcribe(str(audio_path), language="ja")
            return result["text"]
        except Exception as e:
            print(f"Whisper音声認識エラー: {str(e)}")
            return f"音声認識エラー: {str(e)}"

    def generate_minutes_with_claude(self, transcript: str) -> str:
        """Claudeを使って議事録を生成する

        Args:
            transcript (str): 音声認識で得られたテキスト

        Returns:
            str: 生成された議事録
        """
        print("Claude APIを使用して議事録を生成中...")

        # Claudeへのプロンプト
        prompt = f"""
        以下は会議の書き起こしテキストです。このテキストを元に、プロフェッショナルな議事録を作成してください。

        # 書き起こしテキスト:
        {transcript}

        # 議事録の形式:
        1. 会議の基本情報（タイトル、日時、場所、参加者）
        2. 議題
        3. 議論の要点（発言者ごとに整理）
        4. 決定事項（箇条書き）
        5. 次回のアクション項目（担当者と期限）
        6. 次回会議の予定（日時、場所）

        話し言葉から書き言葉に適切に変換し、冗長な表現は省略して簡潔にまとめてください。
        情報が不足している場合は、その項目は「情報なし」と記載してください。
        マークダウン形式で議事録を作成してください。
        """

        try:
            # Claude APIを呼び出して議事録を生成
            response = self.claude_client.messages.create(
                model=self.claude_model,
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # レスポンスから議事録を取得
            minutes = response.content[0].text
            return minutes

        except Exception as e:
            print(f"Claude API呼び出しエラー: {str(e)}")
            return f"議事録生成エラー: {str(e)}"

    def process_recording(self, mp3_path: Path) -> Dict[str, Any]:
        """MP3録音を処理して議事録を生成する

        Args:
            mp3_path (Path): MP3ファイルのパス

        Returns:
            Dict[str, Any]: 処理結果の情報
        """
        result = {
            "input_file": str(mp3_path),
            "timestamp": datetime.datetime.now().isoformat(),
            "success": False,
            "transcript_path": None,
            "minutes_path": None,
            "error": None
        }

        try:
            # ステップ1: 音声をテキストに変換
            transcript = self.transcribe_audio(mp3_path)

            # 変換結果を保存
            transcript_path = self.output_dir / f"{mp3_path.stem}_transcript.txt"
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(transcript)
            result["transcript_path"] = str(transcript_path)

            # ステップ2: Claudeを使って議事録を生成
            minutes = self.generate_minutes_with_claude(transcript)

            # ステップ3: 議事録を保存
            minutes_path = self.output_dir / f"{mp3_path.stem}_minutes.md"
            with open(minutes_path, "w", encoding="utf-8") as f:
                f.write(minutes)
            result["minutes_path"] = str(minutes_path)

            # 処理成功
            result["success"] = True
            print(f"議事録が生成されました: {minutes_path}")

        except Exception as e:
            result["error"] = str(e)
            print(f"エラーが発生しました: {str(e)}")

        return result

    def process_all_recordings(self):
        """指定ディレクトリ内のすべての録音ファイルを処理する"""
        # MP3ファイルを検索
        mp3_files = list(self.input_dir.glob("*.mp3"))

        if not mp3_files:
            print(f"ディレクトリ '{self.input_dir}' にMP3ファイルが見つかりませんでした。")
            return

        print(f"{len(mp3_files)}個のMP3ファイルが見つかりました。処理を開始します...")

        # 処理結果のサマリー
        summary = []

        for mp3_path in mp3_files:
            print(f"\n{mp3_path.name} の処理を開始します...")
            result = self.process_recording(mp3_path)
            summary.append(result)

        # 処理結果のサマリーを保存
        summary_path = self.output_dir / "processing_summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=4)

        print(f"\nすべての処理が完了しました。処理サマリー: {summary_path}")


def main():
    # ファイルパスの設定
    file_path = Path(__file__).parent
    input_dir = file_path / "recordings"  # MP3録音が格納されているディレクトリ
    output_dir = file_path / "minutes"  # 生成された議事録を保存するディレクトリ

    # 議事録生成ツールの初期化と実行
    minutes_generator = EnhancedMinutesGenerator(input_dir, output_dir)
    minutes_generator.process_all_recordings()


if __name__ == "__main__":
    main()
