# -*- coding: utf-8 -*-
from flask import Flask, request
from extension import db, cors
from models import Project,TodoProject
import flaskAPI 
from flaskAPI import ScheduleEventAPI, WeekEventsAPI, CategoriesAPI, DocumentAPI, ContentAPI, ContentSearchAPI, ProjectAPI, TodoTaskAPI, TodoProjectAPI, ProjectTagAPI, updateRagAPI, ConvertedDocumentAPI, LlmConfigAPI
import os

 
def get_db_path():
    # 获取用户文档目录（Windows系统）
    docs_dir = os.path.join(os.path.expanduser('~'), 'Documents')
    app_dir = os.path.join(docs_dir, 'FlowCalendar')
    
    # 确保目录存在
    os.makedirs(app_dir, exist_ok=True)
    
    # 返回完整数据库路径
    return os.path.join(app_dir, 'flowcalendar.db')

# 必须在Flask应用初始化前设置
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{get_db_path()}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 配置CORS
db.init_app(app)
cors.init_app(app, origins=["http://localhost:5173"])

# 注册路由
app.add_url_rule('/api/events', view_func=ScheduleEventAPI.as_view('events_api'), methods=['POST'])
app.add_url_rule('/api/events/<string:event_id>', view_func=ScheduleEventAPI.as_view('event_api'), methods=['PUT', 'DELETE'])
app.add_url_rule('/api/events/week', view_func=WeekEventsAPI.as_view('week_events_api'), methods=['GET'])
app.add_url_rule('/api/categories', view_func=CategoriesAPI.as_view('categories_api'), methods=['GET', 'POST'])
app.add_url_rule('/api/categories/<int:id>', view_func=CategoriesAPI.as_view('category_api'), methods=['PUT', 'DELETE'])# app.add_url_rule('/api/tasks', view_func=TasksAPI.as_view('tasks_api'), methods=['GET', 'POST'])
app.add_url_rule('/api/documents', view_func=DocumentAPI.as_view('documents_api'), methods=['GET', 'POST'])
app.add_url_rule('/api/documents/<string:doc_id>', view_func=DocumentAPI.as_view('document_api'), methods=['GET', 'PUT', 'DELETE'])
app.add_url_rule('/api/contents/<string:content_id>', view_func=ContentAPI.as_view('content_api'), methods=['GET', 'PUT'])
app.add_url_rule('/api/contents/search', view_func=ContentSearchAPI.as_view('content_search_api'), methods=['GET'])
app.add_url_rule('/api/projects', view_func=ProjectAPI.as_view('projects_api'), methods=['GET', 'POST'])
app.add_url_rule('/api/projects/<string:project_id>', view_func=ProjectAPI.as_view('project_api'), methods=['GET', 'PUT', 'DELETE'])
app.add_url_rule('/api/todo/tasks', view_func=TodoTaskAPI.as_view('todo_tasks_api'), methods=['GET', 'POST'])
app.add_url_rule('/api/todo/tasks/<string:task_id>', view_func=TodoTaskAPI.as_view('todo_task_api'), methods=['GET', 'PUT', 'DELETE'])
app.add_url_rule('/api/todo/projects', view_func=TodoProjectAPI.as_view('todo_projects_api'), methods=['GET', 'POST'])
app.add_url_rule('/api/todo/projects/<string:project_id>', view_func=TodoProjectAPI.as_view('todo_project_api'), methods=['GET', 'PUT', 'DELETE'])
app.add_url_rule('/api/todo/projects/<string:project_id>/tags', view_func=ProjectTagAPI.as_view('project_tags_api'), methods=['GET', 'POST'])
app.add_url_rule('/api/todo/projects/<string:project_id>/tags/<string:tag_name>', view_func=ProjectTagAPI.as_view('project_tag_api'), methods=['PUT', 'DELETE'])
app.add_url_rule('/api/rag/update', view_func=updateRagAPI.as_view('update_rag_api'), methods=['POST'])
app.add_url_rule('/api/converted_documents', view_func=ConvertedDocumentAPI.as_view('converted_documents_api'), methods=['POST'])
app.add_url_rule('/api/converted_documents/<string:converted_doc_id>', view_func=ConvertedDocumentAPI.as_view('converted_document_api'), methods=['DELETE'])
app.add_url_rule('/api/llm_config', view_func=LlmConfigAPI.as_view('llm_config_api'), methods=['GET', 'POST'])

# 导入并注册realAgent
import Agent
Agent.create_app(app)
        
@app.cli.command()
def create_db():
    with app.app_context():
        db.create_all()
        print(f"数据库已创建在：{app.config['SQLALCHEMY_DATABASE_URI']}")

@app.cli.command()
def reset_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        add_default_project()
        print("数据库已重置")

def add_default_project():
    # 创建默认的rcwd项目
    default_project = db.session.get(Project, 'rcwd')
    if not default_project:
        default_project = Project(
            id='rcwd',
            name='日程文档',
            documents=[],
            projects=[]
        )
        db.session.add(default_project)
    
    # 检查并创建 daily_todos 项目
    daily_todos_project = db.session.get(TodoProject, 'daily_todos')
    if not daily_todos_project:
        daily_todos_project = TodoProject(
            id='daily_todos',
            name='每日待办',
            todos=[]
        )
        db.session.add(daily_todos_project)
    
    db.session.commit()

if __name__ == '__main__':
    import sys
    # 检查命令行参数以确定是否启用调试模式
    debug_mode = '--debug=False' not in sys.argv
    
    # 将数据库检测和运行服务器放在同一个上下文管理器内
    with app.app_context():
        # 使用统一的get_db_path()方法
        db_path = get_db_path()
        if not os.path.exists(db_path):
            db.create_all()
            # 创建默认项目
            add_default_project()
            print(f'Database created: {db_path}')

        else:
            # 数据库已存在，检查并创建默认项目
            add_default_project()
            print('Default projects checked/created')
            print(f'Using database: {db_path}')

    # 确保app.run在上下文管理器外部执行
    app.run(debug=debug_mode)