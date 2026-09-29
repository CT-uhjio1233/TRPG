#!/usr/bin/env python3
"""至高帝皇任務與召喚系統：抽卡、時長與任務擲骰工具（范恩．戰錘 40K 專用）

所有隨機結果都由本腳本擲出。任何參數有誤時，整批都不會擲出。

用法：
  python3 summon.py pull 卡池 [選項]      抽卡（單抽或十連）
  python3 summon.py dur [選項]            計算在場時長、冷卻、負荷
  python3 summon.py mission [--n N]       擲系統任務類型
  python3 summon.py list [--faction 陣營] [--rarity Rk]
  python3 summon.py rates 卡池 [--focus 陣營]

卡池：training／訓練、frontline／前線、focus／焦點、legend／傳奇、event／活動

pull 選項：
  --ten                    十連（費用 9.5 抽）
  --focus 陣營[,陣營]      陣營焦點池必填：這些陣營在陣營擲骰中權重 ×2
  --featured 名稱[,名稱]   當期指定單位（技能名或召喚單位名）；抽到同稀有度時 1D2 判定是否命中
  --pity R4=數,R5=數       目前的保底計數（距上次命中已抽幾次）；預設皆 0
  --ep 數                  目前持有的帝皇點數，會檢查並算出餘額
  --json                   另外輸出 v1.1 §4.4 格式的 JSON

dur 選項：
  --card 技能名            從白名單取稀有度與類型；或改用 --rarity 與 --type
  --rarity R1–R5  --type 步兵／菁英／角色／載具／怪獸／超重型
  --mu 數                  投入的魔力
  --channels 數            同時維持的通道數 n（預設 1）
  --sync 數                同步度 Lv0–5（預設 0）
  --no-type                不套用類型係數（v1.1 的類型係數是選配）
  --overcast               超載施放：投入上限 +50%，冷卻 +50%
  --mp-max 數              魔力上限，用來檢查投入是否超額
  --legacy-death           死亡冷卻改用 v1.1 的小時制（預設用 v2.0：一般冷卻 ×2）

資料來源：使用者的《至高帝皇任務與召喚系統》v1.1、v2.0；
卡片白名單見 ../references/cards.csv。
"""

import argparse
import csv
import json
import os
import random
import sys

RNG = random.SystemRandom()

HERE = os.path.dirname(os.path.abspath(__file__))
CARDS_PATH = os.path.join(HERE, "..", "references", "cards.csv")

RARITIES = ["R1", "R2", "R3", "R4", "R5"]
BASE_RATES = {"R1": 54, "R2": 24, "R3": 14, "R4": 7, "R5": 1}

# v1.1 §六 4.1：陣營共 10 種，以 1D10 抽取（順序依原文）
FACTIONS = ["黑色聖堂", "太空野狼", "灰騎士", "吞世者", "帝國",
            "星界軍", "渾沌惡魔", "黑暗之奴", "黑暗天使", "禁軍"]

SOURCES = {
    "黑色聖堂": "《聖典·黑色聖堂》（10 版）",
    "太空野狼": "《聖典·太空野狼》（10 版）",
    "灰騎士": "《聖典·灰騎士》（10 版）",
    "吞世者": "《聖典·吞世者》（10 版）",
    "帝國": "《帝國裝甲與傳奇索引》（10 版）",
    "星界軍": "《聖典·星界軍》（10 版）",
    "渾沌惡魔": "《聖典·渾沌惡魔》（10 版）",
    "黑暗之奴": "《黑暗之奴規則翻譯》（西格瑪時代）",
    "黑暗天使": "《聖典·黑暗天使》（10 版）",
    "禁軍": "《聖典·帝皇禁軍》（9 版）",
}

POOLS = {
    "training": {"name": "訓練池", "cap": "R2", "single": 50, "ten": 475, "pity": {}},
    "frontline": {"name": "前線補給池", "cap": "R3", "single": 75, "ten": 712, "pity": {}},
    "focus": {"name": "陣營焦點池", "cap": "R4", "single": 100, "ten": 950, "pity": {"R4": 30}},
    "legend": {"name": "傳奇池", "cap": "R5", "single": 150, "ten": 1425, "pity": {"R4": 30, "R5": 120}},
    "event": {"name": "活動池", "cap": "R5", "single": 150, "ten": 1425, "pity": {"R4": 30, "R5": 120}},
}
POOL_ALIASES = {"訓練": "training", "訓練池": "training", "前線": "frontline", "前線補給池": "frontline",
                "焦點": "focus", "陣營焦點池": "focus", "傳奇": "legend", "傳奇池": "legend",
                "活動": "event", "活動池": "event"}

