# Brampton 2 Zero solar power

>Assisting Brampton 2 Zero with its route for transition to net zero carbon by measuring the maximum capability of solar power for Brampton from rooftop installations, investigating the potential electrical energy reduction from the retrofit, and investigating how the gap between supply and demand be filled by renewable sources.

-------------------------------

## Introduction

Solar Panel output varies significantly depending on the environmental conditions, e.g. solar index, shade and weather. Distributing solar power over a larger area and utilizing integrated systems to redistribute it ([like the Maximum Power Point technique](https://www.sciencedirect.com/topics/engineering/maximum-power-point)) can help alleviate this issue

The purpose of this study is to create a computer model that can investigate the effectiveness of solar panels in reducing the reliance on external energy sources in the city of Brampton. 

-------------
## The scope of this model

When starting new projects in computer modelling, a crucial question must be answered:

> How detailed, exactly, do we need to be? 

Adding too much detail to a model and the project can quickly expand in complexity and cost, with little benefit. On the other hand, when the model is too simplistic, the result is too erroneous to use. As such it's important that we find the ideal target and that we understand the requirements that the model meets. These requirements must be clear before the project begins.

> What are the requirements?

From the top of my head, I can think of a series of objectives to meet when simulating power generation versus consumption. The goal is simple: 

1. find how much energy solar powers produce
2. calculate how much energy Brampton uses
3. estimate the cost saved
4. find external sources of green energy to bridge the gap

With these goals in mind, a series of requirements can be drafted for the minimum viable product (the simulation):



### Essential results

> The absolute minimum target

- Have a 5% (or 10%) precision in the following values: all solar panel output, all energy consumption, cost estimate
- Find at least one nearby green energy source to complete the gap, or provide a summary

This could potentially be done by paper:

Given the following values:

1. Average solar panel output ~= [100 ~ 400 kWh per month](https://uk.renogy.com/blog/average-solar-panel-output-per-day-uk-guide/)  

> In the UK, one of the more common solar system sizes is a four kW system with 16 separate panels. It’s common for a single panel to have an input rate of 1,000 watts. However, the majority of modern solar panels have an efficiency percentage ranging from 15 to 20 per cent. So, for a 16-panel system, with each panel measuring one square metre, each panel can generally produce about 150 to 200 watts per metre. In the UK, a region with an average of four hours of sunlight per day, each square metre of solar panels can generate 0.6kWh to 0.8kWh. And this equals 2.4 to 3.2kWh energy output for a four kW system per day

This works out at about 18-24 kWh/m^2 per month, assuming only 4 hours of sunlight a day (as per the article linked) 

2. Losses ~= assume [50-80%](https://www.theecoexperts.co.uk/solar-panels/electricity-power-output)

3. Total Space for solar panels ~= 60 000 m^2

https://www.citypopulation.de/en/uk/northwestengland/cumbria/E63000109__brampton/

Using this census we can find the total population. Divide this by 4 (assume most people don't leave alone, rather in families or shared accommodation) and multiply by the average house area [60 m^2](https://www.dwh.co.uk/advice-and-inspiration/average-house-sizes-uk/#:~:text=Average%20UK%20house%20size%20(smaller,terraced%20home)%3A%201087%20sq.).

4. Electrical consumption per uk citizen ~= [242 kWh per month](https://www.britishgas.co.uk/energy/guides/average-bill.html#:~:text=Your%20average%20energy%20bill%20by%20house%20size%20and%20usage&text=According%20to%20Ofgem%2C%20the%20average,kWh%20of%20gas%20per%20month.)

>I left out the gas use at around 1000 kWh, this will have to be accounted for when switching to green energy.

Using 1, 2 and 4, the space requirements for one person: 12.6-26.8 m^2.

=>

#### Total space required: 50400 - 108000 m^2 for electricity only 

This is an error of over 50%. More so, the lower estimate can be completely resolved using just solar panels, the upper estimate falls outside this. 

This simple calculation does not satisfy the precision requirements but gives a general estimate of this study is even worth considering. Notice that this would increase fivefold when including heating, however, this is a more complex discussion, as electrical heating is more efficient, especially when using heat pumps, that is why I do not include this in a simple derivation. 

---------
### Accounting for environmental factors.

As stated in the introduction, the difficulty in calculating the effectiveness of solar panels arises from their environmental dependence. But current consumption can also vary depending on the same factors, as well as time. For example the tea kettle effect: most power plants have to increase supply during tea time because everybody is turning the tea kettle on. Or the increase in heating over winter, air conditioning in summer, etc.

As such, I added the following requirements for a model, all increasing in complexity:

1. Account for supply/demand variation over the course of a year
This gap affects how the city relies on external power. The model should be able to look at the "instantaneous" consumption and production and give better estimates of total cost reduction
2. Battery and storage
This can help increase the total energy efficiency of the model, but it increases the cost of installation. Should also account for different storage facilities.
3. Weather effects.
This can be implemented quickly by changing the efficiency coefficient on the solar panels, according to data from previous years.
4. The use of MPPT and other techniques to accommodate for variation in supply/demand. This would require modelling the city by individual sectors.

------
### Flexibility

- Apply to different regions (change houses and configuration, possibly add map)
- Use different solar panels/ technology

An interesting idea would be a follow-up on this study: 
> https://www.sciencedirect.com/science/article/pii/S1364032116302842?via%3Dihub

In theory, given a complex model that simulates the panels themselves, a neural network can be trained to optimize electrical use. 

----

## Previous studies

Currently, I haven't been able to find any similar studies. I expect however that they exist and it is just of matter of searching a bit more.

This study requires a considerable amount of research from my side. I am not extremely familiar with the subject and I can assume there would be a great deal to learn about.

This research can be broken down in:

1. Solar panel operation - how do they work
2. Electrical grid structure - what are the parameters and margins of error
3. Battery and storage options
4. Brampton - details of geography, weather and power supply
5. MPPT and other optimization techniques.


----

# Next Step

Research and write a report similar to a literature review. 