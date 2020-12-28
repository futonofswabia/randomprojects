# Ben Cederlind
# HW6 CSUS CSC 148
# There are some booleans leftover from testing

# This code simulates the creation and resupply of multiple home depot stores by a single warehouse
# Alot of this code could be further optimized btw.
import simpy as simp
import random as rnd
import numpy as np
import pdb

seedName = 25654
np.random.seed(seedName)

env = simp.Environment()
runDuration = 168 #How long it will run for
sharedevents = [None]*21 # Each HD is numbered 1-20 an array is 0-20 so i made it 21 where sharedevent[0] is always empty because there is no hd 0 store
# Shared events timer

totalrestocks = [0]*21
totalstockouts = [0]*21

# doEvents is a global function that assigns and processes the shared event
def doEvent(i):
    if sharedevents[i.hnum] is not None:
        print("Start scheduling & delivering restock to " + i.Hname + " at time " + str(env.now)) 
        yield env.timeout(int(np.random.uniform(2,4)))
        sharedevents[i.hnum].succeed()
        sharedevents[i.hnum] = None    
        i.restock()  # I called restock directly from this function
        totalrestocks[i.hnum] = totalrestocks[i.hnum] + 1

# Warehouse
class W:
    wname = ""
    def __init__(self,env,wname):
        self.env = env
        self.numberofhd = 20
        self.wname = wname
        self.dispatched = False
        self.dispatcher = env.process(self.dispatch())
        print("Running class Warehouse ___init___ fcn at time " + str(env.now) + " for warehouse " + wname + "  //numPy seed is " + str(seedName)) 
        print("Creating " + str(self.numberofhd) + " HD stores")
        
    def inithd(self,hd,amt,name,rp):
        hd.initinv(amt,name,rp)
        
    def dispatch(self):
        while True:
            if env.now % 4 == 0:    # Every 4 T U will print out current HD's waiting for restock
                tmp = "RPT:: The HDks with pending restocks at time " + str(env.now) + " :: [ "
                for i in range (21):               
                  if sharedevents[i] is not None:  # Validate shared event
                   tmp = tmp + " 'HDk" + str(i) + "' , "    
                print(tmp + " ]")  
            try:
               yield env.timeout(1)  # this try doesnt need to do anything so i just had it yield
            except simp.Interrupt as interrupt:  # Interrupt function here
                self.dispatched = True
                print("!!  HD " + interrupt.cause.Hname + " is interrupting warehouse " + self.wname + " at time " + str(env.now))               
                sharedevents[interrupt.cause.hnum] = env.event() # The shared event is created here
                env.process(doEvent(interrupt.cause))            # Global function that will process shared events is called here
                self.dispatched = False

               

# Home Depot
class H:
    maxinv = 100
    curinv = 100
    hnum = 0
    Hname = ""
    orderNumtotal = 0
    ran = 0;
    rpvalue = 50
    restockevent = False
    stockout = False
    stockoutnumber = 0
    temp = 1
    
    def __init__(self,env):   
        self.env = env
        self.orderNumtotal = 0
        self.ran = 0
        self.rpval = 50
        self.tempvar = 0        #if out of stock will process order after restock
                
    # Instead of assigning a string Hname, I assigned a number so the shared event can be accessed from the array
    # The name is constructed later
    def initinv(self,invamt,Hname,rpvalue):
        self.maxinv = invamt
        self.curinv = invamt
        self.hnum = Hname
        self.Hname = "H" + str(Hname)
        self.rpvalue = rpvalue
        
        print("Running " + self.Hname + " ___init___fcn at time " + str(env.now) + " Init.  Inventory & RP values: " + str(self.maxinv) + " & " + str(self.rpvalue))

    # This function is no longer needed
    def bfunc(self):
       while env.now < runDuration:
            yield env.timeout(1)
       print("Finished HD " + self.Hname + " Ops at time " + str(env.now) + " with inventory " + str(self.curinv))  
       self.orderNumtotal = env.now

    # Restock event
    # Stockout order should be processed with this
    def restock(self): 
        while self.restockevent == True:
            self.curinv = self.maxinv-self.ran  # Will set current inventory to the max
            self.temp = 1 # resets temp to a number > 0 if it is negative
            self.restockevent = False
            self.stockout = False  
            
            # If there was a stockout the cur inv will be max - missed order
            print(self.Hname + " completed re-stocking, resuming w. I(t) = " + str(self.curinv) + " at time " + str(env.now))  

    # Customers Order
    def genOrders(self):
        while env.now < runDuration: # Loops forever
            if self.curinv <= self.rpvalue:  # If RP than trigger restock
                if self.restockevent == False:
                    W1.dispatcher.interrupt(self)   
                    self.restockevent = True
            if self.stockout == False:  # This boolean is no longer used (bug)
                yield env.timeout(int(np.random.uniform(1,3)))
                self.ran = int(np.random.uniform(10,45))
                self.temp = self.curinv - self.ran
                if self.temp <= 0:
                    print("Stockout occured for " + self.Hname + " at time " + str(env.now))
                    totalstockouts[self.hnum] = totalstockouts[self.hnum] + 1
                    if sharedevents[self.hnum] is not None:
                        yield sharedevents[self.hnum]  # Will yield here for the restock to finish
                else:
                    self.curinv = self.temp             # process order as normally this should be skipped if a stockout has occured
                    print(self.Hname + " inventory level is " + str(self.curinv) + " at time " + str(env.now)) 
            
    # Initializes the processes for the cj orders        
    def doRun(self):
        #env.process(self.bfunc())
        env.process(self.genOrders())
        print("Starting doRun() for " + self.Hname + " at time " + str(env.now))

           


