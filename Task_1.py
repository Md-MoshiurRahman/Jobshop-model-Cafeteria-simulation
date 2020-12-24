import heapq
import random
import matplotlib.pyplot as plt
import numpy as py
INF = 99999
totalSimulationTime = 8

class States:
    def __init__(self):
        self.avgQdelayperJobs = []
        self.avgQdelayTotalJobs = 0
        self.avgQlength = []
        self.avgnumofJobsInSystem = 0
        self.avgQdelayperStation = []

    def update(self, avgQdelayperJobs, avgQdelayTotalJobs, avgQlength, avgnumofJobsInSystem, avgQdelayperStation):
        self.avgQdelayperJobs = avgQdelayperJobs
        self.avgQdelayTotalJobs = avgQdelayTotalJobs
        self.avgQlength = avgQlength
        self.avgnumofJobsInSystem = avgnumofJobsInSystem
        self.avgQdelayperStation = avgQdelayperStation

    def getResults(self,sim):
        return (self.avgQdelayperJobs, self.avgQdelayTotalJobs, self.avgQlength, self.avgnumofJobsInSystem, self.avgQdelayperStation)


class Simulator:
    def __init__(self):
        self.eventQ = []
        self.queue = []
        self.simclock = 0.0
        self.states = None

        self.jobServed_Station = []
        self.Qdelay_Station = []
        self.numofJobsInSystem = 0
        self.numofJobsInSystem_time = 0
        self.jobTimer = 0
        self.numInQTimer = 0
        self.numInQChecker = []
        self.Qlength = []
        self.totalOccured = []
        self.totalServed = []
        self.Qdelay = []
        self.numofStations = 0
        self.numofmachines = []
        self.numofBGservers = []
        self.interArr_jobs = 0
        self.numofJobType = 0
        self.jobProbabilities = []
        self.cumjobProbabilities = []
        self.numofStations_Task = []
        self.stationRouting = []
        self.serviceTime_station = []




    def initialize(self):
        self.scheduleEvent()

    def configure(self, inputFile, states):
        self.states = states

        lines = inputFile.readlines()

        self.numofStations = int(lines[0])
        temp_numofmachines = lines[1].split()
        for i in temp_numofmachines:
            self.numofmachines.append(int(i))
            self.numofBGservers.append(0)
            innerQ = []
            self.queue.append(innerQ)
            self.Qlength.append(0)
            self.numInQChecker.append(0)
            self.jobServed_Station.append(0)
            self.Qdelay_Station.append(0)

        self.interArr_jobs = float(lines[2])
        self.numofJobType = int(lines[3])
        temp_jobProb = lines[4].split()
        flag = 0
        for i in temp_jobProb:
            self.jobProbabilities.append(float(i))
            self.cumjobProbabilities.append(flag + float(i))
            flag += float(i)
        temp_stations = lines[5].split()
        for i in temp_stations:
            self.numofStations_Task.append(int(i))

        index = 6
        for i in range(self.numofJobType):
            route = []
            x = lines[index].split()
            for j in x:
                route.append(int(j))
            self.stationRouting.append(route)
            index += 1

            serviceTime = []
            x = lines[index].split()
            for j in x:
                serviceTime.append(float(j))
            self.serviceTime_station.append(serviceTime)
            index += 1

            self.Qdelay.append(0)
            self.totalServed.append(0)
            self.totalOccured.append(0)


    def now(self):
        return self.simclock

    def jobType(self):
        randomValue = py.random.uniform(0,1,1)
        job = 0
        for i in range(self.numofJobType):
            if randomValue <= self.cumjobProbabilities[i]:
                job = i
                break
        return job

    def ServiceTime(self, meanTime):
        array1 = py.random.exponential((meanTime/2),1)
        array2 = py.random.exponential((meanTime/2),1)
        return float(array1[0]+array2[0])

    def jobTime(self):
        tempArray = py.random.exponential(self.interArr_jobs, 1)
        return tempArray[0]

    def scheduleEvent(self):

        job = self.jobType()
        self.totalOccured[job] += 1
        self.numofJobsInSystem += 1
        self.jobTimer = self.simclock
        nextjobTime = self.jobTime() + self.simclock
        self.eventQ.append([nextjobTime , 'newJob', 0, 0])

        #print('time-',self.simclock,' eventType-','newJob ', job)

        jobtype = job
        station = self.stationRouting[jobtype][0]
        self.numofBGservers[station-1] += 1

        #############add next depart##########
        meanTime = self.serviceTime_station[jobtype][0]
        deptime =  self.ServiceTime(meanTime) + self.simclock
        eventtype = 'Departure'
        self.eventQ.append([deptime, eventtype, jobtype, station])




    def run(self):
        self.initialize()

        while len(self.eventQ) > 0 :

            ind = self.eventQ.index(min(self.eventQ))
            eventTime, eventType, jobType, Station = self.eventQ.pop(ind)
            self.simclock = eventTime

            #print(eventTime, " ", eventType, " ", jobType," ",Station)


            if self.simclock >= (totalSimulationTime) :     ##########run will stop here###########

                avgQdelayperJobs = []
                totalQdelay = 0
                totalJobsServed = 0
                for i in range(self.numofJobType):
                    if self.totalServed[i] == 0:
                        avgQdelayperJobs.append(0)
                    else:
                        avgQdelayperJobs.append(self.Qdelay[i] / self.totalServed[i])

                #print("here")
                #print(self.Qdelay)
                #print(self.totalOccured)
                #print(self.totalServed)
                #print(avgQdelayperJobs)

                for i in range(self.numofJobType):
                    totalQdelay += self.Qdelay[i]
                    totalJobsServed += self.totalServed[i]

                avgQdelayTotalJobs = totalQdelay / totalJobsServed
                #print(avgQdelayTotalJobs)


                avgQlength = []
                for i in range(self.numofStations):
                    avgQlength.append(self.Qlength[i]/totalSimulationTime)
                #print(avgQlength)

                avgnumofJobsInSystem = self.numofJobsInSystem_time / totalSimulationTime
                #print(avgnumofJobsInSystem)

                avgQdelayperStation = []
                for i in range(self.numofStations):
                    if self.jobServed_Station[i] == 0:
                        avgQdelayperStation.append(0)
                    else:
                        avgQdelayperStation.append(self.Qdelay_Station[i] / self.jobServed_Station[i])

                #print(avgQdelayperStation)



                self.states.update(avgQdelayperJobs, avgQdelayTotalJobs, avgQlength, avgnumofJobsInSystem, avgQdelayperStation)

                break


            if eventType == 'newJob':
                self.numofJobsInSystem_time += (self.simclock - self.jobTimer) * self.numofJobsInSystem
                job = self.jobType()
                self.totalOccured[job] += 1
                self.numofJobsInSystem += 1
                self.jobTimer = self.simclock
                nextjobTime = self.jobTime() + self.simclock
                self.eventQ.append([nextjobTime, 'newJob', 0, 0])

                #print('time-', self.simclock, ' eventType-', 'newJob ', job )

                jobtype = job
                station = self.stationRouting[job][0]
                if self.numofBGservers[station - 1] < self.numofmachines[station-1]:
                    self.numofBGservers[station - 1] += 1
                    #############add next depart##########
                    meanTime = self.serviceTime_station[jobtype][0]
                    deptime = self.ServiceTime(meanTime) + self.simclock
                    eventtype = 'Departure'
                    self.eventQ.append([deptime, eventtype, jobtype, station])

                else:
                    if(len(self.queue[station - 1]) != 0):
                        xtime, xtype = self.queue[station - 1][len(self.queue[station - 1]) - 1]
                        self.Qlength[station - 1] += (self.simclock - xtime) * len(self.queue[station - 1])
                    self.queue[station-1].append([self.simclock,jobtype])



            if eventType == "Departure":
                self.jobServed_Station[Station-1] += 1

                indx = self.stationRouting[jobType].index(Station)
                if indx == self.numofStations_Task[jobType] - 1 :
                    self.numofJobsInSystem_time += (self.simclock - self.jobTimer) * self.numofJobsInSystem
                    self.totalServed[jobType] += 1
                    self.numofJobsInSystem -= 1
                    self.jobTimer = self.simclock
                    #print("Done", jobType)
                else:
                    station = self.stationRouting[jobType][indx+1]
                    if self.numofBGservers[station - 1] < self.numofmachines[station - 1]:
                        self.numofBGservers[station - 1] += 1
                        #############add next depart##########
                        indx = self.stationRouting[jobType].index(station)
                        meanTime = self.serviceTime_station[jobType][indx]
                        deptime = self.ServiceTime(meanTime) + self.simclock
                        eventtype = 'Departure'
                        self.eventQ.append([deptime, eventtype, jobType, station])
                    else:
                        if (len(self.queue[station - 1]) != 0):
                            xtime, xtype = self.queue[station - 1][len(self.queue[station - 1]) - 1]
                            self.Qlength[station - 1] += (self.simclock - xtime) * len(self.queue[station - 1])
                        self.queue[station - 1].append([self.simclock, jobType])

                if len(self.queue[Station-1]) != 0:
                    xtime,xtype = self.queue[Station-1][len(self.queue[Station-1]) - 1]
                    self.Qlength[Station - 1] += (self.simclock - xtime) * len(self.queue[Station-1])

                    eventtime, jobtype = self.queue[Station-1].pop(0)
                    self.Qdelay[jobtype] += (self.simclock - eventtime)
                    self.Qdelay_Station[Station-1] += (self.simclock - eventtime)

                    #############add next depart##########
                    indx = self.stationRouting[jobtype].index(Station)
                    meanTime = self.serviceTime_station[jobtype][indx]
                    deptime = self.ServiceTime(meanTime) + self.simclock
                    eventtype = 'Departure'
                    self.eventQ.append([deptime, eventtype, jobtype, Station])

                else:
                    self.numofBGservers[Station - 1] -= 1



    def printResults(self):
        self.states.printResults(self)

    def getResults(self):
        return self.states.getResults(self)


