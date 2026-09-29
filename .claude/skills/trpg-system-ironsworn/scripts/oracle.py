#!/usr/bin/env python3
"""Ironsworn 神諭批次擲骰工具（范恩．Ironsworn 專用）

一次執行即完成本回合所有神諭查詢。任何參數有誤時，整批都不會擲出。

用法：
  python3 oracle.py 表名 [表名 ...]
  python3 oracle.py --list            列出所有表

特殊查詢：
  ask:機率      是非題。機率＝certain／likely／5050／unlikely／small
                （幾乎必然／可能／五五波／不太可能／機會渺茫），例：ask:likely
  表名*N        同一張表擲 N 次，例：descriptor*2
  標籤=表名     自訂顯示標籤，例：地點=location

資料來源：Ironsworn Rulebook、Playkit、Delve Moves Reference © Shawn Tomkin，
依 CC BY-NC-SA 4.0／CC BY 4.0 授權翻譯改作，譯文同樣以 CC BY-NC-SA 4.0 釋出。
"""

import random
import sys
import unicodedata

RNG = random.SystemRandom()


def seq(words):
    """把 100 個逐一編號的詞轉成 (lo, hi, 文字) 清單。"""
    return [(i + 1, i + 1, w) for i, w in enumerate(words)]


def pairs(words):
    """每兩個數字一格的 50 項表。"""
    return [(i * 2 + 1, i * 2 + 2, w) for i, w in enumerate(words)]


ACTION = seq("""密謀 Scheme|衝突 Clash|削弱 Weaken|發起 Initiate|創造 Create|立誓 Swear|復仇 Avenge|守衛 Guard|擊敗 Defeat|控制 Control|
打破 Break|冒險 Risk|投降 Surrender|檢視 Inspect|劫掠 Raid|躲避 Evade|突襲 Assault|轉移 Deflect|威脅 Threaten|攻擊 Attack|
離開 Leave|保存 Preserve|操弄 Manipulate|移除 Remove|消滅 Eliminate|撤退 Withdraw|拋棄 Abandon|調查 Investigate|堅守 Hold|專注 Focus|
揭開 Uncover|突破 Breach|援助 Aid|維護 Uphold|動搖 Falter|壓制 Suppress|獵捕 Hunt|分享 Share|摧毀 Destroy|迴避 Avoid|
駁斥 Reject|要求 Demand|探索 Explore|鞏固 Bolster|奪取 Seize|哀悼 Mourn|揭露 Reveal|聚集 Gather|違抗 Defy|轉變 Transform|
堅持 Persevere|服侍 Serve|開始 Begin|移動 Move|協調 Coordinate|抵抗 Resist|等待 Await|打動 Impress|拿取 Take|反對 Oppose|
捕獲 Capture|壓倒 Overwhelm|挑戰 Challenge|獲取 Acquire|保護 Protect|完成 Finish|強化 Strengthen|修復 Restore|推進 Advance|命令 Command|
回絕 Refuse|找到 Find|遞送 Deliver|隱藏 Hide|加固 Fortify|背叛 Betray|確保 Secure|抵達 Arrive|影響 Affect|改變 Change|
防禦 Defend|辯論 Debate|支持 Support|追隨 Follow|建造 Construct|定位 Locate|忍受 Endure|釋放 Release|失去 Lose|減少 Reduce|
升級 Escalate|分散注意 Distract|旅行 Journey|護送 Escort|學習 Learn|溝通 Communicate|啟程 Depart|搜尋 Search|衝鋒 Charge|召喚 Summon""".replace("\n", "").split("|"))

