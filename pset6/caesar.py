import sys

# This is the key
k = int(sys.argv[1])

# In case it is greater than 26
k = k % 26

s = input("plaintext: ")
print ( "ciphertext: ", end = "" )

# initialization
i = 0

# logic
while i < len(s):
    
    # for alphabets
    if s[i].isalpha():
        
        # for upper case letters
        if s[i].isupper():
            if ord(s[i]) + k > 90:
                t = ord(s[i]) + k - 90
                print( chr(t + 64).upper(), end = "" )
            else:
                print( chr(ord(s[i]) + k ).upper(), end = ""  )
        
        # for lower case letters
        else:
            if ord(s[i]) + k > 122:
                t = ord(s[i]) + k - 122
                print( chr(t + 96).lower(), end = "" )
            else:
                print( chr(ord(s[i]) + k ).lower(), end = "" )
    
    # for characters other than letters
    else:
        print( s[i], end = "" )
    
    # increment variable
    i+=1

# newline at the end
print()
