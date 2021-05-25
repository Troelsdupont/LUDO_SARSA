import ludopy
import numpy as np

g = ludopy.Game() #(ghost_players=[2,3])  # This will prevent players 1 and 3 from moving out of the start and thereby they are not in the game
there_is_a_winner = False

Qtable = np.array([    # 10 actions = Move out, Normal, goal, Star, Globe, Protect, Kill, Die, Goal Zone, Nothing(the token cannot be moved with current die roll).
    [7,8,7,6,3,5,1,3,7,6], #Home
    [2,1,19,4,5,11,15,3,0,3], #Goal zone
    [0,2,2,9,0,0,0,0,20,6], # Safe
    [3,2,1,14,6,7,5,0,15,2],  #Danger
    [9,0,6,5,3,8,5,3,2,6],  #Goal
    ])

Qtable1 = np.array([    # 10 actions = Move out, Normal, goal, Star, Globe, Protect, Kill, Die, Goal Zone, Nothing(the token cannot be moved with current die roll).
    [0,0,0,0,0,0,0,0,0,0], #Home
    [0,0,0,0,0,0,0,0,0,0], #Goal zone
    [0,0,0,0,0,0,0,0,0,0], # Safe
    [0,0,0,0,0,0,0,0,0,0],  #Danger
    [0,0,0,0,0,0,0,0,0,0],  #Goal
    ])


number_state = 5
LEARN_RATE = 0.7
j_RL = 0
rewardSum = 0
a_RL = 0
EXPLORE_RATE = 0.1
discount_factor = 0.9
tokenToMove = 0
number_action = 10
oldStates = np.array([0,0,0,0])

tokenStates = np.array([0,0,0,0])
tokenStatesString = np.array(["Init_state","Init_state","Init_state","Init_state"])
previousStatesString = np.array(["Init_state","Init_state","Init_state","Init_state"])
counter = 0
reward = 0
np.set_printoptions(precision=3)
tokenAction = np.array([0,1,2,3])
previousAction = np.array([0,0,0,0])
tokenActionString = np.array(["init_action","init_action","init_action","init_action"])
rewardString = np.array(["init          Reward","init           Reward","init        Reward","init       Reward"])


def randomizeQtable():
    for a in range(number_action):
        for s in range(number_state):
            Qtable[s][a]=np.random.randint(0, 10)
#randomizeQtable()
print("Qtable", Qtable)

def findStates():

    for x in range(4):
            if player_pieces[x]==0:
                tokenStates[x]=0 #+ (4*x)  # Home
                tokenStatesString[x]="Home"
                #print("Player ", x, " is home")
            elif player_pieces[x] in (53,54,55,56,57,58):
                tokenStates[x]= 1 #+ (4*x) # GOAL
                tokenStatesString[x]="Goal zone"

                #print("Player ", x, " is in goal")
            elif player_pieces[x] in (1,9,22,35,48):
                tokenStates[x]= 2 #+ (4*x) # SAFE
                tokenStatesString[x] = "Safe"
                #print("Player ", x, " is in safe")
            else:
                tokenStates[x]= 3#+(4*x) #DANGER
                tokenStatesString[x] = "Danger"

            if player_pieces[x]==59:
                tokenStates[x]= 4 #+ (4*x) # GOAL
                tokenStatesString[x]="Goal"
            #for a in range(4):
            if (player_pieces[x]==59 or player_pieces[x]==0):
                pass
            else:
                if x==0 :
                    if (player_pieces[x] in (player_pieces[1],player_pieces[2],player_pieces[3])):
                        tokenStates[x]= 2 # SAFE
                        #print("HEEEEEEEEEEEEEEER -----------------------------", x)
                        tokenStatesString[x] = "Safe"
                elif x==1:
                    if (player_pieces[x] in (player_pieces[0],player_pieces[2],player_pieces[3])):
                        tokenStates[x]= 2 #+ (4*x) # SAFE
                        #print("HEEEEEEEEEEEEEEER -----------------------------", x)
                        tokenStatesString[x] = "Safe"
                elif x==2:
                    if (player_pieces[x] in (player_pieces[0],player_pieces[1],player_pieces[3])):
                        tokenStates[x]= 2 #+ (4*x) # SAFE
                        #print("HEEEEEEEEEEEEEEER -----------------------------", x)
                        tokenStatesString[x] = "Safe"
                elif x==3:
                    if (player_pieces[x] in (player_pieces[0],player_pieces[1],player_pieces[2])):
                        tokenStates[x]= 2 #+ (4*x) # SAFE
                        #print("HEEEEEEEEEEEEEEER -----------------------------", x)
                        tokenStatesString[x] = "Safe"