THEME = seq("""風險 Risk|能力 Ability|代價 Price|盟友 Ally|戰鬥 Battle|安全 Safety|生存 Survival|武器 Weapon|傷口 Wound|庇護所 Shelter|
領袖 Leader|恐懼 Fear|時間 Time|職責 Duty|秘密 Secret|純真 Innocence|名聲 Renown|方向 Direction|死亡 Death|榮譽 Honor|
勞動 Labor|解方 Solution|工具 Tool|平衡 Balance|愛 Love|屏障 Barrier|創造物 Creation|腐朽 Decay|貿易 Trade|羈絆 Bond|
希望 Hope|迷信 Superstition|和平 Peace|欺騙 Deception|歷史 History|世界 World|誓言 Vow|守護 Protection|自然 Nature|意見 Opinion|
負擔 Burden|仇怨 Vengeance|機會 Opportunity|派系 Faction|危險 Danger|腐化 Corruption|自由 Freedom|債務 Debt|仇恨 Hate|所有物 Possession|
陌生人 Stranger|通道 Passage|土地 Land|生物 Creature|疾病 Disease|優勢 Advantage|血 Blood|語言 Language|謠言 Rumor|弱點 Weakness|
貪婪 Greed|家族 Family|資源 Resource|建築 Structure|夢 Dream|社群 Community|戰爭 War|預兆 Portent|獎賞 Prize|命運 Destiny|
動能 Momentum|力量 Power|記憶 Memory|廢墟 Ruin|神秘學 Mysticism|對手 Rival|難題 Problem|點子 Idea|報復 Revenge|健康 Health|
同伴情誼 Fellowship|敵人 Enemy|宗教 Religion|靈魂 Spirit|聲望 Fame|荒蕪 Desolation|力氣 Strength|知識 Knowledge|真相 Truth|任務 Quest|
驕傲 Pride|失落 Loss|法律 Law|道路 Path|警告 Warning|關係 Relationship|財富 Wealth|家 Home|策略 Strategy|補給 Supply""".replace("\n", "").split("|"))

REGION = [(1, 12, "屏障群島 Barrier Islands"), (13, 24, "崎嶇海岸 Ragged Coast"), (25, 34, "深野 Deep Wilds"),
          (35, 46, "氾濫之地 Flooded Lands"), (47, 60, "避風地 Havens"), (61, 72, "腹地 Hinterlands"),
          (73, 84, "風暴丘陵 Tempest Hills"), (85, 94, "霧罩山脈 Veiled Mountains"),
          (95, 99, "破碎荒原 Shattered Wastes"), (100, 100, "他處 Elsewhere")]

LOCATION = seq("""藏身處 Hideout|廢墟 Ruin|礦坑 Mine|荒地 Waste|神秘之地 Mystical Site|小徑 Path|前哨 Outpost|牆 Wall|戰場 Battlefield|陋屋 Hovel|
泉水 Spring|巢穴 Lair|堡壘 Fort|橋 Bridge|營地 Camp|石塚／墳墓 Cairn/Grave""".replace("\n", "").split("|")) + [
    (lo, lo + 1, w) for lo, w in zip(range(17, 73, 2), """商隊 Caravan|瀑布 Waterfall|洞穴 Cave|沼澤 Swamp|泥沼 Fen|峽谷 Ravine|道路 Road|樹 Tree|
池塘 Pond|田野 Fields|濕地 Marsh|農莊 Steading|急流 Rapids|隘口 Pass|山徑 Trail|林間空地 Glade|平原 Plain|山脊 Ridge|懸崖 Cliff|
樹叢 Grove|村莊 Village|荒野 Moor|灌木叢 Thicket|河流淺灘 River Ford|山谷 Valley|海灣／峽灣 Bay/Fjord|山麓 Foothills|湖 Lake""".replace("\n", "").split("|"))
] + [(73, 75, "河 River"), (76, 79, "森林 Forest"), (80, 83, "海岸 Coast"), (84, 88, "丘陵 Hill"),
     (89, 93, "山 Mountain"), (94, 99, "樹林 Woods"), (100, 100, "異常 Anomaly")]

COASTAL = [(1, 1, "船隊 Fleet"), (2, 2, "馬尾藻海 Sargassum"), (3, 3, "漂流物 Flotsam"), (4, 4, "神秘之地 Mystical Site"),
           (5, 5, "巢穴 Lair"), (6, 10, "沉船 Wreck"), (11, 15, "港口 Harbor"), (16, 23, "船 Ship"), (24, 30, "礁石 Rocks"),
           (31, 38, "峽灣 Fjord"), (39, 46, "河口 Estuary"), (47, 54, "小海灣 Cove"), (55, 62, "海灣 Bay"),
           (63, 70, "浮冰 Ice"), (71, 85, "島嶼 Island"), (86, 99, "開闊水域 Open Water"), (100, 100, "異常 Anomaly")]

