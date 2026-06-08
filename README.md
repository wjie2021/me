# me — 数字生命

一个关于我的数字生命项目。通过收集个人资料，AI 自动分析人格特质，生成可被智能体加载的「数字分身」。

支持增量分析——随时添加新资料，重新运行，profile 会持续进化。
Skill 本身也会自进化——分析框架会根据你的资料特点自动调整。

## 目录结构

```text
sources/                    ← 你的原始资料（随便放 .md 文件）
  _template.md              ← 模板示例
profile/                    ← 生成的人格档案
  digital-life.md           ← 数字生命 profile（完整版，保留原始上下文）
  manifest.json             ← 分析状态记录（追踪已分析的文件）
  changelog.md              ← 人格进化日志
  skill-evolution.md        ← skill 自身的进化日志
  skill/                    ← 模块化 skill（可单独加载）
    README.md               ← skill 使用说明
    identity.md             ← 核心身份
    worldview.md            ← 世界观与哲学倾向
    values.md               ← 价值观与原则底线
    thinking.md             ← 思维模式
    communication.md        ← 沟通风格与禁忌
    personality.md          ← 性格特质（大五人格）
    expertise.md            ← 知识与专长领域
    behavior.md             ← 行为指南
    unique-traits.md        ← 独特印记
    growth.md               ← 成长轨迹
    health.md               ← 健康状况与日常管理
.claude/skills/
  analyze-personality.md    ← 核心 skill：增量分析 → 生成/更新 profile + skill 子文档
```

## 使用方式

### 1. 添加资料

在 `sources/` 下创建任意 `.md` 文件，比如：

- `bio.md` — 个人简介
- `projects.md` — 项目经历
- `thoughts.md` — 想法和观点
- `work-style.md` — 工作习惯
- `interests.md` — 兴趣爱好
- ...

内容越丰富，生成的数字生命越接近真实的你。

### 2. 运行分析

在 Claude Code 中执行：

```text
/analyze-personality
```

首次运行：全量分析所有资料，生成完整 profile。
后续运行：自动检测新增/修改/删除的文件，增量更新 profile。

### 3. 持续进化

随时往 `sources/` 添加新资料，然后重新运行 `/analyze-personality`。
AI 会对比变化，只更新受影响的部分，并在 `changelog.md` 中记录每次进化。

### 4. Skill 自进化

每 3 次分析后，skill 会自动反思分析质量：

- 哪些维度始终信息不足 → 合并或降级
- 哪些维度你反复手动修改 → 调整分析方式
- 资料中反复出现但框架没覆盖的主题 → 新增维度

进化记录在 `profile/skill-evolution.md`，你可以审查每次调整。

### 5. 使用数字生命

两种方式：

**方式一：完整加载**

加载 `profile/digital-life.md`，一次获取全部信息。

**方式二：按需组合（推荐）**

从 `profile/skill/` 中选择需要的子文档，单独或组合加载：

- 最小组合：`identity.md` + `communication.md` + `behavior.md`（基本能像他一样说话）
- 完整组合：全部加载 = 完整数字分身
- 按场景组合：比如只需要沟通风格就加载 `communication.md`，涉及技术话题就加 `expertise.md`

详见 `profile/skill/README.md`。

## 设计理念

- **资料层**（sources/）：你提供原始素材，形式不限
- **分析层**（skill）：AI 深度分析人格维度，支持增量
- **人格层**（profile/）：结构化的数字生命档案 + 变更追踪
- **输出层**（profile/skill/）：模块化子文档，可单独加载给其他智能体

四层分离，各司其职。数字生命会随着你的资料积累而不断成长。
