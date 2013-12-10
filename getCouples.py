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

married71HIDcount = dict() # HID -> # married people
married81HIDcount = dict()

for line in census71:
    line = line.strip()
    el=line.split(",")
    censusRecords_71[el[0]] = line
    
    # keep track of how many married people appear in each household
    if(el[7] == "1" and el[0] in id71_to_HID):
        if(id71_to_HID[el[0]] in married71HIDcount):
            married71HIDcount[id71_to_HID[el[0]]] = married71HIDcount[id71_to_HID[el[0]]] + 1
        else:
            married71HIDcount[id71_to_HID[el[0]]] = 1
    
    
    
for line in census81:
    line = line.strip()
    el=line.split(",")
    censusRecords_81[el[0]] = line
    
    # keep track of how many married people appear in each household
    if(el[7] == "1" and el[0] in id81_to_HID):
        if(id81_to_HID[el[0]] in married81HIDcount):
            married81HIDcount[id81_to_HID[el[0]]] = married81HIDcount[id81_to_HID[el[0]]] + 1
        else:
            married81HIDcount[id81_to_HID[el[0]]] = 1

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
            coupleHID_71[household_71].append(el[0]+","+el[1]+","+el_71Rec[4]+","+el_71Rec[1] +","+el_81Rec[1])  # put the couple in it's repective 71 household: 71ID, 81ID, Gender (1 = male, 0 = female), 71 Last Name

diffLastName = 0
sameGender = 0
notOnly2 = 0
diff81HID = 0

count_total_size2_H = 0
         
for hid_71 in coupleHID_71:

    if( len(coupleHID_71[hid_71]) == 2): # only two 1:1 married links in the 1871 household
       
        count_total_size2_H += 1
            
        # store the break down of each record in the household
        A_Record = (coupleHID_71[hid_71][0]).split(",")
        B_Record = (coupleHID_71[hid_71][1]).split(",")
        
        # are they in the same 81 HID?
        if( id81_to_HID[ A_Record[1] ] == id81_to_HID[ B_Record[1] ]):
        
            # are these records the only married ones in the households?
            if( married71HIDcount[id71_to_HID[ A_Record[0]]] == 2 and married81HIDcount[ id81_to_HID[ A_Record[1]] ] == 2):
            
                # are the genders opposite?
                if( A_Record[2] != B_Record[2] ):
                
                    # does the male and female in the 71 household have the EXACT same last name?
                    if(A_Record[3] == B_Record[3] and A_Record[4] == B_Record[4]):
                    
                        # writes out male71 info : male81 info || female71 info : female81 info
                        if( A_Record[2] == "0"):
                            fileLinks.write(censusRecords_71[B_Record[0]]+":"+censusRecords_81[B_Record[1]]+"||"+censusRecords_71[A_Record[0]]+":"+censusRecords_81[A_Record[1]]+"\n")
                        else:
                            fileLinks.write(censusRecords_71[A_Record[0]]+":"+censusRecords_81[A_Record[1]]+"||"+censusRecords_71[B_Record[0]]+":"+censusRecords_81[B_Record[1]]+"\n") 
                    else:
                        diffLastName += 1
                else:
                    sameGender += 1
            else:
                notOnly2 +=1
        else:
            diff81HID += 1
        

            

fileLinks.write("Households with 2 1:1 married links: "+str(count_total_size2_H)+"\n")
fileLinks.write("81 HID is different: "+str(diff81HID)+"\n")
fileLinks.write("Had non-linked married records: "+str(notOnly2)+"\n")
fileLinks.write("Same Gender: "+str(sameGender)+"\n")
fileLinks.write("Different 1871 Last Name: "+str(diffLastName)+"\n")