DESCRIPTOR = pairs("""高聳 High|偏遠 Remote|暴露 Exposed|狹小 Small|殘破 Broken|多樣 Diverse|崎嶇 Rough|黑暗 Dark|陰影籠罩 Shadowy|爭奪中 Contested|
陰森 Grim|蠻荒 Wild|肥沃 Fertile|受阻 Blocked|古老 Ancient|險惡 Perilous|隱密 Hidden|被佔據 Occupied|富饒 Rich|巨大 Big|
野蠻 Savage|有防守 Defended|枯萎 Withered|神秘 Mystical|難以抵達 Inaccessible|受保護 Protected|廢棄 Abandoned|寬廣 Wide|汙穢 Foul|死寂 Dead|
毀壞 Ruined|貧瘠 Barren|寒冷 Cold|荒疫 Blighted|低窪 Low|美麗 Beautiful|豐饒 Abundant|蒼翠 Lush|淹水 Flooded|空蕩 Empty|
詭異 Strange|腐化 Corrupted|寧靜 Peaceful|被遺忘 Forgotten|遼闊 Expansive|有人定居 Settled|茂密 Dense|開化 Civilized|荒涼 Desolate|孤立 Isolated""".replace("\n", "").split("|"))

TROUBLE = pairs("""排斥外人 Outsiders rejected|危險的發現 Dangerous discovery|可怕的徵兆 Dreadful omens|天災 Natural disaster|舊傷重揭 Old wounds reopened|
重要物品遺失 Important object is lost|有人被擄 Someone is captured|神秘現象 Mysterious phenomenon|反抗領袖 Revolt against a leader|懷恨的放逐者 Vengeful outcast|
敵對聚落 Rival settlement|自然反撲 Nature strikes back|有人失蹤 Someone is missing|生產停擺 Production halts|離奇命案 Mysterious murders|
債務到期 Debt comes due|不公的領導 Unjust leadership|災難性意外 Disastrous accident|與敵勾結 In league with the enemy|掠奪者欺凌弱小 Raiders prey on the weak|
受詛咒的過去 Cursed past|無辜者被控 An innocent is accused|遭黑暗魔法腐化 Corrupted by dark magic|惡劣天候造成孤立 Isolated by brutal weather|糧秣短缺 Provisions are scarce|
疫病蔓延 Sickness run amok|盟友反目 Allies become enemies|攻擊迫在眉睫 Attack is imminent|商隊失蹤 Lost caravan|黑暗秘密曝光 Dark secret revealed|
緊急遠征 Urgent expedition|領袖倒下 A leader falls|家族紛爭 Families in conflict|無能的領導 Incompetent leadership|魯莽好戰 Reckless warmongering|
野獸狩獵中 Beast on the hunt|內部背叛 Betrayed from within|停戰破裂 Broken truce|憤怒的怨靈 Wrathful haunt|與初生族衝突 Conflict with firstborn|
商路受阻 Trade route blocked|捲入交火 In the crossfire|陌生人引發不和 Stranger causes discord|重要活動受威脅 Important event threatened|危險的傳統 Dangerous tradition""".replace("\n", "").split("|")) + [
    (91, 100, "@TWICE 擲兩次 Roll twice")]

ROLE = [(1, 2, "罪犯 Criminal"), (3, 4, "醫者 Healer"), (5, 6, "盜匪 Bandit")] + [
    (lo, lo + 2, w) for lo, w in zip(range(7, 55, 3), """嚮導 Guide|表演者 Performer|礦工 Miner|傭兵 Mercenary|放逐者 Outcast|流浪者 Vagrant|
林務人 Forester|旅人 Traveler|秘術師 Mystic|祭司 Priest|水手 Sailor|朝聖者 Pilgrim|竊賊 Thief|冒險者 Adventurer|採集者 Forager|領袖 Leader""".replace("\n", "").split("|"))
] + [(55, 58, "守衛 Guard"), (59, 62, "工匠 Artisan"), (63, 66, "斥候 Scout"), (67, 70, "牧人 Herder"),
     (71, 74, "漁人 Fisher"), (75, 79, "戰士 Warrior"), (80, 84, "獵人 Hunter"), (85, 89, "掠奪者 Raider"),
     (90, 94, "商人 Trader"), (95, 99, "農人 Farmer"), (100, 100, "特殊身分 Unusual role")]

