import { useState } from "react";

const characters = [
  {
    id: 1,
    name: "林書硯",
    player: "你",
    occupation: "記者（《海港晨報》社會線）",
    age: 28,
    gender: "男",
    highlight: true,
    stats: {
      STR: 50, CON: 55, SIZ: 60, DEX: 65, APP: 70,
      INT: 75, POW: 60, EDU: 70
    },
    derived: { HP: 11, SAN: 60, MP: 12, Luck: 55, DB: 0, Build: 0, MOV: 7 },
    skills: {
      "圖書館使用": 60, "偵查": 55, "說服": 65, "攝影": 50,
      "快速交談": 55, "母語": 70, "潛行": 40, "心理學": 45,
      "汽車駕駛": 35, "會計": 30
    },
    gear: ["記者證", "照相機（柯達 Autographic）", "筆記本與鋼筆", "打火機", "零用現金"],
    bio: "在報社跑了三年社會線，什麼暗巷命案、碼頭走私都見過。最近接到匿名線報，指向一樁與港口倉庫相關的失蹤案。直覺告訴你，這不是普通的新聞。"
  },
  {
    id: 2,
    name: "蕭雨桐",
    player: "阿凱",
    occupation: "私家偵探",
    age: 31,
    gender: "女",
    stats: {
      STR: 60, CON: 65, SIZ: 55, DEX: 70, APP: 60,
      INT: 70, POW: 55, EDU: 65
    },
    derived: { HP: 12, SAN: 55, MP: 11, Luck: 60, DB: 0, Build: 0, MOV: 8 },
    skills: {
      "偵查": 65, "鎖匠": 55, "射擊（手槍）": 50, "追蹤": 50,
      "心理學": 55, "潛行": 50, "話術": 45, "汽車駕駛": 45,
      "格鬥（鬥毆）": 40, "法律": 30
    },
    gear: ["乖巧的 .32 左輪手槍（6 發）", "開鎖工具組", "雙筒望遠鏡", "手電筒", "名片夾"],
    bio: "前警局文職人員，受夠了體制內的推諉塞責後掛牌單幹。接的案子多半是抓姦和尋人，但最近一個委託人要求調查自己失蹤的兄長——線索指向港口附近的某座廢棄倉庫。"
  },
  {
    id: 3,
    name: "陳若薇",
    player: "小雅",
    occupation: "外科醫師（市立醫院）",
    age: 35,
    gender: "女",
    stats: {
      STR: 45, CON: 60, SIZ: 50, DEX: 70, APP: 55,
      INT: 80, POW: 65, EDU: 85
    },
    derived: { HP: 11, SAN: 65, MP: 13, Luck: 45, DB: "-1", Build: "-1", MOV: 8 },
    skills: {
      "急救": 70, "醫學": 65, "科學（生物學）": 50, "科學（藥學）": 45,
      "心理學": 50, "圖書館使用": 50, "偵查": 40, "母語": 85,
      "精神分析": 35, "說服": 30
    },
    gear: ["醫師出診包", "手術刀", "嗎啡針劑 ×3", "聽診器", "醫院識別證"],
    bio: "市立醫院的外科醫師，醫術精湛但不擅社交。三天前急診室送來一具『溺斃』屍體，但胸腔切開後發現的東西讓她夜不成眠。她開始私下追查死者的身分與死因。"
  },
  {
    id: 4,
    name: "周敬堯",
    player: "子豪",
    occupation: "民俗學教授（省立大學）",
    age: 52,
    gender: "男",
    stats: {
      STR: 40, CON: 45, SIZ: 65, DEX: 45, APP: 50,
      INT: 85, POW: 70, EDU: 90
    },
    derived: { HP: 11, SAN: 70, MP: 14, Luck: 40, DB: 0, Build: 0, MOV: 5 },
    skills: {
      "圖書館使用": 75, "歷史": 70, "神秘學": 55, "考古學": 50,
      "人類學": 45, "母語": 90, "其他語言（拉丁語）": 40, "偵查": 45,
      "自然學": 35, "說服": 30
    },
    gear: ["厚重公事包（塞滿手稿）", "放大鏡", "舊式懷錶", "菸斗與菸草", "隨身筆記"],
    bio: "研究東亞沿海漁村信仰長達二十年的老學者。最近在翻譯一份從舊書商那裡購得的手稿時，發現其中記載了一種他從未見過的祭祀儀式——而手稿的來源，正好是這座港口城市。"
  },
  {
    id: 5,
    name: "許瀚文",
    player: "小宇",
    occupation: "古董商",
    age: 45,
    gender: "男",
    stats: {
      STR: 50, CON: 50, SIZ: 60, DEX: 55, APP: 65,
      INT: 75, POW: 75, EDU: 75
    },
    derived: { HP: 11, SAN: 75, MP: 15, Luck: 65, DB: 0, Build: 0, MOV: 6 },
    skills: {
      "估價": 70, "歷史": 55, "圖書館使用": 50, "神秘學": 60,
      "說服": 55, "偵查": 50, "會計": 40, "其他語言（法語）": 35,
      "鑑定": 45, "信用評級": 50
    },
    gear: ["鱷魚皮公事包", "估價用珠寶放大鏡", "古董鑑定工具", "高級鋼筆", "名貴懷錶"],
    bio: "在港區經營一間不起眼的古董鋪，但暗地裡經手不少來路不明的文物。一個月前賣出的一件青銅器讓買家精神失常，他開始調查那件古物的真正來歷。"
  }
];