def findAction():
    for x in range(4):
        if (len(move_pieces)==3 and move_pieces[0]!=x and move_pieces[1]!=x and move_pieces[2]!=x): #Tjek om det er muligt at flytte at flytte brikken
            tokenAction[x]=9
            tokenActionString[x] = "Nothing"
        elif (len(move_pieces)==2 and move_pieces[0]!=x and move_pieces[1]!=x):
            tokenAction[x]=9
            tokenActionString[x] = "Nothing"
        elif ((len(move_pieces)==1) and (move_pieces[0]!=x)):
            tokenAction[x]=9
            tokenActionString[x] = "Nothing"
        elif (len(move_pieces)==0):
            tokenAction[x]=9
            tokenActionString[x] = "Nothing"
        else:
            tokenAction[x]=-1
            print("Enemy matrix", enemy_pieces)
        if (tokenAction[x]!=9):
            if ((dice + player_pieces[x]) in (enemy_pieces[0][0],enemy_pieces[0][1],enemy_pieces[0][2],enemy_pieces[0][3],enemy_pieces[1][0],enemy_pieces[1][1],enemy_pieces[1][2],enemy_pieces[1][3],enemy_pieces[2][0],enemy_pieces[2][1],enemy_pieces[2][2],enemy_pieces[2][3])): #Skal nok lige laves mere på
                if ((dice+player_pieces[x]) in (40,27,14,48,9,22,35)):
                    tokenAction[x]=7 # Die
                    tokenActionString[x] = "Die"
                else:
                    tokenAction[x]=6 # Kill

                    tokenActionString[x] = "Kill"
            else:
                if (dice == 6 and player_pieces[x]==0):
                    tokenAction[x]=0 #Move out
                    tokenActionString[x]="Move out"
                elif (dice + player_pieces[x])==59:
                    tokenAction[x]=2 #Goal
                    tokenActionString[x]= "Goal"
                elif (dice + player_pieces[x]) in (12,25,38,51):
                    tokenAction[x]=3 # Star
                    tokenActionString[x]= "Star"
                elif (dice + player_pieces[x]) in (9,22,35,48):
                    tokenAction[x]=4 # Globe
                    tokenActionString[x]= "Globe"
                elif (dice + player_pieces[x]) in (player_pieces[0],player_pieces[1],player_pieces[2],player_pieces[3]):
                    tokenAction[x]=5 # Protect altså oven i en anden af ens brikker
                    tokenActionString[x]="Protect"
                elif (dice + player_pieces[x]) in (53,54,55,56,57,58):
                    tokenAction[x]=8 # Goal zone
                    tokenActionString[x]="Goal zone"
                else: #Normal
                    tokenAction[x]=1 #Normal
                    tokenActionString[x]="Normal"

        if (dice == 6 and player_pieces[x]==0):
            tokenAction[x]=0 #Move out
            tokenActionString[x]="Move out"
    #tokenAction returnere en vektor [0-9 0-9 0-9 0-9]
    # 10 actions = Move out, Normal, goal, Star, Globe, Protect, Kill, Die, Goal Zone, Nothing(the token cannot be moved with current die roll).