# Run Sim
# This is a terrible way to do this code wise but it works
W1 = W(env, "Warehouse1")

# Make HD
H1 = H(env)
H2 = H(env)
H3 = H(env)
H4 = H(env)
H5 = H(env)
H6 = H(env)
H7 = H(env)
H8 = H(env)
H9 = H(env)
H10 = H(env)
H11 = H(env)
H12 = H(env)
H13 = H(env)
H14 = H(env)
H15 = H(env)
H16 = H(env)
H17 = H(env)
H18 = H(env)
H19 = H(env)
H20 = H(env)

# Initialize HD Maxinventory, Hdnumber, RPvalue
W1.inithd(H1,400,1, 50)
W1.inithd(H2,200,2, 50)
W1.inithd(H3,200,3, 50)
W1.inithd(H4,200,4, 50)
W1.inithd(H5,200,5, 50)
W1.inithd(H6,200,6, 50)
W1.inithd(H7,200,7, 50)
W1.inithd(H8,200,8, 50)
W1.inithd(H9,200,9, 50)
W1.inithd(H10,200,10, 50)
W1.inithd(H11,200,11, 50)
W1.inithd(H12,200,12, 50)
W1.inithd(H13,200,13, 50)
W1.inithd(H14,200,14, 50)
W1.inithd(H15,200,15, 50)
W1.inithd(H16,200,16, 50)
W1.inithd(H17,400,17, 50)
W1.inithd(H18,200,18, 50)
W1.inithd(H19,200,19, 50)
W1.inithd(H20,200,20, 50)

# Make a process for dispatch
env.process(W1.dispatch())

# Call function that will monitor the hd functions
H1.doRun()
H2.doRun()
H3.doRun()
H4.doRun()
H5.doRun()
H6.doRun()
H7.doRun()
H8.doRun()
H9.doRun()
H10.doRun()
H11.doRun()
H12.doRun()
H13.doRun()
H14.doRun()
H15.doRun()
H16.doRun()
H17.doRun()
H18.doRun()
H19.doRun()
H20.doRun()


# Begin simulation
env.run(until = runDuration)
print("Finished run at model time " + str(env.now))

stockoutstring = "Total number of stockouts, by HD number  [ "
stockoutrunningtotal = 0
restockrunningtotal = 0
for i in range(21):
    if i >0:
        stockoutstring = stockoutstring + str(totalstockouts[i]) + ", "
        stockoutrunningtotal = stockoutrunningtotal + totalstockouts[i]
        restockrunningtotal = restockrunningtotal + totalrestocks[i]
print(stockoutstring + "]")
stockoutrunningtotal = stockoutrunningtotal/20
restockrunningtotal = restockrunningtotal/20
print("Grand total number of stockouts over all HDk " + str(int(stockoutrunningtotal)))
print("Grand total number of restocks completed over all HDk " + str(int(restockrunningtotal)))