// Stat label helper
const statLabels = ["STR", "CON", "SIZ", "DEX", "APP", "INT", "POW", "EDU"];
const statCN = { STR: "力量", CON: "體質", SIZ: "體型", DEX: "敏捷", APP: "外貌", INT: "智力", POW: "意志", EDU: "教育" };

function StatBar({ label, value }) {
  const pct = (value / 100) * 100;
  const isHigh = value >= 70;
  const isLow = value <= 45;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 3 }}>
      <span style={{ width: 60, fontSize: 11, color: "var(--muted)", fontFamily: "'Courier Prime', monospace", letterSpacing: 1 }}>
        {label} <span style={{ fontSize: 9, opacity: 0.5 }}>{statCN[label]}</span>
      </span>
      <div style={{ flex: 1, height: 6, background: "var(--bar-bg)", borderRadius: 1, overflow: "hidden", position: "relative" }}>
        <div style={{
          width: `${pct}%`, height: "100%",
          background: isHigh ? "var(--accent-green)" : isLow ? "var(--accent-red)" : "var(--accent-amber)",
          borderRadius: 1,
          transition: "width 0.8s cubic-bezier(0.22, 1, 0.36, 1)"
        }} />
      </div>
      <span style={{ width: 28, textAlign: "right", fontSize: 12, fontWeight: 700, fontFamily: "'Courier Prime', monospace", color: isHigh ? "var(--accent-green)" : isLow ? "var(--accent-red)" : "var(--text)" }}>
        {value}
      </span>
    </div>
  );
}

function CharCard({ char, expanded, onToggle }) {
  const isUser = char.highlight;
  return (
    <div
      onClick={onToggle}
      style={{
        background: isUser ? "var(--card-highlight)" : "var(--card-bg)",
        border: isUser ? "1.5px solid var(--accent-amber)" : "1px solid var(--border)",
        borderRadius: 4,
        padding: "14px 16px",
        cursor: "pointer",
        transition: "all 0.3s ease",
        position: "relative",
        overflow: "hidden",
        boxShadow: isUser ? "0 0 20px rgba(200,160,60,0.08)" : "none"
      }}
    >
      {isUser && (
        <div style={{
          position: "absolute", top: 0, right: 0,
          background: "var(--accent-amber)", color: "#1a1410",
          fontSize: 9, fontWeight: 800, padding: "2px 10px 2px 12px",
          letterSpacing: 2, textTransform: "uppercase",
          clipPath: "polygon(12px 0, 100% 0, 100% 100%, 0 100%)"
        }}>YOUR CARD</div>
      )}

      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
        <div>
          <div style={{ fontSize: 18, fontWeight: 800, fontFamily: "'Noto Serif TC', 'Georgia', serif", color: "var(--text)", letterSpacing: 1 }}>
            {char.name}
          </div>
          <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 2, fontFamily: "'Courier Prime', monospace" }}>
            {char.occupation}　｜　{char.age}歲　{char.gender}
          </div>
        </div>
        <div style={{
          fontSize: 11, color: isUser ? "var(--accent-amber)" : "var(--accent-green)",
          fontWeight: 700, fontFamily: "'Courier Prime', monospace",
          background: isUser ? "rgba(200,160,60,0.1)" : "rgba(100,180,100,0.1)",
          padding: "2px 8px", borderRadius: 2, border: `1px solid ${isUser ? "rgba(200,160,60,0.2)" : "rgba(100,180,100,0.2)"}`
        }}>
          PL: {char.player}
        </div>
      </div>

      {/* Derived stats row - always visible */}
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: expanded ? 12 : 0 }}>
        {Object.entries(char.derived).map(([k, v]) => (
          <div key={k} style={{
            background: "var(--tag-bg)", padding: "2px 7px", borderRadius: 2,
            fontSize: 10, fontFamily: "'Courier Prime', monospace", color: "var(--muted)",
            border: "1px solid var(--border)"
          }}>
            <span style={{ opacity: 0.6 }}>{k}</span>{" "}
            <span style={{ color: k === "SAN" ? "var(--accent-blue)" : k === "HP" ? "var(--accent-red)" : "var(--text)", fontWeight: 700 }}>{v}</span>
          </div>
        ))}
      </div>

      {/* Expanded content */}
      {expanded && (
        <div style={{ marginTop: 4, borderTop: "1px solid var(--border)", paddingTop: 12 }}>
          {/* Stats */}
          <div style={{ marginBottom: 14 }}>
            <div style={{ fontSize: 10, fontWeight: 700, color: "var(--muted)", letterSpacing: 2, marginBottom: 6, textTransform: "uppercase" }}>屬性 ATTRIBUTES</div>
            {statLabels.map(s => <StatBar key={s} label={s} value={char.stats[s]} />)}
          </div>

          {/* Skills */}
          <div style={{ marginBottom: 14 }}>
            <div style={{ fontSize: 10, fontWeight: 700, color: "var(--muted)", letterSpacing: 2, marginBottom: 6, textTransform: "uppercase" }}>技能 SKILLS</div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "3px 10px" }}>
              {Object.entries(char.skills).sort((a, b) => b[1] - a[1]).map(([k, v]) => (
                <span key={k} style={{ fontSize: 11, fontFamily: "'Courier Prime', monospace", color: v >= 60 ? "var(--accent-green)" : v >= 50 ? "var(--text)" : "var(--muted)" }}>
                  {k} <span style={{ fontWeight: 700 }}>{v}%</span>
                </span>
              ))}
            </div>
          </div>

          {/* Gear */}
          <div style={{ marginBottom: 14 }}>
            <div style={{ fontSize: 10, fontWeight: 700, color: "var(--muted)", letterSpacing: 2, marginBottom: 6, textTransform: "uppercase" }}>裝備 GEAR</div>
            <div style={{ fontSize: 11, color: "var(--text)", lineHeight: 1.6 }}>
              {char.gear.join("　／　")}
            </div>
          </div>

          {/* Bio */}
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, color: "var(--muted)", letterSpacing: 2, marginBottom: 6, textTransform: "uppercase" }}>背景 BACKGROUND</div>
            <div style={{ fontSize: 12, color: "var(--text)", lineHeight: 1.7, fontFamily: "'Noto Serif TC', 'Georgia', serif", opacity: 0.85, fontStyle: "italic" }}>
              {char.bio}
            </div>
          </div>
        </div>
      )}

      {/* Expand hint */}
      <div style={{ textAlign: "center", marginTop: 8, fontSize: 10, color: "var(--muted)", opacity: 0.5 }}>
        {expanded ? "▲ 收起" : "▼ 點擊展開完整角色卡"}
      </div>
    </div>
  );
}