def rewardFunc(x):
    global oldStates
    global tokenStates
    global rewardString
    #print("rewardFunc tokenToMove", tokenToMove, "oldStates[tokenToMove]", oldStates[tokenToMove],"(tokenStates[tokenToMove]" , tokenStates[tokenToMove] )
    if (oldStates[tokenToMove]==0) and (tokenStates[tokenToMove]!=0): # No longer in home
        x = 7
        rewardString[tokenToMove]="No longer in home"

    elif (oldStates[tokenToMove]!=1) and (tokenStates[tokenToMove]==1):  # From not goal zone to goal zone
        x = 15
        rewardString[tokenToMove]="From Not goal zone to Goal zone "

    elif (oldStates[tokenToMove]!=2) and (tokenStates[tokenToMove]==2): # From not safe to safe
        rewardString[tokenToMove]="From not safe to safe"
        x = 7
    elif (oldStates[tokenToMove]!=4) and (tokenStates[tokenToMove]==4): # From not goal to goal
        rewardString[tokenToMove]="From not goal to goal"
        x = 15
    elif (oldStates[tokenToMove]!=0) and (tokenStates[tokenToMove]==0): # From not goal zone to goal zone
        rewardString[tokenToMove]="DIED"
        x = -5

    else:
        rewardString[tokenToMove]= "Nothing good"
        x = -1

    return x


def findMaxAction():
    global tokenToMove
    global tokenStates

    max = 0
    actionNr = 0
    tempValue = 0
    print("Qtable ", Qtable)

    for x in range(number_action):
        tempValue = Qtable[tokenStates[tokenToMove]][x]
    #    print("Qtable[tokenStates[tokenToMove]][x]", tempValue)
        #print("Find Max Action on Token, tokenToMove",tokenToMove,"tokenStates[tokenToMove]", tokenStates[tokenToMove],"actionNr", actionNr)
        if (tempValue>max):
            max = tempValue
            actionNr = x
    #print("Find Max Action on Token, tokenToMove",tokenToMove,"tokenStates[tokenToMove]", tokenStates[tokenToMove],"actionNr", actionNr)
    return actionNr


def Qvalue():
    global tokenToMove
    global oldStates
    global tokenStates
    global a_RL

    #print("Token1", tokenToMove)

    j_RL = tokenStates[tokenToMove] # Den nye state for den
    i_RL = oldStates[tokenToMove] #
    r_RL = reward


    a1_RL = tokenAction[tokenToMove] #findMaxAction #  return a number between 0-9
    a_RL = previousAction[tokenToMove] # The previous action for the token


    print("Qtable position til update ", i_RL, " ", a_RL)
    print("Value to Qtable", LEARN_RATE*(r_RL+discount_factor*Qtable[j_RL][a1_RL]-Qtable[i_RL][a_RL]))

    # SARSA
    Qtable[i_RL][a_RL]=Qtable[i_RL][a_RL]+LEARN_RATE*(r_RL+discount_factor*Qtable[j_RL][a1_RL]-Qtable[i_RL][a_RL])





    for x in range(4):
        oldStates[x] = tokenStates[x]
        previousStatesString[x] = tokenStatesString[x]
        previousAction[x] = tokenAction[x]






def getMaxActionToken(): #
    #Find the largest Q value for the given state and select the action
    global tokenToMove

    max = -10000



    token = 0

    for t in range(len(move_pieces)):
        token = move_pieces[t]
        #print("token", token)
        #print("tokenStates[token]",tokenStates[token]," tokenAction[token]",tokenAction[token])
        #print("Qtable[tokenStates[token]][tokenAction[token]]", Qtable[tokenStates[token]][tokenAction[token]])
        if (Qtable[tokenStates[token]][tokenAction[token]]>max):
            max = Qtable[tokenStates[token]][tokenAction[token]]
            tokenToMove = token

            #print("TOKEN1", tokenToMove)


    return tokenToMove

