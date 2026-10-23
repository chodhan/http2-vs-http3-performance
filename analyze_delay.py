import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("results.csv")

loss_numeric = {"loss0": 0, "loss1d": 1, "loss5d": 5, "loss10d": 10}
df = df[df["loss_condition"].isin(loss_numeric.keys())]
df["loss_pct"] = df["loss_condition"].map(loss_numeric)

summary = df.groupby(["protocol", "loss_condition", "file"]).agg(
    avg_completion_time=("completion_time", "mean"),
    avg_latency=("latency_ttfb", "mean"),
).reset_index()
summary.to_csv("summary_delay.csv", index=False)
print(summary)

small_files = ["small1.jpg", "small2.jpg", "small3.jpg"]
small_df = df[df["file"].isin(small_files)]

trend = small_df.groupby(["protocol", "loss_pct"])["completion_time"].mean().reset_index()

fig, ax = plt.subplots(figsize=(8,6))
for proto, color in [("http2", "#e07a5f"), ("http3", "#3d5a80")]:
    subset = trend[trend["protocol"] == proto].sort_values("loss_pct")
    ax.plot(subset["loss_pct"], subset["completion_time"], marker="o", label=proto.upper(), color=color, linewidth=2)

ax.set_xlabel("Packet Loss (%) [with 50ms delay]")
ax.set_ylabel("Avg Small-File Completion Time (s)")
ax.set_title("Small File Completion Time vs Packet Loss: HTTP/2 vs HTTP/3")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("trend_small_files_vs_loss_delay.png", dpi=150)
print("Saved trend_small_files_vs_loss_delay.png")

increases = {}
for proto in ["http2", "http3"]:
    base = small_df[(small_df["protocol"]==proto) & (small_df["loss_condition"]=="loss0")]["completion_time"].mean()
    high = small_df[(small_df["protocol"]==proto) & (small_df["loss_condition"]=="loss10d")]["completion_time"].mean()
    increases[proto] = ((high-base)/base)*100 if base else 0

fig2, ax2 = plt.subplots(figsize=(6,5))
ax2.bar(increases.keys(), increases.values(), color=["#e07a5f","#3d5a80"])
ax2.set_ylabel("% Increase in Small-File Completion Time (0% -> 10% loss, 50ms delay)")
ax2.set_title("Impact of High Packet Loss + Delay on Unrelated Small Files")
for i,(k,v) in enumerate(increases.items()):
    ax2.text(i, v, f"{v:.1f}%", ha="center", va="bottom")
plt.tight_layout()
plt.savefig("barchart_small_file_impact_delay.png", dpi=150)
print("Saved barchart_small_file_impact_delay.png")
print(f"\nHTTP/2 increase: {increases['http2']:.1f}%")
print(f"HTTP/3 increase: {increases['http3']:.1f}%")