GOAL = [(lo, lo + 2, w) for lo, w in zip(range(1, 91, 3), """取得物品 Obtain an object|達成協議 Make an agreement|建立關係 Build a relationship|
破壞關係 Undermine a relationship|追尋真相 Seek a truth|償還債務 Pay a debt|駁斥謊言 Refute a falsehood|傷害對手 Harm a rival|治癒病痛 Cure an ill|
尋找某人 Find a person|尋找歸宿 Find a home|奪取權力 Seize power|修復關係 Restore a relationship|製作物品 Create an item|前往某地 Travel to a place|
取得補給 Secure provisions|反抗權勢 Rebel against power|討債 Collect a debt|守護秘密 Protect a secret|傳播信仰 Spread faith|自肥 Enrich themselves|
保護某人 Protect a person|維持現狀 Protect the status quo|提升地位 Advance status|守衛某地 Defend a place|為冤屈復仇 Avenge a wrong|履行職責 Fulfill a duty|
獲取知識 Gain knowledge|證明自己 Prove worthiness|尋求救贖 Find redemption""".replace("\n", "").split("|"))] + [
    (91, 92, "逃離某事 Escape from something"), (93, 95, "化解爭端 Resolve a dispute"), (96, 100, "@TWICE 擲兩次 Roll twice")]

CHAR_DESCRIPTOR = seq("""堅忍 Stoic|迷人 Attractive|被動 Passive|冷淡 Aloof|深情 Affectionate|慷慨 Generous|自鳴得意 Smug|武裝 Armed|聰明 Clever|勇敢 Brave|
醜陋 Ugly|善交際 Sociable|注定毀滅 Doomed|人脈廣 Connected|大膽 Bold|嫉妒 Jealous|憤怒 Angry|積極 Active|多疑 Suspicious|敵意 Hostile|
鐵石心腸 Hardhearted|功成名就 Successful|有天賦 Talented|老練 Experienced|狡詐 Deceitful|野心勃勃 Ambitious|好鬥 Aggressive|自負 Conceited|驕傲 Proud|嚴厲 Stern|
依賴 Dependent|警覺 Wary|強壯 Strong|有洞察力 Insightful|危險 Dangerous|古怪 Quirky|開朗 Cheery|毀容 Disfigured|偏狹 Intolerant|熟練 Skilled|
吝嗇 Stingy|膽小 Timid|遲鈍 Insensitive|狂野 Wild|憤世 Bitter|狡猾 Cunning|懊悔 Remorseful|善良 Kind|有魅力 Charming|渾然不覺 Oblivious|
挑剔 Critical|謹慎 Cautious|足智多謀 Resourceful|疲憊 Weary|負傷 Wounded|焦慮 Anxious|有權勢 Powerful|矯健 Athletic|執著 Driven|殘酷 Cruel|
安靜 Quiet|誠實 Honest|惡名昭彰 Infamous|垂死 Dying|隱居 Reclusive|有藝術氣息 Artistic|身障 Disabled|困惑 Confused|善於操弄 Manipulative|從容 Relaxed|
鬼祟 Stealthy|自信 Confident|虛弱 Weak|友善 Friendly|睿智 Wise|有影響力 Influential|年輕 Young|愛冒險 Adventurous|受壓迫 Oppressed|記仇 Vengeful|
合作 Cooperative|披甲 Armored|冷漠 Apathetic|堅決 Determined|忠誠 Loyal|生病 Sick|虔誠 Religious|自私 Selfish|年老 Old|狂熱 Fervent|
暴力 Violent|隨和 Agreeable|暴躁 Hot-tempered|固執 Stubborn|無能 Incompetent|貪心 Greedy|懦弱 Cowardly|著魔 Obsessed|粗心 Careless|鐵誓者 Ironsworn""".replace("\n", "").split("|"))

NAMES = seq("""Solana|Keelan|Cadigan|Sola|Kodroth|Kione|Katja|Tio|Artiga|Eos|Bastien|Elli|Maura|Haleema|Abella|Morter|Wulan|Mai|Farina|Pearce|
Wynne|Haf|Aeddon|Khinara|Milla|Nakata|Kynan|Kiah|Jaggar|Beca|Ikram|Melia|Sidan|Deshi|Tessa|Sibila|Morien|Mona|Padma|Avella|
Naila|Lio|Cera|Ithela|Zhan|Kaivan|Valeri|Hirsham|Pemba|Edda|Lestara|Lago|Elstan|Saskia|Kabeera|Caldas|Nisus|Serene|Chenda|Themon|
Erin|Alban|Parcell|Jelma|Willa|Nadira|Gwen|Amara|Masias|Kanno|Razeena|Mira|Perella|Myrick|Qamar|Kormak|Zura|Zanita|Brynn|Tegan|
Pendry|Quinn|Fanir|Glain|Emelyn|Kendi|Althus|Leela|Ishana|Flint|Delkash|Nia|Nan|Keeara|Katania|Morell|Temir|Bas|Sabine|Tallus""".replace("\n", "").split("|"))

