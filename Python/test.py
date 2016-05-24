import csv
import time
import sys

start = time.time()

#load
names = [] 
matches = []
with open(str(sys.argv[1]), 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')

    for row in reader:
        names.append(row[0])
        matches.append(row[1])
        
#algo
#reasonable cutoff to not match peculiar matches
cutoff = 0.7
#multiplier for having a better prefix
pmult = 0.1
        
def winkler(str1, str2):
    global pmult
    
    marker = chr(1)
    if (str1 == str2):
        return 1.0

    len1 = len(str1)
    len2 = len(str2)
    halflen = max(len1,len2) / 2 - 1
    prefix = 0
    
    chars1  = ''  
    chars2  = ''
    temp1 = str1
    temp2 = str2
    common1 = 0    # Number of common characters
    common2 = 0
    
    #prefix check
    i=0
    while i < min(len(str1),len(str2)):
        #Jaro-Winkler never went above 4 matches for a prefix
        if i==4:
            break
        if(str1[i]==str2[i]):
            prefix+=1
            i+=1
        else:
            break
    
    for i in range(len1):
        start = i - halflen if i > halflen else 0
        end = i+halflen+1 if i+halflen+1 < len2 else len2
        index = temp2.find(str1[i],start,end)
        if (index > -1):    # Found common character
            common1 += 1
            chars1 = chars1 + str1[i]
            temp2 = temp2[:index]+marker+temp2[index+1:]
    for i in range(len2):
        start = max(0,i-halflen)
        end   = min(i+halflen+1,len1)
        index = temp1.find(str2[i],start,end)
        if (index > -1):    # Found common character
            common2 += 1
            chars2 = chars2 + str2[i]
            temp1 = temp1[:index]+marker+temp1[index+1:]

    if (common1 == 0):
        return 0.0

    transposition = 0
    for i in range(common1):
        if (chars1[i] != chars2[i]):
            transposition += 1
            
    t = transposition / 2.0
    m = common1
    a = str1
    b = str2
    
    if(m>0):
        dj = (1.0/3)*(m*1.0/len(a) + m*1.0/len(b) + (m-t)*1.0/m) 
        
    #jarowinkler with prefix bonus
        dw = dj + (prefix*pmult*(1-dj))
    return dw

def jaro(name, regex):
    #Initialize globals
    global bm_score, bm_name, cutoff
    
    #Swap so that the smaller string is looped over
    func = winkler(name, regex)
    if len(name) < len(regex):
        func = winkler(regex, name)
        
    #Check if the Jaro-Winkler score is best ifso update
    jw_score = winkler(name, regex)
    if jw_score > cutoff and jw_score > bm_score:
        bm_score = winkler(name, regex)
        bm_name = regex
    return

#Initialize writer
with open(str(sys.argv[2]), "w") as outputfile:
    writer = csv.writer(outputfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #Main loop to run over matches
    for i,na in enumerate(names):
        print "-------"+str(i)+"-------"
        print "SEARCH: " + na
        bm_score = 0
        bm_name = "none"
        for ex in matches:
            jaro(na, ex)
        #print "-------------"
        print "MATCH: " + bm_name
        print "Jaro-Winkler SCORE: " + str(bm_score)
        row = [na, bm_score, bm_name]
        writer.writerow(row)
    
  
print "--------------"
print "Result written to output.csv"
end = time.time()
print "Calculated in " + str(end - start) + "s"  