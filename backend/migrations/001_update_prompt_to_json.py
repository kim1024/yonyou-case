"""迁移脚本：将 prompt_versions 表中的模板内容从 Markdown 格式更新为 JSON 格式。

背景：旧模板要求 LLM "使用 Markdown 格式输出"，但解析器 _parse_llm_json() 期望 JSON，
导致解析失败并回退到模板生成。本脚本将已有的 prompt_versions 记录更新为 JSON 输出格式。

用法：
    cd backend && python migrations/001_update_prompt_to_json.py
"""

import logging
import sys
from pathlib import Path

# 将 backend/ 加入 sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
_logger = logging.getLogger(__name__)

# ---------- 新的 JSON 格式模板内容 ----------

NEW_PROMPT_CONTENT = """请根据以下信息，生成一份产业案例教学课程设计方案。

专业方向：{major}
行业：{industry}
企业：{enterprise_name}
地区：{region}
课时：{hour}课时

<企业简介>
{company_intro}
</企业简介>
<用友建设内容>
{yonyou_content}
</用友建设内容>

课时分配参考：
- 模块一（行业背景与需求分析）：{hour_block1}课时
- 模块二（技术基础与工具介绍）：{hour_block2}课时
- 模块三（案例实战与项目实施）：{hour_block3}课时
- 模块四（总结与拓展）：{hour_block4}课时

请严格按照以下 JSON 结构输出（仅输出 JSON，不要输出任何其他内容）：

{{
  "title": "{enterprise_name}案例",
  "subtitle": "教学课程方案",
  "introduction": "（请根据实际信息丰富此段介绍，不少于100字。说明本教学案例基于{enterprise_name}公司的真实业务场景，结合{industry}专业技术，设计了{hour}课时教学方案。需要强调的动态内容（如企业名、行业名、专业名、课时数等）请用 HTML 标签 <b class=\\"highlight\\">内容</b> 包裹，使其加粗并使用特殊颜色显示。）",
  "modules": [
    {{
      "name": "模块一：行业背景与需求分析",
      "hours": {hour_block1},
      "items": [
        "{industry}行业现状与发展趋势",
        "{enterprise_name}业务模式与技术需求分析",
        "数字化转型痛点与机遇"
      ]
    }},
    {{
      "name": "模块二：技术基础与工具介绍",
      "hours": {hour_block2},
      "items": [
        "{major}核心技术原理与架构",
        "用友产品体系与解决方案概览",
        "开发环境搭建与工具链配置"
      ]
    }},
    {{
      "name": "模块三：案例实战与项目实施",
      "hours": {hour_block3},
      "items": [
        "{enterprise_name}真实业务场景解析",
        "基于用友平台的功能开发与集成",
        "项目方案设计、实施与优化"
      ]
    }},
    {{
      "name": "模块四：总结与拓展",
      "hours": {hour_block4},
      "items": [
        "项目成果展示与答辩",
        "{industry}领域最佳实践总结",
        "职业发展路径与学习资源推荐"
      ]
    }}
  ],
  "positions": [
    {{
      "title": "{major}工程师",
      "description": [
        "负责{industry}领域的数据/系统开发",
        "参与企业数字化转型项目",
        "熟练使用用友产品体系"
      ]
    }},
    {{
      "title": "{industry}解决方案架构师",
      "description": [
        "设计行业数字化解决方案",
        "对接客户需求与技术实现"
      ]
    }},
    {{
      "title": "项目实施顾问",
      "description": [
        "负责用友产品在企业的落地实施",
        "提供客户培训与技术支持"
      ]
    }},
    {{
      "title": "业务分析师",
      "description": [
        "分析{industry}业务流程与需求",
        "设计数字化优化方案"
      ]
    }},
    {{
      "title": "技术项目经理",
      "description": [
        "管理{industry}领域IT项目",
        "协调团队与客户资源"
      ]
    }},
    {{
      "title": "数字化运营专员",
      "description": [
        "负责{industry}领域数字化运营与持续优化",
        "监控系统运行指标，推动业务流程改进"
      ]
    }}
  ],
  "deliverables": [
    "PPT课件",
    "教学视频",
    "实验指导书",
    "数据集",
    "代码包",
    "实操环境配置文档"
  ],
  "notes": "以上内容由 AI 生成，请结合实际教学需求进行调整。"
}}

重要提示：
1. 仅输出上述 JSON 对象，不要输出其他任何内容。
2. JSON 中所有字段均为必填项。
3. introduction 字段不少于100字。
4. modules 数组必须包含4个模块，每个模块的 items 不少于3条。
5. positions 数组必须包含6个岗位，岗位和描述需结合 {industry} 领域与 {major} 专业。
6. introduction 中需要强调的动态内容（企业名、行业名、专业名、课时数等），请用 HTML 标签包裹：<b class="highlight">xxx</b>，使其加粗并使用特殊颜色显示。
7. 报价信息不需要生成，由系统另行计算。"""

NEW_VARIABLES = '["major", "industry", "enterprise_name", "region", "hour", "company_intro", "yonyou_content", "hour_block1", "hour_block2", "hour_block3", "hour_block4"]'


def migrate():
    """执行迁移：更新 prompt_versions 表中的模板内容。"""
    db_path = BACKEND_DIR / "data" / "app.db"

    if not db_path.exists():
        _logger.error("数据库文件不存在: %s", db_path)
        sys.exit(1)

    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        # 查找课程方案生成场景关联的模板
        rows = session.execute(
            text("""
                SELECT pv.id, pv.template_id, pv.version_number, pv.remark,
                       pt.scene, pt.name
                FROM prompt_versions pv
                JOIN prompt_templates pt ON pv.template_id = pt.id
                WHERE pt.scene = '课程方案生成'
                ORDER BY pv.id
            """)
        ).fetchall()

        if not rows:
            _logger.warning("未找到场景为'课程方案生成'的模板版本记录，跳过迁移。")
            return

        _logger.info("找到 %d 条待更新的版本记录：", len(rows))
        for row in rows:
            _logger.info("  prompt_version id=%d, template='%s', version=%d, remark=%s",
                         row[0], row[5], row[2], row[3])

        # 逐条更新
        updated_count = 0
        for row in rows:
            version_id = row[0]
            result = session.execute(
                text("UPDATE prompt_versions SET content = :content, variables = :variables, remark = :remark WHERE id = :id"),
                {
                    "content": NEW_PROMPT_CONTENT,
                    "variables": NEW_VARIABLES,
                    "remark": "迁移：将 Markdown 输出格式更新为 JSON 输出格式，新增 HTML highlight 标签要求",
                    "id": version_id,
                },
            )
            if result.rowcount > 0:
                _logger.info("  已更新 prompt_version id=%d", version_id)
                updated_count += 1

        session.commit()
        _logger.info("迁移完成，共更新 %d 条记录。", updated_count)


if __name__ == "__main__":
    _logger.info("=== 开始迁移：prompt_versions Markdown → JSON ===")
    migrate()
    _logger.info("=== 迁移脚本执行完毕 ===")