PREFIX = [(i * 4 + 1, i * 4 + 4, w) for i, w in enumerate(
    "Bleak 荒涼|Green 翠綠|Wolf 狼|Raven 渡鴉|Gray 灰|Red 赤|Axe 斧|Great 大|Wood 林|Low 低|White 白|Storm 風暴|Black 黑|"
    "Mourn 哀悼|New 新|Stone 石|Grim 冷峻|Lost 失落|High 高|Rock 岩|Shield 盾|Sword 劍|Frost 霜|Thorn 荊棘|Long 長".split("|"))]
SUFFIX = [(i * 4 + 1, i * 4 + 4, w) for i, w in enumerate(
    "moor 沼|ford 渡|crag 崖|watch 哨|hope 望|wood 林|ridge 嶺|stone 石|haven 港|fall(s) 瀑|river 河|field 田|hill 丘|"
    "bridge 橋|mark 界|cairn 塚|land 地|hall 廳|mount 山|rock 岩|brook 溪|barrow 墓丘|stead 莊|home 家|wick 村".split("|"))]

SETTLEMENT_NAME = [
    (1, 15, "地貌特徵 A feature of the landscape（例：Highmount、Brackwater、Frostwood、Three Rivers）"),
    (16, 30, "人造建物 A manmade edifice（例：Whitebridge、Lonefort、Darkwell、Stonetower）"),
    (31, 45, "生物圖騰 A creature（例：Ravencliff、Bearmark、Wolfcrag、Wyvern's Rest）"),
    (46, 60, "歷史事件 A historical event（例：Swordbreak、Fool's Fall、Olgar's Stand、Lastmarch）"),
    (61, 75, "舊世界語言的詞 A word in an Old World language（例：Abon、Kazeera、Khazu、Sova）"),
    (76, 90, "季節或環境 A season or environmental aspect（例：Winterhome、Windhaven、Stormrest、Summersong）"),
    (91, 100, "其他 Something else：貿易品、舊世界城市、創建者、神祇、歷史物件、初生族、精靈語、神話、正面詞、負面詞"),
]

PAY_THE_PRICE = [
    (1, 2, "再擲一次並讓結果更糟；若又擲到此項，構想一件改變任務走向的可怕事件並讓它發生 Roll again and make it worse"),
    (3, 5, "你信任的人或社群對你失去信心，或採取不利於你的行動"),
    (6, 9, "你在乎的人或社群陷入危險"),
    (10, 16, "你與某物或某人分離"),
    (17, 23, "你的行動產生了意料之外的效果"),
    (24, 32, "有價值之物遺失或被毀"),
    (33, 41, "眼前的情況惡化"),
    (42, 50, "新的危險或敵人現身"),
    (51, 59, "造成延誤，或讓你陷入劣勢"),
    (60, 68, "它造成傷害（Endure Harm）"),
    (69, 76, "它造成壓力（Endure Stress）"),
    (77, 85, "出乎意料的發展讓任務更複雜"),
    (86, 90, "它浪費資源"),
    (91, 94, "它迫使你違背自己的本意行事"),
    (95, 98, "朋友、夥伴或盟友陷入險境（若你獨行，則是你自己）"),
    (99, 100, "@TWICE 再擲兩次，兩個結果都發生；若相同，讓它更糟"),
]

HARM_AT_ZERO = [
    (1, 10, "致命傷。進行 Face Death"),
    (11, 20, "瀕死。一兩個小時內必須 Heal，否則 Face Death"),
    (21, 35, "失去意識、無法行動。若無人打擾，一兩個小時後醒來；若落入不留情的敵人手中，Face Death"),
    (36, 50, "搖搖欲墜、勉強保持清醒。若未先喘息幾分鐘就進行劇烈活動，先再擲一次本表"),
    (51, 100, "遍體鱗傷，但仍站著"),
]

STRESS_AT_ZERO = [
    (1, 10, "被徹底壓垮。進行 Face Desolation"),
    (11, 25, "放棄了。Forsake Your Vow（盡可能選與當前危機相關的誓言）"),
    (26, 50, "屈服於恐懼或衝動，做出違背理智的事"),
    (51, 100, "你撐了下來"),
]

