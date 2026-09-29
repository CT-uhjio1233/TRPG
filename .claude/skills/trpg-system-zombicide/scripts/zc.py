#!/usr/bin/env python3
"""無盡殺戮（Zombicide）批次擲骰工具（范恩．無盡殺戮專用）

一次執行即完成本回合所有擲骰。任何參數有誤時，整批都不會擲出。

用法：
  python3 zc.py "標籤:規格" ["標籤:規格" ...]
  python3 zc.py --list            列出替代牌堆的內容

規格：
  NdA                 攻擊或破門：N 顆骰、準度 A（例：3d4 ＝ 3 顆、4 點以上命中）
    可加後綴（以空白或逗號分隔）：
      +1              每顆骰點 +1（上限 6）；「+1 骰點」類技能
      x6              每擲出一個自然 6 就追加一顆骰（可連鎖）；「投六點」類技能
      ao:K            加上 K 顆全力骰（第二版）：自然 1 為「損壞」
    例：「瑟莉-手弩:4d3」「阿凱-鏈鋸:2d5 ao:2」「小宇-長弓:1d3 +1 x6」
  def:NdA             防禦骰（護甲）：N 顆骰、A 點以上抵消一次攻擊
  keep:K              保存擲骰（第二版戰役）：K 顆全力骰，出現任何損壞即失去該裝備
  hedge               穿越樹牆（獸之死）：1D6，結果 1 則目標區域出現 1 隻獸人行屍
  cat:彈藥[:見]        投石車開火（獸之死）：彈藥＝碎石／霰彈／巨石；加「:見」表示有倖存者看得到目標區域（準度 3+）
  spawn:gh:危險級別    獸之死替代喪屍卡；危險級別＝藍／黃／橙／紅
  spawn:2e:危險級別    第二版替代喪屍卡
  search:gh           從獸之死的一般裝備牌堆抽一張（名稱與張數依規則書配件表）

替代牌堆：規則書沒有列出喪屍卡的內容，spawn 使用本 skill 自訂的替代牌堆
（張數、卡片種類與範例卡依規則書，各級別數量為自訂）；搜索與生成都以「抽後放回」近似。
有實體遊戲時，請改用實體卡。
"""

import random
import re
import sys
import unicodedata

RNG = random.SystemRandom()

LEVELS = {"藍": 0, "藍色": 0, "blue": 0, "黃": 1, "黃色": 1, "yellow": 1,
          "橙": 2, "橙色": 2, "orange": 2, "紅": 3, "紅色": 3, "red": 3}
LEVEL_NAMES = ["藍", "黃", "橙", "紅"]

# 獸之死替代喪屍卡：54 張（規則書：喪屍卡 #167–#220）
# 每張：(名稱, 張數, [藍, 黃, 橙, 紅] 各級別的出現內容, 各級別的屍群效果或 None)
GH_DECK = [
    ("獸人行屍 A", 6, ["1 獸人行屍", "2 獸人行屍", "4 獸人行屍", "6 獸人行屍"], ["+1 獸人行屍"] * 4),
    ("獸人行屍 B", 5, ["2 獸人行屍", "3 獸人行屍", "5 獸人行屍", "7 獸人行屍"], ["+1 獸人行屍"] * 4),
    ("獸人行屍 C", 5, ["無喪屍", "2 獸人行屍", "3 獸人行屍", "5 獸人行屍"], ["+1 獸人行屍"] * 4),
    ("獸人行屍 D", 4, ["1 獸人行屍", "1 獸人行屍", "2 獸人行屍", "3 獸人行屍"], ["+1 獸人行屍"] * 4),
    ("獸人疾行屍 A", 4, ["1 獸人疾行屍", "1 獸人疾行屍", "2 獸人疾行屍", "3 獸人疾行屍"], ["+1 獸人疾行屍"] * 4),
    ("獸人疾行屍 B", 3, ["無喪屍", "2 獸人疾行屍", "2 獸人疾行屍", "4 獸人疾行屍"], ["+1 獸人疾行屍"] * 4),
    ("混合（規則書範例卡）", 1, ["無喪屍", "4 獸人疾行屍", "5 獸人行屍", "2 獸人碩屍"], [None, "+1 獸人疾行屍", "+1 獸人行屍", "+1 獸人碩屍"]),
    ("獸人碩屍 A", 4, ["1 獸人碩屍", "1 獸人碩屍", "2 獸人碩屍", "3 獸人碩屍"], ["+1 獸人碩屍"] * 4),
    ("獸人碩屍 B", 4, ["無喪屍", "1 獸人碩屍", "2 獸人碩屍", "2 獸人碩屍"], ["+1 獸人碩屍"] * 4),
    ("獸人憎惡", 2, ["1 獸人碩屍", "1 獸人憎惡", "1 獸人憎惡", "1 獸人憎惡"], ["+1 獸人碩屍", None, None, None]),
    ("獸人死靈法師", 6, ["1 獸人死靈法師＋死靈法師出生點", "1 獸人死靈法師＋死靈法師出生點",
                      "1 獸人死靈法師＋死靈法師出生點", "1 獸人死靈法師＋死靈法師出生點"], ["行屍、碩屍、疾行屍各 +1"] * 4),
    ("額外激活：行屍", 2, ["無效果", "所有獸人行屍額外激活", "所有獸人行屍額外激活", "所有獸人行屍額外激活"], None),
    ("額外激活：疾行屍", 2, ["無效果", "所有獸人疾行屍額外激活", "所有獸人疾行屍額外激活", "所有獸人疾行屍額外激活"], None),
    ("額外激活：碩屍", 2, ["無效果", "所有獸人碩屍額外激活", "所有獸人碩屍額外激活", "所有獸人碩屍額外激活"], None),
    ("屍群來襲！", 4, ["屍群全部放入此區域，並立刻結束本次喪屍現身"] * 4, None),
]

