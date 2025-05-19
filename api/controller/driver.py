from flask import Blueprint, request, current_app, jsonify
import api.external as external
from api.models.plan import User, Plan

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
        
        plans = external.db.session.query(Plan)\
        .filter(Plan.user_id == user.id)
        plans_json = {}
        # 取得した予定を辞書に格納
        for plan in plans:
            # 各予定の情報を辞書に追加
            plans_json[plan.id] = {
                'plan_text': plan.plan_text,
                'completed': plan.completed
            }
        
        # ユーザーオブジェクトを JSON に変換して返す
        return jsonify(plans_json), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch user data", "details": str(e)}), 500