DELVE_DANGER = [
    (1, 30, "查看主題（Theme）卡"), (31, 45, "查看領域（Domain）卡"), (46, 57, "遭遇敵對的棲居者"),
    (58, 68, "環境或建築上的危害"), (69, 76, "一項發現讓任務受挫或更複雜"), (77, 79, "令人毛骨悚然的情境或感受"),
    (80, 82, "先前的選擇或做法帶來後果"), (83, 85, "去路被阻或設有陷阱"), (86, 88, "資源減少、損壞或遺失"),
    (89, 91, "令人困惑的謎團或艱難抉擇"), (92, 94, "迷路或延誤"), (95, 100, "@TWICE 再擲兩次，兩者皆發生；若相同，讓它更糟"),
]

DELVE_DANGER_ALT = [
    (1, 22, "遭遇敵對的棲居者"), (23, 42, "環境或建築上的危害"), (43, 58, "一項發現讓任務受挫或更複雜"),
    (59, 64, "令人毛骨悚然的情境或感受"), (65, 70, "先前的選擇或做法帶來後果"), (71, 76, "去路被阻或設有陷阱"),
    (77, 82, "資源減少、損壞或遺失"), (83, 88, "令人困惑的謎團或艱難抉擇"), (89, 94, "迷路或延誤"),
    (95, 100, "@TWICE 再擲兩次，兩者皆發生；若相同，讓它更糟"),
]

DELVE_OPPORTUNITY = [
    (1, 25, "地形對你有利，或發現隱藏的通道"), (26, 45, "揭露此地歷史或本質的一個面向"), (46, 57, "找到一處安全區域"),
    (58, 68, "一條線索提供洞見或方向"), (69, 78, "你搶先一步察覺某個棲居者"), (79, 86, "此區可以搜刮、採集或狩獵"),
    (87, 90, "找到有趣或有用的物品"), (91, 94, "你警覺到潛在威脅"), (95, 98, "遇到可能支持你的棲居者"),
    (99, 100, "遇到需要幫助的棲居者"),
]

THREAT = [
    (1, 30, "威脅準備下一步，或新的危險逼近（若你有機會阻止並成功，Reach a Milestone；否則標記威脅值 menace）"),
    (31, 70, "威脅暗中推進目標，或危險升級。標記 menace"),
    (71, 100, "威脅採取戲劇性的立即行動，或重大事件揭露新的複雜情勢。標記 menace 兩次"),
]

def delve_weak(bounds):
    texts = ["標記進度並 Reveal a Danger", "標記進度", "選一：標記進度，或 Find an Opportunity",
             "兩者皆得：標記進度並 Find an Opportunity", "標記進度兩次並 Reveal a Danger"]
    rows, lo = [], 1
    for hi, text in zip(bounds, texts):
        rows.append((lo, hi, text))
        lo = hi + 1
    return rows


DELVE_WEAK_EDGE = delve_weak([45, 65, 75, 80, 100])
DELVE_WEAK_SHADOW = delve_weak([30, 65, 90, 99, 100])
DELVE_WEAK_WITS = delve_weak([40, 55, 80, 99, 100])

TABLES = {
    "action": ("行動 Action", ACTION),
    "theme": ("主題 Theme", THEME),
    "region": ("區域 Region", REGION),
    "location": ("地點 Location", LOCATION),
    "coastal": ("沿海地點 Coastal Waters Location", COASTAL),
    "descriptor": ("地點描述 Location Descriptor", DESCRIPTOR),
    "settlement-name": ("聚落命名方式 Settlement Name", SETTLEMENT_NAME),
    "quick-settlement": ("快速聚落名 Quick Settlement Name", None),
    "trouble": ("聚落麻煩 Settlement Trouble", TROUBLE),
    "role": ("角色身分 Character Role", ROLE),
    "goal": ("角色目標 Character Goal", GOAL),
    "character": ("角色描述 Character Descriptor", CHAR_DESCRIPTOR),
    "name": ("鐵地人名 Ironlander Names（A 表）", NAMES),
    "pay-the-price": ("付出代價 Pay the Price", PAY_THE_PRICE),
    "harm-at-0": ("生命值 0 時的 Endure Harm 失手表", HARM_AT_ZERO),
    "stress-at-0": ("精神值 0 時的 Endure Stress 失手表", STRESS_AT_ZERO),
    "delve-danger": ("Delve 揭示危險 Reveal a Danger", DELVE_DANGER),
    "delve-danger-alt": ("Delve 揭示危險（無主題／領域卡版）", DELVE_DANGER_ALT),
    "delve-opportunity": ("Delve 發現機會 Find an Opportunity", DELVE_OPPORTUNITY),
    "delve-weak-edge": ("Delve 深入遺跡弱成功（迅捷）", DELVE_WEAK_EDGE),
    "delve-weak-shadow": ("Delve 深入遺跡弱成功（暗影）", DELVE_WEAK_SHADOW),
    "delve-weak-wits": ("Delve 深入遺跡弱成功（機智）", DELVE_WEAK_WITS),
    "threat": ("Delve 推進威脅 Advance a Threat", THREAT),
}