# 第二版替代喪屍卡：40 張（濃縮規則：核心盒喪屍卡 #001–#040）
TWO_E_DECK = [
    ("行屍 A", 7, ["1 行屍", "2 行屍", "4 行屍", "6 行屍"]),
    ("行屍 B", 6, ["2 行屍", "3 行屍", "5 行屍", "7 行屍"]),
    ("行屍 C", 5, ["1 行屍", "1 行屍", "2 行屍", "3 行屍"]),
    ("行屍（突襲）", 2, ["1 行屍，突襲", "2 行屍，突襲", "3 行屍，突襲", "4 行屍，突襲"]),
    ("疾行屍 A", 4, ["1 疾行屍", "1 疾行屍", "2 疾行屍", "3 疾行屍"]),
    ("疾行屍（突襲）", 2, ["1 疾行屍，突襲", "1 疾行屍，突襲", "2 疾行屍，突襲", "2 疾行屍，突襲"]),
    ("蠻屍", 6, ["1 蠻屍", "1 蠻屍", "2 蠻屍", "3 蠻屍"]),
    ("憎惡", 2, ["1 蠻屍", "1 憎惡", "1 憎惡", "1 憎惡"]),
    ("額外激活：行屍", 2, ["無效果", "所有行屍額外激活", "所有行屍額外激活", "所有行屍額外激活"]),
    ("額外激活：疾行屍", 2, ["無效果", "所有疾行屍額外激活", "所有疾行屍額外激活", "所有疾行屍額外激活"]),
    ("額外激活：蠻屍", 2, ["無效果", "所有蠻屍額外激活", "所有蠻屍額外激活", "所有蠻屍額外激活"]),
]

# 獸之死一般裝備牌堆（規則書配件表，扣除起始裝備與地窖秘寶）：66 張
GH_EQUIP = [
    ("獸人喪屍！！", 4, "特殊"), ("蘋果", 2, "食物"), ("戰斧", 2, "近戰"), ("鎖甲", 2, "護甲"),
    ("弩", 2, "遠程"), ("彎匕首", 4, "近戰"), ("死亡吹息", 2, "法術"), ("龍涎", 4, "特殊"),
    ("矮人之錘", 2, "近戰"), ("偃月刀", 2, "近戰"), ("幽靈視野", 1, "法術"), ("巨斧", 2, "近戰"),
    ("手弩", 2, "遠程"), ("治療術", 1, "法術"), ("閃電球", 2, "法術"), ("長弓", 2, "遠程"),
    ("北歐盾", 2, "盾牌"), ("北歐劍", 1, "近戰"), ("板甲", 1, "護甲"), ("弓箭袋", 3, "輔助"),
    ("弩箭袋", 3, "輔助"), ("連弩", 2, "遠程"), ("吹飛術", 1, "法術"), ("鹹肉", 2, "食物"),
    ("半月刀", 2, "近戰"), ("盾牌", 2, "盾牌"), ("短劍", 1, "近戰"), ("瞬身術", 1, "法術"),
    ("刺弓", 1, "近戰／遠程"), ("念動力", 1, "法術"), ("火把", 4, "特殊"), ("震懾術", 1, "法術"),
    ("水袋", 2, "食物"),
]

