import pandas as py
import numpy as np
from dataclasses import dataclass

### Intuition Behind Backtest Class ###
# we want to create a module backtest class on an generic strategy
# return a central metric for optimization (option of Sharpe Ratio or DWL)

class backtestEngine(object):
    bt_cols = ['ID', 'start_buy', 'start_sell', 'trigger_buy', 'trigger_sell']

# compute boolean masks for when to trigger open position buy/sell
bdf['start_buy'] = bdf['signal'] >= buy_level
bdf['start_sell'] = bdf['signal'] <= sell_level
# combine into a single boolean mask.
# we cannot take the same position twice.
bdf['cstarts'] = (1*bdf['start_buy']) - (1*bdf['start_sell'])
bdf.loc[bdf['cstarts'] == 0, 'cstarts'] = pd.NA
# need to fillNA in order to maintain the most recent action.
bdf['cstarts'] = bdf['cstarts'].fillna(method='ffill').fillna(0)
# use leq and geq because we start most likely from a zero-state.
# other than the initialization, the diff should be +2 or -2.
# to take care of non-zero initial state (see AAPL on 6/2/2023) we catch the NA diff and starting values of +1 and -1.
bdf['trigger_buy'] = (bdf['cstarts'].diff() >= 1) | (pd.isna(bdf['cstarts'].diff()) & bdf['cstarts']==1)
bdf['trigger_sell'] = (bdf['cstarts'].diff() <= -1) | (pd.isna(bdf['cstarts'].diff()) & bdf['cstarts']==-1)

# figure out when to buy/sell back from an opened position
bdf['end_buy'] = (bdf['signal'] <= mean) & (bdf['cstarts'] == 1)
bdf['end_sell'] = (bdf['signal'] >= mean) & (bdf['cstarts'] == -1)
# need to combine the above to determine triggers. can't end the same position twice.
bdf['cends'] = (1*bdf['end_buy']) - (1*bdf['end_sell'])
bdf.loc[bdf['cends'] == 0, 'cends'] = pd.NA
# need to fillNA in order to maintain the most recent action.
bdf['cends'] = bdf['cends'].fillna(method='ffill').fillna(0)
# use leq and geq because we will start from a zero-state (cstarts==0).
# other than the initialization, the diff should be +2 or -2.
bdf['trigger_end_buy'] = bdf['cends'].diff() >= 1
bdf['trigger_end_sell'] = bdf['cends'].diff() <= -1

# now combine all the triggers to see when we are holding or shorting.
# with somewhat-continuity of the signal, we can just assume that after a buy, the end-buy will occur BEFORE starting a new sale, and the same for sell->endsell->newbuy.
# note, for signing purposes, the end-buy is actually selling.
bdf['holding_action'] = 1*bdf['trigger_buy'] - 1*bdf['trigger_end_buy'] - 1*bdf['trigger_sell'] + 1*bdf['trigger_end_sell']
# by design of the boolean triggers and the continuity assumption, the cumulative sum of the actions should range within [1, -1]. check it in the plot.
bdf['position'] = bdf['holding_action'].cumsum()

#%% plot the signal over time, then plot the position overlay.
plt.figure(figsize=(12,8), dpi=200)
plt.plot(bdf.index, bdf['signal'])
plt.axhline(mean, label='mean signal')
plt.axhline(buy_level)
plt.axhline(sell_level)
plt.ylabel('signal')
plt.tick_params(axis='y', labelcolor='C0')

plt.gca().twinx()
plt.plot(bdf.index, bdf['position'], color='C1')
plt.ylabel('position')
plt.tick_params(axis='y', labelcolor='C1')
plt.tight_layout()
plt.show()

#%% compute profit over time, plot the buys and sells on top of the stock price.
# costs the half spread each time we trade. thus enter+exit position costs 1 entire spread (ask-bid).
bdf['tcost'] = (bdf['ask0'] - bdf['bid0']) / 2 * (bdf['trigger_buy'] | bdf['trigger_end_buy'] | bdf['trigger_sell'] | bdf['trigger_end_sell'])
bdf['mid'] = (bdf['ask0'] + bdf['bid0']) / 2
bdf['profit'] = (bdf['position'].shift(1) * (bdf['mid'] - bdf['mid'].shift(1))).fillna(0)

bdf['cum_profit_no_tcost'] = bdf['profit'].cumsum()
bdf['cum_profit'] = (bdf['profit'] - bdf['tcost']).cumsum()
