import sys
import os

# 添加Graph目录到Python路径
graph_dir = os.path.dirname(os.path.abspath(__file__))
if graph_dir not in sys.path:
    sys.path.insert(0, graph_dir)

# Import the calendar_agent_flow from graph.py
from .graph import calendar_agent_flow

# 可选：明确导出内容
__all__ = ['calendar_agent_flow']