import numpy as np
import scipy.stats as sc
import matplotlib.pyplot as plt
%matplotlib inline
import pandas as pd
np.random.seed(0)
import math

# General class for the queues themselves
class Queue(object):
    
    name = ""
    capacity = 1
    serviceRate = 1
    serversOn = 0
    waitingentities = []
    
    # Initialize a Queue
    def __init__(self, name, capacity, serviceRate, serversOn, waiting, inSystem):
        self.name = name
        self.waitingentities = waiting
         #servers
        self.capacity = capacity
        self.serviceRate = serviceRate
        self.serversOn = 0
        self.inSystem = inSystem
        
    # Print a Queue (just its name and the entire list of waiting Entities)
    def __repr__(self):
        queue = self.name + " queue: " + str(self.waitingentities) 
        system = self.name + " system: " + str(self.inSystem) 
        return queue + " \n " + system
    
    # A new Entity arrives at this Queue
    def ArriveatQueue(self, newarrival):
        self.waitingentities.append(newarrival)
        self.waitingentities.sort(key = lambda x: x.fee, reverse = True)
      
    def FinishBlock(self, currentBlock):
        newentities = []
        for e in range(currentBlock,np.size(self.waitingentities)):
            newentities.append(self.waitingentities[e])
        self.waitingentities = newentities  
    
    def inSys(self):
        return np.size(self.waitingentities)
                    

# General class for the entities that move through the Queues
class Entity(object):    
    starttime = 0
    value = 0
    feerate = 0
    fee = 0    
    # Initialize an Entity
    def __init__(self, start, val, f):
        self.starttime = start
        self.value = val
        self.feerate = f
        self.fee = f*val        
    # Print an Entity (just arrival time)
    def __repr__(self):
        return str(self.starttime)
      
      
################################################################################
################################################################################

#Parameters
mu = 10 #block mining rate; upper bound = 30/hr
K = 20 #number of transactions per block
lam = 120 #transaction arrival rate; reccomended 120/hr
N = 10 #number of active miners
mineRate = N*mu #exponential race between all miners
totalRate = mineRate + lam

pendingTransactions = Queue("pendingTransactions", N, mineRate, 1, [],[])

# Store data
times = []
transactionQlength = [] #record queue length of diagnosis
timeinSys = []  #record total time in system for patient
feeRate = [] #record the rate that was collected to average later
feeAmount = []
through = []


#adding as a test for delay in system - Zoe
delayInfo = []


#initializations for the loop
currentBlock = 0
t_end = 1 #length of the simulation
t = 0 #start
throughput = 0
 
while (t < t_end):
  nextEventTime = t + np.random.exponential(1/totalRate)
  t = nextEventTime
  U = np.random.rand()
  if U <=mineRate/totalRate:
    event = 0 #a miner posts a block
  else:
    event = 1 #a transaction arrives
  
  # Do the events corresponding to whatever the "soonest" next time is
  
  if event == 0: # a miner posts a block, multiple transactions leave the queue
    #post the block
    for i in range(currentBlock):
      #donezo = pendingTransactions.LeaveQueue()
      #timeinSys.append(t - donezo.starttime) 
      timeinSys.append(t-pendingTransactions.waitingentities[i].starttime)
      
      # delay in system
      delayInfo.append(pendingTransactions.waitingentities[i].fee)
      
    pendingTransactions.FinishBlock(currentBlock)
    #get the new block to be posted next time
    throughput = throughput + currentBlock
    currentBlock = min(pendingTransactions.inSys(), K)
    
    
    
  else: #arrival to the queue
    #add random valued transaction - between 5 and 25 - to the queue
    #get a random fee - uniform 1 or 2 percent
    arrivalVal = np.random.randint(5, 26)
    rate = 0
    U = np.random.rand()
    if(U <= 0.5):
      rate = 0.01
    else:
      rate = 0.02
    newArrival = Entity(t, arrivalVal, rate)
    pendingTransactions.ArriveatQueue(newArrival)
    feeRate.append(rate)
    feeAmount.append(rate*arrivalVal)
    
             
  # Record data
  times.append(t)
  transactionQlength.append(np.size(pendingTransactions.waitingentities))
  through.append(throughput)
    
# Make an informative plot of queue length over time
plt.figure(figsize=(12,8))
plt.step(times, transactionQlength, label="Queue", where='post')
plt.ylabel("Queue Length")
plt.xlabel("Time")
plt.legend()
plt.title("Length of BRC transactions in system over simulation")
plt.show()

plt.figure(figsize=(12,8))
plt.step(times, through, label="throughput", where='post')
plt.ylabel("throughput Length")
plt.xlabel("Time")
plt.legend()
plt.title("throughput over life of simulation")
plt.show()



# delay in system
set_fees = list(set(delayInfo))
delay_list = {set_fees[i]: [] for i in range(len(set_fees))}
for i in range(len(timeinSys)):
  delay_list[delayInfo[i]].append(timeinSys[i])
avg_delay = {i: np.mean(delay_list[i]) for i in delay_list}
avg_delay = dict(sorted(avg_delay.items()))

delay_fees = [i for i in avg_delay]
delay_time = [avg_delay[i] for i in avg_delay]

plt.figure(figsize=(12,8))
plt.step(delay_fees, delay_time, label="Time in system", where='post')
plt.ylabel("time in system")
plt.xlabel("transaction fee offered")
plt.legend()
plt.title("Delay in system")
plt.show()

print("Overall Cumulative Fees Paid over time = BRC's entering the system:", overallCumulativeFees)
print("Fees Paid into the system per hour=", overallCumulativeFees/t_end)
print("Average time in system", np.average(delay_time))
print("Average transaction amt", np.average(feeAmount))
