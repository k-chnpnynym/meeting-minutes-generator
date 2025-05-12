# AI議事録作成ツール
MP3形式で録音された会議音声から、AIを活用して議事録を自動生成するPythonツールです。OpenAI Whisperで音声をテキストに変換し、Claude AIで構造化された議事録を作成します。

## 機能
* MP3音声ファイルのテキスト変換（時間制限なし）
* AIによる議事録の自動生成
* 会議の基本情報、議題、議論内容、決定事項などの抽出
* マークダウン形式での出力

## サンプルファイル
動作のイメージをつかんでいただけるよう、このリポジトリには以下のサンプルファイルが含まれています。
実際にツールをご利用になる際は、これらのファイルを削除してからご使用ください。
* `recordings/ja.mp3` - テスト用のサンプル会議音声
* `minutes/ja_transcript.txt` - 音声認識結果のサンプル
* `minutes/ja_minutes.md` - 生成された議事録のサンプル
* `minutes/processing_summary.json` - 処理結果のサンプル

## プロジェクトのセットアップ

### リポジトリのクローン
```bash
git clone https://github.com/k-chnpnynym/meeting-minutes-generator.git
cd meeting-minutes-generator
```

### 仮想環境の作成
```bash
# 仮想環境を作成
python -m venv venv

# 仮想環境の有効化
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 必要なライブラリのインストール
```bash
pip install -r requirements.txt
```

### 環境変数の設定
プロジェクトのルートディレクトリに `.env` ファイルを作成し、以下の内容を記載します：
```
ANTHROPIC_API_KEY=あなたのClaudeAPIキー
```

## API設定

### Anthropic Claude API の取得
1. [Anthropic](https://console.anthropic.com/) にアクセスしてアカウントを作成
2. API キーを生成
3. `.env` ファイルにAPIキーを追加

> 注意：このツールはOpenAI Whisperを使用するため、音声認識は完全無料でローカル処理されます。

## 使用方法
1. `recordings` フォルダにMP3ファイルを配置
2. スクリプトを実行:
```bash
python claude_minutes_generator.py
```
3. 生成された議事録は `minutes` フォルダに保存:
   * テキスト変換結果（`*_transcript.txt`）
   * 議事録（`*_minutes.md`）
   * 処理サマリー（`processing_summary.json`）

## 出力例
```markdown
# プロジェクト進捗会議
**日時**: 2025年4月12日 10:30  
**場所**: 会議室A  
**参加者**: 佐藤、鈴木、田中、山本、渡辺

## 議題
1. 前回の進捗確認
2. 新商品のデザイン案検討
3. スケジュールの見直し

## 議事内容
（議論の詳細）

## 決定事項
- デザインはC案をベースに進めることが決定
- 外部デザイナーを追加で1名アサインすることが決定

## 次回予定
**日時**: 4月19日 10:00  
**場所**: 会議室A
```

## 関連リソース

### Anthropic Claude API ドキュメント
* [メインドキュメント](https://docs.anthropic.com/)
* [API リファレンス](https://docs.anthropic.com/claude/reference/)
* [Python SDKドキュメント](https://github.com/anthropics/anthropic-sdk-python)
* [Messages API](https://docs.anthropic.com/claude/reference/messages_post)
* [クイックスタート](https://docs.anthropic.com/claude/docs/getting-started-with-claude)

## トラブルシューティング

### よくある警告メッセージ
音声認識中に「FP16 is not supported on CPU; using FP32 instead」という警告が表示される場合がありますが、これは正常な動作です。CPUでの処理のため精度を落として実行していることを示しています。

### 音声認識が遅い場合
* CPUで処理するため時間がかかることがあります
* より小さなWhisperモデル（「base」から「tiny」に変更）を使用することで高速化できます
* メモリ不足のエラーが出る場合は、他のアプリケーションを閉じてください

### API キーの問題
* Claude API キーが正しく設定されていることを確認
* API が有効化されていることを確認

### ライブラリのインストール問題
* Python のバージョンが 3.8 以上であることを確認
* 仮想環境がアクティブであることを確認
* PIPの更新:
  ```bash
  pip install --upgrade pip
  ```

## 注意事項
* Claude APIの利用には、Anthropicから取得したAPIキーが必要です
* API の利用には各プロバイダーの利用規約が適用されます
* Claude APIの使用にはAnthropicの利用料金が発生する場合があります
* OpenAI Whisperは初回起動時にモデルをダウンロードするため、時間がかかります（その後は高速）
* 仮想環境を使用することで、システム全体に影響を与えずにパッケージをインストールできます
* 生成された議事録は完璧ではない場合があります。重要な会議では、内容を確認・編集することをお勧めします
