from flask import Blueprint, request, current_app, jsonify
import api.external as external
from api.models.task import User, Task

app = Blueprint('todo_api', __name__)

# ユーザー情報取得API
@app.route('/get_user', methods=["GET"])
def get_user():
    try:
        # データベースから最初のユーザーを取得
        user = external.db.session.query(User).first()
        # ユーザーが存在しない場合
        if user is None:
            # 新しい User オブジェクトを作成
            user = User()
            # アプリケーションコンテキスト内でデータベースに新しいユーザーを追加し、コミットする
            with current_app.app_context():
                external.db.session.add(user)
                external.db.session.commit()
        
        tasks = external.db.session.query(Task)\
        .filter(Task.user_id == user.id)
        tasks_json = {}
        # 取得した予定を辞書に格納
        for task in tasks:
            # 各予定の情報を辞書に追加
            tasks_json[task.id] = {
                'task_text': task.task_text,
                'completed': task.completed
            }
        
        # ユーザーオブジェクトを JSON に変換して返す
        return jsonify(tasks_json), 200
    except Exception as e:
        return "", 500

# タスク追加API    
@app.route('/settask', methods=["POST"])
def settask():
    if request.is_json:
        try:
            data = request.get_json() # dataは辞書
            for item in data: # リストの各要素（辞書）を処理
                task_text = item['text']
            # データベースから最初のユーザーを取得
            user = external.db.session.query(User).first()
            
            # 新しい Task オブジェクトを作成
            task = Task(
                user_id = user.id,
                task_text = task_text ,
            )
            # ユーザーの tasks リストに新しい予定を追加
            user.tasks.append(task)
            # データベースに変更をコミット
            external.db.session.commit()

            return "", 200
        except Exception as e:
            print("JSON データの処理中にエラーが発生しました:", e)
            return "", 400
    else:
        return "", 400