CATAPULT = {"碎石": (6, 1), "霰彈": (3, 2), "巨石": (1, 3)}


class SpecError(Exception):
    pass


def display_width(text):
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in text)


def pad(text, width):
    return text + " " * (width - display_width(text))


def expand(deck):
    faces = []
    for entry in deck:
        faces.extend([entry] * entry[1])
    return faces


def parse(arg):
    keys = ("def:", "keep:", "cat:", "spawn:", "search:")
    if arg.startswith(keys) or arg == "hedge" or re.match(r"\d+d", arg):
        label, spec = arg, arg
    elif ":" in arg:
        label, _, spec = arg.partition(":")
    else:
        raise SpecError(f"「{arg}」：寫法為「標籤:規格」")
    spec = spec.strip()
    kind_head = spec.split(":")[0]

    if kind_head == "hedge":
        return (label, "hedge", None)
    if kind_head == "search":
        if spec != "search:gh":
            raise SpecError(f"「{arg}」：目前只有 search:gh")
        return (label, "search", None)
    if kind_head == "keep":
        m = re.fullmatch(r"keep:(\d+)", spec)
        if not m or not 1 <= int(m.group(1)) <= 10:
            raise SpecError(f"「{arg}」：保存擲骰寫法為 keep:K（K 為 1–10）")
        return (label, "keep", int(m.group(1)))
    if kind_head == "def":
        m = re.fullmatch(r"def:(\d+)d([2-6])", spec)
        if not m or not 1 <= int(m.group(1)) <= 30:
            raise SpecError(f"「{arg}」：防禦骰寫法為 def:NdA，例如 def:2d4")
        return (label, "def", (int(m.group(1)), int(m.group(2))))
    if kind_head == "cat":
        parts = spec.split(":")
        if len(parts) not in (2, 3) or parts[1] not in CATAPULT or (len(parts) == 3 and parts[2] != "見"):
            raise SpecError(f"「{arg}」：投石車寫法為 cat:碎石／霰彈／巨石，可加 :見")
        return (label, "cat", (parts[1], len(parts) == 3))
    if kind_head == "spawn":
        parts = spec.split(":")
        if len(parts) != 3 or parts[1] not in ("gh", "2e") or parts[2] not in LEVELS:
            raise SpecError(f"「{arg}」：生成寫法為 spawn:gh:藍 或 spawn:2e:紅（藍／黃／橙／紅）")
        return (label, "spawn", (parts[1], LEVELS[parts[2]]))

    tokens = [t for t in re.split(r"[\s,，]+", spec) if t]
    m = re.fullmatch(r"(\d+)d([2-6])", tokens[0]) if tokens else None
    if not m:
        raise SpecError(f"「{arg}」：攻擊寫法為 NdA（例 3d4），可加 +1、x6、ao:K")
    n, acc = int(m.group(1)), int(m.group(2))
    if not 0 <= n <= 30:
        raise SpecError(f"「{arg}」：骰數必須是 0–30")
    plus, chain, allout = False, False, 0
    for t in tokens[1:]:
        if t == "+1":
            plus = True
        elif t == "x6":
            chain = True
        elif re.fullmatch(r"ao:\d+", t) and 1 <= int(t[3:]) <= 10:
            allout = int(t[3:])
        else:
            raise SpecError(f"「{arg}」：看不懂後綴「{t}」")
    if n == 0 and allout == 0:
        raise SpecError(f"「{arg}」：至少要有一顆骰")
    return (label, "atk", (n, acc, plus, chain, allout))


def roll_pool(n, allout, chain):
    """回傳 [(自然點數, 是否全力骰)]；x6 追加的骰子視為一般骰。"""
    dice = [(RNG.randint(1, 6), False) for _ in range(n)] + [(RNG.randint(1, 6), True) for _ in range(allout)]
    if chain:
        pending = sum(1 for v, _ in dice if v == 6)
        while pending:
            extra = [(RNG.randint(1, 6), False) for _ in range(pending)]
            dice.extend(extra)
            pending = sum(1 for v, _ in extra if v == 6)
    return dice


