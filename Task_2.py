import heapq
import random
import matplotlib.pyplot as plt
import numpy as py
INF = 99999
totalSimulationTime = 90*60

cusGrpSize = [1,2,3,4]
cusGrpProb = [0.5,0.3,0.1,0.1]
interArr_Grp = 30
ST_Hotfood = [50,120]
ACT_Hotfood = [20,40]
ST_Sandwiches = [60,180]
ACT_Sandwiches = [5,15]
ST_Drinks = [5,20]
ACT_Drinks = [5,10]
numofServer_Station = [1,1,0,2]
prob_TypesofCus = [0.8,0.15,0.05]
stationRouting = [[1,3,4],[2,3,4],[3,4]]

class States:
    def __init__(self):
        self.totalCusServerd = 0
        self.overAllavgQdelay = 0

    def update(self, overAllavgQdelay, totalCusServerd):
        self.totalCusServerd = totalCusServerd
        self.overAllavgQdelay = overAllavgQdelay

    def getResults(self,sim):
        return (self.overAllavgQdelay, self.totalCusServerd)


class Simulator:
    def __init__(self):
        self.eventQ = []
        self.queueHotFood = []
        self.queueSand = []
        self.queueCashier = []
        self.simclock = 0.0
        self.states = None
        self.Qlength = 0

        self.cusGrpSize = cusGrpSize
        self.cusGrpProb = cusGrpProb
        self.interArr_Grp = interArr_Grp
        self.ST_Hotfood = ST_Hotfood
        self.ACT_Hotfood = ACT_Hotfood
        self.ST_Sandwiches = ST_Sandwiches
        self.ACT_Sandwiches = ACT_Sandwiches
        self.ST_Drinks = ST_Drinks
        self.ACT_Drinks = ACT_Drinks
        self.numofServer_Station = numofServer_Station
        self.prob_TypesofCus = prob_TypesofCus
        self.stationRouting = stationRouting

        self.numofCusInSystem = 0
        self.maxnumofCusInSystem = 0
        self.numofCusInSystem_time = 0
        self.cusTimer = 0

        self.totalCusServerd = 0
        self.Qdelay_customer = []
        self.maxQdelay_customer = []
        self.totalServed_customertype = []
        self.cashprevtime = 0
        self.Qlength_hotfood = 0
        self.Qlength_sandwiches = 0
        self.Qlength_cashier = 0
        self.totalQlength_cashier = 0
        self.maxQlength_hotfood = 0
        self.maxQlength_sandwiches =0
        self.maxQlength_cashir = 0

        self.Qdelay_hotfood = 0
        self.Qdelay_sandwiches = 0
        self.Qdelay_cashier = 0
        self.maxQdelay_hotfood = 0
        self.maxQdelay_sandwiches = 0
        self.maxQdelay_cashier = 0

        self.totalServed_hotfood = 0
        self.totalServed_sandwiches = 0
        self.totalServed_cashier = 0
        self.cumcusGrpProb = []
        self.cumprob_TypesofCus = []
        self.numofBGservers = []
        self.numofStations_Task = []
        self.bgServersofCash = []

    def initialize(self):
        #self.simclock = 0
        self.scheduleEvent()

    def configure(self, states):
        self.states = states

        i = 0
        while i < self.numofServer_Station[3]:
            innerQ = []
            self.queueCashier.append(innerQ)
            self.bgServersofCash.append(0)
            i += 1

        flag = 0
        for i in self.prob_TypesofCus:
            self.cumprob_TypesofCus.append(flag + i)
            flag += i
            self.Qdelay_customer.append(0)
            self.maxQdelay_customer.append(0)
            self.totalServed_customertype.append(0)

        flag = 0
        for i in self.cusGrpProb:
            self.cumcusGrpProb.append(flag+i)
            flag += i

        for i in range(4):
            self.numofBGservers.append(0)

        for i in self.stationRouting:
            self.numofStations_Task.append(len(i))

    def AddEmployee(self,employee):
        if employee[0] == 1:
            self.ST_Hotfood[0] = self.ST_Hotfood[0]/2
            self.ST_Hotfood[1] = self.ST_Hotfood[1]/2
        if employee[1] == 1:
            self.ST_Sandwiches[0] = self.ST_Sandwiches[0] / 2
            self.ST_Sandwiches[1] = self.ST_Sandwiches[1] / 2
        if employee[2] == 1:
            self.numofServer_Station[3] += 1

    def now(self):
        return self.simclock

    def CustomerArrTime(self):
        tempArray = py.random.exponential(self.interArr_Grp, 1)
        return tempArray[0]

    def CustomerType(self):
        randomValue = py.random.uniform(0,1,1)
        customer = 0
        for i in range(len(self.cumprob_TypesofCus)):
            if randomValue <= self.cumprob_TypesofCus[i]:
                customer = i
                break
        return customer

    def GroupType(self):
        randomValue = py.random.uniform(0, 1, 1)
        group = 0
        for i in range(len(self.cumcusGrpProb)):
            if randomValue <= self.cumcusGrpProb[i]:
                group = i
                break
        return group

    def ServiceTime(self, station, customertype):
        #time = []
        if station == 1:
            time = py.random.uniform(self.ST_Hotfood[0],self.ST_Hotfood[1],1)
            return time[0]
        if station == 2:
            time = py.random.uniform(self.ST_Sandwiches[0],self.ST_Sandwiches[1],1)
            return time[0]
        if station == 3:
            time = py.random.uniform(self.ST_Drinks[0],self.ST_Drinks[1],1)
            return time[0]
        if station == 4:
            if customertype == 0:
                time1 = py.random.uniform(self.ACT_Hotfood[0],self.ACT_Hotfood[1],1)
                time2 = py.random.uniform(self.ACT_Drinks[0],self.ACT_Drinks[1],1)
                time = time1[0]+time2[0]
                return time
            if customertype == 1:
                time1 = py.random.uniform(self.ACT_Sandwiches[0], self.ACT_Sandwiches[1], 1)
                time2 = py.random.uniform(self.ACT_Drinks[0], self.ACT_Drinks[1], 1)
                time = time1[0] + time2[0]
                return time
            if customertype == 2:
                time = py.random.uniform(self.ACT_Drinks[0],self.ACT_Drinks[1],1)
                return time[0]



    def scheduleEvent(self):


        groupType = self.GroupType()
        groupSize = self.cusGrpSize[groupType]

        nextCusTime = self.CustomerArrTime() + self.simclock
        self.eventQ.append([nextCusTime, 'newCustomer', 0, 0, 0])

        #print('time-',self.simclock,' eventType-','newCustomer ')

        for i in range(groupSize):
            customertype = self.CustomerType()
            self.numofCusInSystem += 1
            if(self.numofCusInSystem > self.maxnumofCusInSystem):
                self.maxnumofCusInSystem = self.numofCusInSystem
            self.cusTimer = self.simclock

            station = self.stationRouting[customertype][0]
            if station == 3:
                #############add next depart##########
                deptime = self.ServiceTime(station, customertype) + self.simclock
                eventtype = 'Departure'
                self.eventQ.append([deptime, eventtype, customertype, station, 0])

            elif self.numofBGservers[station - 1] < self.numofServer_Station[station - 1]:
                self.numofBGservers[station - 1] += 1
                #############add next depart##########
                deptime = self.ServiceTime(station, customertype) + self.simclock
                eventtype = 'Departure'
                self.eventQ.append([deptime, eventtype, customertype, station, 0])

            else:
                if station == 1:
                    if (len(self.queueHotFood) != 0):
                        xtime, xtype = self.queueHotFood[len(self.queueHotFood) - 1]
                        self.Qlength_hotfood += (self.simclock - xtime) * len(self.queueHotFood)
                    self.queueHotFood.append([self.simclock, customertype])

                    if len(self.queueHotFood) > self.maxQlength_hotfood:
                        self.maxQlength_hotfood = len(self.queueHotFood)
                if station == 2:
                    if (len(self.queueSand) != 0):
                        xtime, xtype = self.queueSand[len(self.queueSand) - 1]
                        self.Qlength_sandwiches += (self.simclock - xtime) * len(self.queueSand)
                    self.queueSand.append([self.simclock, customertype])

                    if len(self.queueSand) > self.maxQlength_sandwiches:
                        self.maxQlength_sandwiches = len(self.queueSand)


    def run(self):
        self.initialize()
        #print(self.simclock, " ", "Start")

        while len(self.eventQ) > 0 :

            min = [totalSimulationTime+1000, 'xyz', 0, 0, 0]
            ind = -1
            for i in self.eventQ:
                if i < min:
                    min = i
                    ind = self.eventQ.index(i)

            #print(min)
            #print(ind)

            #ind = self.eventQ.index(min(self.eventQ))
            eventTime, eventType, customerType, Station, subStation = self.eventQ.pop(ind)
            self.simclock = eventTime

            #print(eventTime, " ", eventType, " ", customerType," ",Station)

            if self.simclock >= (totalSimulationTime):  ##########run will stop here###########
                avgQdelay_hotfood = self.Qdelay_hotfood / self.totalServed_hotfood
                avgQdelay_sandwiches = self.Qdelay_sandwiches / self.totalServed_sandwiches
                avgQdelay_cashier = self.Qdelay_cashier / self.totalServed_cashier

                #print("\n")
                #print(avgQdelay_hotfood/60," delay hot food ", self.maxQdelay_hotfood/60)
                #print(avgQdelay_sandwiches/60," delay sand ", self.maxQdelay_sandwiches/60)
                #print(avgQdelay_cashier/60," delay cashier ", self.maxQdelay_cashier/60)

                avgQlength_hotfood = self.Qlength_hotfood / totalSimulationTime
                avgQlength_sandwiches = self.Qlength_sandwiches / totalSimulationTime
                avgQlength_cashier = self.Qlength_cashier / totalSimulationTime

                #print("\n")
                #print(avgQlength_hotfood, " length hot food ", self.maxQlength_hotfood)
                #print(avgQlength_sandwiches , " length sand ", self.maxQlength_sandwiches)
                #print(avgQlength_cashier, " length cashier ", self.maxQlength_cashir)

                avgQdelay_customertype = []
                for i in range(len(self.Qdelay_customer)):
                    avgQdelay_customertype.append(self.Qdelay_customer[i] / self.totalServed_customertype[i])

                #print("\n")
                for i in range(len(avgQdelay_customertype)):
                    #print(avgQdelay_customertype[i]/60, " delay customer type ", self.maxQdelay_customer[i]/60)
                    pass

                overAllavgQdelay = 0
                for i in range(len(avgQdelay_customertype)):
                    overAllavgQdelay += (avgQdelay_customertype[i] * self.prob_TypesofCus[i])

                #print("\n")
                #print(overAllavgQdelay/60, " overall avg qdelay")

                avgnumofCusInSystem = self.numofCusInSystem_time / totalSimulationTime
                #print("\n")
                #print(avgnumofCusInSystem, " avg num of customer in system ", self.maxnumofCusInSystem)

                for i in range(len(self.totalServed_customertype)):
                    self.totalCusServerd += self.totalServed_customertype[i]

                self.states.update(overAllavgQdelay, self.totalCusServerd)

                break

            if eventType == 'newCustomer':
                #self.numofJobsInSystem_time += (self.simclock - self.jobTimer) * self.numofJobsInSystem

                #self.totalOccured[job] += 1
                #self.numofJobsInSystem += 1
                #self.jobTimer = self.simclock
                groupType = self.GroupType()
                groupSize = self.cusGrpSize[groupType]

                nextCusTime = self.CustomerArrTime() + self.simclock
                self.eventQ.append([nextCusTime, 'newCustomer', 0, 0, 0])

                #print('time-', self.simclock, ' eventType-', 'newCustomer ')

                for i in range(groupSize):
                    self.numofCusInSystem_time += (self.simclock - self.cusTimer) * self.numofCusInSystem
                    customertype = self.CustomerType()
                    self.numofCusInSystem += 1
                    if (self.numofCusInSystem > self.maxnumofCusInSystem):
                        self.maxnumofCusInSystem = self.numofCusInSystem
                    self.cusTimer = self.simclock
                    station = self.stationRouting[customertype][0]
                    if station == 3:
                        #############add next depart##########
                        deptime = self.ServiceTime(station, customertype) + self.simclock
                        eventtype = 'Departure'
                        self.eventQ.append([deptime, eventtype, customertype, station, 0])

                    elif self.numofBGservers[station - 1] < self.numofServer_Station[station - 1]:
                        self.numofBGservers[station - 1] += 1
                        #############add next depart##########
                        deptime = self.ServiceTime(station, customertype) + self.simclock
                        eventtype = 'Departure'
                        self.eventQ.append([deptime, eventtype, customertype, station, 0])

                    else:
                        if station == 1:
                            if (len(self.queueHotFood) != 0):
                                xtime, xtype = self.queueHotFood[len(self.queueHotFood) - 1]
                                self.Qlength_hotfood += (self.simclock - xtime) * len(self.queueHotFood)
                            self.queueHotFood.append([self.simclock, customertype])

                            if len(self.queueHotFood) > self.maxQlength_hotfood:
                                self.maxQlength_hotfood = len(self.queueHotFood)
                        if station == 2:
                            if (len(self.queueSand) != 0):
                                xtime, xtype = self.queueSand[len(self.queueSand) - 1]
                                self.Qlength_sandwiches += (self.simclock - xtime) * len(self.queueSand)
                            self.queueSand.append([self.simclock, customertype])

                            if len(self.queueSand) > self.maxQlength_sandwiches:
                                self.maxQlength_sandwiches = len(self.queueSand)


            if eventType == "Departure":

                indx = self.stationRouting[customerType].index(Station)
                if indx == self.numofStations_Task[customerType] - 1:
                    self.numofCusInSystem_time += (self.simclock - self.cusTimer) * self.numofCusInSystem
                    self.totalServed_customertype[customerType] += 1
                    self.numofCusInSystem -= 1
                    self.cusTimer = self.simclock
                    #print("Done", customerType)
                else:
                    station = self.stationRouting[customerType][indx + 1]
                    if station == 3:
                        #############add next depart##########
                        deptime = self.ServiceTime(station, customerType) + self.simclock
                        eventtype = 'Departure'
                        self.eventQ.append([deptime, eventtype, customerType, station, 0])

                    elif self.numofBGservers[station - 1] < self.numofServer_Station[station - 1]:
                        self.numofBGservers[station - 1] += 1
                        #############add next depart##########
                        deptime = self.ServiceTime(station, customerType) + self.simclock
                        eventtype = 'Departure'

                        if station == 4:
                            min = INF
                            ind = -1
                            for i in self.bgServersofCash:
                                if i < min:
                                    min = i
                                    ind = self.bgServersofCash.index(i)
                            self.bgServersofCash[ind] = 1
                            self.eventQ.append([deptime, eventtype, customerType, station, ind])
                        else:
                            self.eventQ.append([deptime, eventtype, customerType, station, 0])
                    else:
                        if station == 1:
                            if (len(self.queueHotFood) != 0):
                                xtime, xtype = self.queueHotFood[len(self.queueHotFood) - 1]
                                self.Qlength_hotfood += (self.simclock - xtime) * len(self.queueHotFood)
                            self.queueHotFood.append([self.simclock, customerType])

                            if len(self.queueHotFood) > self.maxQlength_hotfood:
                                self.maxQlength_hotfood = len(self.queueHotFood)
                        if station == 2:
                            if (len(self.queueSand) != 0):
                                xtime, xtype = self.queueSand[len(self.queueSand) - 1]
                                self.Qlength_sandwiches += (self.simclock - xtime) * len(self.queueSand)
                            self.queueSand.append([self.simclock, customerType])

                            if len(self.queueSand) > self.maxQlength_sandwiches:
                                self.maxQlength_sandwiches = len(self.queueSand)
                        if station == 4:
                            min = INF
                            ind = -1
                            for i in self.queueCashier:
                                if len(i) < min:
                                    min = len(i)
                                    ind = self.queueCashier.index(i)

                            if self.totalQlength_cashier != 0:
                                self.Qlength_cashier += (self.simclock - self.cashprevtime) * self.totalQlength_cashier
                            self.queueCashier[ind].append([self.simclock, customerType])
                            self.cashprevtime = self.simclock
                            self.totalQlength_cashier += 1

                            if self.totalQlength_cashier > self.maxQlength_cashir:
                                self.maxQlength_cashir = self.totalQlength_cashier


                if Station == 1:
                    self.totalServed_hotfood += 1
                    if len(self.queueHotFood) != 0:
                        xtime, xtype = self.queueHotFood[len(self.queueHotFood) - 1]
                        self.Qlength_hotfood += (self.simclock - xtime) * len(self.queueHotFood)

                        eventtime, customertype = self.queueHotFood.pop(0)
                        self.Qdelay_hotfood += (self.simclock - eventtime)
                        if (self.simclock - eventtime) > self.maxQdelay_hotfood:
                            self.maxQdelay_hotfood = (self.simclock - eventtime)
                        self.Qdelay_customer[customertype] += (self.simclock - eventtime)
                        if (self.simclock - eventtime) > self.maxQdelay_customer[customertype]:
                            self.maxQdelay_customer[customertype] = (self.simclock - eventtime)
                        #############add next depart##########
                        deptime = self.ServiceTime(Station, customertype) + self.simclock
                        eventtype = 'Departure'
                        self.eventQ.append([deptime, eventtype, customertype, Station, 0])
                    else:
                        self.numofBGservers[Station - 1] -= 1

                if Station == 2:
                    self.totalServed_sandwiches += 1
                    if len(self.queueSand) != 0:
                        xtime, xtype = self.queueSand[len(self.queueSand) - 1]
                        self.Qlength_sandwiches += (self.simclock - xtime) * len(self.queueSand)

                        eventtime, customertype = self.queueSand.pop(0)
                        self.Qdelay_sandwiches += (self.simclock - eventtime)
                        if (self.simclock - eventtime) > self.maxQdelay_sandwiches:
                            self.maxQdelay_sandwiches = (self.simclock - eventtime)
                        self.Qdelay_customer[customertype] += (self.simclock - eventtime)
                        if (self.simclock - eventtime) > self.maxQdelay_customer[customertype]:
                            self.maxQdelay_customer[customertype] = (self.simclock - eventtime)
                        #############add next depart##########
                        deptime = self.ServiceTime(Station, customertype) + self.simclock
                        eventtype = 'Departure'
                        self.eventQ.append([deptime, eventtype, customertype, Station, 0])
                    else:
                        self.numofBGservers[Station - 1] -= 1

                if Station == 4:
                    self.totalServed_cashier += 1
                    if len(self.queueCashier[subStation]) != 0:
                        if self.totalQlength_cashier != 0:
                            self.Qlength_cashier += (self.simclock - self.cashprevtime) * self.totalQlength_cashier
                        eventtime, customertype = self.queueCashier[subStation].pop(0)
                        self.cashprevtime = self.simclock
                        self.totalQlength_cashier -= 1
                        self.Qdelay_cashier += (self.simclock - eventtime)
                        if (self.simclock - eventtime) > self.maxQdelay_cashier:
                            self.maxQdelay_cashier = (self.simclock - eventtime)
                        self.Qdelay_customer[customertype] += (self.simclock - eventtime)
                        if (self.simclock - eventtime) > self.maxQdelay_customer[customertype]:
                            self.maxQdelay_customer[customertype] = (self.simclock - eventtime)
                        #############add next depart##########
                        deptime = self.ServiceTime(Station, customertype) + self.simclock
                        eventtype = 'Departure'
                        self.eventQ.append([deptime, eventtype, customertype, Station, subStation])
                    else:
                        self.numofBGservers[Station - 1] -= 1
                        self.bgServersofCash[subStation] = 0



    def printResults(self):
        self.states.printResults(self)

    def getResults(self):
        return self.states.getResults(self)


