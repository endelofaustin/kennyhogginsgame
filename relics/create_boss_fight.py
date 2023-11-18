def create_boss_fight():
 
    matrix = [[0,0,0,0,0,0,0,0,0,0], 
              [0,0,0,0,0,0,0,0,0,0], 
              [0,0,0,0,0,0,0,0,0,0], 
              [0,0,0,0,0,0,0,0,0,0], 
              [0,0,0,0,0,0,0,0,0,0], 
              [0,0,0,0,0,0,0,0,0,0], 
              [0,0,0,0,0,0,0,0,0,0]] 
 
    matrix = matrix * 400 
    with open('bossfight.dill', 'wb') as f: 
        dill.dump(matrix, f) 
 
create_boss_fight () 
