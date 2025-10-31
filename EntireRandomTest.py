# -*- coding: utf-8 -*-
import random
import datetime
import os
import sys

VOCAB_FILE = "..\CET-6.txt"

def load_vocab(path):
    vocab = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # 格式示例：consistent\tadj. 一致的
            parts = line.split("\t")
            if len(parts) >= 2:
                eng = parts[0].strip()
                cn = parts[1].strip()
                if eng and cn:
                    vocab.append((eng, cn))
            else:
                # 可能是以空格分隔的遗留行
                # 找到第一个连续空白分隔
                sp = line.split(None, 1)
                if len(sp) == 2:
                    eng = sp[0].strip()
                    cn = sp[1].strip()
                    if eng and cn:
                        vocab.append((eng, cn))
    # 去重（以英文为键）
    dedup = {}
    for eng, cn in vocab:
        if eng not in dedup:
            dedup[eng] = cn
    vocab = [(k, v) for k, v in dedup.items()]
    return vocab

def pick_distractors(vocab, correct_cn, k=3):
    # 从其他中文释义中随机挑选干扰项，避免与正确释义重复
    pool = [cn for _, cn in vocab if cn != correct_cn]
    # 去重
    pool = list(dict.fromkeys(pool))
    if len(pool) < k:
        return random.sample(pool, len(pool))
    return random.sample(pool, k)

def format_question(idx, eng, options):
    letters = ["A", "B", "C", "D"]
    lines = [f"第{idx}题：{eng} 的中文意思是？"]
    for i, opt in enumerate(options):
        lines.append(f"  {letters[i]}. {opt}")
    lines.append("  E. 不会（直接记为错）")
    return "\n".join(lines)

def get_user_choice():
    while True:
        ans = input("你的选择（A/B/C/D/E）：").strip().upper()
        if ans in ["A", "B", "C", "D", "E"]:
            return ans
        print("输入无效，请输入 A/B/C/D/E。")

def main():
    try:
        vocab = load_vocab(VOCAB_FILE)
    except Exception as e:
        print(f"读取词库失败：{e}")
        sys.exit(1)

    if len(vocab) < 4:
        print("词库条目不足以出题（至少需要4条）。")
        sys.exit(1)

    # 随机抽取30个不同的单词作为题目
    questions = random.sample(vocab, min(30, len(vocab)))

    wrong_list = []  # 在答题过程中临时保存错题（题干英文与正确中文）

    print("神功大成版测试开始！共30题（若库不足则以库大小为准）。\n")

    try:
        for i, (eng, cn) in enumerate(questions, start=1):
            distractors = pick_distractors(vocab, cn, k=3)
            options = distractors + [cn]
            random.shuffle(options)
            correct_index = options.index(cn)  # 0..3

            print(format_question(i, eng, options))
            choice = get_user_choice()

            if choice == "E":
                print(f"正确答案：{cn}\n")
                wrong_list.append((eng, cn))
                continue

            chosen_index = {"A":0, "B":1, "C":2, "D":3}[choice]
            if chosen_index == correct_index:
                print("答对了！\n")
            else:
                print(f"答错了。正确答案：{cn}\n")
                wrong_list.append((eng, cn))

        # 统一写错题文件
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        if wrong_list:
            filename = f"..\\final_test_{timestamp}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                for eng, cn in wrong_list:
                    f.write(f"{eng}\t{cn}\n")
            print(f"测试结束！错题已保存至：{filename}")
        else:
            print("测试结束！本次全对，太厉害了！")

    except KeyboardInterrupt:
        print("\n检测到中断，正在保存错题...")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        if wrong_list:
            filename = f"..\\final_test_{timestamp}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                for eng, cn in wrong_list:
                    f.write(f"{eng}\t{cn}\n")
            print(f"已保存当前进度的错题至：{filename}")
        else:
            print("无错题需要保存。")
        print("已退出。")

if __name__ == "__main__":
    main()


