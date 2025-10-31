四/六级词汇测验小工具

A lightweight CLI toolset to practice CET-4/6 vocabulary with randomized multiple-choice quizzes and a “wrongbook” mode to focus on mistakes.

- 语言/Language: Python 3
- 文件/Files:
  - CET-6.txt：词库文件
  - EntireRandomTest.py：随机测验模式
  - Wrongbookmode.py：错题本练习模式

本项目提供两个命令行小工具，帮助高效刷词：
- 随机测验模式（EntireRandomTest.py）：从完整词库中随机抽题，生成四选一中文释义题。
- 错题本模式（Wrongbookmode.py）：从错题本中出题，答对问题自动删除该选项；支持自动创建/重建错题本，支持去重策略。

目录结构
- 4 六级-乱序.txt：词库示例，格式为“英文[TAB]中文释义”，亦兼容“英文 空白 中文释义”。
- EntireRandomTest.py：完整词库随机刷题脚本。
- Wrongbookmode.py：错题本模式脚本（包含去重/重建逻辑）。

快速开始
1) 配置路径
- 两个脚本中默认使用路径：
  - VOCAB_FILE = Path_to_ur_vocabulary\CET-6.txt
  - WRONGBOOK_FILE = r".\Wrongbook\wrongbook.txt"（仅 Wrongbookmode.py 需要）

2) 运行随机测验
- 执行 EntireRandomTest.py
- 程序将读取词库、随机抽题、生成四选一中文释义选项，并在控制台交互答题。

3) 运行错题本模式
- 执行 Wrongbookmode.py
- 首次运行将创建错题本；如错题本条目显著少于原库，会提示是否重建。
- 按提示进行测验与错题维护，每次回答正确会删除对应单词。

词库格式说明
- 推荐使用制表符分隔：consistent[TAB]adj. 一致的
- 也兼容“英文 空格 中文释义”的行
- 空行或以 # 开头的行将被忽略
- 文件编码需为 UTF-8

去重策略（Wrongbookmode.py）
- DEDUP_MODE 取值：
  - "english"：按英文唯一
  - "pair"：按英文+中文释义唯一（默认）
  - "none"：不去重
- 根据词库特点选择最合适的策略，建议默认 "pair"。

错题本重建阈值
- WRONGBOOK_REBUILD_RATIO = 0.001
- 当错题本条目数量 < 原库 × 阈值 时，运行脚本会提示是否重建
- 可按个人学习进度调整该比例

致谢
- 词库来自(https://github.com/KyleBing/english-vocabulary)


