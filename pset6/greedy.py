import math

print("O hai! How much change is owed?")
f = float(input())

if f > 0:
    f = f * 100
    f = round( f )
    f = int (f)
    count = int ( f / 100 ) * 4
    f = int ( f % 100 )
    
    while f - 25 >= 0:
        count = count + 1
        f = f - 25
    while f - 10 >= 0:
        count = count + 1
        f = f - 10
    while f - 5 >= 0:
        count = count + 1
        f = f - 1
    print(count)
        
    
    