def fmt_dice(dice, plus):
    out = []
    for v, ao in dice:
        if ao and v == 1:
            out.append("損")
        else:
            shown = min(6, v + 1) if plus else v
            out.append(f"{shown}{'*' if ao else ''}")
    return " ".join(out)


def run(label, kind, data, width):
    tag = pad(label, width)
    if kind == "atk":
        n, acc, plus, chain, allout = data
        dice = roll_pool(n, allout, chain)
        hits = sum(1 for v, ao in dice if not (ao and v == 1) and (min(6, v + 1) if plus else v) >= acc)
        breaks = sum(1 for v, ao in dice if ao and v == 1)
        misses = len(dice) - hits
        mods = "".join([" +1" if plus else "", " x6" if chain else "", f" 全力{allout}" if allout else ""])
        extra = f"｜損壞 {breaks}（武器於行動後棄掉）" if breaks else ""
        print(f"[骰] {tag} {n}D6 準度 {acc}+{mods} → {fmt_dice(dice, plus)}（命中 {hits}｜未中 {misses}{extra}）")
    elif kind == "def":
        n, acc = data
        dice = [RNG.randint(1, 6) for _ in range(n)]
        ok = sum(1 for v in dice if v >= acc)
        print(f"[骰] {tag} 防禦 {n}D6 準度 {acc}+ → {' '.join(map(str, dice))}（抵消 {ok} 次攻擊）")
    elif kind == "keep":
        dice = [RNG.randint(1, 6) for _ in range(data)]
        broken = any(v == 1 for v in dice)
        shown = " ".join("損" if v == 1 else str(v) for v in dice)
        print(f"[骰] {tag} 保存 {data} 顆全力骰 → {shown}（{'失去' if broken else '保留到下個任務'}）")
    elif kind == "hedge":
        v = RNG.randint(1, 6)
        print(f"[骰] {tag} 穿越樹牆 1D6 → {v}（{'目標區域出現 1 隻獸人行屍' if v == 1 else '沒有東西'}）")
    elif kind == "cat":
        ammo, seen = data
        n, dmg = CATAPULT[ammo]
        acc = 3 if seen else 4
        dice = [RNG.randint(1, 6) for _ in range(n)]
        hits = sum(1 for v in dice if v >= acc)
        print(f"[骰] {tag} 投石車・{ammo} {n}D6 準度 {acc}+ 傷害 {dmg} → {' '.join(map(str, dice))}（命中 {hits}，不發出噪音）")
    elif kind == "spawn":
        game, level = data
        faces = expand(GH_DECK if game == "gh" else TWO_E_DECK)
        idx = RNG.randint(1, len(faces))
        card = faces[idx - 1]
        result = card[2][level]
        horde = ""
        if game == "gh" and card[3] and card[3][level] and result != "無喪屍":
            horde = f"｜屍群 {card[3][level]}"
        name = "獸之死" if game == "gh" else "第二版"
        print(f"[骰] {tag} {name}喪屍卡（{LEVEL_NAMES[level]}級）1D{len(faces)} → {idx}｜{card[0]}：{result}{horde}")
    elif kind == "search":
        faces = expand(GH_EQUIP)
        idx = RNG.randint(1, len(faces))
        name, _, cat = faces[idx - 1]
        print(f"[骰] {tag} 搜索 1D{len(faces)} → {idx}｜{name}（{cat}）")


def list_decks():
    for title, deck, total in (("獸之死替代喪屍卡", GH_DECK, 54), ("第二版替代喪屍卡", TWO_E_DECK, 40)):
        print(f"== {title}（{sum(e[1] for e in deck)}／{total} 張）")
        for e in deck:
            print(f"  ×{e[1]} {e[0]}：" + "／".join(f"{LEVEL_NAMES[i]} {e[2][i]}" for i in range(4)))
    print(f"== 獸之死一般裝備牌堆（{sum(e[1] for e in GH_EQUIP)} 張）")
    print("  " + "、".join(f"{n}×{c}" for n, c, _ in GH_EQUIP))


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv else 2
    if argv[0] == "--list":
        list_decks()
        return 0
    try:
        plan = [parse(a) for a in argv]
    except SpecError as e:
        print(f"參數錯誤（整批未擲出）：{e}", file=sys.stderr)
        return 2
    width = max(display_width(p[0]) for p in plan)
    for label, kind, data in plan:
        run(label, kind, data, width)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