ODDS = {
    "certain": ("幾乎必然 Almost Certain", 11),
    "likely": ("可能 Likely", 26),
    "5050": ("五五波 50/50", 51),
    "unlikely": ("不太可能 Unlikely", 76),
    "small": ("機會渺茫 Small Chance", 91),
}


def display_width(text):
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)


def pad(text, width):
    return text + " " * max(0, width - display_width(text))


def is_match(value):
    return value == 100 or value % 11 == 0


def lookup(table, value):
    for lo, hi, text in table:
        if lo <= value <= hi:
            return text
    raise ValueError(f"表格缺少 {value}")


def fmt(value):
    return "00" if value == 100 else f"{value:02d}"


def roll_table(key, depth=0):
    """回傳 [(骰值, 文字)]；遇到「擲兩次」會自動再擲兩次。"""
    if key == "quick-settlement":
        a, b = RNG.randint(1, 100), RNG.randint(1, 100)
        pre, suf = lookup(PREFIX, a).split(" "), lookup(SUFFIX, b).split(" ")
        return [(a, f"{pre[0]}{suf[0]}（{pre[1]}{suf[1]}）｜字尾骰 {fmt(b)}")]
    table = TABLES[key][1]
    value = RNG.randint(1, 100)
    text = lookup(table, value)
    if text.startswith("@TWICE"):
        results = [(value, text.replace("@TWICE ", ""))]
        if depth < 2:
            for _ in range(2):
                results += [(v, "  ↳ " + t) for v, t in roll_table(key, depth + 1)]
        return results
    return [(value, text)]


def parse(arg):
    label, spec = (arg.split("=", 1) if "=" in arg else (None, arg))
    times = 1
    if "*" in spec:
        spec, n = spec.rsplit("*", 1)
        if not n.isdigit() or not 1 <= int(n) <= 10:
            raise ValueError(f"「{arg}」次數需介於 1–10")
        times = int(n)
    spec = spec.strip().lower()
    if spec.startswith("ask:"):
        odds = spec[4:]
        if odds not in ODDS:
            raise ValueError(f"「{arg}」機率請用：{', '.join(ODDS)}")
        return (label or f"是非題（{ODDS[odds][0]}）", "ask", odds, times)
    if spec not in TABLES:
        raise ValueError(f"找不到表「{spec}」，可用 --list 查看")
    return (label or TABLES[spec][0], "table", spec, times)


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv else 2
    if argv[0] == "--list":
        for key, (name, _) in TABLES.items():
            print(f"{pad(key, 20)} {name}")
        for key, (name, threshold) in ODDS.items():
            print(f"{pad('ask:' + key, 20)} 是非題：{name}（{threshold} 以上為「是」）")
        return 0
    try:
        plan = [parse(a) for a in argv]
    except ValueError as e:
        print(f"參數錯誤（整批未擲出）：{e}", file=sys.stderr)
        return 2

    width = max(display_width(p[0]) for p in plan)
    for label, kind, key, times in plan:
        for _ in range(times):
            if kind == "ask":
                name, threshold = ODDS[key]
                value = RNG.randint(1, 100)
                answer = "是" if value >= threshold else "否"
                twist = "，對子（極端結果或轉折）" if is_match(value) else ""
                print(f"[神諭] {pad(label, width)} 1D100 → {fmt(value)}（{threshold} 以上為是｜{answer}{twist}）")
                continue
            for i, (value, text) in enumerate(roll_table(key)):
                head = f"[神諭] {pad(label, width)} 1D100 → {fmt(value)}" if i == 0 else f"       {pad('', width)}        {fmt(value)}"
                print(f"{head}｜{text}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