SEC_PER_MU = {"R1": 5, "R2": 4, "R3": 3, "R4": 2, "R5": 1}
TYPE_COEF = {"步兵": 1.0, "菁英": 0.9, "角色": 0.8, "載具": 0.7, "怪獸": 0.7, "超重型": 0.5}
COOLDOWN = {"R1": 30, "R2": 60, "R3": 120, "R4": 180, "R5": 300}
LEGACY_DEATH_HOURS = {"R1": 6, "R2": 12, "R3": 24, "R4": 48, "R5": 72}
TICK = {"R1": 30, "R2": 30, "R3": 30, "R4": 20, "R5": 10}

MISSIONS = [
    ("掃蕩", "清除 X 區域污染據點 ≤N 座；限時 24h；推薦 R2–3 步兵召喚"),
    ("宣戰", "對敵軍節點造成裝甲損失 ≥M；限時 48h；推薦 R3–4 載具召喚"),
    ("情報", "連續三次無擊殺偵巡；限時 12h；推薦 R1–2 偵察步兵召喚"),
    ("協助", None),
    ("拯救", "確保目標抵達撤離點；限時 2h；推薦 R2–3 護衛步兵＋運輸"),
    ("蒐集", None),
    ("鎮壓", None),
    ("護送", "確保目標抵達撤離點；限時 2h；推薦 R2–3 護衛步兵＋運輸"),
    ("淨化", "將污染度清零；限時 72h；強制開啟渾沌池（高獎）。需有污染事件為前提，尚無污染時先佈置污染前兆"),
    ("其他", None),
]


class ArgError(Exception):
    pass


