# 维护者发布约定

每次版本更新必须同时更新 `SKILL.md`、README 的版本、`CHANGELOG.md` 和 `VERIFICATION.md`。日志写清日期、变化、影响及实际验证范围；未发布的开发记录标明状态。不能只改版本号、不写日志。

1. 从唯一维护源准备本 Skill 的公开文件，保留其他工作区改动，检查没有私人档案、学生材料、凭据或电脑固定路径。
2. 按变化测试代表性任务；有检查器变化时测试正常、缺文件、改文件、本地修改、错误来源、无网络和版本比较等分支。结构验证不能代替实际平台验证。
3. 最后一次编辑后生成根目录 `update-manifest.json`：`schema: 1`、`repository: Amasun93/ai-hackathon-skills`、`version`、`hash_mode: sha256-lf`、`files`（相对路径到 SHA256）。包含全部公开文本文件，排除清单自身、`.git`、`__pycache__` 和测试临时文件。计算前将 CRLF 转 LF，不删除其他内容。清单不包含远程执行命令。
4. 运行 `python scripts/check_update.py --offline`，核对 `integrity` 为 `local_manifest_ok`，且更新日志有对应版本条目。用 Skill Creator 核对元数据与相对引用。失败不能发布。清单生成后再改文件必须重新生成。
5. 同步到独立公开仓库，检查差异后提交、推送。建立新的 `v版本号` 标签及同名 GitHub Release，把本版日志作为 Release 内容；不移动既有标签，不提供 ZIP 安装流程。不将私有开发仓库改为公开。
6. 用匿名网络访问检查最新 Release、标签入口与清单；从 GitHub 新克隆或安全更新一个验证安装，运行联网自检。记录实际通过项和未验证范围，再交付仓库、版本、日志与更新用法。

自检采用 [GitHub 最新正式 Release API](https://docs.github.com/en/rest/releases/releases#get-the-latest-release)，正式更新使用 [Git 的快进合并原则](https://git-scm.com/docs/git-pull)。不让学生安装跟随尚未发布的开发修改。
