from pwn import *
import sys

# Connection Details
ip = "35.194.142.188"
port = 8002

# Current Position
curr_x = 0
curr_y = 0


############ FUNCS ############

# Save the successful position in file
def saveCorrect(_x, _y):
	with open("record.txt", "a") as f:
        f.write(str(_x) +"," + str(_y) + "\n")

# Save the current position in file
def saveCurrentPos(_x, _y):
	with open("current.txt", "w") as f:	
        f.write(str(_x) +"," + str(_y) + "\n")

# Reset the current position to the latest position that is "to be mined"
def loadCurrentPos():
	global curr_x
	global curr_y

	with open("current.txt") as f:	
        for line in f:
            x,y = line.rstrip().split(",")
            curr_x,curr_y = int(x),int(y)
            curr_x += 1
            checkBound()

# Update the x or y to prevent out of index
def checkBound():
	global curr_x
	global curr_y

	if curr_x >= 36:
        curr_x = 0
        curr_y += 1
	if curr_y >= 36:
        return False
	return True

# Execute the given position (used as checking purpose)
def doPos(_x,_y):	
	r.sendline(str(_x) + " " + str(_y))
	res = r.recvrepeat(0.2)
	if("?" in res):
        return True
	return False

# Try to mine the position and check the result
def tryPos(_x, _y):
	r.sendline(str(_x) + " " + str(_y))
	res = r.recvrepeat(0.2)

    # Success Case
	if("?" in res):
        # Save the success position
        saveCorrect(_x,_y)
        # Save current success position
        saveCurrentPos(_x,_y)

    # Fail Case
	else:
        # Save current success position
        saveCurrentPos(_x,_y)
        print("saving fail position", _x, _y)
        return False

	return True

# Repeat all the successful actions/positions that have been done before
# This ensures that the incoming randomized mine position will remain the same
def doPreRecord():
	global curr_x
	global curr_y
	with open("record.txt") as f:
    		for line in f:
			x,y = line.rstrip().split(",")
			#print(x,y)	
			doPos(x,y)
			curr_x,curr_y = int(x),int(y)		


############### New Connection ###############
while (checkBound() is True):
    # Init connection
    r = remote(ip, port)

    # Reset current position
    curr_x = 0
    curr_y = 0

    # Enter game screen
    r.recvline()
    s = r.recvuntil("Select")

    # Start the game
    r.sendline("1")

    ### LOGICS ###
    print("starting...")

    # Repeat all the "successful" actions taken before
    doPreRecord()

    # Reset position to the latest position
    loadCurrentPos()

    # Loop that keep mining positions
    res = True
    while(res):
        checkBound()
        # Mine the position and to success or fail
        res = tryPos(curr_x,curr_y)
        curr_x += 1

# Keep the screen awake
r.interactive()
