# -*- coding: utf-8 -*-
import random
import os
import sys

# 自行按需修改为你的绝对路径
VOCAB_FILE = r"..\CET-6.txt"
WRONGBOOK_FILE = r"..\Wrongbook\wrongbook.txt"

# 去重模式: "english"（按英文去重）, "pair"（按英文+中文去重）, "none"（不去重）
DEDUP_MODE = "pair"

# 当已有 wrongbook 条目显著少于原库时（比例阈值），提示是否重建
WRONGBOOK_REBUILD_RATIO = 0.001  # 低于 0.1% 则提醒

def load_vocab(path):
    vocab = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            # 优先按制表符分割；如没有，则按第一个空白分割
            if "\t" in line:
                parts = line.split("\t")
                # 兼容多段 tab：英文=第一段，中文=其余段合并
                eng = parts[0].strip()
                cn = "\t".join(parts[1:]).strip()
            else:
                sp = line.split(None, 1)
                if len(sp) != 2:
                    continue
                eng = sp[0].strip()
                cn = sp[1].strip()
            if eng and cn:
                vocab.append((eng, cn))

    if not vocab:
        return []

    if DEDUP_MODE == "english":
        dedup = {}
        for eng, cn in vocab:
            if eng not in dedup:
                dedup[eng] = cn
        return [(k, v) for k, v in dedup.items()]
    elif DEDUP_MODE == "pair":
        seen = set()
        out = []
        for eng, cn in vocab:
            key = (eng, cn)
            if key not in seen:
                seen.add(key)
                out.append((eng, cn))
        return out
    else:  # "none"
        return vocab

def save_vocab(path, vocab):
    # 确保目录存在
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for eng, cn in vocab:
            f.write(f"{eng}\t{cn}\n")

def ensure_wrongbook():
    all_vocab = load_vocab(VOCAB_FILE)
    if not all_vocab:
        print("原词库为空或读取失败。请检查 VOCAB_FILE 路径与内容。")
        sys.exit(1)

    if not os.path.exists(WRONGBOOK_FILE):
        save_vocab(WRONGBOOK_FILE, all_vocab)
        print(f"已创建错题本：{WRONGBOOK_FILE}（与原库一致）")
        return

    # 如果已存在，检查是否显著偏少，提示用户是否重建
    wb = load_vocab(WRONGBOOK_FILE)
    if len(wb) < len(all_vocab) * WRONGBOOK_REBUILD_RATIO:
        print(f"检测到错题本条目显著少于原库（{len(wb)} vs {len(all_vocab)}）。")
        ans = input("是否重建错题本为原库内容？(y/N)：").strip().lower()
        if ans == "y":
            save_vocab(WRONGBOOK_FILE, all_vocab)
            print("错题本已重建为原库内容。")

def pick_distractors(pool_vocab, correct_cn, k=3):
    pool = [cn for _, cn in pool_vocab if cn != correct_cn]
    # 去重但保持顺序
    seen = set()
    dedup_pool = []
    for cn in pool:
        if cn not in seen:
            seen.add(cn)
            dedup_pool.append(cn)
    if len(dedup_pool) <= k:
        return dedup_pool[:]  # 可能少于k
    return random.sample(dedup_pool, k)

def format_question(idx, total, eng, options):
    letters = ["A", "B", "C", "D"]
    left_msg = ""
    if total % 100 == 0:
        left_msg = f"（提示：还剩 {total} 词）"
    lines = [f"[{idx}/{total}] {eng} 的中文意思是？{left_msg}"]
    for i, opt in enumerate(options):
        lines.append(f"  {letters[i]}. {opt}")
    lines.append("  E. 不会（保留在错题本中）")
    lines.append("  F. 退出（安全退出，不丢进度）")
    return "\n".join(lines)

def get_user_choice():
    while True:
        ans = input("你的选择（A/B/C/D/E/F）：").strip().upper()
        if ans in ["A", "B", "C", "D", "E", "F"]:
            return ans
        print("输入无效，请输入 A/B/C/D/E/F。")

def main():
    try:
        ensure_wrongbook()
    except Exception as e:
        print(f"初始化错题本失败：{e}")
        sys.exit(1)

    print("无限循环直到完全学会模式已启动！")
    print("说明：答对则该词从错题本删除；答错或选E则保留。错题本清空即完成。")
    print("按 F 可随时安全退出。\n")

    question_counter = 0

    try:
        while True:
            wrongbook = load_vocab(WRONGBOOK_FILE)
            if not wrongbook:
                print("恭喜！错题本已清空，全部掌握！")
                break

            total = len(wrongbook)
            # 随机抽一道题，同时记住在 wrongbook 中的索引，便于精确删除
            idx = random.randrange(total)
            eng, cn = wrongbook[idx]

            distractors = pick_distractors(wrongbook, cn, k=3)
            if len(distractors) < 3:
                # 从原库补充干扰项
                all_vocab = load_vocab(VOCAB_FILE)
                extra_need = 3 - len(distractors)
                extra_pool = [cn2 for _, cn2 in all_vocab if cn2 != cn and cn2 not in distractors]
                # 去重
                seen = set(distractors)
                extra_pool_dedup = []
                for x in extra_pool:
                    if x not in seen:
                        seen.add(x)
                        extra_pool_dedup.append(x)
                if extra_pool_dedup:
                    distractors += random.sample(extra_pool_dedup, min(extra_need, len(extra_pool_dedup)))

            options = distractors + [cn]
            # 去重再保证4个
            seen = set()
            options_dedup = []
            for o in options:
                if o not in seen:
                    seen.add(o)
                    options_dedup.append(o)
            options = options_dedup
            if len(options) < 4:
                all_vocab = load_vocab(VOCAB_FILE)
                extra_pool = [cn2 for _, cn2 in all_vocab if cn2 not in options]
                # 去重
                seen2 = set(options)
                extra_pool_dedup = []
                for x in extra_pool:
                    if x not in seen2:
                        seen2.add(x)
                        extra_pool_dedup.append(x)
                need = 4 - len(options)
                if extra_pool_dedup:
                    options += random.sample(extra_pool_dedup, min(need, len(extra_pool_dedup)))
            # 若仍不足4个，则直接跳过本轮（极少情况）
            if len(options) < 4:
                continue

            options = options[:4]
            random.shuffle(options)
            correct_index = options.index(cn)

            question_counter += 1
            print(format_question(question_counter, total, eng, options))
            choice = get_user_choice()

            if choice == "F":
                print("已选择退出。错题本在每题后即时保存，进度安全。再见！")
                break

            if choice == "E":
                print(f"正确答案：{cn}\n")
                # 不移除，直接保留
                continue

            chosen_index = {"A":0, "B":1, "C":2, "D":3}[choice]
            if chosen_index == correct_index:
                print("答对了！该词将从错题本移除。\n")
                # 精确删除：按索引删除当前这一条（避免同英文多条时误删）
                del wrongbook[idx]
                save_vocab(WRONGBOOK_FILE, wrongbook)
            else:
                print(f"答错了。正确答案：{cn}（该词继续保留在错题本）\n")
                # 保留，不做改动

    except KeyboardInterrupt:
        print("\n检测到中断，进度已自动保存（错题本每题即时写回）。再见！")

if __name__ == "__main__":
    main()

