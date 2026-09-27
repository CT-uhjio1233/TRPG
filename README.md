# 「虛擬實境級」線下 TRPG 社交模擬系統｜Skills 版

把《「虛擬實境級」線下 TRPG 社交模擬系統 v7》系統提示詞（原文保存在 [`docs/TRPG-social-simulator-v7.md`](docs/TRPG-social-simulator-v7.md)）拆解成一組 Claude Skills：

- 每位虛擬隊友各一個 skill
- 范恩（GM）拆成十個職能 skill
- 一個總控 skill 負責調度

## 結構

```
.claude/skills/
├── trpg-simulator/            總控：核心速查卡、裁決優先序、回合輸出協議、語言規範、紅線（入口）
│
├── trpg-fane-persona/         范恩｜人格：身分、認知邊界、場外人格、發言額度
├── trpg-fane-storywriter/     范恩｜編劇：撰寫故事劇情、勢力與背叛、幕後大綱
│   └── references/outline-template.md
├── trpg-fane-rules/           范恩｜規則：審定規則、亂數協議、群體戰鬥
│   ├── scripts/roll.py        批次擲骰腳本
│   └── references/horde-combat.md
├── trpg-fane-narrator/        范恩｜說書：把故事說好、提升帶入感、擲骰儀式感
├── trpg-fane-ambience/        范恩｜感官：桌遊吧基準線、張力—感官共振表
├── trpg-fane-pacing/          范恩｜節奏：張力判定、篇幅、壓力—釋放循環、強制轉場
├── trpg-fane-ledger/          范恩｜帳本：狀態帳本、反幻覺、資訊隔離
│   └── references/ledger-template.md
├── trpg-fane-visuals/         范恩｜圖像：ASCII 地圖、情報道具、角色卡
├── trpg-fane-session/         范恩｜場務：開局、Meta 指令、安全閥、中場休息、收工存檔
├── trpg-fane-crisis/          范恩｜危機：心智崩潰、角色死亡與接續
│
├── trpg-party/                隊友共同協議：自主行動、自主權邊界、耳語、情緒傳染、人際關係
├── trpg-xiaoyu/               🎯 小宇（戰術家）
├── trpg-akai/                 🎉 阿凱（社交家）
├── trpg-xiaoya/               🎭 小雅（演員）
└── trpg-zihao/                🛡️ 子豪（輔助者）
```

## 使用方式

**Claude Code（本 repo 內）**：skills 放在 `.claude/skills/`，開啟本專案即自動載入。輸入 `/trpg-simulator`，或直接說「范恩，開團吧」。擲骰需要 `python3`。

**Claude Code（任何專案都能用）**：把 `.claude/skills/` 底下的所有資料夾複製到 `~/.claude/skills/`。

**Claude.ai**：把每個 skill 資料夾各自壓成 zip，在 Skills 設定中上傳，並開啟程式碼執行功能。

## 原文章節 → Skill 對照

| 原文章節 | 所在 skill |
|----------|-----------|
| 卷首 A–D（身分、每回合必做、五條紅線、裁決優先序） | `trpg-simulator` |
| §1.1 四大後台職能、§1.2 三層架構 | `trpg-simulator`（配比表在 `trpg-fane-pacing`） |
| §1.3 絕對敘事基調、清晰度 vs 不可名狀 | `trpg-fane-narrator` |
| §2 范恩 | `trpg-fane-persona`（IC 細節在 `trpg-fane-narrator`） |
| §3 環境與感官系統 | `trpg-fane-ambience` |
| §4.1、§4.3–4.7 隊友共同協議 | `trpg-party` |
| §4.2 四大社交原型設定卡 | `trpg-xiaoyu`、`trpg-akai`、`trpg-xiaoya`、`trpg-zihao` |
| §5.1–5.2 規則適配與亂數協議 | `trpg-fane-rules` |
| §5.3 擲骰儀式感 | `trpg-fane-narrator` |
| §5.4 心智崩潰、§5.5 角色死亡 | `trpg-fane-crisis` |
| §6.1–6.3 回合輸出協議、提問白名單 | `trpg-simulator` |
| §6.4–6.6 長度、節奏、自發互動 | `trpg-fane-pacing` |
| §7 文字圖像化、§8.2 角色卡 | `trpg-fane-visuals` |
| §8.1 開局流程 | `trpg-fane-session`（定場在 `trpg-fane-narrator`） |
| §8.3–8.4 劇本生成、幕後大綱 | `trpg-fane-storywriter` |
| §9.1–9.2 狀態帳本、反幻覺 | `trpg-fane-ledger` |
| §9.3 規則嚴格性 | `trpg-fane-rules` |
| §9.4 人格一致性 | `trpg-party` 與各角色 skill |
| §9.5 語言規範、第拾壹章 紅線清單 | `trpg-simulator` |
| §10 場外管理與跨場次 | `trpg-fane-session` |
| 附錄 A 代理人速查表 | `trpg-party`、`trpg-fane-persona` |
| 附錄 B 張力節奏循環圖 | `trpg-fane-pacing` |
| 附錄 C 群體戰鬥模組 | `trpg-fane-rules/references/horde-combat.md` |

## 轉換時修正的原文問題

1. **「每回合必做的六件事」實際列了七項**：改為七件事。第 6 項「收尾不提問」與第 7 項「補上三個行動選項」的調和方式：先以懸念收尾，再另起區塊用陳述句列出選項，不寫成問句。
2. **提問白名單寫「五種情境」，實際列了六種**：改為六種。
3. **工具失效退路的台詞寫成「小凱」**：改為阿凱。
4. **附錄 C 的 `2d6**` 格式錯誤**：修正為 `2d6`。原文沒有說明 `1d4+1` 與 `2d6` 怎麼選，改為由 GM 依武器威力裁量並公開說明理由（依 §9.3）。
5. **附錄 B 的程式碼區塊沒有關閉**：已修正。
6. **章節交叉引用（§x.x）**：改為指向對應的 skill 名稱。

## 原文沒有、轉換時補上的內容

- `trpg-fane-rules/scripts/roll.py`：依亂數協議實作的批次擲骰腳本。
  - 一次呼叫擲完整回合，骰式有誤時整批不擲
  - 支援 CoC 獎勵骰／懲罰骰與成功等級、D&D 優劣勢與 DC、PbtA 結果帶、條件預擲、`3d6*5` 屬性擲骰
- 模板：幕後大綱（`trpg-fane-storywriter/references/outline-template.md`）、狀態帳本（`trpg-fane-ledger/references/ledger-template.md`）、`/收工` 存檔摘要格式（`trpg-fane-session`）。
- 語氣參考：
  - 每位隊友與范恩的示範台詞，皆依原文的語言指紋撰寫
  - 各角色在大成功、大失敗、心智崩潰等時刻的反應表
- 延伸設定（依原文推演，皆已註明）：
  - 隊友人際關係矩陣
  - 說書 skill 的「讓玩家身在其中的寫法」與 NPC 聲線區辨表
  - 文字對話中「靜默超時」的判讀方式
