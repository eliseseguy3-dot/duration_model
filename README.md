# Bond Duration Sensitivity Model
Bond Duration Sensitivity Model is a tool for bond analysis, built to model and visualise the price sensitivity of bonds to interest rate movements. Developed as a side project, this tool formalises the mathematical relationships between yield, duration and price into an interactive dashboard.

---

## What it does

Given a bond's nominal, coupon rate, maturity and yield, the model computes:

- **Modified Duration**: first-order price sensitivity to yield changes
- **Convexity** : second-order correction, capturing the curvature of the price/yield relationship
- **DV01** : dollar value of a basis point (P&L impact of a 1bp move)
- **Stress tests** : simulated price and P&L impact for +10bp, +50bp and +100bp yield shocks

Results are displayed in an interactive dashboard with adjustable parameters (sliders for coupon, maturity and yield), and a price/yield curve comparing the linear duration approximation against the convexity-adjusted estimate.

---

## Key output

<img width="1702" height="786" alt="dashboard_screenshot" src="https://github.com/user-attachments/assets/5b2a0a17-7e8a-4d92-b907-ef3f503cde96" />


The chart illustrates the divergence between the modified duration approximation (dashed blue) and the true convex price/yield curve (orange) — a gap that becomes material for large yield moves or long-dated bonds.

---

## Mathematical framework

Price of a bond:

$$P = \sum_{t=1}^{T} \frac{C}{(1+y)^t} + \frac{N}{(1+y)^T}$$

Modified Duration:

$$D_{mod} = \frac{D_{Macaulay}}{1+y}$$

Price approximation with convexity adjustment:

$$\Delta P \approx -D_{mod} \cdot P \cdot \Delta y + \frac{1}{2} \cdot Convexity \cdot P \cdot (\Delta y)^2$$
