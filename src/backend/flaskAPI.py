from flask import jsonify, request
from flask.views import MethodView
from models import ScheduleEvent, Categories, Document,Project,Content,TodoTask,TodoProject, ProjectTag, ConvertedDocument
from datetime import datetime, timezone
from markitdown import MarkItDown
from extension import db
md = MarkItDown()
def format_naive_as_utc(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc).isoformat()
    return dt.astimezone(timezone.utc).isoformat()

def serialize_event(event):
    return {
        'id': event.id,
        'title': event.title,
        'category': event.category,
        'start': format_naive_as_utc(event.start),
        'end': format_naive_as_utc(event.end),
        'allDay': event.all_day,
        'location': event.location,
        'description': event.description,
        'repeat': event.repeat,
        'recurrence': event.recurrence or None,
        'originalEventId': event.originalEventId,
        'exceptions': event.exceptions if event.exceptions else [],
        'lastState': event.lastState if event.lastState else None
    }
    
class WeekEventsAPI(MethodView):
    def get(self):
        try:
            # 解析为aware datetime并转换为UTC
            start_str = request.args['start']
            end_str = request.args['end']
            
            start_date = datetime.fromisoformat(start_str).astimezone(timezone.utc)
            if start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=timezone.utc)
            else:
                start_date = start_date.astimezone(timezone.utc)
            
            end_date = datetime.fromisoformat(end_str).astimezone(timezone.utc)
            if end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=timezone.utc)
            else:
                end_date = end_date.astimezone(timezone.utc)

            # 转换为naive UTC用于数据库查询
            start_naive_utc = start_date.replace(tzinfo=None)
            end_naive_utc = end_date.replace(tzinfo=None)

            events = ScheduleEvent.query.filter(
                (ScheduleEvent.repeat == True) |
                ((ScheduleEvent.start <= end_naive_utc) &
                (ScheduleEvent.end >= start_naive_utc))
            ).all()
            events = [serialize_event(event) for event in events]
            return jsonify(events), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

class ScheduleEventAPI(MethodView):
    def post(self):
        data = request.json
        if not all([data.get('title'), data.get('start'), data.get('end')]):
            return jsonify({'error': '缺少必要字段'}), 400
        
        start_aware = datetime.fromisoformat(data['start']).astimezone(timezone.utc)
        end_aware = datetime.fromisoformat(data['end']).astimezone(timezone.utc)
        
        # 统一存储为 naive UTC 时间
        new_event = ScheduleEvent(
            id=data.get('id'),
            start=start_aware.replace(tzinfo=None),  
            end=end_aware.replace(tzinfo=None),     
            title=data['title'],
            category=data.get('category'),
            all_day=data.get('allDay', False),
            location=data.get('location'),
            description=data.get('description'),
            repeat=data.get('repeat', False),
            recurrence=data.get('recurrence'),
            originalEventId=data.get('originalEventId'),
            exceptions=data.get('exceptions', []),
            lastState=data.get('lastState')
        )

        db.session.add(new_event)
        db.session.commit()
        return jsonify(serialize_event(new_event)), 201
    
    def put(self, event_id):
        event = ScheduleEvent.query.get(event_id)
        if not event:
            return jsonify({'error': '事件不存在'}), 404
        data = request.json
        
        if not all([data.get('title'), data.get('start'), data.get('end')]):
            return jsonify({'error': '缺少必要字段'}), 400
        
        # 转换为aware datetime并存储为naive UTC
        start_time = datetime.fromisoformat(data['start']).astimezone(timezone.utc).replace(tzinfo=None)
        end_time = datetime.fromisoformat(data['end']).astimezone(timezone.utc).replace(tzinfo=None)
        
        event.id = data.get('id')
        event.title = data['title']
        event.category = data.get('category')
        event.start = start_time
        event.end = end_time
        event.all_day = data.get('allDay', False)
        event.location = data.get('location')
        event.description = data.get('description')
        event.repeat = data.get('repeat', False)
        event.recurrence = data.get('recurrence')
        if 'originalEventId' in data:
            event.originalEventId = data['originalEventId']
        if 'exceptions' in data:
            event.exceptions=data.get('exceptions', [])
        if 'lastState' in data:
            event.lastState=data.get('lastState')
        db.session.commit()
        return jsonify(serialize_event(event))

    def delete(self, event_id):
        # 添加调试日志
        print(f'尝试删除事件 ID: {event_id}')
        event = ScheduleEvent.query.get(event_id)
        if not event:
            return jsonify({'error': '事件不存在'}), 404
            
        db.session.delete(event)
        db.session.commit()
        return '', 204