def load_cards():
    with open(CARDS_PATH, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        if r["陣營"] not in FACTIONS or r["稀有度"] not in RARITIES or r["類型"] not in TYPE_COEF:
            raise SystemExit(f"cards.csv 資料錯誤：{r}")
    return rows


def resolve_pool(name):
    key = POOL_ALIASES.get(name, name)
    if key not in POOLS:
        raise ArgError(f"未知卡池「{name}」；可用：training／frontline／focus／legend／event")
    return key


def split_list(text):
    return [s.strip() for s in text.replace("，", ",").split(",") if s.strip()] if text else []


def normalized_rates(cap):
    allowed = RARITIES[: RARITIES.index(cap) + 1]
    total = sum(BASE_RATES[r] for r in allowed)
    thresholds, acc = [], 0
    for r in allowed:
        acc += BASE_RATES[r]
        thresholds.append((r, round(acc * 10000 / total)))
    thresholds[-1] = (thresholds[-1][0], 10000)
    return allowed, total, thresholds


def faction_faces(focus, eligible=None):
    faces = []
    for f in FACTIONS:
        if eligible is not None and f not in eligible:
            continue
        faces.extend([f] * (2 if f in focus else 1))
    return faces


def card_ref(card):
    return f"{SOURCES[card['陣營']]}／{card['召喚單位']}（{card['索引']}）" if card["索引"] != card["召喚單位"] \
        else f"{SOURCES[card['陣營']]}／{card['召喚單位']}"


def timing_text(card, legacy):
    coef = TYPE_COEF[card["類型"]]
    per = SEC_PER_MU[card["稀有度"]] * coef
    cd = COOLDOWN[card["稀有度"]]
    death = f"{LEGACY_DEATH_HOURS[card['稀有度']]} 小時（v1.1）" if legacy else f"{cd * 2} 秒（v2.0：一般冷卻 ×2）"
    return (f"{SEC_PER_MU[card['稀有度']]} s/MU × {card['類型']} {coef:g} = {per:g} s/MU"
            f"｜冷卻 {cd} 秒｜死亡冷卻 {death}")


def cmd_pull(args, cards):
    pool_key = resolve_pool(args.pool)
    pool = POOLS[pool_key]
    focus = split_list(args.focus)
    featured_names = split_list(args.featured)
    for f in focus:
        if f not in FACTIONS:
            raise ArgError(f"未知陣營「{f}」；可用：{'、'.join(FACTIONS)}")
    if pool_key == "focus" and not focus:
        raise ArgError("陣營焦點池必須以 --focus 指定焦點陣營")
    if focus and pool_key != "focus":
        raise ArgError("--focus 只用於陣營焦點池")
    if featured_names and pool_key not in ("focus", "legend", "event"):
        raise ArgError("--featured 只用於陣營焦點池、傳奇池、活動池")
    allowed, _, thresholds = normalized_rates(pool["cap"])
    featured = []
    for name in featured_names:
        hit = [c for c in cards if name in (c["技能名"], c["召喚單位"])]
        if not hit:
            raise ArgError(f"白名單中找不到指定單位「{name}」")
        for c in hit:
            if c["稀有度"] not in allowed:
                raise ArgError(f"指定單位「{name}」是 {c['稀有度']}，超過本池上限 {pool['cap']}")
        featured.extend(hit)
    pity = {"R4": 0, "R5": 0}
    for part in split_list(args.pity):
        k, _, v = part.partition("=")
        if k not in pity or not v.isdigit():
            raise ArgError(f"保底計數格式錯誤「{part}」，應為 R4=數,R5=數")
        pity[k] = int(v)
    count = 10 if args.ten else 1
    cost = pool["ten"] if args.ten else pool["single"]
    if args.ep is not None and args.ep < cost:
        raise ArgError(f"帝皇點數不足：需要 {cost} EP，持有 {args.ep} EP")

    by_key = {}
    for c in cards:
        by_key.setdefault((c["陣營"], c["稀有度"]), []).append(c)

    head = f"[召喚] {pool['name']}（上限 {pool['cap']}"
    if focus:
        head += f"｜焦點：{'、'.join(focus)} 權重 ×2"
    if featured:
        head += f"｜指定：{'、'.join(c['技能名'] for c in featured)}"
    head += f"）{'十連' if args.ten else '單抽'} {cost} EP"
    print(head)
    start = dict(pity)
    results = []
    for i in range(1, count + 1):
        tag = f"#{i}" if count > 1 else "  "
        forced = None
        if "R5" in pool["pity"] and pity["R5"] + 1 >= pool["pity"]["R5"]:
            forced = "R5"
        elif "R4" in pool["pity"] and pity["R4"] + 1 >= pool["pity"]["R4"]:
            forced = "R4"
        if forced:
            rarity = forced
            print(f"{tag} 稀有度 保底觸發 → {rarity}")
        else:
            value = RNG.randint(1, 10000)
            rarity = next(r for r, t in thresholds if value <= t)
            bands = " ".join(f"{r}≤{t}" for r, t in thresholds)
            print(f"{tag} 稀有度 1D10000 → {value}（{bands}）→ {rarity}")

        card = None
        feat_here = [c for c in featured if c["稀有度"] == rarity]
        if feat_here:
            coin = RNG.randint(1, 2)
            if coin == 1:
                pick = RNG.randint(1, len(feat_here)) if len(feat_here) > 1 else 1
                card = feat_here[pick - 1]
                print(f"   指定單位 1D2 → 1（命中）" + (f"｜1D{len(feat_here)} → {pick}" if len(feat_here) > 1 else ""))
            else:
                print(f"   指定單位 1D2 → 2（未命中，改抽一般卡）")
        if card is None:
            faces = faction_faces(focus)
            roll = RNG.randint(1, len(faces))
            faction = faces[roll - 1]
            print(f"   陣營 1D{len(faces)} → {roll} → {faction}")
            if (faction, rarity) not in by_key:
                eligible = [f for f in FACTIONS if (f, rarity) in by_key]
                faces = faction_faces(focus, eligible)
                roll = RNG.randint(1, len(faces))
                print(f"   （{faction}無 {rarity} 卡，於有 {rarity} 卡的陣營中重擲）1D{len(faces)} → {roll} → {faces[roll - 1]}")
                faction = faces[roll - 1]
            pool_cards = by_key[(faction, rarity)]
            pick = RNG.randint(1, len(pool_cards))
            card = pool_cards[pick - 1]
            print(f"   卡片 1D{len(pool_cards)} → {pick}")
        print(f"   ➜ {card['稀有度']}「{card['技能名']}」召喚：{card['召喚單位']}（{card['陣營']}｜{card['類型']}｜{card['規模']}）")
        print(f"     資料卡：{card_ref(card)}")
        print(f"     時長與冷卻：{timing_text(card, args.legacy_death)}")
        if card["備註"]:
            print(f"     備註：{card['備註']}")

        idx = RARITIES.index(rarity)
        if "R4" in pool["pity"]:
            pity["R4"] = 0 if idx >= 3 else pity["R4"] + 1
        if "R5" in pool["pity"]:
            pity["R5"] = 0 if idx == 4 else pity["R5"] + 1
        results.append({
            "pool_id": pool_key, "pool_name": pool["name"], "rarity_cap": pool["cap"],
            "cost_ep": cost if count == 1 else round(cost / count, 1),
            "faction": card["陣營"], "rarity": card["稀有度"], "skill_name": card["技能名"],
            "summons": card["召喚單位"], "datasheet_ref": card_ref(card), "type": card["類型"],
            "is_featured_hit": card in featured,
        })

    shown = [k for k in ("R4", "R5") if k in pool["pity"]]
    if shown:
        print("保底計數：" + "｜".join(f"{k} {start[k]}→{pity[k]}（{pool['pity'][k]} 抽保底）" for k in shown))
    else:
        print("保底計數：本池無保底，計數不變")
    if args.ep is not None:
        print(f"帝皇點數：{args.ep} − {cost} = {args.ep - cost} EP")
    if args.json:
        print(json.dumps(results if count > 1 else results[0], ensure_ascii=False, indent=2))


def cmd_dur(args, cards):
    if args.card:
        hit = [c for c in cards if args.card in (c["技能名"], c["召喚單位"])]
        if not hit:
            raise ArgError(f"白名單中找不到「{args.card}」")
        rarity, ctype, label = hit[0]["稀有度"], hit[0]["類型"], f"「{hit[0]['技能名']}」{hit[0]['召喚單位']}"
    else:
        if args.rarity not in RARITIES or args.type not in TYPE_COEF:
            raise ArgError("請用 --card，或同時給 --rarity R1–R5 與 --type 步兵／菁英／角色／載具／怪獸／超重型")
        rarity, ctype, label = args.rarity, args.type, f"{args.rarity} {args.type}"
    if args.mu is None or args.mu <= 0:
        raise ArgError("--mu 必須是正數")
    n, sync = args.channels, args.sync
    if not 1 <= n <= 4:
        raise ArgError("--channels 必須是 1–4（傳奇上限 4 通道）")
    if not 0 <= sync <= 5:
        raise ArgError("--sync 必須是 0–5")
    mu_cap = None
    if args.mp_max is not None:
        mu_cap = args.mp_max * (1.5 if args.overcast else 1)
        if args.mu > mu_cap:
            raise ArgError(f"投入 {args.mu:g} MU 超過上限 {mu_cap:g}（魔力上限 {args.mp_max:g}{'，超載 ×1.5' if args.overcast else ''}）")

    coef = 1.0 if args.no_type else TYPE_COEF[ctype]
    eta = 0.85 ** (n - 1)
    sync_bonus = 1.1 if sync >= 1 else 1.0
    per = SEC_PER_MU[rarity] * coef * eta * sync_bonus
    seconds = per * args.mu
    cd = COOLDOWN[rarity] * (0.7 if sync >= 5 else 1) * (1.5 if args.overcast else 1)
    death_mult = 0.7 if sync >= 3 else 1
    if args.legacy_death:
        death = f"{LEGACY_DEATH_HOURS[rarity] * death_mult:g} 小時（v1.1{'，Lv3 −30%' if sync >= 3 else ''}）"
    else:
        death = f"{cd * 2 * death_mult:g} 秒（v2.0：一般冷卻 ×2{'，Lv3 −30%' if sync >= 3 else ''}）"

    parts = [f"{SEC_PER_MU[rarity]} s/MU"]
    parts.append("類型係數未套用" if args.no_type else f"× {ctype} {coef:g}")
    if n > 1:
        parts.append(f"× η({n}) {eta:.4g}")
    if sync >= 1:
        parts.append("× 同步 Lv1 1.1")
    print(f"[時長] {label}：{' '.join(parts)} = {per:.4g} s/MU")
    print(f"       投入 {args.mu:g} MU → 在場 {seconds:.1f} 秒")
    print(f"       冷卻 {cd:g} 秒{'（Lv5 −30%）' if sync >= 5 else ''}{'（超載 +50%）' if args.overcast else ''}｜死亡冷卻 {death}")
    tick = TICK[rarity] / n
    print(f"       負荷：持續時長每 {tick:.3g} 秒 +1" + (f"｜負荷鎖定 +{2 * (n - 1)}（常駐）" if n > 1 else "")
          + f"｜專注穩定度基礎 10{'，Lv5 +3' if sync >= 5 else ''}")


def cmd_mission(args, _cards):
    if args.n < 1 or args.n > 10:
        raise ArgError("--n 必須是 1–10")
    for _ in range(args.n):
        value = RNG.randint(1, 10)
        kind, template = MISSIONS[value - 1]
        print(f"[任務] 類型 1D10 → {value}｜{kind}")
        print(f"       範本：{template if template else '原文無範本，由范恩依劇情自訂'}")
        print("       任務卡欄位：目標＋地點／時限＋限制條件＋推薦稀有度＋推薦技能卡")


def cmd_list(args, cards):
    rows = [c for c in cards
            if (not args.faction or c["陣營"] == args.faction) and (not args.rarity or c["稀有度"] == args.rarity)]
    if not rows:
        raise ArgError("沒有符合條件的卡")
    for c in rows:
        print(f"{c['陣營']}｜{c['稀有度']}｜{c['技能名']}｜{c['召喚單位']}｜{c['類型']}｜{c['規模']}")
    print(f"共 {len(rows)} 張")


def cmd_rates(args, cards):
    pool = POOLS[resolve_pool(args.pool)]
    focus = split_list(args.focus)
    for f in focus:
        if f not in FACTIONS:
            raise ArgError(f"未知陣營「{f}」")
    allowed, total, thresholds = normalized_rates(pool["cap"])
    print(f"{pool['name']}：上限 {pool['cap']}｜單抽 {pool['single']} EP｜十連 {pool['ten']} EP")
    print("機率：" + "｜".join(f"{r} {BASE_RATES[r] * 100 / total:.2f}%" for r in allowed))
    print("1D10000 區間：" + " ".join(f"{r}≤{t}" for r, t in thresholds))
    if pool["pity"]:
        print("保底：" + "、".join(f"{k} {v} 抽" for k, v in pool["pity"].items()))
    faces = faction_faces(focus)
    print(f"陣營 1D{len(faces)}：" + " ".join(f"{i}={f}" for i, f in enumerate(faces, 1)))


def main(argv):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", "--help", action="store_true")
    sub = parser.add_subparsers(dest="cmd")
    p = sub.add_parser("pull")
    p.add_argument("pool")
    p.add_argument("--ten", action="store_true")
    p.add_argument("--focus")
    p.add_argument("--featured")
    p.add_argument("--pity")
    p.add_argument("--ep", type=int)
    p.add_argument("--json", action="store_true")
    p.add_argument("--legacy-death", action="store_true")
    d = sub.add_parser("dur")
    d.add_argument("--card")
    d.add_argument("--rarity")
    d.add_argument("--type")
    d.add_argument("--mu", type=float)
    d.add_argument("--channels", type=int, default=1)
    d.add_argument("--sync", type=int, default=0)
    d.add_argument("--no-type", action="store_true")
    d.add_argument("--overcast", action="store_true")
    d.add_argument("--mp-max", type=float)
    d.add_argument("--legacy-death", action="store_true")
    m = sub.add_parser("mission")
    m.add_argument("--n", type=int, default=1)
    li = sub.add_parser("list")
    li.add_argument("--faction")
    li.add_argument("--rarity")
    r = sub.add_parser("rates")
    r.add_argument("pool")
    r.add_argument("--focus")

    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv else 2
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("參數錯誤（整批未擲出），用 --help 查看用法", file=sys.stderr)
        return 2
    cards = load_cards()
    handler = {"pull": cmd_pull, "dur": cmd_dur, "mission": cmd_mission, "list": cmd_list, "rates": cmd_rates}
    try:
        handler[args.cmd](args, cards)
    except ArgError as e:
        print(f"參數錯誤（整批未擲出）：{e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
