# 提示词模板管理指南

本指南面向系统管理员，说明如何查看、编辑和管理课程方案生成所使用的 AI 提示词模板。

---

## 1. 工作原理

用户在前台填写「专业、行业、企业、地区、课时」后，系统将这些信息填入提示词模板，发送给大语言模型（LLM），由 LLM 生成完整的教学课程方案。

```
用户填写参数 → 填入提示词模板 → 调用 LLM → 解析 JSON → 渲染方案
```

系统按以下优先级选择提示词：

| 优先级 | 来源 | 说明 |
|--------|------|------|
| 1 | 数据库中的活跃模板 | 管理员通过 API 维护的模板（**当前生效**） |
| 2 | 代码内置兜底模板 | 当数据库无活跃模板时自动使用 |

---

## 2. 可用变量

提示词模板中可使用以下变量，系统会在调用 LLM 前自动替换为实际值：

| 变量 | 说明 | 示例 |
|------|------|------|
| `{major}` | 专业方向 | 软件工程 |
| `{industry}` | 行业 | 制造业 |
| `{enterprise_name}` | 企业名称 | 用友网络 |
| `{region}` | 地区（省份） | 北京 |
| `{hour}` | 总课时数 | 24 |
| `{hour_block1}` | 模块一课时（行业背景） | 3 |
| `{hour_block2}` | 模块二课时（技术基础） | 3 |
| `{hour_block3}` | 模块三课时（案例实战） | 12 |
| `{hour_block4}` | 模块四课时（总结拓展） | 6 |
| `{company_intro}` | 企业简介（截断 1000 字） | … |
| `{yonyou_content}` | 用友建设内容（截断 1000 字） | … |
| `{total_cost}` | 总报价（元） | 48000 |

> **注意**：变量使用 Python `str.format()` 语法，模板中的花括号 `{` `}` 需写成 `{{` `}}` 转义，否则会被当作变量解析。

---

## 3. 必须输出的 JSON 结构

LLM 必须严格按照以下 JSON 结构输出，系统依赖这些字段渲染方案页面：

```json
{
  "title": "{enterprise_name}案例",
  "subtitle": "教学课程方案",
  "introduction": "（不少于 100 字的方案介绍）",
  "modules": [
    {
      "name": "模块一：行业背景与需求分析",
      "hours": 3,
      "items": ["知识点1", "知识点2", "知识点3"]
    }
  ],
  "positions": [
    {
      "title": "岗位名称",
      "description": ["职责1", "职责2"]
    }
  ],
  "deliverables": ["PPT课件", "实验指导书", "代码包"],
  "notes": "备注信息"
}
```

### 字段要求

| 字段 | 类型 | 要求 |
|------|------|------|
| `title` | string | 主标题，格式为 `{企业名}案例` |
| `subtitle` | string | 副标题，固定为 `教学课程方案` |
| `introduction` | string | 方案介绍，不少于 100 字 |
| `modules` | array | 4 个教学模块，每模块 items 不少于 3 条 |
| `positions` | array | 6 个相关岗位，需结合行业与专业 |
| `deliverables` | array | 交付物清单 |
| `notes` | string | 备注 |

> **注意**：`title` 和 `subtitle` 字段由系统在代码层面强制覆盖，无论 LLM 输出什么，最终都会被规范为 `{企业名}案例` / `教学课程方案`。因此编辑模板时可以随意填写这两个字段的示例值，不影响最终结果。

### 高亮标记

在 `introduction` 中需要强调的动态内容（企业名、行业名、专业名、课时数等），使用 HTML 标签包裹：

```html
<b class="highlight">用友网络</b>公司是一家专注于<b class="highlight">制造业</b>领域的企业...
```

---

## 4. 管理操作（通过 Swagger UI）

系统暂无独立的提示词管理页面，所有操作通过后端自带的 API 文档完成。

**访问地址**：`http://yonyou-caseedu.hongyaa.com.cn/docs`

打开后找到 **prompts** 分组，包含以下接口：

### 4.1 查看当前模板

1. 点击 `GET /api/admin/prompts` → 点击 **Try it out** → **Execute**
2. 返回列表中找到目标模板，记下 `id` 和 `current_version_number`
3. 点击 `GET /api/admin/prompts/{template_id}`，填入模板 ID → Execute
4. 查看 `current_version.content` 即为当前生效的完整提示词

### 4.2 编辑提示词（创建新版本）

提示词不支持原地修改。每次编辑都是**创建一个新版本**，新版本自动成为当前生效版本。

1. 点击 `POST /api/admin/prompts/{template_id}/versions`
2. 填写请求体：

```json
{
  "content": "（将完整的提示词内容粘贴在此处）",
  "variables": "major, industry, enterprise_name, region, hour",
  "remark": "v2: 优化了模块三的实战案例描述"
}
```

