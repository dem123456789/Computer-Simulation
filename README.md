# Computer Simulation

Computer Simulation Projects involving Cellular Automata, Event-driven, Agent-driven conceptual model, etc.
![Visulization](https://raw.githubusercontent.com/dem123456789/Computer-Simulation/master/Generic%20Bacteria%20Simulation%20on%20Human%20Body/pic/Screen%20Shot%202016-05-14%20at%2012.38.40%20AM.png "Visulization")
## Introduction

1. This Project is inspired by a course project from CX 4230 in Georgia Tech.
2. We realize there is a shortage of biological data and simulation. For the past 60 years, no detailed and comprehensive human body data and simulation model are publically available. We focus on human body biological simulation based on real anatomical data.

## 1.0
1. Initial commits including all in-class labs and projects to github.
2. Decide to move forward from Project 3

#### Segregation
1. Use cellular automata to model human migration and segregation
2. Parameters like size of world MxN and probability of occupation and migration are included for simulation.
3. Interaction enabled with Jupyter Notebook

#### Diffusion of Infection and Campus Evacuation
##### Part A
1. Use diffusion-based simulation and cellular automata to model propogation of infectious disease
2. Use ODE solver to solver Ficks' second law  
3. Introduce variations of simulation [1]
4. Interaction enabled with Jupyter Notebook

##### Part B&C
1. Use Event-driven simulation to model emergency evacuation of Georgia Tech traffic
2. Topological data of real Gatech data is used to setup the world.
3. Parameters like intersection mode, and randomness are enabled

#### Generic Bacteria Simulation on Human Body
1. Use biological data and VTK (Visuliation Tool Kit) to model and visualize human body, arterial system and organs [2][3]
2. Offer cellcluster and host interface for organs, immune and bacterial clusters
3. Create test immune and bacterial clusters for simulation
4. Model organ as 3D matrix with cellular automata
5. Model interaction and migration of cellclusters with Event-driven and agent-driven simulation
6. Plot blood residual flow and cellcluster flow for simulation
7. Attend final poster session to present our work

#### Future Work
1. Retrieve government anatomical data to generate mathematical data for simulation and visulization based on OpenCV
2. Optimize data structure and conceptual model for simulation
3. Document details for our development process

#### Source
[1] Dianne P. O’Leary, Scientific Computing with Case Studies, SIAM Press, Philadelphia, 2009.  
[2] Avolio, A. P., A model of the human arterial system was constructed based on the anatomical journal article. Medical and  Biological Engineering and Computing 1980;18(6):709-18  
[3] Freitas, Robert A. Nanomedicine, Volume I: Basic Capabilities. Austin: Landes Bioscience, 1999. Web.


## Contributing

1. Fork
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request




## Credits

*Enmao Diao  
HaoLi Du*

