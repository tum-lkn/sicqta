import random
import numpy
from matplotlib import pyplot as plt
import csv
'''
INPUT VARIABLES
n:          the number of active devices in the network
id_length:  if given, all the binary id strings will be in certain length.
'''


def initialiseIDs(id_length,n):
    '''
    Given parameters n(the number of active devices in the network) and id_length(The length of the binary ID string),
    then n random unique binary ID strings will be generated, each represents a device in the network
    '''
    id_max = 2**id_length - 1
    for i in range(n):
        id = random.randint(0,id_max)
        if id in id_list_int:       #ensure all the IDs are unique
            while(id in id_list_int):
                id = random.randint(0,id_max)
        id_list_int.append(id)
    for a in id_list_int:
        id_bin = ("{:0%db}"%(id_length)).format(a) # here addtional prefix (like"00" or "11") can be added
        ID_list.append(id_bin)
    return ID_list

def responseToquery(query):
    '''
    If the query is a prefix to a device, then this device will repond to the gateway.
    This function will return:
        0 if no devices responded 
        2 if more than 1 devices reponded (caused collision)
        "ID"  if only one ID successfully transmitted
    '''
    counter = 0
    for i in ID_list:
        if i.startswith(query):
            counter += 1
            res_id = i
    if counter > 1:
        return 2    # functions returns 2 when theres a collision
    if counter == 1:
        return res_id # if only one ID successfully transmitted, returns the ID
    if counter == 0:
        return 0    # returns 0 if no reponse.

def queryTree():
    '''
    Simulate the querytree algorithm,
    at the end, the number of slots needed to resolve the collision will be returned
    '''
    slot = 1
    query_list = ['0','1'] # the query list corresponding to the Q in algorithm
    Memory_list = [] # memory list of the gateway, corresponding M in the algorithm
    while(len(query_list)!=0):
        slot += 1
        q = query_list[0] # q is the query sended by the gateway at the beginning of each time slot
        #print(q)
        response = responseToquery(q)
        if response == 0:   #if no response, delete the query from list
            query_list.remove(q)
        elif response == 2:     # if collided, append "q0" and "q1" to the list
            q1 = q + '0'
            q2 = q + '1'
            query_list.append(q1)
            query_list.append(q2)
            query_list.remove(q)
        else :
            Memory_list.append(response)
            query_list.remove(q)
    #print(Memory_list)
    #print ("QT:    %d slots"%slot,file=f)
    return slot

def rdm(p): #for SICTA,generate '0' with probablity of p, or '1' otherwise
    '''
    a random simulator, it returns 0 with probability p, returns 1 with probability of "1-p"
    '''
    a = random.random()
    if a < p:
        return 0
    else:
        return 1


def calcuK(reception,slot=0):
    '''
    For SICTA and SICQTA, calculate the feedback k, where k means how many packet or empty slot
    are decoded after one successful transmission
    '''
    k = 1  #Because the Pre-condition to calculate k is "already one successful transmission"
    i=0
    while(1):
        flag = 0
        buff=[]
        a = reception[-2-i].copy() #Father of the successful transmitted slot
        if (2+i) == len(reception): #when Father is the same as the first slot, it comes to end.
            flag = 1
        b = reception[-1-i].copy()  #the successful transmitted slot
        for ele in b:
            a.remove(ele)  # Interference Cancellation
        buff = a
        if len(buff) > 1:  # No single ID is decoded from SIC(after Cancellation, still collision)
            break
        else:   #After Cancellation, one ID is successfully decoded
            k = k + 1
            i += 1
            if len(buff)==1:
                memory_list.append(buff[0])
                res_list.append(slot)
            if flag == 1:
                break
    return k

def SICTA():
    '''
    simulate the SICTA algorithm,
    at the end, the number of slots needed to resolve the collision will be returned
    '''
    slot = 0
    end_con = 0
    sicta_id = [] # local counter of each ID
    gateway= []   # Gateway received IDs from each time slot
    buffer = []
    for i in ID_list: #Initailise all local counter to '0'
        sicta_id.append([i,0])
    while (end_con!= 1):
        slot += 1
        buffer = []
        for i in sicta_id: # when counter is '0'. this device can send its ID
            if i[1] == 0:
                buffer.append(i[0])
        response = len(buffer) #detect if there's a collision(when response>1)
        gateway.append(buffer)
        if response > 1: #according the algorithm in PAPER 7
            for i in sicta_id:
                if i[1] > 0:
                    i[1] += 1
                if i[1]==0:
                    i[1]=rdm(p)
        if response == 0: #according the algorithm in PAPER 7
            #slot = slot - 1 #MTA! saves one slot if empty slot(doesn't work by rdm method)
            for i in sicta_id:
                if i[1]>1:
                    pass
                if i[1]==1:
                    i[1] = rdm(p)
        if response == 1: #according the algorithm in PAPER 7
            memory_list.append(buffer[0])
            tmp=[]
            for emp in gateway: # Delete the empty slots(1.NULL Transmission.2.some slots are decoded)
                if emp != []:
                    tmp.append(emp)
            gateway=tmp
            k=calcuK(gateway)   # Calculate the feedback K
            for c in range(k):
                gateway.pop()   # pop out the decoded(saved through SIC) time slots fron gateway
            sicta_id_copy = sicta_id.copy()
            for i in sicta_id:
                i[1] = i[1]-(k-1)
                if i[1]<= 0:
                    #i[1]=-100  #to enhance the ID-Quit Condition, i set all decoded to -100
                    for j in gateway:
                        if i[0] in j:
                            j.remove(i[0])  #remove the decoded IDs from each slot
                    sicta_id_copy.remove(i)
                   # end_con += 1    # each time an ID is decoded, end_con + 1
                elif i[1] == 1:
                    i[1]=rdm(p)
            sicta_id = sicta_id_copy.copy()
        if len(sicta_id)==0:
            end_con = 1
    # double check if all the IDs are decoded.
    for check in ID_list:
        if check not in memory_list:
            print(check,file=f),
            print("not decoded",file=f)

    #print ("SICTA: %d slots"%slot,file=f)
    return slot

