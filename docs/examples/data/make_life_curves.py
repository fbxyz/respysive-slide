"""Draw ``life_curves.png``, the picture used by the examples of images and backgrounds.

Run from ``docs/examples``: ``python data/make_life_curves.py``.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.express as px

gapminder = px.data.gapminder()
life = gapminder.pivot(index="year", columns="country", values="lifeExp")
weighted = gapminder.groupby("year").apply(lambda d: (d["lifeExp"] * d["pop"]).sum() / d["pop"].sum())

fig, ax = plt.subplots(figsize=(16, 9), dpi=80)
ax.plot(life.index, life.values, color="#457b9d", alpha=0.25, linewidth=1.2)
ax.plot(weighted.index, weighted.values, color="#e63946", linewidth=5)
ax.set_xlim(life.index.min(), life.index.max())
ax.set_ylabel("Life expectancy at birth (years)", fontsize=20)
ax.tick_params(labelsize=18)
ax.spines[["top", "right"]].set_visible(False)
ax.text(
    life.index.max(),
    weighted.iloc[-1] + 1,
    "World, weighted by population",
    color="#e63946",
    fontsize=20,
    ha="right",
    va="bottom",
)
ax.set_title(f"{life.shape[1]} countries, {life.index.min()}-{life.index.max()}", fontsize=24, loc="left")
fig.text(0.99, 0.01, "Source: Gapminder", ha="right", va="bottom", fontsize=14, color="#6b7280")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig("data/life_curves.png")