3. 点击 **Execute**，返回的 `version_number` 即为新版本号
4. 新版本立即生效，下次用户生成方案时将使用新提示词

### 4.3 回滚到历史版本

如果新版本效果不理想，可以快速回滚：

1. `GET /api/admin/prompts/{template_id}/versions` — 查看所有历史版本
2. 找到要回滚的目标版本，记下 `version_id`
3. `POST /api/admin/prompts/{template_id}/versions/{version_id}/rollback` — Execute
4. 该版本立即恢复为当前生效版本

### 4.4 创建全新模板

```json
{
  "name": "制造业专项方案模板",
  "description": "针对制造业企业的定制化提示词",
  "content": "（完整提示词内容）",
  "variables": "major, industry, enterprise_name, region, hour",
  "remark": "初始版本"
}
```

> 新创建的模板 `is_active` 默认为 `true`。系统只使用 `scene = "课程方案生成"` 且 `is_active = true` 的模板。如需切换模板，需通过数据库直接修改 `is_active` 字段。

---

## 5. 编辑提示词的注意事项

### 5.1 花括号转义

模板中所有非变量的花括号必须双写转义：

```
{enterprise_name}      ← 变量，正确
{{enterprise_name}}    ← 错误，不会被替换

"modules": [           ← 错误，JSON 中的 { 会被当作变量
"modules": [[          ← 正确，[[ 转义为 {
```

### 5.2 保持 JSON 输出格式

模板末尾必须明确要求 LLM 仅输出 JSON，建议保留以下约束语句：

```
重要提示：
1. 仅输出上述 JSON 对象，不要输出其他任何内容。
2. JSON 中所有字段均为必填项。
3. introduction 字段不少于100字。
4. modules 数组必须包含4个模块，每个模块的 items 不少于3条。
5. positions 数组必须包含6个岗位。
```

### 5.3 课时分配参考

模板中的 `{hour_block1}` ~ `{hour_block4}` 由系统自动计算，建议在模板中保留参考说明：

```
课时分配参考：
- 模块一（行业背景与需求分析）：{hour_block1}课时
- 模块二（技术基础与工具介绍）：{hour_block2}课时
- 模块三（案例实战与项目实施）：{hour_block3}课时
- 模块四（总结与拓展）：{hour_block4}课时
```

计算规则：
- 模块一 = 总课时 / 8（最少 1 课时）
- 模块二 = 总课时 / 8（最少 1 课时）
- 模块三 = 总课时 / 2
- 模块四 = 总课时 - 模块一 - 模块二 - 模块三

---

## 6. 快速参考：当前默认模板

当前系统内置的默认模板结构如下（仅供参考，实际内容可能因版本不同而变化）：

```
请根据以下信息，生成一份产业案例教学课程设计方案。

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
  "introduction": "（不少于100字，动态内容用 <b class=\"highlight\">内容</b> 标记）",
  "modules": [
    {{
      "name": "模块一：行业背景与需求分析",
      "hours": {hour_block1},
      "items": ["...", "...", "..."]
    }},
    ...（共4个模块）
  ],
  "positions": [
    {{
      "title": "岗位名称",
      "description": ["职责1", "职责2"]
    }}
    ...（共6个岗位）
  ],
  "deliverables": ["PPT课件", "教学视频", "实验指导书", "数据集", "代码包", "实操环境配置文档"],
  "notes": "以上内容由 AI 生成，请结合实际教学需求进行调整。"
}}

重要提示：
1. 仅输出上述 JSON 对象，不要输出其他任何内容。
2. JSON 中所有字段均为必填项。
3. introduction 字段不少于100字。
4. modules 数组必须包含4个模块，每个模块的 items 不少于3条。
5. positions 数组必须包含6个岗位，岗位和描述需结合行业与专业。
6. 报价信息不需要生成，由系统另行计算。
```

---

## 7. 常见问题

**Q: 修改模板后多久生效？**
A: 立即生效。创建新版本后，下一次用户请求生成方案时就会使用新模板。

**Q: 可以同时启用多个模板吗？**
A: 系统只使用第一个 `scene = "课程方案生成"` 且 `is_active = true` 的模板。如果有多个同场景模板，只有其中一个会生效。

**Q: 回滚版本会影响已生成的方案吗？**
A: 不会。已生成的方案存储在数据库中，与模板版本无关。回滚只影响后续新生成的方案。

**Q: 模板写错了导致生成结果异常怎么办？**
A: 立即回滚到上一个正常版本即可。所有历史版本都保留，可随时切换。

**Q: 如何测试新模板效果？**
A: 在前台使用同一个企业连续生成两次方案，第一次用旧模板、第二次用新模板，对比效果。
