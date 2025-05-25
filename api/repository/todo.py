from flask import Blueprint, request, current_app, jsonify
from abc import ABC, abstractmethod
import api.external as external
from api.models.task import User, Task # Task モデルを使用

# Blueprintを定義
app = Blueprint('todo_api', __name__)

# --- 抽象リポジトリクラス ---
class TaskRepository(ABC):
    """
    Todoタスクのデータアクセス操作を定義する抽象基底クラス
    """

    @abstractmethod
    def get_user_tasks(self):
        """
        データベースからユーザーと関連する全てのタスクを取得

        Returns:
            tuple: JSON形式のタスクデータとHTTPステータスコード
        """
        pass

    @abstractmethod
    def add_task(self, data):
        """
        新しいタスクをデータベースに追加

        Args:
            data (list): リクエストボディから取得したJSONデータ
                         [{ "text": "タスク内容" }] の形式を想定

        Returns:
            tuple: 成功メッセージとHTTPステータスコード
        """
        pass

    @abstractmethod
    def delete_task(self, data):
        """
        指定されたIDのタスクをデータベースから削除

        Args:
            data (list): リクエストボディから取得したJSONデータ
                         [{ "id": タスクID }] の形式を想定

        Returns:
            tuple: 成功メッセージとHTTPステータスコード
        """
        pass

# --- 具体的なリポジトリ実装クラス ---
class TaskRepositoryImpl(TaskRepository):
    """
    TaskRepository 抽象クラスの具体的な実装
    """

    def _get_first_user(self):
        """
        データベースから最初のユーザーを取得
        ユーザーが存在しない場合は新しく作成
        """
        # データベースから最初のユーザーを取得
        user = external.db.session.query(User).first()
        # ユーザーが存在しない場合は新しく作成
        if user is None:
            user = User()
            with current_app.app_context():
                external.db.session.add(user)
                external.db.session.commit()
        return user

    # override
    def get_user_tasks(self):
        """
        ユーザーに関連付けられた全てのタスクを取得し、JSON形式で返
        """
        try:
            user = self._get_first_user()
            
            # ユーザーに紐づく全てのタスクを取得
            tasks = external.db.session.query(Task).filter(Task.user_id == user.id).all()
            
            tasks_json = {}
            # 取得したタスクを辞書に格納 (IDをキーとする)
            for task in tasks:
                tasks_json[task.id] = {
                    'task_text': task.task_text,
                    'completed': task.completed
                }
            
            # タスクの辞書をJSON形式で返す
            return jsonify(tasks_json), 200
        except Exception as e:
            return "", 500

    # override
    def add_task(self, data):
        """
        新しいタスクをデータベースに追加
        """
        # データがリストであり、かつ少なくとも1つの要素があることを確認
        if not isinstance(data, list) or not data:
            return "", 400
        
        # 最初のタスクアイテムを取得 (フロントエンドが単一のタスクをリストとして送信するため)
        item = data[0] 
        
        # 'text' キーが存在し、文字列であることを確認
        task_text = item.get('text')
        if not isinstance(task_text, str) or not task_text.strip():
            return "", 400

        try:
            user = self._get_first_user()
            if user is None:
                return "", 404
            
            # 新しい Task オブジェクトを作成
            task = Task(
                user_id=user.id,
                task_text=task_text.strip(), # 前後の空白を削除
                completed=False # 新しいタスクは未完了として追加
            )
            
            # データベースに新しいタスクを追加
            external.db.session.add(task)
            # データベースに変更をコミット
            external.db.session.commit()

            return "", 201
        except Exception as e:
            return "", 500

    # override
    def delete_task(self, data):
        """
        指定されたIDのタスクをデータベースから削除
        """
        # データがリストであり、かつ少なくとも1つの要素があることを確認
        if not isinstance(data, list) or not data:
            return "", 400

        # 最初のIDアイテムを取得 (フロントエンドが単一のIDをリストとして送信するため)
        item = data[0]
        
        # 'id' キーが存在し、整数に変換可能であることを確認
        id_value = item.get('id')
        if id_value is None:
            return "", 400
        
        try:
            task_id = int(id_value)
        except ValueError:
            return "", 400
            
        try:
            # 削除対象のタスクを取得
            task_to_delete = external.db.session.query(Task).filter(Task.id == task_id).first()

            if task_to_delete:
                # タスクを削除
                external.db.session.delete(task_to_delete)
                external.db.session.commit()
                return "", 204 # 削除成功、コンテンツなし
            else:
                return "", 404
        except Exception as e:
            return "", 500