export default function CoC7eCharacterCards() {
  const [expandedId, setExpandedId] = useState(null);

  return (
    <div style={{
      "--bg": "#1a1410",
      "--card-bg": "rgba(30,26,20,0.95)",
      "--card-highlight": "rgba(40,34,22,0.95)",
      "--border": "rgba(200,180,140,0.12)",
      "--text": "#e8dcc8",
      "--muted": "#8a7e6a",
      "--accent-amber": "#c8a03c",
      "--accent-green": "#6aaa5c",
      "--accent-red": "#c45c4a",
      "--accent-blue": "#5a8ab4",
      "--bar-bg": "rgba(200,180,140,0.08)",
      "--tag-bg": "rgba(200,180,140,0.05)",
      minHeight: "100vh",
      background: "var(--bg)",
      padding: "24px 16px",
      fontFamily: "-apple-system, 'Noto Sans TC', 'Helvetica Neue', sans-serif",
      color: "var(--text)"
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&family=Noto+Serif+TC:wght@400;700;900&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: rgba(200,180,140,0.2); border-radius: 2px; }
      `}</style>

      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: 24 }}>
        <div style={{ fontSize: 9, letterSpacing: 6, color: "var(--muted)", textTransform: "uppercase", marginBottom: 4, fontFamily: "'Courier Prime', monospace" }}>
          Call of Cthulhu 7th Edition
        </div>
        <div style={{ fontSize: 22, fontWeight: 900, fontFamily: "'Noto Serif TC', serif", letterSpacing: 3, color: "var(--accent-amber)" }}>
          角色卡一覽
        </div>
        <div style={{ width: 40, height: 1, background: "var(--accent-amber)", margin: "8px auto", opacity: 0.4 }} />
        <div style={{ fontSize: 11, color: "var(--muted)", fontFamily: "'Courier Prime', monospace" }}>
          5 Investigators — 點擊展開詳細資訊
        </div>
      </div>

      {/* Cards */}
      <div style={{ maxWidth: 520, margin: "0 auto", display: "flex", flexDirection: "column", gap: 10 }}>
        {characters.map(c => (
          <CharCard
            key={c.id}
            char={c}
            expanded={expandedId === c.id}
            onToggle={() => setExpandedId(expandedId === c.id ? null : c.id)}
          />
        ))}
      </div>

      {/* Footer */}
      <div style={{ textAlign: "center", marginTop: 24, fontSize: 10, color: "var(--muted)", opacity: 0.4, fontFamily: "'Courier Prime', monospace" }}>
        「有些門，推開之後就回不了頭了。」
      </div>
    </div>
  );
}
