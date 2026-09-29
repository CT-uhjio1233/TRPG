---
name: trpg-system-ironsworn
description: Ironsworn 鐵誓系列規則與世界素材——經典版 Ironsworn（鐵地 Ironlands 黑暗奇幻）、Delve 地城探索擴充、Starforged 太空科幻續作、Sundered Isles 海盜群島擴充。提供核心機制（行動擲骰 1d6＋屬性對兩顆 d10 挑戰骰、強成功／弱成功／失手、動能與燃燒動能、進度條與五級難度）、角色創建流程、全部招式中文摘要、資產清單、世界真相、敵人等級，以及以程式碼擲出的神諭表（scripts/oracle.py）。在 trpg-simulator 中使用者選擇 Ironsworn／Starforged／Sundered Isles／鐵誓，或要求單人神諭、誓言驅動的奇幻冒險時使用。
---

# Ironsworn 鐵誓系列

> 本 skill 是 `trpg-simulator` 的規則系統模組，供范恩的 `trpg-fane-rules`（規則）、`trpg-fane-storywriter`（世界與劇本）、`trpg-fane-visuals`（角色卡）引用。
> 所有擲骰與神諭一律以程式碼產生（P1）。本 skill 的術語不得以系統口吻出現在輸出文本，須由范恩以 GM 身分自然說明。

## 1. 系列總覽

| 產品 | 類型 | 本 skill 的資料 |
|------|------|----------------|
| **Ironsworn**（經典版） | 黑暗奇幻，舊世界難民在嚴酷的鐵地求生 | 規則書、Playkit、世界真相工作簿、資產全集 → 完整整理 |
| **Ironsworn: Delve** | 經典版擴充，地城／遺跡探索、威脅、稀有物 | 招式參考、免費預覽 → `references/delve.md` |
| **Ironsworn: Starforged** | 太空科幻續作，舞台為球狀星團「熔爐 The Forge」 | 規則與設定導讀（第一章）、資產表 → `references/starforged.md` |
| **Sundered Isles** | Starforged 擴充，海盜、帝國與詛咒群島 | 真相工作簿、Playkit、資產表、試閱 → `references/sundered-isles.md` |

三者共用同一套核心判定；差異在招式細節、狀態名稱與世界觀。開局時由范恩確認要玩哪一個。

## 2. 核心機制

### 2.1 行動擲骰（Action Roll）

**行動分數** ＝ 行動骰（1d6）＋屬性＋加值，**上限 10**。與兩顆**挑戰骰**（d10）比較：

| 結果 | 條件 | 意義 |
|------|------|------|
| **強成功 Strong Hit** | 行動分數**大於**兩顆挑戰骰 | 成功，通常還有額外好處 |
| **弱成功 Weak Hit** | 只大於其中一顆 | 成功但有代價、或效果打折 |
| **失手 Miss** | 兩顆都沒超過 | 失敗，通常要 *Pay the Price*（付出代價） |
| **對子 Match** | 兩顆挑戰骰點數相同 | 強成功＋對子＝意外的機會；失手＋對子＝事情急轉直下 |

**平手算挑戰骰贏。** 擲骰一律用 `trpg-fane-rules` 的腳本：

```bash
python3 <trpg-fane-rules 目錄>/scripts/roll.py "使用者-直面危險:1d6+2#is" "使用者-履行誓言:6#prog"
```

### 2.2 屬性（五項，開局分配 3、2、2、1、1）

| 屬性 | 代表 |
|------|------|
| **迅捷 Edge** | 速度、敏捷、遠程戰鬥 |
| **心志 Heart** | 勇氣、意志、同理、社交、忠誠 |
| **鋼鐵 Iron** | 力量、耐力、侵略性、近身戰鬥 |
| **暗影 Shadow** | 潛行、欺瞞、狡詐 |
| **機智 Wits** | 專業、知識、觀察 |

### 2.3 動能（Momentum）

- 範圍 −6 到 +10；開局 +2，**上限** 10、**重置值** +2。每個衰弱（debility）使上限 −1；有 1 個衰弱時重置值為 +1，2 個以上為 0。
- **燃燒動能：** 擲完行動骰後，若動能大於某顆挑戰骰，可取消該骰（視為被打敗），然後把動能設回重置值。**進度擲骰不能燃燒動能。**
- **負動能：** 動能為負時，若行動骰點數等於負動能的絕對值，行動骰視為 0。
- 動能已在 −6 又要再扣時，改做 *Face a Setback*（遭遇挫折）。
- 燃燒與否是**使用者的決定**，范恩只能提醒「你的動能可以燒」，不可代為決定。

