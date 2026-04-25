import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# -----------------------------
# Pricing functions
# -----------------------------

def bond_price(face, coupon_rate, ytm, maturity):
    periods = int(maturity)
    coupon = face * coupon_rate 
    y = ytm 

    cashflows = np.array([coupon] * periods)
    cashflows[-1] += face

    discount_factors = 1 / (1 + y) ** np.arange(1, periods + 1)
    return np.sum(cashflows * discount_factors)

def macaulay_duration(face, coupon_rate, ytm, maturity):
    periods = int(maturity)
    coupon = face * coupon_rate
    y = ytm 

    cashflows = np.array([coupon] * periods)
    cashflows[-1] += face

    times = np.arange(1, periods + 1)
    discount_factors = 1 / (1 + y) ** times

    pv = cashflows * discount_factors
    price = np.sum(pv)

    return np.sum(times * pv) / price 

def modified_duration(mac_dur, ytm):
    return mac_dur / (1 + ytm)

def convexity(face, coupon_rate, ytm, maturity):
    periods = int(maturity)
    coupon = face * coupon_rate
    y = ytm

    cashflows = np.array([coupon] * periods)
    cashflows[-1] += face

    times = np.arange(1, periods + 1)
    discount_factors = 1 / (1 + y) ** times

    pv = cashflows * discount_factors
    price = np.sum(pv)

    conv = np.sum(pv * times * (times + 1)) / ((1 + y) ** 2 * price)
    return conv

def dv01(price_func, face, coupon, ytm, maturity):
    bump = 0.0001
    price_up = price_func(face, coupon, ytm + bump, maturity)
    price_down = price_func(face, coupon, ytm - bump, maturity)
    return (price_down - price_up) / 2

# -----------------------------
# UI
# -----------------------------
st.set_page_config(layout="wide")

st.title("Duration dashboard")

col_a, col_b = st.columns([3,2])

# Sidebar
st.sidebar.header("Settings")

face = st.sidebar.number_input("Nominal", value=100)
coupon_rate = st.sidebar.slider("Coupon (%)", 0.0, 10.0, 3.5) / 100
maturity = st.sidebar.slider("Maturité (années)", 1, 50, 15)
ytm = st.sidebar.slider("Yield (%)", 0.0, 10.0, 2.75) / 100

# -----------------------------
# Calculs
# -----------------------------

price = bond_price(face, coupon_rate, ytm, maturity)
mac_dur = macaulay_duration(face, coupon_rate, ytm, maturity)
mod_dur = modified_duration(mac_dur, ytm)
conv = convexity(face, coupon_rate, ytm, maturity)
dv01_val = dv01(bond_price, face, coupon_rate, ytm, maturity)

# -----------------------------
# OUTPUT
# -----------------------------

with col_a:
    col1, col2, col3, col4 = st.columns([1,2,1,3])

    col1.metric("Price", f"{price:,.0f}")
    col2.metric("Mod Duration", f"{mod_dur:.1f}")
    col3.metric("DV01", f"{dv01_val:,.1f}")
    col4.metric("Convexity", f"{conv:.2f}")

# -----------------------------
# Graph
# -----------------------------

yields = np.linspace(ytm - 0.02, ytm + 0.02, 100)
prices = [bond_price(face, coupon_rate, y, maturity) for y in yields]

approx_prices = [
    price * (1 - mod_dur * (y - ytm) + 0.5 * conv * (y - ytm)**2)
    for y in yields
]

duration_m = [
    price * (1 - mod_dur * (y - ytm))
    for y in yields
]

x_vals = yields * 100

with col_a:
    fig = go.Figure()

    # Courbe duration
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=duration_m,
        mode='lines',
        name='Modified duration',
        line=dict(color='blue', dash='dash'),
        hovertemplate="Yield: %{x:.2f}%<br>Price: %{y:.2f}<extra></extra>"
    ))

    # Courbe convexité (orange)
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=approx_prices,
        mode='lines',
        name='Convexe duration',
        line=dict(color='#FFA500'),
        hovertemplate="Yield: %{x:.2f}%<br>Price: %{y:.2f}<extra></extra>"
    ))

    fig.update_layout(
        hovermode="x unified",
        margin=dict(l=40, r=20, t=20, b=40)
    )

    fig.update_xaxes(
        title="Yield (%)",
        tickmode='linear',
        dtick=0.5,
        tickformat=".1f",
        range=[float(x_vals.min()), float(x_vals.max())],
        autorange=False,
        showgrid=True
    )

    fig.update_yaxes(
        title="Price",
        tickformat=".2f",
        showgrid=True
    )

    # st.plotly_chart(fig, use_container_width=True)

    st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False
    }
)

# -----------------------------
# DV01 display
# -----------------------------

with col_b:
    st.subheader("Sensitivity DV01")
    st.write(f"+1 bp → {-dv01_val:,.1f}€")
    st.write(f"-1 bp → {dv01_val:,.1f}€")

# -----------------------------
# Stress Test
# -----------------------------

with col_b:
    st.subheader("Stress Test")
    
    shocks = [0.001, 0.005, 0.01]
    for shock in shocks:
        new_price = bond_price(face, coupon_rate, ytm + shock, maturity)
        pnl = new_price - price
        st.write(f"+{int(shock*10000)} bps → Price: {new_price:,.1f} | P&L: {pnl:,.1f}")
