from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class RecurrenceRule(BaseModel):
    """重复规则定义"""

    type: Literal["daily", "weekly", "monthly", "yearly"] = Field(
        ..., description="重复类型，只能从 daily/weekly/monthly/yearly 中选择"
    )
    interval: int = Field(..., gt=0)
    daysOfWeek: Optional[List[int]] = Field(
        default=None,
        description="1代表周一,2代表周二,3代表周三，4代表周四，5代表周五，6代表周六，7代表周日，请严格遵循这个规则。",
    )
    endCondition: Literal["never", "untilDate", "occurrences"] = Field(
        ..., description="优先选用 occurrences"
    )
    occurrences: Optional[int] = Field(default=None, gt=0)
    endDate: Optional[datetime] = Field(default=None, description="结束日期")


class ScheduleEvent(BaseModel):
    """日历事件数据结构"""

    title: str = Field(
        ..., max_length=100, description="尽量简短到几个字，只需要包括主要事件内容"
    )
    category: str = Field(
        ...,
        max_length=50,
        description="先从提供的类别中选择最相近的，如果都不符合，请自行生成",
    )
    start: datetime = Field(
        ...,
        description="精确到分钟即可，五分钟为一个尺度，如果不是整的五分钟，向下取整，不需要进行时区转换",
    )
    end: datetime = Field(
        ...,
        description="精确到分钟即可，五分钟为一个尺度，如果不是整的五分钟，向下取整，不需要进行时区转换",
    )
    allDay: bool = False
    location: str = Field(..., max_length=200)
    description: str
    repeat: bool = Field(..., description="是否重复，只发生一次的事件设置为 false")
    recurrence: Optional[RecurrenceRule] = Field(
        default=None, description="重复规则,如果不是重复事件,此字段为 None"
    )
    exceptions: Optional[List[datetime]] = Field(
        default=None,
        description=(
            "重复例外，如果不是重复事件，不需要输出此字段。"
            "如果是重复事件且有'除了某一天'的例外情况，请在这里列出这些日期，"
            "格式为 2025-05-30T11:00:00.000Z"
        ),
    )


class ScheduleList(BaseModel):
    """用于存储从 CSV 文本中提取出的所有日程信息"""

    schedules: List[ScheduleEvent] = Field(
        description="一个包含多个日程信息的列表"
    )

