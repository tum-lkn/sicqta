# Introduction
This is a python-based implementation of the SICQTA, as well as traditional Query Tree and SICTA to compare the   
performance of each algorithm.
## Static_simulation
In this simulation, a group of unique IDs will be generated and we let all 3 algorithms to identify them individually.  
We record the needed time slots for the whole identification process as a metric of the performance.  
**For convenient, a loop is pre-writen, where the above process will be repeated for different groups with different active user numbers.**   
*E.g. on line 249, for active in range(2,2**id_length+1,2), the first group contains 2 users, and add 2 more users after each time, until the group with 2^id_length(Maximum) users*   
### Parameters
1 parameter must be given: on line 248: id_length. (the length of the binary ID strings)  
1 optional parameter on line 260: p=0.5. It's the probability for SICTA only.  
Furthermore, the loop times and active user numbers can be changed as needed.  

## Dynamic_simulation
In this simulation, unlike Static_simulation, there will be new incomers into the network, which is simluated  
by a possion probability. And the delay will be calculated as the metric of the performance.  
**For convenient, a loop is pre-writen, where the above process will be repeated for different lamda(possion parameter) from 0 to 1.**
### Parameters
1 parameter must be given: on line 272: id_length. (the length of the binary ID strings).  
#### Optional parameters: 
End condition: In default the simulation will end after 30000 new incomers(line 264).  
lamda: on line 293, change the loop condition.



