#!/usr/bin/env python


import sys
import glob
from collections import defaultdict


#-----------houseInfo Loading (Record-> HID) -------------

#load in the house ID's for each record
try:
    HID_71 = open("houseInfo/fc1871_hhid.csv", 'r') # household Ids file
except IOError:
    print 'Can\'t open file for reading1.'
    sys.exit(0)
    
try:
    HID_81 = open("houseInfo/fc1881_hhid.csv", 'r') # household Ids file
except IOError:
    print 'Can\'t open file for reading1.'
    sys.exit(0)    
    
id71_to_HID = dict() # Record number -> house number
id81_to_HID = dict()

for line in HID_71:

    line = line.strip()
    house_id = line.split(",")
    id71_to_HID[house_id[0]] = house_id[1]
    
for line in HID_81:

    line = line.strip()
    house_id = line.split(",")
    id81_to_HID[house_id[0]] = house_id[1]

    
HID_71.close()
HID_81.close()


#--------------------------------------------------------#

#Stores each line of the censuses, for looking up age, etc.
try:
    census71 = open("census/1871.csv", 'r') # 1871 Census file
except IOError:
    print 'Can\'t open file for reading.'
    sys.exit(0)
    
try:
    census81 = open("census/1881.csv", 'r') # 1881 Census file
except IOError:
    print 'Can\'t open file for reading.'
    sys.exit(0)
    
    
censusRecords_71 = dict()   
censusRecords_81 = dict() 


for line in census71:
    line = line.strip()
    el=line.split(",")
    censusRecords_71[el[0]] = line
    
    
for line in census81:
    line = line.strip()
    el=line.split(",")
    censusRecords_81[el[0]] = line

census71.close()
census81.close()

# --------------------------------------------------

try:
    file_IN = open(sys.argv[1], 'r') #open file that has the 1:1 links
except IOError:
    print 'Can\'t open file for reading.'
    sys.exit(0)

try:
    fileLinks = open(sys.argv[2], 'w')  # file for writing out the couple links found
except IOError:
    print 'Can\'t open file for reading.'
    sys.exit(0)

coupleHID_71 = defaultdict(list) # set up as 71HID -> [(71ID, 81ID, Gender), ...]
    

# go through each line of the file and update the dicts   
for line in file_IN:

    line = line.strip()
    el=line.split(",")
    
    #pull out the corresponding census infomation for the record-pair
    el_71Rec = (censusRecords_71[el[0]]).split(",")
    el_81Rec = (censusRecords_81[el[1]]).split(",")
    
    # is each record seen as married through time? Have their genders stayed the same through time and are not empty?
    if(el_71Rec[7] == "1" and el_81Rec[7] == "1" and el_71Rec[4] == el_81Rec[4] and el_71Rec[4] != ""):

        # does each record have a household?
        if(el[0] in id71_to_HID and el[1] in id81_to_HID):
        
            household_71 = id71_to_HID[el[0]]
            coupleHID_71[household_71].append(el[0]+","+el[1]+","+el_71Rec[4])  # put the couple in it's repective 71 household: 71ID, 81ID, Gender (1 = male, 0 = female)

count_sameGend = 0
count_diff81H = 0

count_singleM = 0
count_moreM = dict()
    
         
for hid_71 in coupleHID_71:

    if( len(coupleHID_71[hid_71]) == 2):
            
        # store the break down of each record in the household
        A_Record = (coupleHID_71[hid_71][0]).split(",")
        B_Record = (coupleHID_71[hid_71][1]).split(",")
        
        # are the genders opposite?
        if( A_Record[2] != B_Record[2] ):
        
            # are the records in the same 81 HID?
            if( id81_to_HID[ A_Record[1] ] == id81_to_HID[ B_Record[1] ] ):
            
                # writes out male71 info : male81 info || female71 info : female81 info
                if( A_Record[2] == "0"):
                    fileLinks.write(censusRecords_71[B_Record[0]]+":"+censusRecords_81[B_Record[1]]+"||"+censusRecords_71[A_Record[0]]+":"+censusRecords_81[A_Record[1]]+"\n")
                else:
                    fileLinks.write(censusRecords_71[A_Record[0]]+":"+censusRecords_81[A_Record[1]]+"||"+censusRecords_71[B_Record[0]]+":"+censusRecords_81[B_Record[1]]+"\n")
            else:
                count_diff81H += 1   
        else:
            count_sameGend += 1
              
    elif( len(coupleHID_71[hid_71]) == 1):
        count_singleM += 1
    else:
        # keep track of how many households have 3+ couples in them ( key = # couples  item = # households)     
        if(len(coupleHID_71[hid_71]) in count_moreM):
            count_moreM[ len(coupleHID_71[hid_71]) ] += 1
        else:
            count_moreM[ len(coupleHID_71[hid_71]) ] = 1
        

            

# write out the counting for the households that did not have exactly 2 married records in the house, or have 2 married records but they are wrong (ex. Both M, or not in the same house)     
fileLinks.write("2M BUT GenderSame: "+str(count_sameGend)+"\n")
fileLinks.write("2M-GDiff BUT 81HDiff: "+str(count_diff81H)+"\n")
fileLinks.write("1M: "+str(count_singleM)+"\n")

fileLinks.write("xM -> #households: ")
for num in count_moreM:
    fileLinks.write(str(num)+","+str(count_moreM[num])+"\n")

      