def feedbackToSICQT(query): # By SICQT, all the slots received by gateway must be saved for SIC
    '''
    This function is for the SICQTA algorithm, it saves the response from each slot for the future use.
    '''
    receiving = []
    for i in ID_list:
        if i.startswith(query):
            receiving.append(i)
    return receiving

def SICQT(): #with shortcutting
    '''
    Simulate the SICQTA algorithm,
    at the end, the number of slots needed to resolve the collision will be returned
    '''
    slot = 1 # all the IDs transmitted already in the first slot!
    query_brother = [] # saves the brother of each time slot, so we know which query-slot to skip later
    received = [] # all received time slots are saved here
    re_id_tmp = ID_list.copy()
    received.append(re_id_tmp) # initialise first time slot with all IDs
    q = '0' # initalise first query with '0'
    end_con = 0
    while(end_con!=1):
        buffer = []
        q_b = q[:-1] +'1' #the brother of query
        slot += 1
        buffer = feedbackToSICQT(q)
        if len(buffer) == 0:
            q = q_b+'0' # if no response, append '0' to the last q_b, but not append q_b to list querybrother
        elif len(buffer) > 1:
            query_brother.append(q_b) #append q_b to list querybrother
            q = q + '0'
            received.append(buffer)
        elif len(buffer) == 1 :
            query_brother.append(q_b)
            memory_list.append(buffer[0]) # save the decoded IDs. which must be the same as ID_list in the end
            res_list.append(slot)
            received.append(buffer)
            k=calcuK(received,slot)
            if k > len(query_brother): #end condtion when k> existed time slots, means it goes all way back to first slot
                end_con = 1
                break
            pos_in_qbrother = -1 - (k-1) # find out which query can be skipped
            q = query_brother[pos_in_qbrother] + '0' # the next query is the + '0'
            query_brother = query_brother[:pos_in_qbrother] #delete the skipped query
            for a in range(k):
                received.pop()
                
            for j in received: # delete the decoded IDs from list 'received'
                for suc in memory_list:
                    if suc in j:
                        j.remove(suc)

    # double check if all the IDs are decoded.
    for check in ID_list:
        if check not in memory_list:
            print(check,file=f),
            print("not decoded",file=f)



def possion(interval,lamda):
    '''
    Generate new income users according to a possion destrubution
    '''
    total=0
    for i in range(interval):
        come=numpy.random.poisson(lamda)
        total=total+come
    return total

def delay(lamda):
    '''
    Use SICQTA to resolve a dynamic collision-resolving problem with parameter lamda for possion,
    in the end the delay will be returned after accepting 30000 new incomers.
    '''
    global ID_list,memory_list,id_list_int,res_list
    total_user=0
    interval=100  #initalise first collision by assuming theres a CRI before 
    result=[]   
    while(total_user<30000):
        ID_list=[]
        memory_list=[]
        id_list_int=[]
        user_nr=possion(interval,lamda)
        if user_nr == 0:
            user_nr=1
        total_user += user_nr
        id_length = ??? 
        ID_list=initialiseIDs(id_length,user_nr) 
        if user_nr == 1:
            res_list=[1]
        else:
            res_list=[]
            SICQT()
        res_list = list(numpy.asarray(res_list) + interval/2)
        result = result + res_list
        interval=res_list[-1]
    return result

if __name__ == '__main__':
    '''
    Main function: Test for different possion parameter lamda from 0 to 1,
    in the end a csv file will be generated, which records the average delay of corresponding lamda
    '''
    f = open("test_possion.csv","a",newline='')
    csv_writer=csv.writer(f)
    csv_writer.writerow(['lamda','mean-delay'])
    lamda=0.1
    for i in range(20):
        lamda=lamda+0.05
        a=delay(lamda)
        row=[lamda,numpy.mean(a)]
        csv_writer.writerow(row)