### 2.4 狀態條與衰弱

- **生命 Health、精神 Spirit、補給 Supply**：各 0–5，開局都是 5。補給由同行隊伍共用。
- **衰弱 Debilities：**
  - 狀態（可清除）：負傷 Wounded、動搖 Shaken、準備不足 Unprepared、負重 Encumbered——負傷時不能回生命、動搖時不能回精神、準備不足時不能回補給
  - 禍根（永久）：殘缺 Maimed、墮落 Corrupted
  - 重擔（完成任務才能清除）：受詛 Cursed、受折磨 Tormented

### 2.5 進度條與難度

誓言、旅程、戰鬥都用 10 格進度條（每格 4 刻度）。難度決定每次標記的進度，也決定敵人的傷害：

| 難度 | 每次標記 | 敵人造成的傷害 | 履行誓言經驗（強成功／弱成功） |
|------|----------|----------------|-------------------------------|
| 麻煩 Troublesome | 3 格 | 1 | 1／0 |
| 危險 Dangerous | 2 格 | 2 | 2／1 |
| 艱鉅 Formidable | 1 格 | 3 | 3／2 |
| 極端 Extreme | 2 刻度 | 4 | 4／3 |
| 史詩 Epic | 1 刻度 | 5 | 5／4 |

**進度擲骰**（`#prog`）：以已填滿的格數為分數，對兩顆挑戰骰，不擲行動骰、不計動能。

### 2.6 傷害

致命武器（劍、斧、矛、弓）造成 2 點傷害；徒手或簡易武器（盾、棍、杖、石頭）造成 1 點。*Strike* 強成功再 +1。

## 3. 角色創建（經典版）

1. **確立世界真相：** 從 `references/ironlands-truths.md` 的 11 個類別各選一項（或擲 1d3、或自訂），順手記下吸引你的任務起點。
2. **構想角色：** 動機、專長、個性、弱點。名字可擲 `oracle.py name`。
3. **分配屬性：** 3、2、2、1、1 任意分配到五項屬性。
4. **設定狀態：** 生命 5、精神 5、補給 5、動能 +2（上限 10、重置 +2），衰弱全部未標記。
5. **選擇三項資產：** 從 `references/assets.md` 的夥伴、道途、戰鬥天賦、儀式中挑選（儀式通常需要劇情前提）。
6. **背景羈絆：** 最多三個，與人或社群締結，在羈絆進度條標記對應刻度。
7. **兩個誓言：** 長期的**背景誓言**（極端或史詩），以及必須立刻處理的**引發事件**；對引發事件執行 *Swear an Iron Vow*。
8. **裝備：** 一般裝備由補給涵蓋；只需記下主要武器（決定 1 或 2 點傷害）與具敘事意義的物品。

Starforged 與 Sundered Isles 的創建差異見各自的參考文件。角色卡依 `trpg-fane-visuals` 格式輸出，欄位改為：屬性、生命／精神／補給、動能（目前／上限／重置）、資產、誓言與進度、羈絆、衰弱、經驗。

## 4. 招式

全部經典版招式的中文摘要見 `references/moves.md`。最常用的：

| 情境 | 招式 |
|------|------|
| 冒險、面對迫近的威脅 | 直面危險 *Face Danger*（依做法選屬性） |
| 準備、評估、取得槓桿 | 取得優勢 *Secure an Advantage* |
| 調查、追蹤、詢問 | 蒐集情報 *Gather Information* |
| 說服、威脅、欺騙 | 說服 *Compel* |
| 旅行 | 踏上旅程 *Undertake a Journey* → 抵達目的地 *Reach Your Destination* |
| 戰鬥 | 投入戰局 → 打擊／交鋒 → 結束戰鬥 |
| 承受後果 | 承受傷害／承受壓力／付出代價 |
| 不確定時 | 詢問神諭 *Ask the Oracle* |

## 5. 神諭（以程式碼擲出）

Ironsworn 的神諭表是單人遊玩的靈感引擎。本 skill 附 `scripts/oracle.py`，一次呼叫擲完本回合所有查詢：

