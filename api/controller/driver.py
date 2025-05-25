from flask import Blueprint, request
from api.repository.todo import TaskRepositoryImpl

app = Blueprint('todo_api', __name__)

# ユーザー情報取得API
@app.route('/get_user', methods=["GET"])
def get_user_route():
    """
    ユーザーと関連するタスクを取得するAPI
    """
    return TaskRepositoryImpl().get_user_tasks()

# タスク追加API    
@app.route('/settask', methods=["POST"])
def settask_route():
    """
    新しいタスクを追加するAPI
    """
    if not request.is_json:
        return "", 400
    
    return TaskRepositoryImpl().add_task(request.get_json())
    
# タスク削除API
@app.route('/deletetask', methods=["POST"])
def deletetask_route():
    """
    指定されたIDのタスクを削除するAPI
    """
    if not request.is_json:
        return "", 400
    
    return TaskRepositoryImpl().delete_task(request.get_json())