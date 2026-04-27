"""Pure helper functions for plan generation — no DB dependency."""

import html
import json
import logging
import re

_logger = logging.getLogger(__name__)

DELIVERABLES = ["PPT", "视频", "指导书", "数据集", "代码包", "实操环境"]


def _parse_llm_json(content: str) -> dict | None:
    """解析 LLM 返回的 JSON，失败则返回 None。"""
    try:
        # 如果包含 markdown 代码块标记，先提取 JSON 部分
        match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', content, re.DOTALL)
        if match:
            content = match.group(1).strip()

        parsed = json.loads(content)

        # 校验必填字段
        required_fields = ("title", "introduction", "modules", "positions", "deliverables")
        for field in required_fields:
            if field not in parsed:
                _logger.warning("LLM JSON 缺少必填字段: %s，回退模板", field)
                return None

        return parsed
    except (json.JSONDecodeError, TypeError) as e:
        _logger.warning("LLM 返回内容 JSON 解析失败: %s，回退模板", e)
        return None


def _normalize_title_subtitle(plan_json: dict, enterprise_name: str) -> None:
    """强制规范 title/subtitle 格式，不依赖 LLM 输出。

    目标格式：title = "{enterprise_name}案例"，subtitle = "教学课程方案"
    """
    plan_json["title"] = f"{enterprise_name}案例"
    plan_json["subtitle"] = "教学课程方案"


def _safe(text: str, max_len: int = 500) -> str:
    """对数据库字段做长度限制，防止提示注入和 JSON 结构破坏。"""
    return (
        str(text)[:max_len]
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("{", "{{")
        .replace("}", "}}")
    )


def _build_fallback_json(
    enterprise_name: str,
    major: str,
    industry: str,
    hour: int,
    hour_block1: int,
    hour_block2: int,
    hour_block3: int,
    hour_block4: int,
    rate: int,
    total_cost: int,
) -> dict:
    """构建兜底 JSON 模板。"""
    return {
        "title": f"{enterprise_name}案例",
        "subtitle": "教学课程方案",
        "introduction": (
            f'本教学案例基于<b class="highlight">{html.escape(enterprise_name)}</b>公司的真实业务场景，'
            f'结合<b class="highlight">{html.escape(industry)}</b>专业技术，'
            f'设计了一套完整的<b class="highlight">{hour}</b>课时教学方案。'
            f'通过本案例的学习，学员将深入理解'
            f'<b class="highlight">{html.escape(industry)}</b>行业与'
            f'<b class="highlight">{html.escape(major)}</b>技术的融合应用，'
            f'掌握实际项目中的核心技能。'
        ),
        "modules": [
            {
                "name": "模块一：行业背景与需求分析",
                "hours": hour_block1,
                "items": [
                    f"{industry}行业现状与发展趋势",
                    f"{enterprise_name}业务模式与技术需求分析",
                    "数字化转型痛点与机遇",
                ],
            },
            {
                "name": "模块二：技术基础与工具介绍",
                "hours": hour_block2,
                "items": [
                    f"{major}核心技术原理与架构",
                    "用友产品体系与解决方案概览",
                    "开发环境搭建与工具链配置",
                ],
            },
            {
                "name": "模块三：案例实战与项目实施",
                "hours": hour_block3,
                "items": [
                    f"{enterprise_name}真实业务场景解析",
                    "基于用友平台的功能开发与集成",
                    "项目方案设计、实施与优化",
                ],
            },
            {
                "name": "模块四：总结与拓展",
                "hours": hour_block4,
                "items": [
                    "项目成果展示与答辩",
                    f"{industry}领域最佳实践总结",
                    "职业发展路径与学习资源推荐",
                ],
            },
        ],
        "positions": [
            {
                "title": f"{major}工程师",
                "description": [
                    f"负责{industry}领域的数据/系统开发",
                    "参与企业数字化转型项目",
                    "熟练使用用友产品体系",
                ],
            },
            {
                "title": f"{industry}解决方案架构师",
                "description": [
                    "设计行业数字化解决方案",
                    "对接客户需求与技术实现",
                ],
            },
            {
                "title": "项目实施顾问",
                "description": [
                    "负责用友产品在企业的落地实施",
                    "提供客户培训与技术支持",
                ],
            },
            {
                "title": "业务分析师",
                "description": [
                    f"分析{industry}业务流程与需求",
                    "设计数字化优化方案",
                ],
            },
            {
                "title": "技术项目经理",
                "description": [
                    f"管理{industry}领域IT项目",
                    "协调团队与客户资源",
                ],
            },
            {
                "title": "数字化运营专员",
                "description": [
                    f"负责{industry}领域数字化运营与持续优化",
                    "监控系统运行指标，推动业务流程改进",
                ],
            },
        ],
        "deliverables": DELIVERABLES,
        "notes": "以上内容由 AI 生成，请结合实际教学需求进行调整。",
        "pricing": {
            "hour": hour,
            "unit_price": rate,
            "total_cost": total_cost,
        },
    }