if __name__ == "__main__":
    sim = Simulator()
    states = States()
    sim.configure(states)
    sim.run()

    overAllavgQdelay, totalCusServerd = sim.getResults()
    print("normal--> ",overAllavgQdelay/60 ," ",totalCusServerd)


    sim = Simulator()
    states = States()
    sim.AddEmployee([0, 0, 1])
    sim.configure(states)
    sim.run()
    overAllavgQdelay, totalCusServerd = sim.getResults()
    print("[0, 0, 1]--> ",overAllavgQdelay / 60, " ", totalCusServerd)

    MinoverAllavgQdelay = overAllavgQdelay
    MaxtotalCusServerd = totalCusServerd
    Employee_MinQdelay = [0,0,1]
    Employee_MaxCusServed = [0,0,1]


    sim = Simulator()
    states = States()
    sim.AddEmployee([1, 0, 0])
    sim.configure(states)
    sim.run()
    overAllavgQdelay, totalCusServerd = sim.getResults()
    print("[1, 0, 0]--> ", overAllavgQdelay / 60, " ", totalCusServerd)

    if overAllavgQdelay < MinoverAllavgQdelay:
        MinoverAllavgQdelay = overAllavgQdelay
        Employee_MinQdelay = [1,0,0]
    if totalCusServerd > MaxtotalCusServerd:
        MaxtotalCusServerd = totalCusServerd
        Employee_MaxCusServed = [1,0,0]



    sim = Simulator()
    states = States()
    sim.AddEmployee([0, 1, 0])
    sim.configure(states)
    sim.run()
    overAllavgQdelay, totalCusServerd = sim.getResults()
    print("[0, 1, 0]--> ", overAllavgQdelay / 60, " ", totalCusServerd)

    if overAllavgQdelay < MinoverAllavgQdelay:
        MinoverAllavgQdelay = overAllavgQdelay
        Employee_MinQdelay = [0, 1, 0]
    if totalCusServerd > MaxtotalCusServerd:
        MaxtotalCusServerd = totalCusServerd
        Employee_MaxCusServed = [0, 1, 0]


    sim = Simulator()
    states = States()
    sim.AddEmployee([1, 1, 0])
    sim.configure(states)
    sim.run()
    overAllavgQdelay, totalCusServerd = sim.getResults()
    print("[1, 1, 0]--> ", overAllavgQdelay / 60, " ", totalCusServerd)

    if overAllavgQdelay < MinoverAllavgQdelay:
        MinoverAllavgQdelay = overAllavgQdelay
        Employee_MinQdelay = [1, 1, 0]
    if totalCusServerd > MaxtotalCusServerd:
        MaxtotalCusServerd = totalCusServerd
        Employee_MaxCusServed = [1, 1, 0]


    sim = Simulator()
    states = States()
    sim.AddEmployee([1, 0, 1])
    sim.configure(states)
    sim.run()
    overAllavgQdelay, totalCusServerd = sim.getResults()
    print("[1, 0, 1]--> ", overAllavgQdelay / 60, " ", totalCusServerd)

    if overAllavgQdelay < MinoverAllavgQdelay:
        MinoverAllavgQdelay = overAllavgQdelay
        Employee_MinQdelay = [1, 0, 1]
    if totalCusServerd > MaxtotalCusServerd:
        MaxtotalCusServerd = totalCusServerd
        Employee_MaxCusServed = [1, 0, 1]


    sim = Simulator()
    states = States()
    sim.AddEmployee([0, 1, 1])
    sim.configure(states)
    sim.run()
    overAllavgQdelay, totalCusServerd = sim.getResults()
    print("[0, 1, 1]--> ", overAllavgQdelay / 60, " ", totalCusServerd)

    if overAllavgQdelay < MinoverAllavgQdelay:
        MinoverAllavgQdelay = overAllavgQdelay
        Employee_MinQdelay = [0, 1, 1]
    if totalCusServerd > MaxtotalCusServerd:
        MaxtotalCusServerd = totalCusServerd
        Employee_MaxCusServed = [0, 1, 1]


    sim = Simulator()
    states = States()
    sim.AddEmployee([1, 1, 1])
    sim.configure(states)
    sim.run()
    overAllavgQdelay, totalCusServerd = sim.getResults()
    print("[1, 1, 1]--> ", overAllavgQdelay / 60, " ", totalCusServerd)

    if overAllavgQdelay < MinoverAllavgQdelay:
        MinoverAllavgQdelay = overAllavgQdelay
        Employee_MinQdelay = [1, 1, 1]
    if totalCusServerd > MaxtotalCusServerd:
        MaxtotalCusServerd = totalCusServerd
        Employee_MaxCusServed = [1, 1, 1]


    print(Employee_MinQdelay," ",MinoverAllavgQdelay/60)
    print(Employee_MaxCusServed," ",MaxtotalCusServerd)