if __name__ == "__main__":
    inputFile = open("input.txt")

    FinalavgQdelayperJobs = []
    FinalavgQdelayTotalJobs = 0
    FinalavgQlength = []
    FinalavgnumofJobsInSystem = 0
    FinalavgQdelayperStation = []

    sim = Simulator()
    states = States()
    sim.configure(open("input.txt"), states)
    sim.run()
    temp1avgQdelayperJobs, temp1avgQdelayTotalJobs, temp1avgQlength, temp1avgnumofJobsInSystem, temp1avgQdelayperStation = sim.getResults()


    j = 0
    while j < 29 :
        sim = Simulator()
        states = States()
        sim.configure(open("input.txt"), states)
        sim.run()
        temp2avgQdelayperJobs, temp2avgQdelayTotalJobs, temp2avgQlength, temp2avgnumofJobsInSystem, temp2avgQdelayperStation = sim.getResults()

        for i in range(0, len(temp2avgQdelayperJobs)):
            FinalavgQdelayperJobs.append(temp1avgQdelayperJobs[i] + temp2avgQdelayperJobs[i])

        FinalavgQdelayTotalJobs = temp1avgQdelayTotalJobs + temp2avgQdelayTotalJobs

        for i in range(0, len(temp2avgQlength)):
            FinalavgQlength.append(temp1avgQlength[i] + temp2avgQlength[i])

        FinalavgnumofJobsInSystem = temp1avgnumofJobsInSystem + temp2avgnumofJobsInSystem

        for i in range(0, len(temp2avgQdelayperStation)):
            FinalavgQdelayperStation.append(temp1avgQdelayperStation[i] + temp2avgQdelayperStation[i])

        temp1avgQdelayperJobs = FinalavgQdelayperJobs
        temp1avgQdelayTotalJobs = FinalavgQdelayTotalJobs
        temp1avgQlength = FinalavgQlength
        temp1avgnumofJobsInSystem = FinalavgnumofJobsInSystem
        temp1avgQdelayperStation = FinalavgQdelayperStation

        FinalavgQdelayperJobs = []
        FinalavgQdelayTotalJobs = 0
        FinalavgQlength = []
        FinalavgnumofJobsInSystem = 0
        FinalavgQdelayperStation = []

        j += 1




    for i in range(0, len(temp1avgQdelayperJobs)):
        FinalavgQdelayperJobs.append(temp1avgQdelayperJobs[i] / 30 )

    FinalavgQdelayTotalJobs = temp1avgQdelayTotalJobs / 30

    for i in range(0, len(temp1avgQlength)):
        FinalavgQlength.append(temp1avgQlength[i] / 30)

    FinalavgnumofJobsInSystem = temp1avgnumofJobsInSystem / 30

    for i in range(0, len(temp1avgQdelayperStation)):
        FinalavgQdelayperStation.append(temp1avgQdelayperStation[i] / 30)



    print("Expected average total delay in queue for each job type -> ",FinalavgQdelayperJobs)
    print("Expected overall average job total delay -> ",FinalavgQdelayTotalJobs)
    print("Expected average number in each queue -> ",FinalavgQlength)
    print("Expected average number of jobs in the whole system -> ",FinalavgnumofJobsInSystem)
    print("Expected average delay in queue for each station -> ",FinalavgQdelayperStation)

    new = FinalavgQdelayperStation.index(max(FinalavgQdelayperStation))
    print("new machine will be added to station {}".format(new+1))






