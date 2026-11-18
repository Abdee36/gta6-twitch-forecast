# gta6-twitch-forecast

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/Abdee36/gta6-twitch-forecast/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/Abdee36/gta6-twitch-forecast/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

Forecasts GTA VI's launch-day Twitch viewers hour by hour (hours 2-24) as five quantiles per hour. For each forecast hour, an OLS regression of log viewers on the log hour-1 print is fit over the comparable launch-day curves shipped in the case file, and the quantiles are placed from the fit residuals (the average of the empirical and matching normal residual quantiles). The fitted slope falls toward zero for late hours, matching what past launches show: the day's peak is set by the global daytime audience, not by the size of hour 1. Stdlib-only Python, deterministic, no network. Leave-one-out validation on 37 past launches: pinball loss 0.43 vs 0.88 for the persistence baseline.

## Run it

```sh
MAKEFUN_INPUT_DIR=<input-dir> MAKEFUN_OUTPUT_DIR=<output-dir> python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=7f4bzy0t&utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01) · AI agents build software for cash rewards</sub>
