# Implementation of Popular Swarming Techniques This project implements several of the most popular swarming strategies.## Reynolds FlockingHere we implement Reynolds Rules of Flocking (or *Boids*), which is based on a balance between three steering forces:1. **Cohesion**: the tendency to steer towards the center of mass of neighbouring agents.2. **Alignment**: the tendency to steer in the same direction as neighbouring agents.3. **Separation**: the tendency to steer away from neighbouring agents. Below is a demonstration of the technique, including an additional **Navigation** term to facilitate target tracking:<p float="center">  <img src="https://github.com/tjards/swarming_sim/blob/master/Figs/animation_reynolds_01.gif" width="45%" /></p>Source: Craig Reynolds, ["Flocks, Herds, and Schools:A Distributed Behavioral Model"](https://www.red3d.com/cwr/papers/1987/boids.html), *Computer Graphics, 21(4) (SIGGRAPH '87 Conference Proceedings)*, pages 25-34, 1987.## Olfati-Saber FlockingHere we implement the 3-part distributed Olfati-Saber flocking formulation that involves the following terms:1. **Alpha-Alpha Interaction (alignment)** - encourages the agents to align in a lattice formation. The function represents other vehicles as "alpha" agents. 2. **Alpha-Beta Interaction (obstacle avoidance)** - discourages the agents from colliding with obstacles. The function represents obstacles as "beta" agents.3. **Gamma Feedback (navigation)** - encourages motion towards a static or dynamic target. The function represents the target as a "gamma" agent.When compared to the Reynolds implementation above, this results in a more structured flock with many convenient mathematical properties:<p float="center">    <img src="https://github.com/tjards/swarming_sim/blob/master/Figs/animation_worx3.gif" width="45%" />    <img src="https://github.com/tjards/swarming_sim/blob/master/Figs/animation_worx3.gif" width="45%" /></p>Source: Reza Olfati-Saber, ["Flocking for Multi-Agent Dynamic Systems: Algorithms and Theory"](https://ieeexplore.ieee.org/document/1605401), *IEEE Transactions on Automatic Control*, Vol. 51 (3), 2006.## Starling FlockingFor more natural behavior, we model of starlings as follows:1. **Cohesion**, **Alignment**, and **Separation** rules of Reynolds above.2. **Horizontal Roosting**, which encourages all agents to steer towards a central location as a function of their heading and distance away.3. **Vertical Roosting**, which encourages all agents to hover over a nest.Below is a demonstration of this roosting:<p float="center">  <img src="https://github.com/tjards/swarming_sim/blob/master/Figs/animation_starling.gif" width="45%" /></p>Source: H. Hildenbrandt, C. Carere, and C.K. Hemelrijk,["Self-organized aerial displays of thousands of starlings: a model"](https://academic.oup.com/beheco/article/21/6/1349/333856?login=false), *Behavioral Ecology*, Volume 21, Issue 6, pages 1349–1359, 2010.## EncirclementHere we formulate overlapping planes of encirclement (using quaternions) to achieve dynamic encirclement:<p float="center">  <img src="https://github.com/tjards/swarming_sim/blob/master/Figs/animation_circle_01.gif" width="45%" /></p>Source: P. T. Jardine and S. N. Givigi, ["Bimodal Dynamic Swarms"](https://ieeexplore.ieee.org/document/9857917), *IEEE Access*, vol. 10, pp. 94487-94495, 2022.## Dynamic Lemniscateto be added<p float="center">    <img src="https://github.com/tjards/swarming_sim/blob/master/Figs/animation_lemni_01.gif" width="45%" /></p># CitingThe code is opensource but, if you reference this work in your own reserach, please cite me. I have provided an example bibtex citation below:`@techreport{Jardine-2022,  title={Swarming Simulator},  author={Jardine, P.T.},  year={2022},  institution={Royal Military College of Canada, Kingston, Ontario},  type={Technical Report},}`Alternatively, you can cite any of my related papers, which are listed in [Google Scholar](https://scholar.google.com/citations?hl=en&user=RGlv4ZUAAAAJ&view_op=list_works&sortby=pubdate).# Some plots 