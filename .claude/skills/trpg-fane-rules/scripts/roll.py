#!/usr/bin/env python3
"""TRPG 批次擲骰工具（范恩．規則仲裁專用）

一次執行即完成本回合所有判定。任何骰式有誤時，整批都不會擲出，
以免「先擲一部分、修正後再擲」變相成為重擲。

用法：
  python3 roll.py "標籤:骰式" ["標籤:骰式" ...]

骰式語法：
  NdS            基本骰，例：1d100、3d6、d20（N 省略時為 1）
  d%             等同 1d100
  NdSkhK／klK    保留最高／最低 K 顆，例：4d6kh3
  +M／-M         修正值，可與多個骰項相加，例：1d8+2、2d6+1d4-1
  *N             整體乘以 N（CoC 屬性用），例：3d6*5、(2d6+6)*5
  1d20adv／dis   D&D 優勢／劣勢（等同 2d20kh1／2d20kl1）
  1d100bN／pN    CoC 7e 獎勵骰／懲罰骰 N 顆（十位數多擲 N 顆取優／取劣）

判定後綴（選用，接在骰式最後）：
  @技能值        CoC 7e 成功等級，例：1d100@65、1d100b1@40
  >=目標值       對 DC／AC 判定，例：1d20+5>=15
  #pbta          PbtA 2D6 結果帶，例：2d6+1#pbta

條件預擲：標籤前加 ?，例："?小宇-傷害:1d8+2"
  （條件未觸發時該數值作廢，不得挪用至其他判定）
"""

import random
import re
import sys
import unicodedata

RNG = random.SystemRandom()

MAX_DICE = 1000
MAX_SIDES = 10000

TERM_RE = re.compile(
    r"""
    (?P<dice>
        (?P<n>\d*)d(?P<sides>\d+|%)
        (?:
            (?P<keep>kh|kl)(?P<k>\d+)
          | (?P<adv>adv|dis)
          | (?P<bp>[bp])(?P<bpn>\d+)
        )?
    )
    | (?P<const>\d+)
    """,
    re.VERBOSE,
)


class DiceError(ValueError):
    pass


def display_width(text):
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)


def pad(text, width):
    return text + " " * max(0, width - display_width(text))


def parse_spec(spec):
    """把 '標籤:骰式' 拆成 (標籤, 條件預擲, 骰項清單, 乘數, 判定, 骰式)。"""
    spec = spec.strip()
    conditional = spec.startswith("?") or spec.startswith("？")
    if conditional:
        spec = spec[1:].strip()

    for sep in (":", "："):
        if sep in spec:
            label, expr = spec.rsplit(sep, 1)
            break
    else:
        label, expr = spec, spec
    label = label.strip() or expr.strip()
    expr = expr.strip().lower().replace(" ", "").replace("＋", "+").replace("－", "-")

    check = None
    m = re.search(r"(@(\d+)|>=(\d+)|#pbta)$", expr)
    if m:
        if m.group(2) is not None:
            check = ("coc", int(m.group(2)))
        elif m.group(3) is not None:
            check = ("dc", int(m.group(3)))
        else:
            check = ("pbta", None)
        expr = expr[: m.start()]

    multiplier = 1
    m = re.fullmatch(r"\((.+)\)[*x×](\d+)|(.+?)[*x×](\d+)", expr)
    if m:
        inner = m.group(1) if m.group(1) is not None else m.group(3)
        multiplier = int(m.group(2) or m.group(4))
        if m.group(3) is not None and re.search(r"[+-]", inner):
            raise DiceError(f"「{label}」有加減時請用括號標明乘法範圍，例：(2d6+6)*5")
        if multiplier < 1:
            raise DiceError(f"「{label}」乘數需大於 0")
        body_expr = inner
    else:
        body_expr = expr
    if not body_expr:
        raise DiceError(f"「{label}」沒有骰式")

    terms = []
    pos = 0
    sign = 1
    first = True
    while pos < len(body_expr):
        if not first:
            if body_expr[pos] not in "+-":
                raise DiceError(f"「{label}」的骰式無法解析：{expr}")
            sign = 1 if body_expr[pos] == "+" else -1
            pos += 1
        elif body_expr[pos] in "+-":
            sign = 1 if body_expr[pos] == "+" else -1
            pos += 1
        m = TERM_RE.match(body_expr, pos)
        if not m or m.end() == pos:
            raise DiceError(f"「{label}」的骰式無法解析：{expr}")
        terms.append((sign, build_term(label, m)))
        pos = m.end()
        first = False

    if not any(t["type"] == "dice" for _, t in terms):
        raise DiceError(f"「{label}」沒有任何骰子：{expr}")
    if check and check[0] == "coc":
        dice_terms = [t for _, t in terms if t["type"] == "dice"]
        if len(terms) != 1 or multiplier != 1 or dice_terms[0]["sides"] != 100 or dice_terms[0]["n"] != 1:
            raise DiceError(f"「{label}」：@技能值 判定只適用於單顆 1d100")
    return label.strip(), conditional, terms, multiplier, check, expr


