# Financial-Modelling-Playground
[ARCHIVED]
This repo USED TO be a collection of things that I had worked during my Master's program: a trading paper on oil futures calendar spread, a paper on barrier options pricing with non-constant strikes, and a genetic algorithm on optimal trading strategies. I've archived them in the zip folder as to stash away the less relevant topics + embarassment.

Now, I mainly focus on creating a quantitative trading system in the quant trading folder. The idea to this library is as follows: 
- Creating a systematic backtest framework for both single and multiple assets using an order book structure to keep track of trade execution
- Formalizing a space to create purely statistical/quantitative measures (as opposed to fundamental analysis) to create pairs trading signals
- TO BE DONE: Implementing a pipeline to combine and boost simple signals into more complicated ones.

While the baseline is quite simple, this library is implemented with the intention of scaling and incoporating more bespoke/complex models. Some future references may be made with respect to my other library on Options Pricing. A lot of work will be leverage on various forms of optimization. 

Referential data primarily relies on polygon.io data (order book data from databento is being considered for future features) as well as yahoo finance for index data. The api calls have been wrapped to enabling multithreading, error-logging, and caching. 

Additional data visualization tools are being introduced as the library comes along but most of the heavy computation lies in the optimization folder (for mixed integer programming) as well as the filtering folder (for kalman filters). 