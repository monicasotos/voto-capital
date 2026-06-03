- avoid writing unnecessary comments, unless there is a reason, just write the why.
- use `pytest` as only test suite
- only TDD approach
- prefer small changes. If big, explain briefly the plan first
- always show the changes that you plan to execute, wait for approval
- python 3.13
- Streamlit for the dashboard

## Goal of this repo

Create a proper well-structured repository, with nice architecture to be able to display via a dashboard some data.
In the `data/raw/` folder, I have some `ETF` stock prices for some of the countries. More or less, this data looks like
below (from 2019 to 2026):

```
"Date","Price","Open","High","Low","Vol.","Change %"
"06/02/2026","41.82","41.54","41.99","41.32","96.47K","0.19%"
"06/01/2026","41.74","41.45","43.10","41.45","1.25M","6.64%"
```

In the `data/` folder, a file mapping the countries with the filenames is also present.

I want to answer the following question: how true or false is the following affirmation (given in spanish,
too lazy to translate now):

> Left-wing victories have been associated with currency depreciation, widening risk premiums, and the devaluation of
> local assets, whereas outcomes aligned with the right have generated the opposite behavior, reflecting a rapid shift
> in
> country risk perception.

Now, to make a careful analysis, I do not have all the data. I just know that the person who made this sentence used
only the case of Chile, and besides the ETF index, used the historical dollar price, the public debt, maybe something
else. Below is the full "analysis" of this person.

"How Would Markets React to Election Results?

* We analyze the market impact of presidential election results in scenarios where either the right or the left has won.
* The analysis suggests that markets tend to anticipate the outcome most likely to materialize; once confirmed, they
  reinforce the prevailing trend 📌.
* Victories for the left have been associated with currency depreciation, widening risk premiums, and a decline in the
  value of local assets, whereas results favoring the right have generated the opposite behavior, reflecting a rapid
  shift in country risk perception 🔍.

👉 Financial Asset Reactions to Presidential Election Results

* The analysis covers a period spanning 30 days prior to the first round of voting and 30 days following the second
  round of the presidential election. For reference, the day immediately preceding the first round is designated as "
  time zero"; asset values ​​are normalized to a base index of 100 on that date, while 10-year local-currency public
  debt is expressed as a change in basis points (bps), using 0 bps as the reference point on that same day.

* Within this framework, we evaluate the reaction of the #dollar 💵, 10-year public debt, country risk metrics, and the
  equity market to presidential election results in Chile 🇨🇱: specifically, the elections held between November and
  December 2025—in which a right-wing candidate was elected—and those held in May and June 2022, where the outcome
  favored the left.

* The primary finding is that the market tends to anticipate the scenario most likely to materialize and, once the
  election result is confirmed, continues to follow the previously established trend.

* In the scenario involving a victory for the left, the dollar appreciated by as much as 23% (equivalent to COP 850
  Colombian pesos) before subsequently moderating to a 14% gain. 10-year local-currency public debt experienced a
  decline of 215 basis points, although it closed with an adjustment of only 23 basis points 🔍. Meanwhile, country risk
  surged by 77% 📈, subsequently correcting to an increase of 40%. Finally, stocks recorded a drop of 21% ⬇️.

* In the event of a right-wing victory, the dollar depreciated by 11% 📉 (equivalent to COP 450), 10-year local-currency
  public debt remained relatively stable, country risk fell by 24%, and stocks rose by 31% ⬆️."

We can start slowly, like maybe making just a graph of how the ETF prices and the price changes have evolved. Idk where
to start, but I want to do it slowly, not 2000 lines of code at once. Which other data do I need or could be useful?
maybe we can also set up some sort of scraper? or I can get you the data that you want as well, in the format that you
want. Feel free to rename or suggest something else with the current structure that I have.