```bash
python3 <本 skill 目錄>/scripts/oracle.py action theme ask:likely 地點=location descriptor
python3 <本 skill 目錄>/scripts/oracle.py --list
```

| 用途 | 表 |
|------|------|
| 萬用靈感（行動＋主題） | `action` `theme` |
| 是非題 | `ask:certain`（11+）、`ask:likely`（26+）、`ask:5050`（51+）、`ask:unlikely`（76+）、`ask:small`（91+）；兩位數相同為**對子**，代表極端結果或轉折 |
| 地點 | `region` `location` `coastal` `descriptor` |
| 聚落 | `settlement-name` `quick-settlement` `trouble` |
| NPC | `role` `goal` `character` `name` |
| 後果 | `pay-the-price` `harm-at-0` `stress-at-0` |
| Delve | `delve-danger` `delve-danger-alt` `delve-opportunity` `delve-weak-edge／shadow／wits` `threat` |

**未收錄的表：** 規則書第 6 章的鐵地人名 B 表、精靈名、其他種族名、戰鬥行動、秘術反噬、重大劇情轉折、挑戰難度，在本次讀取的規則書文字中被截斷，沒有收錄。需要時先用 `action`＋`theme` 替代，或請使用者提供該頁內容，**不得憑記憶補寫**。

神諭結果是**靈感而非命令**。范恩依「最有趣也最合理」的方向詮釋，並以 GM 的口吻呈現（「我翻一下表……嗯，是『背叛』跟『家族』」），不要把表格輸出原封不動貼給使用者。

## 6. 由范恩主持 Ironsworn（引導模式 Guided Play）

Ironsworn 原生支援單人、合作與有引導者（GM）三種模式；在本模擬系統中一律採**引導模式**，由范恩擔任引導者，四位隊友是合作玩家。

- **誓言是故事的引擎：** 每位角色都有背景誓言與引發事件。`trpg-fane-storywriter` 的幕後大綱要以角色誓言為核心展開，而不是另起一條與誓言無關的主線。
- **先敘事，後招式：** 使用者描述行動 → 范恩判斷是否觸發招式、用哪個屬性（有歧義時可以問，屬提問白名單第 2 項）→ 擲骰 → 依結果敘事。安全、確定的行動不需要招式。
- **付出代價：** 失手時優先讓「最明顯的負面結果」發生；想不出來再擲 `pay-the-price`。
- **世界充滿惡意** 與 Ironsworn 的「失手必有代價」相容，但 Ironsworn 的主角被設定為**能幹的英雄**，失敗是推進故事的轉折，不是羞辱。
- **隊友的招式：** 隊友同樣做行動擲骰，並依各自人格選擇招式（小宇愛 *Gather Information*、阿凱愛 *Face Danger* 衝過去、小雅常 *Forge a Bond*、子豪常 *Aid Your Ally* 與 *Heal*）。
- **共用補給：** 同行者共用補給條，帳本（`trpg-fane-ledger`）只記一個數值。
- **敵人：** 參考 `references/foes.md` 設定難度；戰鬥採進度條，敵人不擲骰，攻擊由招式結果表現。

## 7. 參考文件

| 檔案 | 內容 |
|------|------|
| `references/moves.md` | 經典版全部招式中文摘要 |
| `references/assets.md` | 經典版資產清單與一句話說明 |
| `references/ironlands-truths.md` | 鐵地 11 類世界真相與任務起點 |
| `references/foes.md` | 敵人分類、難度與 NPC 組成要素 |
| `references/delve.md` | Delve：遺跡探索、失敗軌、威脅、稀有物 |
| `references/starforged.md` | Starforged：熔爐星團、影響、傳承軌、載具 |
| `references/sundered-isles.md` | Sundered Isles：11 類群島真相、招式分類、建議資產與派系 |
| `scripts/oracle.py` | 神諭批次擲骰 |

## 8. 授權與出處

Ironsworn、Ironsworn: Delve、Ironsworn: Starforged、Sundered Isles © Shawn Tomkin（ironswornrpg.com）。規則書文字以 CC BY-NC-SA 4.0 授權，其餘參考資料以 CC BY 4.0 授權。本 skill 的中文翻譯與整理為改作，以 **CC BY-NC-SA 4.0** 釋出。
