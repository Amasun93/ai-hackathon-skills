# 从 GitHub 直接安装 AI黑客松

本仓库根目录就是完整 Skill。安装后的文件夹必须名为 `dawei-heikesong`，里面直接有 `SKILL.md`、`references/` 和 `agents/`。不需要 ZIP，也不需要把六个模块分别安装。

## 给 WorkBuddy 执行的安装方法

1. 读取本文件和仓库入口，确认来源为 `https://github.com/Amasun93/ai-hackathon-skills`。
2. 确认当前平台具备本地文件和网络操作能力。Windows 用户技能位置为当前用户目录下 `.workbuddy/skills/`；macOS 为 `~/.workbuddy/skills/`。以当前 WorkBuddy 的实际目录为准，不能只装进 Codex 或 `.agents` 后就声称 WorkBuddy 能用。
3. 目标名为 `dawei-heikesong`。若目标不存在且 Git 可用，直接 clone 本仓库到该目标。已有目录先检查来源、版本和本地修改；同来源且已安装时复用，不叠套一层目录。不覆盖其他来源的同名文件。
4. 检查入口、全部引用文件可读，再开新任务验证技能可选／可调用。文件写入成功和平台实际加载成功分别核对；未显示时先开新任务，必要时由用户重启 WorkBuddy，不擅自终止未完成任务。

Windows PowerShell，首次安装（目标已存在会停止，保留原安装）：

```powershell
$skillTarget = Join-Path $env:USERPROFILE '.workbuddy\skills\dawei-heikesong'
if (Test-Path -LiteralPath $skillTarget) { throw '已存在同名目录，请先核对来源和版本。' }
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $skillTarget) | Out-Null
git clone https://github.com/Amasun93/ai-hackathon-skills.git $skillTarget
if ($LASTEXITCODE -ne 0) { throw 'GitHub 下载未完成，请检查网络和 Git。' }
Get-Content -LiteralPath (Join-Path $skillTarget 'SKILL.md') -TotalCount 10
```

macOS 终端，首次安装：

```sh
skill_target="$HOME/.workbuddy/skills/dawei-heikesong"
if [ -e "$skill_target" ]; then
  echo "已存在同名目录，请先核对来源和版本。"
else
  mkdir -p "$HOME/.workbuddy/skills"
  git clone https://github.com/Amasun93/ai-hackathon-skills.git "$skill_target"
fi
```

这些命令也可以由 WorkBuddy 根据平台执行，学生不必自己敲。没有 Git 时，可以让平台通过 GitHub 官方 API／raw 文件接口获取仓库文件：保留相同相对目录，至少包含 `SKILL.md`、`agents/openai.yaml` 和 `references/` 下全部 Markdown；只读取本仓库内容，不执行下载来的无关脚本。逐个校验文件存在与引用后再检查宿主加载。若平台既不能执行 Git 又不能获取文件，说明缺少哪项能力，请老师在可用环境完成安装；不要用浏览仓库成功代替安装。

## 安装后这样开始

如果运行中的 WorkBuddy 尚未发现新文件，等现有任务结束后关闭并重新打开，再检查“专家·技能·连接器 → 技能 → 已安装”中是否有 `dawei-heikesong`。只有文件已下载时，应明确说“文件已安装，平台识别待验证”。

在 WorkBuddy 新建本地任务，选定保存作品的外层文件夹；使用能读写文件的模式。发送：

```text
使用 AI黑客松。我叫小林，项目名称还没确定，先帮我建立项目文件夹。
```

可以输入 `/`，搜索 `dawei-heikesong` 选择技能。自然语言没有触发时明确说“读取已安装的 dawei-heikesong 技能来完成这个任务”。研究疾病无需先建项目；正式保存作品时再补姓名和目录。

已有项目时在同一个外层工作区说“继续我的项目”。一台电脑有多个学生项目时，说明学生姓名或选择正确目录，避免串档。

## 老师更新

课前选定一个已检查的版本，课中不静默切换学生环境。Git 安装可先在目标目录检查 `git remote -v` 和 `git status --short`；确认来源正确且没有本地修改，再 `git pull --ff-only`。有改动或冲突先保留并比较，不能 `reset --hard`。更新后新建任务检查入口。学生项目位于工作区，不在 Skill 安装目录，更新 Skill 不应改学生作品。

## 平台依据与验证边界

WorkBuddy 官方 [技能说明](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market) 的市场对话安装和本地上传入口，与本仓库的“Agent 从 GitHub 获取文件并放入本地技能目录”是不同路径。本包不声称已经上架技能市场。本地目录亦参考 WorkBuddy 自带 `find-skills` 的安装指引；具体实测版本与结果见 [验证记录](VERIFICATION.md)。

其他支持 Agent Skills 的平台，按该平台自己的入口安装同一个 Skill；方法和相对引用可复用，具体制作能力需在目标平台验证。
