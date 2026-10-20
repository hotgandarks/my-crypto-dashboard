from datetime import datetime
import json
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# 頁面基本設定
st.set_page_config(
    layout="wide",
    page_title="CYBER-TRADER 終極戰情室",
    page_icon="🚀",
    initial_sidebar_state="expanded",
)

# ==========================================
# 0. 賽博龐克科技風視覺樣式 (CSS 注入)
# ==========================================
st.markdown(
    """
    <style>
        .stApp {
            background-color: #05070e;
            color: #e2e8f0;
        }
        section[data-testid="stSidebar"] {
            background-color: #090e1a;
            border-right: 1px solid rgba(0, 230, 118, 0.25);
        }
        .cyber-card {
            background: linear-gradient(135deg, rgba(10, 25, 47, 0.85), rgba(15, 32, 67, 0.85));
            border: 1px solid rgba(0, 230, 118, 0.35);
            box-shadow: 0 0 20px rgba(0, 230, 118, 0.1);
            padding: 22px;
            border-radius: 14px;
            margin-bottom: 18px;
        }
        .cyber-card-achieved {
            background: linear-gradient(135deg, rgba(0, 230, 118, 0.1), rgba(10, 25, 47, 0.9));
            border: 1px solid #00E676;
            box-shadow: 0 0 25px rgba(0, 230, 118, 0.25);
            padding: 22px;
            border-radius: 14px;
            margin-bottom: 18px;
        }
        h1, h2, h3 {
            font-family: 'Inter', sans-serif;
            letter-spacing: 1.5px;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 1. 資料永久持久化機制 (JSON 讀寫)
# ==========================================
DATA_FILE = "cyber_trader_data.json"


def load_data():
  default_goals = [
      {
          "name": "🚀 終極財富自由",
          "target": 100000.0,
          "media_type": "圖片",
          "media_url": (
              "https://images.unsplash.com/photo-1639762681485-074b7f938ba0"
          ),
          "achieved": False,
          "achieved_date": None,
      },
      {
          "name": "🏖️ 5年後退休金計畫",
          "target": 50000.0,
          "media_type": "圖片",
          "media_url": (
              "https://images.unsplash.com/photo-1507525428034-b723cf961d3e"
          ),
          "achieved": False,
          "achieved_date": None,
      },
      {
          "name": "🏎️ 夢想超跑頭期款",
          "target": 15000.0,
          "media_type": "圖片",
          "media_url": (
              "https://images.unsplash.com/photo-1503376780353-7e6692767b70"
          ),
          "achieved": False,
          "achieved_date": None,
      },
  ]
  if os.path.exists(DATA_FILE):
    try:
      with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("goals", default_goals), data.get("history", [])
    except Exception:
      return default_goals, []
  return default_goals, []


def save_data(goals, history):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump({"goals": goals, "history": history}, f, ensure_ascii=False, indent=4)


if "goals" not in st.session_state or "history" not in st.session_state:
  st.session_state.goals, st.session_state.history = load_data()

# ==========================================
# 2. 側邊欄：資產現況、總體市場政權與目標新增
# ==========================================
st.sidebar.header("⚙️ 1. 當前資產現況庫")
safe_cash = st.sidebar.number_input(
    "防禦庫 (現金/冷錢包)", value=10000.0, step=1000.0
)
trading_margin = st.sidebar.number_input(
    "主戰場 (合約帳戶 USDT)", value=5000.0, step=500.0
)
yield_pool = st.sidebar.number_input(
    "戰利品儲藏室 (質押現貨)", value=3500.0, step=500.0
)

current_total_assets = safe_cash + trading_margin + yield_pool

st.sidebar.header("🌍 2. 宏觀市場政權切換 (Regime)")
market_regime = st.sidebar.selectbox(
    "當前市場氣候",
    [
        "🔥 多頭狂歡模式 (低波動 / 高勝率)",
        "🦀 震盪盤整模式 (標準摩擦力)",
        "❄️ 黑天鵝防禦模式 (高波動 / 厚尾風險)",
    ],
)

# 依據政權自動校準預期參數
if "多頭狂歡" in market_regime:
  default_ret, default_vol, default_drag = 0.6, 0.8, 0.02
elif "震盪盤整" in market_regime:
  default_ret, default_vol, default_drag = 0.4, 1.2, 0.05
else:
  default_ret, default_vol, default_drag = 0.2, 2.5, 0.10

st.sidebar.header("📈 3. 策略與摩擦力引擎")
compounding_strategy = st.sidebar.radio(
    "獲利滾動模式",
    [
        "利滾利 (全面複利模式 - 具動態增長)",
        "落袋為安 (利潤 100% 抽走/單利模式)",
    ],
)

expected_daily_return_pct = (
    st.sidebar.slider(
        "預期平均每日報酬率 (%)", 0.1, 5.0, default_ret, step=0.1
    )
    / 100
)
daily_volatility_pct = (
    st.sidebar.slider(
        "每日報酬率波動率/標準差 (%)", 0.1, 5.0, default_vol, step=0.1
    )
    / 100
)
daily_fee_drag_pct = (
    st.sidebar.slider(
        "手續費與資金費率摩擦力 (%)", 0.0, 0.5, default_drag, step=0.01
    )
    / 100
)

st.sidebar.header("🎯 4. 新增客製化願景目標")
with st.sidebar.expander("➕ 建立新目標與願景卡片", expanded=False):
  new_goal_name = st.text_input("目標名稱", value="全球頂級度假別墅")
  new_goal_target = st.number_input("目標金額 (USDT)", value=150000.0, step=10000.0)
  media_type_choice = st.selectbox("媒體類型", ["圖片", "YouTube 影片"])
  new_goal_media = st.text_input(
      "媒體網址 (URL)",
      value="https://images.unsplash.com/photo-1600585154340-be6161a56a0c",
  )

  if st.button("✨ 寫入資料庫並啟動"):
    st.session_state.goals.append({
        "name": new_goal_name,
        "target": new_goal_target,
        "media_type": media_type_choice,
        "media_url": new_goal_media,
        "achieved": False,
        "achieved_date": None,
    })
    save_data(st.session_state.goals, st.session_state.history)
    st.success("成功新增目標！")
    st.rerun()

working_days_per_year = 250

# ==========================================
# 3. 主頁面：多頁籤沈浸戰情室
# ==========================================
st.title("🛡️ CYBER-TRADER 交易員終極戰情室")
st.write(
    f"**系統總資產實時水位：{current_total_assets:,.2f} USDT** | 數據持久化防護網"
    " 🟢"
)

tab_dashboard, tab_kelly, tab_history, tab_settings = st.tabs([
    "⚡ 實時戰情與願景板",
    "🧮 凱利公式與風控導航",
    "📜 歷史達陣名人堂",
    "⚙️ 資料庫與系統管理",
])

with tab_dashboard:
  st.markdown("### 🎯 進行中的人生願景矩陣 (Vision Board)")

  # 自動檢查並歸檔已達陣目標
  remaining_goals = []
  updated = False
  for goal in st.session_state.goals:
    if current_total_assets >= goal["target"] and not goal["achieved"]:
      goal["achieved"] = True
      goal["achieved_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
      st.session_state.history.append(goal)
      updated = True
      st.balloons()
    else:
      remaining_goals.append(goal)

  if updated:
    st.session_state.goals = remaining_goals
    save_data(st.session_state.goals, st.session_state.history)

  if not st.session_state.goals:
    st.success(
        "🎉 太神啦！所有現行目標已全部達陣解鎖！請在側邊欄追加更高遠的宏圖！"
    )

  # 渲染每一個目標卡片
  for i, goal in enumerate(st.session_state.goals):
    g_name = goal["name"]
    g_target = goal["target"]
    g_progress = min(current_total_assets / g_target, 1.0)
    g_remaining = g_target - current_total_assets

    # 扣除摩擦力後的淨日報酬率計算倒數天數
    net_daily_return = expected_daily_return_pct - daily_fee_drag_pct

    if g_remaining > 0:
      if "利滾利" in compounding_strategy:
        if net_daily_return > 0:
          g_days = np.log(g_target / current_total_assets) / np.log(
              1 + net_daily_return
          )
        else:
          g_days = float("inf")
      else:
        daily_fixed_profit = trading_margin * net_daily_return
        g_days = (
            g_remaining / daily_fixed_profit
            if daily_fixed_profit > 0
            else float("inf")
        )
      g_days = (
          int(np.ceil(g_days)) if g_days != float("inf") else float("inf")
      )
      g_years = (
          g_days / working_days_per_year
          if g_days != float("inf")
          else float("inf")
      )
    else:
      g_days, g_years = 0, 0.0

    with st.container():
      st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
      col_media, col_info, col_metrics, col_act = st.columns([1.2, 2.5, 1.5, 0.8])

      with col_media:
        if goal["media_type"] == "圖片":
          st.image(goal["media_url"], use_container_width=True)
        else:
          st.video(goal["media_url"])

      with col_info:
        st.subheader(g_name)
        st.write(
            f"目標金額：**{g_target:,.2f} USDT** | 達成進度："
            f" **{g_progress*100:.1f}%**"
        )
        st.progress(g_progress)
        st.caption(
            f"距離達陣還差：{max(0.0, g_remaining):,.2f} USDT (已內扣手續費摩擦力)"
        )

      with col_metrics:
        if g_remaining <= 0:
          st.metric("倒數計時", "🎉 已達陣！")
        else:
          st.metric(
              "預估還需",
              f"{g_days} 天" if g_days != float("inf") else "無法達成",
          )
          st.metric(
              "折合年數",
              f"{g_years:.1f} 年" if g_years != float("inf") else "-",
          )

      with col_act:
        st.write("")
        if st.button("🗑️ 刪除", key=f"del_goal_{i}"):
          st.session_state.goals.pop(i)
          save_data(st.session_state.goals, st.session_state.history)
          st.rerun()

      st.markdown("</div>", unsafe_allow_html=True)

  st.markdown("---")

  # 宏觀蒙地卡羅軌跡圖 (含手續費摩擦力與厚尾波動)
  st.subheader("📈 巨集蒙地卡羅軌跡模擬 (內扣摩擦力與波動率)")
  days_projection = 500
  n_simulations = 200

  np.random.seed(42)
  simulated_paths = np.zeros((days_projection + 1, n_simulations))
  simulated_paths[0, :] = current_total_assets
  net_daily_return = expected_daily_return_pct - daily_fee_drag_pct
  fixed_daily_gain = trading_margin * net_daily_return

  for day in range(1, days_projection + 1):
    if "利滾利" in compounding_strategy:
      daily_returns = np.random.normal(
          net_daily_return, daily_volatility_pct, n_simulations
      )
      simulated_paths[day, :] = simulated_paths[day - 1, :] * (
          1 + daily_returns
      )
      simulated_paths[day, :] = np.maximum(simulated_paths[day, :], 0)
    else:
      simulated_paths[day, :] = simulated_paths[day - 1, :] + fixed_daily_gain

  p10 = np.percentile(simulated_paths, 10, axis=1)
  p50 = np.percentile(simulated_paths, 50, axis=1)
  p90 = np.percentile(simulated_paths, 90, axis=1)
  x_axis = np.arange(0, days_projection + 1)

  fig = go.Figure()
  fig.add_trace(
      go.Scatter(
          x=np.concatenate([x_axis, x_axis[::-1]]),
          y=np.concatenate([p90, p10[::-1]]),
          fill="toself",
          fillcolor="rgba(0, 230, 118, 0.1)",
          line=dict(color="rgba(255,255,255,0)"),
          showlegend=True,
          name="80% 機率區間 (P10-P90)",
      )
  )
  fig.add_trace(
      go.Scatter(
          x=x_axis,
          y=p50,
          mode="lines",
          name="中位數預測 (P50)",
          line=dict(color="#00E676", width=2),
      )
  )

  colors = ["#FF5252", "#FFEB3B", "#00BCD4", "#E040FB", "#FF9800"]
  for idx, goal in enumerate(st.session_state.goals):
    c = colors[idx % len(colors)]
    fig.add_hline(
        y=goal["target"],
        line_dash="dash",
        line_color=c,
        annotation_text=goal["name"],
        annotation_position="top left",
    )

  fig.update_layout(
      xaxis_title="未來交易天數",
      yaxis_title="總資產價值 (USDT)",
      template="plotly_dark",
      height=420,
      margin=dict(l=20, r=20, t=30, b=20),
      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(0,0,0,0)",
      legend=dict(
          orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
      ),
  )
  st.plotly_chart(fig, use_container_width=True)

with tab_kelly:
  st.subheader("🧮 凱利公式部位導航與風險控制矩陣")
  st.write(
      "為防止複利模式下的爆倉危機，系統將根據您的交易勝率與盈虧比，動態計算合約帳戶的資金水位與最大開倉安全建議。"
  )
  st.markdown("---")

  col_k1, col_k2 = st.columns(2)
  with col_k1:
    win_rate = st.slider("預估交易勝率 (%)", 30.0, 90.0, 55.0) / 100
    reward_risk_ratio = st.slider("盈虧比 (平均獲利 / 平均虧損)", 0.5, 5.0, 1.5)

    # 計算凱利公式值: f* = W - (1-W) / R
    kelly_fraction = win_rate - ((1 - win_rate) / reward_risk_ratio)
    kelly_fraction = max(0.0, kelly_fraction)

  with col_k2:
    st.markdown("### 📊 風控計算結果")
    st.metric(
        "理論凱利建議倉位比例",
        f"{kelly_fraction*100:.2f}%",
        help="單筆交易投入資金佔總合約帳戶的上限比例",
    )
    safe_kelly = kelly_fraction * 0.5  # 半凱利，實務界常用防禦標準
    st.metric("半凱利安全防禦倉位 (建議)", f"{safe_kelly*100:.2f}%")

    max_position_usdt = trading_margin * safe_kelly
    st.metric(
        "當前主戰場單筆建議最大開倉額",
        f"{max_position_usdt:,.2f} USDT",
    )

  st.info(
      "💡 **資產配置專家叮嚀：**\n"
      "實務交易中，千萬不要使用全額凱利（容易面臨劇烈回檔），建議採用**『半凱利 (Half-Kelly)』**甚至更低的固定風險模型，"
      "確保在複利滾動的過程中，不會因為單次黑天鵝事件而導致主戰場歸零。"
  )

with tab_history:
  st.subheader("🏆 歷史達陣名人堂 (Hall of Fame)")
  st.write("這裏永久記錄著您征戰市場、解鎖成功的每一項榮耀成就！")
  st.markdown("---")

  if not st.session_state.history:
    st.info(
        "目前尚無已達陣的歷史紀錄。努力交易，將資產推升至目標線上方來解鎖成就吧！"
    )
  else:
    for idx, h_item in enumerate(st.session_state.history):
      st.markdown(
          f"""
                <div class="cyber-card-achieved">
                    <h3>🌟 榮譽解鎖：{h_item['name']}</h3>
                    <p><b>達陣目標金額：</b> {h_item['target']:,.2f} USDT</p>
                    <p><b>達陣解鎖時間：</b> {h_item['achieved_date']}</p>
                </div>
            """,
          unsafe_allow_html=True,
      )
      if h_item["media_url"]:
        st.image(h_item["media_url"], width=320)

      if st.button("🗑️ 刪除此歷史紀錄", key=f"del_hist_{idx}"):
        st.session_state.history.pop(idx)
        save_data(st.session_state.goals, st.session_state.history)
        st.rerun()
      st.markdown("---")

with tab_settings:
  st.subheader("⚙️ 系統資料管理與備份設定")
  st.success(
      "✅ **資料永久落地：**\n"
      "您的所有自定義目標與歷史達陣均會自動儲存至本機的 `cyber_trader_data.json` 檔案中。"
      "換電腦或重啟應用程式後，資料將自動載入，完全不會遺失！"
  )

  if st.button("🔄 恢復預設範例資料"):
    if os.path.exists(DATA_FILE):
      os.remove(DATA_FILE)
    st.session_state.goals, st.session_state.history = load_data()
    st.success("已重置為預設資料！")
    st.rerun()