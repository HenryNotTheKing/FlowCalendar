# -*- coding: utf-8 -*-
from sqlalchemy import JSON
from extension import db
 
class ScheduleEvent(db.Model):
    __tablename__ = 'schedule_events'
    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(100))
    category = db.Column(db.String(50))
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    all_day = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(200))
    description = db.Column(db.Text)
    repeat = db.Column(db.Boolean, default=False)
    originalEventId = db.Column(db.String(50))
    exceptions = db.Column(JSON)
    recurrence = db.Column(JSON)
    lastState = db.Column(JSON)

class Categories(db.Model):
    __tablename__ ='categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    color = db.Column(db.String(50))

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(100))
    event_id = db.Column(db.String(50))  
    project_id = db.Column(db.String(50))  # 添加项目ID字段
    event_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    deleted_at = db.Column(db.DateTime, nullable=True)  # 添加删除时间戳字段


class Content(db.Model):
    __tablename__ = 'contents'
    id = db.Column(db.String(50), primary_key=True)  # 与Document的ID相同
    content = db.Column(db.String)
    converted_document = db.relationship('ConvertedDocument', backref=db.backref('content'))


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100))
    projects = db.Column(JSON)#储存其子项目的id列表
    documents = db.Column(JSON)#储存其下文档的id列表

class TodoTask(db.Model):
    __tablename__ = 'todo_tasks'
    id = db.Column(db.String(50), primary_key=True)
    original_task_id = db.Column(db.String(50))  # 关联原始任务ID（用于重复任务）
    project_id = db.Column(db.String(50), db.ForeignKey('todo_projects.id'))  # 关联项目ID
    title = db.Column(db.String(200))
    date = db.Column(db.DateTime)
    tag = db.Column(db.String(50))
    priority = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    fade_out = db.Column(db.Boolean, default=False)  # 添加缺失的字段
    fade_in = db.Column(db.Boolean, default=False)    # 添加缺失的字段
    completion_timer = db.Column(db.Integer, nullable=True)  # 添加缺失的字段
    repeat = db.Column(db.Boolean, default=False)
    recurrence_type = db.Column(db.String(20))  # 存储重复规则类型
    recurrence_interval = db.Column(db.Integer)
    recurrence_days_of_week = db.Column(JSON)  # 存储每周重复的天数
    recurrence_end_condition = db.Column(db.String(20))  # 结束条件
    recurrence_occurrences = db.Column(db.Integer)  # 重复次数
    recurrence_end_date = db.Column(db.DateTime)  # 结束日期


class ProjectTag(db.Model):
    __tablename__ = 'project_tags'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.String(50), db.ForeignKey('todo_projects.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    # 建立与TodoProject的关联关系
    project = db.relationship('TodoProject', backref=db.backref('project_tags', lazy=True, cascade='all, delete-orphan'))


class TodoProject(db.Model):
    __tablename__ = 'todo_projects'
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100))
    # 建立与TodoTask的关联关系
    todos = db.relationship('TodoTask', backref='project', lazy=True, cascade='all, delete-orphan')

class ConvertedDocument(db.Model):
    __tablename__ = 'converted_documents'
    id = db.Column(db.String(50), primary_key=True)
    content_id = db.Column(db.String(50), db.ForeignKey('contents.id'), nullable=False)
    markdown_content = db.Column(db.Text)
