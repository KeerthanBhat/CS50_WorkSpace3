import cs50

print("Height: ",end="")
h = int(input())

i = 1

while h >= 0 and h <= 23:
    
    for i in range(h+1):
        
        for j in range(h-i):
            print(" ",end="")
        
        for k in range(i):
            print("#",end="")
        
        print(" ",end="")
        
        for k in range(i):
            print("#",end="")
        
        print()
    
    exit()
        