class CategoriesAPI(MethodView):
    def get(self):
        try:
            categories = Categories.query.all()
            return jsonify([{
                'id': c.id,
                'name': c.name,
                'color': c.color
            } for c in categories]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def post(self):
        data = request.json
        if not data.get('name') or not data.get('color'):
            return jsonify({'error': '缺少必要字段 name 或 color'}), 400
            
        try:
            new_category = Categories(
                name=data['name'],
                color=data['color']
            )
            db.session.add(new_category)
            db.session.commit()
            return jsonify({
                'id': new_category.id,
                'name': new_category.name,
                'color': new_category.color
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    def delete(self, id):
        category = Categories.query.get(id)
        if not category:
            return jsonify({'error': '分类不存在'}), 404
            
        try:
            db.session.delete(category)
            db.session.commit()
            return jsonify({}), 204
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    def put(self, id):
        category = Categories.query.get(id)
        if not category:
            return jsonify({'error': '分类不存在'}), 404
            
        data = request.json
        try:
            if 'name' in data: 
                category.name = data['name']
            if 'color' in data:
                category.color = data['color']
            db.session.commit()
            return jsonify({
                'id': category.id,
                'name': category.name,
                'color': category.color
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        
    @staticmethod
    def get_formatted_names(separator="\n"):
        """获取所有分类名称的格式化字符串"""
        try:
            categories = Categories.query.all()
            return separator.join([c.name for c in categories])
        except Exception as e:
            print(f"获取分类名称失败: {str(e)}")
            return ""
    @staticmethod
    def name_exists(name):
        """检查分类名称是否存在"""
        try:
            return bool(Categories.query.filter_by(name=name).first())
        except Exception as e:
            print(f"数据库查询失败: {str(e)}")
            return False

# class TasksAPI(MethodView):
#     def get(self, id=None):
#         try:
#             if id is None:
#                 tasks = Tasks.query.order_by(Tasks.order.asc()).all()
#                 return jsonify([self.serialize_task(task) for task in tasks]), 200
#             task = Tasks.query.get_or_404(id)
#             return jsonify(self.serialize_task(task)), 200
#         except Exception as e:
#             print(f"获取任务失败: {str(e)}")
#             return jsonify({'error': str(e)}), 500

#     def post(self):
#         data = request.json
#         if not data.get('name'):
#             return jsonify({'error': '缺少必要字段 name'}), 400
            
#         try:
#             new_task = Tasks(
#                 name=data['name'],
#                 start=datetime.fromisoformat(data['start']).astimezone(timezone.utc).replace(tzinfo=None) if data.get('start') else None,
#                 end=datetime.fromisoformat(data['end']).astimezone(timezone.utc).replace(tzinfo=None) if data.get('end') else None,
#                 description=data.get('description', ''),
#                 startColor=data.get('startColor'),
#                 endColor=data.get('endColor')
#             )
#             db.session.add(new_task)
#             db.session.commit()
#             return jsonify(self.serialize_task(new_task)), 201
#         except Exception as e:
#             db.session.rollback()
#             return jsonify({'error': str(e)}), 500

#     def put(self, id):
#         task = Tasks.query.get_or_404(id)
#         data = request.json
        
#         try:
#             if 'name' in data:
#                 task.name = data['name']
#             if 'start' in data:
#                 task.start = datetime.fromisoformat(data['start']).astimezone(timezone.utc).replace(tzinfo=None)
#             if 'end' in data:
#                 task.end = datetime.fromisoformat(data['end']).astimezone(timezone.utc).replace(tzinfo=None)
#             if 'description' in data:
#                 task.description = data['description']
#             if 'startColor' in data:
#                 task.startColor = data['startColor']
#             if 'endColor' in data:
#                 task.endColor = data['endColor']
                
#             db.session.commit()
#             return jsonify(self.serialize_task(task)), 200
#         except Exception as e:
#             db.session.rollback()
#             return jsonify({'error': str(e)}), 500

#     def delete(self, id):
#         task = Tasks.query.get_or_404(id)
#         try:
#             db.session.delete(task)
#             db.session.commit()
#             return '', 204
#         except Exception as e:
#             db.session.rollback()
#             return jsonify({'error': str(e)}), 500
        
#     @staticmethod
#     def serialize_task(task):
#         return {
#             'id': task.id,
#             'name': task.name,
#             'start': format_naive_as_utc(task.start) if task.start else None,
#             'end': format_naive_as_utc(task.end) if task.end else None,
#             'description': task.description,
#             'startColor': task.startColor,
#             'endColor': task.endColor
#         }

# class TasksReorderAPI(MethodView):
#     def put(self):
#         try:
#             task_ids = request.json.get('taskIds')
#             if not isinstance(task_ids, list):
#                 return jsonify({'error': 'Invalid task IDs format'}), 400

#             # 批量获取任务
#             tasks = Tasks.query.filter(Tasks.id.in_(task_ids)).all()
#             task_map = {t.id: t for t in tasks}
            
#             # 单次批量更新
#             update_list = []
#             for order, task_id in enumerate(task_ids, 1):
#                 if task := task_map.get(task_id):
#                     task.order = order
#                     update_list.append({'id': task.id, 'order': order})
            
#             if update_list:
#                 db.session.bulk_update_mappings(Tasks, update_list)
#                 db.session.commit()
            
#             return jsonify({'success': True}), 200
#         except Exception as e:
#             db.session.rollback()
#             return jsonify({'error': str(e)}), 500 ###

def serialize_document(doc): 
    return {
        'id': doc.id,
        'title': doc.title,
        'eventId': doc.event_id,
        'projectId': doc.project_id,  # 添加projectId字段
        'eventName': doc.event_name,
        'createdAt': format_naive_as_utc(doc.created_at),
        'updatedAt': format_naive_as_utc(doc.updated_at),
        'deletedAt': format_naive_as_utc(doc.deleted_at) if doc.deleted_at else None  # 添加删除时间戳
    }

# 添加内容API类
class ContentAPI(MethodView):
    def get(self, content_id):
        try:
            content_obj = db.session.get(Content, content_id)
            if not content_obj:
                return jsonify({'error': '内容不存在'}), 404
            return jsonify({'id': content_obj.id, 'content': content_obj.content}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def put(self, content_id):
        try:
            content_obj = db.session.get(Content, content_id)
            if not content_obj:
                return jsonify({'error': '内容不存在'}), 404
            
            data = request.json
            if 'content' in data:
                content_obj.content = data['content']
            
            db.session.commit()
            return jsonify({'id': content_obj.id, 'content': content_obj.content}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

def serialize_project(project):
    return {
        'id': project.id,
        'name': project.name,
        'projects': project.projects if project.projects else [],
        'documents': project.documents if project.documents else []
    }

def serialize_todo_task(task):
    # 构建 recurrence 对象
    recurrence = None
    if task.repeat and task.recurrence_type:
        recurrence = {
            'type': task.recurrence_type,
            'interval': task.recurrence_interval,
            'endCondition': task.recurrence_end_condition
        }
        if task.recurrence_days_of_week:
            recurrence['daysOfWeek'] = task.recurrence_days_of_week
        if task.recurrence_occurrences:
            recurrence['occurrences'] = task.recurrence_occurrences
        if task.recurrence_end_date:
            recurrence['endDate'] = task.recurrence_end_date
    
    return {
        'id': task.id,
        'originalTaskId': task.original_task_id,
        'projectId': task.project_id,
        'title': task.title,
        'date': format_naive_as_utc(task.date),
        'tag': task.tag,
        'priority': task.priority,
        'completed': task.completed,
        'fadeOut': task.fade_out,
        'fadeIn': task.fade_in,
        'completionTimer': task.completion_timer,
        'repeat': task.repeat,
        'recurrence': recurrence
    }

def serialize_todo_project(project):
    # 序列化项目标签
    tags = [{'name': pt.name, 'color': pt.color} for pt in project.project_tags]
    
    # 序列化项目任务
    todos = [serialize_todo_task(task) for task in project.todos]
    
    return {
        'id': project.id,
        'name': project.name,
        'tags': tags,
        'todos': todos
    }

# 添加项目API类
class ProjectAPI(MethodView):
    def get(self, project_id=None):
        try:
            if project_id is None:
                # 获取所有项目
                projects = Project.query.all()
                return jsonify([serialize_project(project) for project in projects]), 200
            else:
                # 获取特定项目
                project = Project.query.get(project_id)
                if not project:
                    return jsonify({'error': '项目不存在'}), 404
                return jsonify(serialize_project(project)), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def post(self):
        try:
            data = request.json
            if not data.get('name'):
                return jsonify({'error': '缺少必要字段 name'}), 400
            
            project_id = data.get('id') or str(int(datetime.now().timestamp() * 1000))
            
            # 检查项目是否已存在
            existing_project = db.session.get(Project, project_id)
            if existing_project:
                return jsonify({'error': '项目ID已存在'}), 400
            
            new_project = Project(
                id=project_id,
                name=data['name'],
                projects=data.get('projects', []),
                documents=data.get('documents', [])
            )
            
            db.session.add(new_project)
            db.session.commit()
            return jsonify(serialize_project(new_project)), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    def put(self, project_id):
        try:
            project = Project.query.get(project_id)
            if not project:
                return jsonify({'error': '项目不存在'}), 404
            
            data = request.json
            if 'name' in data:
                project.name = data['name']
            if 'projects' in data:
                project.projects = data['projects']
            if 'documents' in data:
                project.documents = data['documents']
            
            db.session.commit()
            return jsonify(serialize_project(project)), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    def delete(self, project_id):
        try:
            project = Project.query.get(project_id)
            if not project:
                return jsonify({'error': '项目不存在'}), 404
            
            # 阻止删除默认项目
            if project_id == 'rcwd':
                return jsonify({'error': '不能删除默认项目'}), 400
            
            db.session.delete(project)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

# 添加内容搜索API类
class ContentSearchAPI(MethodView):
    def get(self):
        try:
            query = request.args.get('query', '')
            if not query:
                return jsonify([]), 200
            # 在Content数据库中搜索匹配的字符串
            results = []
            contents = Content.query.all()
            for content_obj in contents:
                content = content_obj.content
                if query in content:
                    # 找到匹配位置
                    match_index = content.find(query)
                    if match_index != -1:
                        # 提取匹配位置前后的文本
                        start = max(0, match_index - 20)
                        end = min(len(content), match_index + len(query) + 20)
                        before_text = '...' if start > 0 else ''
                        after_text = '...' if end < len(content) else ''
                        
                        # 构造节选文本
                        before_match = content[start:match_index]
                        match_text = content[match_index:match_index + len(query)]
                        after_match = content[match_index + len(query):end]
                        
                        snippet = f"{before_text}{before_match}<strong>{match_text}</strong>{after_match}{after_text}"
                        
                        # 获取文档标题
                        document = Document.query.get(content_obj.id)
                        title = document.title if document else '未命名文档'
                        
                        results.append({
                            'id': content_obj.id,
                            'title': title,
                            'snippet': snippet
                        })
            return jsonify(results), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# 添加文档API类
class DocumentAPI(MethodView):
    def get(self, doc_id=None):
        try:
            if doc_id is None:
                # 获取所有文档（包括已删除的）
                docs = Document.query.all()
                return jsonify([serialize_document(doc) for doc in docs]), 200
            else:
                # 获取特定文档
                doc = Document.query.get(doc_id)
                if not doc:
                    return jsonify({'error': '文档不存在'}), 404
                return jsonify(serialize_document(doc)), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def post(self):
        try:
            data = request.json
            if not data.get('title'):
                return jsonify({'error': '缺少必要字段 title'}), 400
            
            doc_id = data.get('id') or str(int(datetime.now().timestamp() * 1000))
            
            # 检查文档是否已存在
            existing_doc = db.session.get(Document, doc_id)
            if existing_doc:
                return jsonify({'error': '文档ID已存在'}), 400
            
            # 创建文档内容
            content_obj = Content(
                id=doc_id,
                content=data.get('content', '')
            )
            
            new_doc = Document(
                id=doc_id,
                title=data['title'],
                event_id=data.get('eventId'),
                project_id=data.get('projectId'),  # 添加项目ID
                event_name=data.get('eventName')
            )
            
            db.session.add(new_doc)
            db.session.add(content_obj)
            db.session.commit()
            return jsonify(serialize_document(new_doc)), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    def put(self, doc_id):
        try:
            doc = Document.query.get(doc_id)
            if not doc:
                return jsonify({'error': '文档不存在'}), 404
            
            data = request.json
            if 'title' in data:
                doc.title = data['title']
            if 'projectId' in data:
                doc.project_id = data['projectId']
            if 'eventId' in data:
                doc.event_id = data['eventId']
            if 'eventName' in data:
                doc.event_name = data['eventName']
            # 处理删除状态
            if 'deletedAt' in data:
                if data['deletedAt'] is None:
                    doc.deleted_at = None  # 恢复文档
                else:
                    doc.deleted_at = datetime.fromisoformat(data['deletedAt']).astimezone(timezone.utc).replace(tzinfo=None)
            
            db.session.commit()
            return jsonify(serialize_document(doc)), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    def delete(self, doc_id):
        try:
            doc = Document.query.get(doc_id)
            if not doc:
                return jsonify({'error': '文档不存在'}), 404
            
            # 查找并删除关联的 Content 记录
            content = Content.query.get(doc_id)
            if content:
                db.session.delete(content)
            
            # 查找并删除关联的 ConvertedDocument 记录
            converted_docs = ConvertedDocument.query.filter_by(content_id=doc_id).all()
            for converted_doc in converted_docs:
                db.session.delete(converted_doc)
            
            # 删除文档本身
            db.session.delete(doc)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

# 添加待办任务API类
class TodoTaskAPI(MethodView):
    def get(self, task_id=None):
        try:
            if task_id is None:
                # 获取所有任务
                tasks = TodoTask.query.all()
                return jsonify([serialize_todo_task(task) for task in tasks]), 200
            else:
                # 获取特定任务
                task = TodoTask.query.get(task_id)
                if not task:
                    return jsonify({'error': '任务不存在'}), 404
                return jsonify(serialize_todo_task(task)), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def post(self):
        try:
            data = request.json
            if not data.get('title'):
                return jsonify({'error': '缺少必要字段 title'}), 400
            
            task_id = data.get('id') or str(int(datetime.now().timestamp() * 1000))
            
            # 检查任务是否已存在
            existing_task = db.session.get(TodoTask, task_id)
            if existing_task:
                return jsonify({'error': '任务ID已存在'}), 400
            
            # 处理 recurrence 数据
            recurrence_data = data.get('recurrence')
            recurrence_type = None
            recurrence_interval = None
            recurrence_days_of_week = None
            recurrence_end_condition = None
            recurrence_occurrences = None
            recurrence_end_date = None
            
            if recurrence_data:
                recurrence_type = recurrence_data.get('type')
                recurrence_interval = recurrence_data.get('interval')
                recurrence_days_of_week = recurrence_data.get('daysOfWeek')
                recurrence_end_condition = recurrence_data.get('endCondition')
                recurrence_occurrences = recurrence_data.get('occurrences')
                if recurrence_data.get('endDate'):
                    recurrence_end_date = datetime.fromisoformat(recurrence_data['endDate']).astimezone(timezone.utc).replace(tzinfo=None)
            
            new_task = TodoTask(
                id=task_id,
                original_task_id=data.get('originalTaskId'),
                project_id=data.get('projectId'),
                title=data['title'],
                date=datetime.fromisoformat(data['date']).astimezone(timezone.utc).replace(tzinfo=None) if data.get('date') else None,
                tag=data.get('tag', ''),
                priority=data.get('priority', 0),
                completed=data.get('completed', False),
                fade_out=data.get('fadeOut', False),
                fade_in=data.get('fadeIn', False),
                completion_timer=data.get('completionTimer'),
                repeat=data.get('repeat', False),
                recurrence_type=recurrence_type,
                recurrence_interval=recurrence_interval,
                recurrence_days_of_week=recurrence_days_of_week,
                recurrence_end_condition=recurrence_end_condition,
                recurrence_occurrences=recurrence_occurrences,
                recurrence_end_date=recurrence_end_date
            )
            
            db.session.add(new_task)
            db.session.commit()
            return jsonify(serialize_todo_task(new_task)), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    def put(self, task_id):
        try:
            task = TodoTask.query.get(task_id)
            if not task:
                return jsonify({'error': '任务不存在'}), 404
            
            data = request.json
            if 'title' in data:
                task.title = data['title']
            if 'originalTaskId' in data:
                task.original_task_id = data['originalTaskId']
            if 'projectId' in data:
                task.project_id = data['projectId']
            if 'date' in data:
                task.date = datetime.fromisoformat(data['date']).astimezone(timezone.utc).replace(tzinfo=None)
            if 'tag' in data:
                task.tag = data['tag']
            if 'priority' in data:
                task.priority = data['priority']
            if 'completed' in data:
                task.completed = data['completed']
            if 'fadeOut' in data:
                task.fade_out = data['fadeOut']
            if 'fadeIn' in data:
                task.fade_in = data['fadeIn']
            if 'completionTimer' in data:
                task.completion_timer = data['completionTimer']
            if 'repeat' in data:
                task.repeat = data['repeat']
            # 处理 recurrence 数据
            if 'recurrence' in data:
                recurrence_data = data['recurrence']
                if recurrence_data:
                    task.recurrence_type = recurrence_data.get('type')
                    task.recurrence_interval = recurrence_data.get('interval')
                    task.recurrence_days_of_week = recurrence_data.get('daysOfWeek')
                    task.recurrence_end_condition = recurrence_data.get('endCondition')
                    task.recurrence_occurrences = recurrence_data.get('occurrences')
                    if recurrence_data.get('endDate'):
                        task.recurrence_end_date = datetime.fromisoformat(recurrence_data['endDate']).astimezone(timezone.utc).replace(tzinfo=None)
                else:
                    # 如果 recurrence 为 null，清空所有相关字段
                    task.recurrence_type = None
                    task.recurrence_interval = None
                    task.recurrence_days_of_week = None
                    task.recurrence_end_condition = None
                    task.recurrence_occurrences = None
                    task.recurrence_end_date = None
            
            db.session.commit()
            return jsonify(serialize_todo_task(task)), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    def delete(self, task_id):
        try:
            task = TodoTask.query.get(task_id)
            if not task:
                return jsonify({'error': '任务不存在'}), 404
            
            db.session.delete(task)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

# 添加项目标签API类
class ProjectTagAPI(MethodView):
    def get(self, project_id):
        """获取项目的所有标签"""
        try:
            project = TodoProject.query.get(project_id)
            if not project:
                return jsonify({'error': '项目不存在'}), 404
            
            tags = [{'name': pt.name, 'color': pt.color} for pt in project.project_tags]
            return jsonify(tags), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def post(self, project_id):
        """为项目添加标签"""
        try:
            project = TodoProject.query.get(project_id)
            if not project:
                return jsonify({'error': '项目不存在'}), 404
            
            data = request.json
            if not data.get('name') or not data.get('color'):
                return jsonify({'error': '缺少必要字段 name 或 color'}), 400
            
            # 检查标签是否已存在
            existing_tag = ProjectTag.query.filter_by(project_id=project_id, name=data['name']).first()
            if existing_tag:
                return jsonify({'error': '标签已存在'}), 400
            
            new_tag = ProjectTag(
                project_id=project_id,
                name=data['name'],
                color=data['color']
            )
            
            db.session.add(new_tag)
            db.session.commit()
            return jsonify({'name': new_tag.name, 'color': new_tag.color}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    def put(self, project_id, tag_name):
        """更新项目标签"""
        try:
            project = TodoProject.query.get(project_id)
            if not project:
                return jsonify({'error': '项目不存在'}), 404
            
            tag = ProjectTag.query.filter_by(project_id=project_id, name=tag_name).first()
            if not tag:
                return jsonify({'error': '标签不存在'}), 404
            
            data = request.json
            if 'name' in data:
                tag.name = data['name']
            if 'color' in data:
                tag.color = data['color']
            
            db.session.commit()
            return jsonify({'name': tag.name, 'color': tag.color}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    def delete(self, project_id, tag_name):
        """删除项目标签"""
        try:
            project = TodoProject.query.get(project_id)
            if not project:
                return jsonify({'error': '项目不存在'}), 404
            
            tag = ProjectTag.query.filter_by(project_id=project_id, name=tag_name).first()
            if not tag:
                return jsonify({'error': '标签不存在'}), 404
            
            db.session.delete(tag)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

# 添加待办项目API类
class TodoProjectAPI(MethodView):
    def get(self, project_id=None):
        try:
            if project_id is None:
                # 获取所有项目
                projects = TodoProject.query.all()
                return jsonify([serialize_todo_project(project) for project in projects]), 200
            else:
                # 获取特定项目
                project = TodoProject.query.get(project_id)
                if not project:
                    return jsonify({'error': '项目不存在'}), 404
                return jsonify(serialize_todo_project(project)), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def post(self):
        try:
            data = request.json
            if not data.get('name'):
                return jsonify({'error': '缺少必要字段 name'}), 400
            
            project_id = data.get('id') or str(int(datetime.now().timestamp() * 1000))
            
            # 检查项目是否已存在
            existing_project = db.session.get(TodoProject, project_id)
            if existing_project:
                return jsonify({'error': '项目ID已存在'}), 400
            
            new_project = TodoProject(
                id=project_id,
                name=data['name']
            )
            
            db.session.add(new_project)
            db.session.commit()
            return jsonify(serialize_todo_project(new_project)), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    def put(self, project_id):
        try:
            project = TodoProject.query.get(project_id)
            if not project:
                return jsonify({'error': '项目不存在'}), 404
            
            data = request.json
            if 'name' in data:
                project.name = data['name']
            # 注意：tags 和 todos 不再直接存储在项目中，而是通过关联表处理
            # 这里不需要处理 tags 和 todos 字段
            
            db.session.commit()
            return jsonify(serialize_todo_project(project)), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    def delete(self, project_id):
        try:
            project = TodoProject.query.get(project_id)
            if not project:
                return jsonify({'error': '项目不存在'}), 404
            
            db.session.delete(project)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

class ConvertedDocumentAPI(MethodView):
    def post(self):
        """创建新的转换文档记录"""
        try:
            data = request.json
            if not data.get("id") or not data.get('content_id') or not data.get('file_path'):
                return jsonify({'error': '缺少必要字段 content_id 或 file_path'}), 400
            
            result = md.convert(data.get('file_path'))
            if not result:
                return jsonify({'error': '转换文档失败'}), 400
            
            # 创建新的 ConvertedDocument 记录
            new_converted_doc = ConvertedDocument(
                id=data.get('id') or str(int(datetime.now().timestamp() * 1000000)),  # 生成唯一ID
                content_id=data['content_id'],
                markdown_content=str(result),
            )
            
            db.session.add(new_converted_doc)
            db.session.commit()
            
            return jsonify({
                'id': new_converted_doc.id,
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    def delete(self, converted_doc_id):
        """删除转换文档记录"""
        try:
            converted_doc = ConvertedDocument.query.get(converted_doc_id)
            if not converted_doc:
                return jsonify({'error': '转换文档不存在'}), 404
            
            db.session.delete(converted_doc)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500


import langchain_community.embeddings
import langchain_community.vectorstores
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import DashScopeEmbeddings
import os
dashscope_api_key = "sk-17ac2b2ecf484caba72a55292d658feb"

embeddings = DashScopeEmbeddings(
    model="text-embedding-v1", dashscope_api_key=dashscope_api_key
)

def get_db_path():
    # 获取用户文档目录（Windows系统）
    docs_dir = os.path.join(os.path.expanduser('~'), 'Documents')
    app_dir = os.path.join(docs_dir, 'FlowCalendar')
    
    # 确保目录存在
    os.makedirs(app_dir, exist_ok=True)
    
    # 返回完整数据库路径
    return os.path.join(app_dir, 'faiss_index')


class updateRagAPI(MethodView):
    def post(self):
        try:
            data = request.json
            if not data.get('update'):
                return jsonify({'error': '缺少必要字段 update'}), 400
            
            contents = Content.query.all()
            converted_docs = ConvertedDocument.query.all()
            
            # 准备文本数据列表
            chunks = []
            metadata = []
            
            # 导入文本分割器
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            
            # 创建文本分割器，设置最大块大小为2000字符，留出一些余量
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
            )
            
            # 处理 Content 表中的数据
            for content in contents:
                if content.content and len(content.content) > 0:  # 确保内容不为空
                    # 如果文本长度超过2000字符，进行分割
                    if len(content.content) > 2000:
                        content_chunks = text_splitter.split_text(content.content)
                        for i, chunk in enumerate(content_chunks):
                            chunks.append(chunk)
                            metadata.append({
                                'id': content.id,
                                'type': 'content',
                                'chunk_index': i,
                                'total_chunks': len(content_chunks)
                            })
                    else:
                        chunks.append(content.content)
                        metadata.append({
                            'id': content.id,
                            'type': 'content',
                            'chunk_index': 0,
                            'total_chunks': 1
                        })
            
            # 处理 ConvertedDocument 表中的数据
            for doc in converted_docs:
                if doc.markdown_content and len(doc.markdown_content) > 0:  # 确保内容不为空
                    # 如果文本长度超过2000字符，进行分割
                    if len(doc.markdown_content) > 2000:
                        doc_chunks = text_splitter.split_text(doc.markdown_content)
                        for i, chunk in enumerate(doc_chunks):
                            chunks.append(chunk)
                            metadata.append({
                                'id': doc.id,
                                'content_id': doc.content_id,
                                'type': 'converted_document',
                                'chunk_index': i,
                                'total_chunks': len(doc_chunks)
                            })
                    else:
                        chunks.append(doc.markdown_content)
                        metadata.append({
                            'id': doc.id,
                            'content_id': doc.content_id,
                            'type': 'converted_document',
                            'chunk_index': 0,
                            'total_chunks': 1
                        })
            
            # 如果没有数据，返回空结果
            if not chunks:
                return jsonify({'message': '没有找到需要索引的文本数据'}), 200
            
            # 创建 FAISS 向量数据库
            vector_store = FAISS.from_texts(chunks, embeddings, metadatas=metadata)
            
            # 保存向量数据库到本地文件
            vector_store.save_local(get_db_path())
            
            return jsonify({
                'message': '向量数据库更新成功',
                'indexed_items': len(chunks),
                'original_documents': len(contents) + len(converted_docs),
                'chunks_created': len(chunks)
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# ============================================================
# LLM Config API - 管理 DeepSeek / DashScope 的 base_url 与 api_key
# ============================================================
import json as _json
from pathlib import Path as _Path

_LLM_CONFIG_PATH = _Path(os.path.expanduser("~")) / "Documents" / "FlowCalendar" / "llm_config.json"


def _mask_api_key(key: str) -> str:
    if not key:
        return ""
    if len(key) <= 8:
        return "*" * len(key)
    return key[:4] + "*" * (len(key) - 8) + key[-4:]


def _read_llm_config_file() -> dict:
    if _LLM_CONFIG_PATH.is_file():
        try:
            with open(_LLM_CONFIG_PATH, "r", encoding="utf-8") as f:
                return _json.load(f) or {}
        except (OSError, _json.JSONDecodeError):
            return {}
    return {}


class LlmConfigAPI(MethodView):
    def get(self):
        cfg = _read_llm_config_file()
        result = {}
        for provider in ("deepseek", "dashscope"):
            p = cfg.get(provider) or {}
            api_key = (p.get("api_key") or "").strip()
            result[provider] = {
                "base_url": (p.get("base_url") or "").strip(),
                "api_key_masked": _mask_api_key(api_key),
                "has_key": bool(api_key),
            }
        return jsonify(result), 200

    def post(self):
        data = request.json or {}
        existing = _read_llm_config_file()
        new_cfg = {}
        for provider in ("deepseek", "dashscope"):
            incoming = data.get(provider) or {}
            current = existing.get(provider) or {}
            base_url = (incoming.get("base_url") or "").strip()
            # api_key 为空字符串 / None -> 保留旧值
            new_key = incoming.get("api_key")
            if new_key is None or str(new_key).strip() == "":
                api_key = (current.get("api_key") or "").strip()
            else:
                api_key = str(new_key).strip()
            new_cfg[provider] = {"base_url": base_url, "api_key": api_key}
        try:
            _LLM_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(_LLM_CONFIG_PATH, "w", encoding="utf-8") as f:
                _json.dump(new_cfg, f, ensure_ascii=False, indent=2)
            return jsonify({"message": "ok"}), 200
        except OSError as exc:
            return jsonify({"error": str(exc)}), 500

# ============================================================
# LLM Config API
# ============================================================
import json as _json
import os as _os
from pathlib import Path as _Path

_LLM_CONFIG_PATH = _Path(_os.path.expanduser("~")) / "Documents" / "FlowCalendar" / "llm_config.json"


def _mask_api_key(key: str) -> str:
    if not key:
        return ""
    if len(key) <= 8:
        return "*" * len(key)
    return key[:4] + "*" * (len(key) - 8) + key[-4:]


def _read_llm_config_file() -> dict:
    if _LLM_CONFIG_PATH.is_file():
        try:
            with open(_LLM_CONFIG_PATH, "r", encoding="utf-8") as f:
                return _json.load(f) or {}
        except (OSError, _json.JSONDecodeError):
            return {}
    return {}


class LlmConfigAPI(MethodView):
    def get(self):
        cfg = _read_llm_config_file()
        result = {}
        for provider in ("deepseek", "dashscope"):
            p = cfg.get(provider) or {}
            api_key = (p.get("api_key") or "").strip()
            result[provider] = {
                "base_url": (p.get("base_url") or "").strip(),
                "api_key_masked": _mask_api_key(api_key),
                "has_key": bool(api_key),
            }
        return jsonify(result), 200

    def post(self):
        data = request.json or {}
        existing = _read_llm_config_file()
        new_cfg = {}
        for provider in ("deepseek", "dashscope"):
            incoming = data.get(provider) or {}
            current = existing.get(provider) or {}
            base_url = (incoming.get("base_url") or "").strip()
            new_key = incoming.get("api_key")
            if new_key is None or str(new_key).strip() == "":
                api_key = (current.get("api_key") or "").strip()
            else:
                api_key = str(new_key).strip()
            new_cfg[provider] = {"base_url": base_url, "api_key": api_key}
        try:
            _LLM_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(_LLM_CONFIG_PATH, "w", encoding="utf-8") as f:
                _json.dump(new_cfg, f, ensure_ascii=False, indent=2)
            return jsonify({"message": "ok"}), 200
        except OSError as exc:
            return jsonify({"error": str(exc)}), 500