def tokenSelection(move_pieces,x):
    exploration_activation = np.random.randint(0, 1000)/1000.0 #Between 0 and 1
    global tokenToMove
    global EXPLORE_RATE

    if(exploration_activation >(((1000.0-x)/1000.0)*EXPLORE_RATE)): #
        print("Token To move", tokenToMove)
        tokenToMove = getMaxActionToken()
        return tokenToMove
    else:
        print("Token To move", tokenToMove, "BUT random")
        tokenToMove = move_pieces[np.random.randint(0,len(move_pieces))]
        return  tokenToMove


winningStats = np.array([0,0,0,0])
succesRate = np.array([]) #np.array([0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])
rewardRate = np.array([])
tempSum = 0.0

nrOfGames = 1000
for x in range(nrOfGames): #Number of games played
    g = ludopy.Game() #(ghost_players=[2,3])  # This will prevent players 1 and 3 from moving out of the start and thereby they are not in the game
    there_is_a_winner = False




    while not there_is_a_winner:
        (dice, move_pieces, player_pieces, enemy_pieces, player_is_a_winner, there_is_a_winner), player_i = g.get_observation()


        #print("\n NEW Roll ------------------------------------------------------------------------------")
        #print("Dice ", dice , " player pieces positions", player_pieces, " Move pieces ", move_pieces, "Player i ", player_i)
        if len(move_pieces): #

            if (player_i==0):
                counter = counter + 1
                print("\n \n ",counter)
                findStates()

                print("Previos states", oldStates, previousStatesString, "These new states ", tokenStates, tokenStatesString)

                #print("Token states     ", tokenStatesString, tokenStates)
                findAction()


                #print("Token To Move Max Q value: ", tokenToMove, " Possible pieces to move ", move_pieces)
                reward = rewardFunc(reward)
                rewardSum = rewardSum + reward
                #tokenToMove = getMaxActionToken()

                print("Reward ", rewardString, " = ", reward)

                Qvalue()
                print("Qtable \n ", Qtable)

                print("Dice ", dice , " player pieces positions", player_pieces, " Move pieces ", move_pieces, "Player i ", player_i," Player pieces positions", player_pieces )
                print("Actions :    ", tokenActionString)


                piece_to_move = tokenSelection(move_pieces,x)
            else:
                #print("Random move")
                piece_to_move = move_pieces[np.random.randint(0, len(move_pieces))]
        else:
            #print("No piece can be moved")
            piece_to_move = -1

        #print("piece to move ", piece_to_move)

        _, _, _, _, _, there_is_a_winner = g.answer_observation(piece_to_move)

        # OKAY FÅ DEN TIL AT STARTE FORFRA

    player_is_a_winner = g.get_winner_of_game()
    winningStats[player_is_a_winner] = winningStats[player_is_a_winner] + 1

    if (player_is_a_winner == 0):
        tempSum = tempSum + 0.01

    #print("Temp sum ", tempSum)
    if ((x+1)%100==0):
        #print("I WAS HERE Mod")
        rewardRate = np.append(rewardRate,[rewardSum])
        succesRate = np.append(succesRate,[tempSum])
        tempSum = 0.0
        rewardSum = 0.0


    print("Winning stats : " , winningStats," Games : ", x+1,"discount_factor Gamma ",discount_factor, " SuccesRate : ", succesRate , "Reward Rate ", rewardRate)



if False:
    player_is_a_winner = g.get_winner_of_game()
    print("Saving history to numpy file")
    g.save_hist(f"game_history.npy")

    #print("stateActionMatrice", stateActionMatrice)
    #print("player_pieces", player_pieces)

    print("THE winner is: ", player_is_a_winner)

    print("Player Pieces : ", player_pieces)
    print("\n dice : ", dice)
    print("\n move_pieces", move_pieces)

    print("\n enemy_pieces : ", enemy_pieces)


    print("Saving game video")
    g.save_hist_video(f"game_video.mp4")
