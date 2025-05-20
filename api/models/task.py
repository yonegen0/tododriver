from api.external import db
from datetime import datetime

# User モデルの定義
class User(db.Model):
    # テーブル名を設定
    __tablename__ = 'users'
    # テーブルに関する追加情報（コメント）
    __table_args__ = {
        'comment': 'ユーザー情報'
    }
    # ユーザーID
    id = db.Column(db.Integer, primary_key=True)
    # 予定の一覧
    tasks = db.relationship('Task', backref='todolist', cascade="all, delete-orphan", lazy=True, uselist=True, foreign_keys='Task.user_id')

# Task モデルの定義
class Task(db.Model):
    # テーブル名を設定
    __tablename__ = 'tasks'
    # テーブルに関する追加情報（コメント）
    __table_args__ = {
        'comment': '予定'
    }
    # 予定ID
    id = db.Column(db.Integer, primary_key=True)
    # ユーザーID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # 予定のテキスト
    task_text = db.Column(db.String(255), nullable=False)
    # 完了か否かの判定
    completed = db.Column(db.Boolean, default=False, nullable=False)