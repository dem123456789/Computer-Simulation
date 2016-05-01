from Node import *
from Container import *
from AbstractHost import *
import numpy as np
from globals import globals
from parameters import *

class Organ(AbstractHost):
    #retention rate.
    def __init__(self, name, id, mass, sideLength, length, start_points, end_points, health=100):
        self.name = name
        self.id = id
        self.mass = mass
        self.sideLength = sideLength
        self.length = length
        self.start_points = start_points
        self.end_points = end_points
        self.parents = []
        self.health = health
        self.bacteriaClusters = []
        self.immuneCellClusters = []
        self._sideLengthBoxes = round(0.5+((sideLength) / parameters.organ_grid_resolution))
        self._lengthBoxes = round(0.5+((length) / parameters.organ_grid_resolution))
        print(self._sideLengthBoxes)
        self._grid = np.empty((self._sideLengthBoxes, self._sideLengthBoxes, self._lengthBoxes),dtype=Container)
        #for index,container in np.ndenumerate(self._grid):
        #    container = Container()
        #    print(index)
        xs = np.random.uniform(0, self._sideLengthBoxes, 2)
        zs = np.random.uniform(0, self._sideLengthBoxes, 2)
        ys = np.random.uniform(0, self._lengthBoxes, 2)
        self._grid_entrance = Point(int(xs[0]), int(ys[0]), int(zs[0]))
        self._grid_exit = Point(int(xs[1]), int(ys[1]), int(zs[1]))
        self.volume = sideLength ** 2 * length
        self.residualVolume = 0
        self._flowEvent = []
        self.bacteriaCountHistory = []

    def getCellCountHistory(self):
        return self.bacteriaCountHistory

    def setHealth(self, heath):
        self.heath = heath
    
    def getHealth(self, heath):
        return self.health
    
    def setFlow(self, flow): #return actualFlow
        if (self.residualVolume + flow) > self.volume:
            flow = self.volume - self.residualVolume
            self.residualVolume = self.volume
        else:
            self.residualVolume += flow
        heappush(self._flowEvent, (globals.time + int(self.length / (self.getFlowVelocity() * parameters.delta_t)), flow))
        return flow

    def setParent(self, parents): #may be used to calculate this velocity
        self.parents = parents

    def addParent(self, parent):
        assert(isinstance(parent, Node))
        self.parents.append(parent)

    def addStart(self, start_point):
        assert(isinstance(start_point, Point))
        self.start_points.append(start_point)

    def addEnd(self, end_point):
        assert(isinstance(start_point, Point))
        self.end_points.append(end_point)

    def getChildren(self): #return both nodes and organs
        if not hasattr(self, '_sinks'):
            return self.edges
        
        children = []
        for edge in self.edges:
            children.append(edge)
        children.extend(self._sinks)
        return children
        
    def getFlowVelocity(self):
        return parameters.sink_velocity

    def enterImmuneCellCluster(self, cluster):
        assert(isinstance(cluster, AbstractImmuneCellCluster))
        self.immuneCellClusters.append(cluster)
        container = self._grid[self._grid_entrance.x][self._grid_entrance.y][self._grid_entrance.z]
        assert container is not None

        container.immuneCellClusters.append(cluster)
        cluster.enterHost(self)
        cluster.setRelativeLocation(self._grid_entrance)

    def exitImmuneCellCluster(self):
        for cluster in self.immuneCellClusters:
            if not cluster.canExitHost():
                continue
            point = cluster.getRelativeLocation()
            assert point is not None
            if point == self._grid_exit:
                #exit
                cluster.exitHost(self)
                self.immuneCellClusters.remove(cluster)

    def getImmuneCellCount(self):
        cellCount = 0
        if self.converge is None:
            return cellCount
        for cluster in self.immuneCellClusters:
            cellCount += node.cellCount()
        return cellCount
        
    def getBacteriaCount(self):
        bacteriaCount = 0
        for node in self.bacteriaClusters:
            bacteriaCount += node.bacteriaCount()
        return bacteriaCount
    
    def getBacteriaClusters(self):
        return self.bacteriaClusters

    def getImmuneCellClusters(self):
        return self.immuneCellClusters

    def enterBacteriaCluster(self, cluster):
        assert(isinstance(cluster, AbstractBacteriaCellCluster))
        bacteriaClusters.append(cluster)
        container = self._grid[self._grid_entrance.x][self._grid_entrance.y][self._grid_entrance.z]
        assert container is not None

        container.bacteriaClusters.append(cluster)
        cluster.enterHost(self)
        cluster.setRelativeLocation(self._grid_entrance)

    def exitBacteriaCluster(self):
        for cluster in self.bacteriaClusters:
            if not cluster.canExitHost():
                continue
            point = cluster.getRelativeLocation()
            assert point is not None
            if point == self._grid_exit:
                #exit
                cluster.exitHost(self)
                self.bacteriaClusters.remove(cluster)
                
    def interact(self):
        if not self.bacteriaClusters:
            for bacteriaCluster1 in bacteriaClusters:
                for bacteriaCluster2 in bacteriaClusters:
                    if(bacteriaCluster1.getRelativeLocation()==bacteriaCluster2.getRelativeLocation()):
                        bacteriaCluster1.inContact(bacteriaCluster2)
                        bacteriaCluster2.inContact(bacteriaCluster1)
        if not self.immuneCellClusters:
            for immuneCellCluster1 in immuneCellClusters:
                for immuneCellCluster2 in immuneCellClusters:
                    if(immuneCellCluster1.getRelativeLocation()==immuneCellCluster2.getRelativeLocation()):
                        immuneCellCluster1.inContact(immuneCellCluster2)
                        immuneCellCluster2.inContact(immuneCellCluster1)
        if not self.bacteriaClusters and not self.immuneCellClusters:
            for bacteriaCluster in bacteriaClusters:
                for immuneCellCluster in immuneCellClusters:
                    if(bacteriaCluster.getRelativeLocation()==immuneCellCluster.getRelativeLocation()):
                        bacteriaCluster.inContact(cluster)
                        immuneCellCluster.inContact(bacteriaCluster)

    def moveClusters(self):
        for index,container in np.ndenumerate(self._grid):
            assert(isinstance(container, Container))
            bacteriaClusters = container.getBacteriaClusters()
            immuneCellClusters = container.getImmuneCellClusters()
            for bacteriaCluster in bacteriaClusters:
                move_range = int(bacteriaCluster.getMoveSpeed()/parameters.organ_grid_resolution)
                concentration = []
                for i in range(-move_range,move_range+1):
                    for j in range(-move_range,move_range+1):
                        for k in range(-move_range,move_range+1):
                            concentration.append(self._grid[index[0]+i][index[1]+j][index[2]+k].getBacteriaClustersConcentration())
                min_concentration_index = concentration.index(min(concentration))
                side = 2*move_range+1
                new_x = int(min_concentration_index/side**2)
                temp = min_concentration_index % side**2
                new_y = int(temp/side)
                new_z = temp % side
                if(i != new_x and y != new_y and z != new_z):
                    self._grid[index[0]+i][index[1]+j][index[2]+k].removeBacteriaCluster(bacteriaCluster)
                    self._grid[new_x][new_y][new_z].addBacteriaCluster(bacteriaCluster)
                
            for immuneCellCluster in immuneCellClusters:
                move_range = int(immuneCellCluster.getMoveSpeed()/parameters.organ_grid_resolution)
                concentration = []
                for i in range(-move_range,move_range+1):
                    for j in range(-move_range,move_range+1):
                        for k in range(-move_range,move_range+1):
                            concentration.append(self._grid[index[0]+i][index[1]+j][index[2]+k].getImmuneCellClustersConcentration())
                min_concentration_index = concentration.index(min(concentration))
                side = 2*move_range+1
                new_x = int(min_concentration_index/side**2)
                temp = min_concentration_index % side**2
                new_y = int(temp/side)
                new_z = temp % side
                if(i != new_x and y != new_y and z != new_z):
                    self._grid[index[0]+i][index[1]+j][index[2]+k].removeImmuneCellClusterCluster(immuneCellCluster)
                    self._grid[new_x][new_y][new_z].addImmuneCellClusterCluster(immuneCellCluster)
    
    def timeStep(self):
        #Move, Grow bacteria
        for cluster in self.bacteriaClusters:
            cluster.timeStep(self)

        #Immune response -> move, attack bacteria, remove infected host cells
        for cluster in self.immuneCellClusters:
            cluster.timeStep(self)
        
        while len(self._flowEvent) > 0 and self._flowEvent[0][0] <= globals.time:
            (time, flow) = heappop(self._flowEvent)
            self.residualVolume -= flow
            assert(self.residualVolume > 0)

        #Calculate new cells position
        self.moveClusters()
            
        #Interactions betwee cell clusters
        self.interact()
        #exits
        self.exitBacteriaCluster()
        self.exitImmuneCellCluster()
        if globals.time % parameters.cell_count_history_interval == 0:
            self.bacteriaCountHistory.append(self.getBacteriaCount())

    def __repr__(self):
        return "Organ: " + self.name + "\n" \
            + "    id: " + str(self.id) + " mass: " + str(self.mass) + " \n" \
            + "    length: " + self.length + "\n" \
            + "    side length: " + self.sideLength + "\n" \
            + "    health: " + self.health + "\n" \