def build_term(label, m):
    if m.group("const") is not None:
        return {"type": "const", "value": int(m.group("const"))}

    n = int(m.group("n")) if m.group("n") else 1
    sides = 100 if m.group("sides") == "%" else int(m.group("sides"))
    if n < 1 or n > MAX_DICE:
        raise DiceError(f"「{label}」骰數需介於 1–{MAX_DICE}")
    if sides < 2 or sides > MAX_SIDES:
        raise DiceError(f"「{label}」面數需介於 2–{MAX_SIDES}")

    term = {"type": "dice", "n": n, "sides": sides, "mode": None}
    if m.group("keep"):
        k = int(m.group("k"))
        if k < 1 or k > n:
            raise DiceError(f"「{label}」保留顆數需介於 1–{n}")
        term["mode"] = (m.group("keep"), k)
    elif m.group("adv"):
        if n != 1:
            raise DiceError(f"「{label}」優勢／劣勢請寫成 1d20adv／1d20dis")
        term["mode"] = (m.group("adv"), None)
    elif m.group("bp"):
        bpn = int(m.group("bpn"))
        if sides != 100 or n != 1:
            raise DiceError(f"「{label}」獎勵骰／懲罰骰只適用於 1d100")
        if bpn < 1 or bpn > 9:
            raise DiceError(f"「{label}」獎勵骰／懲罰骰顆數需介於 1–9")
        term["mode"] = (m.group("bp"), bpn)
    return term


def roll_term(term):
    """回傳 (小計, 顯示用明細)。"""
    if term["type"] == "const":
        return term["value"], str(term["value"])

    n, sides, mode = term["n"], term["sides"], term["mode"]

    if mode and mode[0] in ("b", "p"):
        units = RNG.randint(0, 9)
        tens = [RNG.randint(0, 9) for _ in range(1 + mode[1])]
        values = [(t * 10 + units) or 100 for t in tens]
        chosen = min(values) if mode[0] == "b" else max(values)
        kind = "獎勵骰" if mode[0] == "b" else "懲罰骰"
        tens_text = "／".join(f"{t * 10:02d}" for t in tens)
        return chosen, f"[十位 {tens_text}｜個位 {units}｜{kind}取 {chosen}]"

    if mode and mode[0] in ("adv", "dis"):
        rolls = [RNG.randint(1, sides) for _ in range(2)]
        chosen = max(rolls) if mode[0] == "adv" else min(rolls)
        kind = "優勢" if mode[0] == "adv" else "劣勢"
        return chosen, f"[{rolls[0]}, {rolls[1]}｜{kind}取 {chosen}]"

    rolls = [RNG.randint(1, sides) for _ in range(n)]
    if mode and mode[0] in ("kh", "kl"):
        k = mode[1]
        order = sorted(range(n), key=lambda i: rolls[i], reverse=(mode[0] == "kh"))
        kept = set(order[:k])
        shown = ", ".join(str(r) if i in kept else f"~{r}~" for i, r in enumerate(rolls))
        return sum(rolls[i] for i in kept), f"[{shown}]"

    return sum(rolls), f"[{', '.join(map(str, rolls))}]"


def natural_d20(parts):
    """骰項中恰有一顆有效的 d20（含優劣勢）時，回傳其天然骰值，供 DC 判定標註。"""
    dice = [(term, value) for _, term, value, _ in parts if term["type"] == "dice"]
    if len(dice) != 1:
        return None
    term, value = dice[0]
    if term["sides"] != 20:
        return None
    mode = term["mode"]
    if term["n"] == 1 or (mode and mode[0] in ("kh", "kl") and mode[1] == 1):
        return value
    return None


def pretty(expr):
    return re.sub(r"(\d*)d(\d+|%)", lambda m: f"{m.group(1)}D{m.group(2)}", expr)


def judge(check, total, nat):
    kind, target = check
    if kind == "coc":
        skill = target
        if total == 1:
            level = "大成功"
        elif (skill < 50 and total >= 96) or total == 100:
            level = "大失敗"
        elif total <= skill // 5:
            level = "極難成功"
        elif total <= skill // 2:
            level = "困難成功"
        elif total <= skill:
            level = "常規成功"
        else:
            level = "失敗"
        return f"技能 {skill}｜困難 {skill // 2}／極難 {skill // 5}｜{level}"
    if kind == "dc":
        result = "成功" if total >= target else "失敗"
        note = ""
        if nat == 20:
            note = "，天然 20"
        elif nat == 1:
            note = "，天然 1"
        return f"目標 {target}｜{result}{note}"
    if total <= 6:
        return "PbtA｜失敗"
    if total <= 9:
        return "PbtA｜部分成功"
    return "PbtA｜完全成功"


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv else 2

    try:
        parsed = [parse_spec(a) for a in argv]
    except DiceError as e:
        print(f"骰式錯誤（整批未擲出）：{e}", file=sys.stderr)
        return 2

    width = max(display_width(("(條件預擲) " if c else "") + label) for label, c, *_ in parsed)
    for label, conditional, terms, multiplier, check, expr in parsed:
        total = 0
        parts = []
        for sign, term in terms:
            value, detail = roll_term(term)
            total += sign * value
            parts.append((sign, term, value, detail))

        only = parts[0][1]
        if len(parts) == 1 and only["type"] == "dice" and only["n"] == 1 and not only["mode"]:
            body = str(total)
        elif len(parts) == 1 and only["type"] == "dice" and only["mode"] and only["mode"][0] in ("b", "p", "adv", "dis"):
            body = parts[0][3]
        else:
            shown = []
            for i, (sign, term, value, detail) in enumerate(parts):
                op = "" if i == 0 and sign > 0 else ("+ " if sign > 0 else "- ")
                shown.append(f"{op}{detail}")
            body = f"{' '.join(shown)} = {total}"
        if multiplier != 1:
            body = f"{body if body.startswith('[') or '=' in body else f'[{body}]'} ×{multiplier} = {total * multiplier}"
            total *= multiplier

        name = ("(條件預擲) " if conditional else "") + label
        line = f"[骰] {pad(name, width)} {pretty(expr)} → {body}"
        if check:
            line += f"（{judge(check, total, natural_d20(parts))}）"
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
