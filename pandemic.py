import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image
import cv2

print ("Pandemic simulation")

WRITE_VIDEO = True

class Human:
    virus_state = 0
    virus_days = 0
    age = 30    
    immunity = 50

    def __init__(self, virus_state, age, immunity):
        self.virus_state = virus_state
        self.age = age
        self.immunity = immunity

#init population
x_size = 500
y_size = 500
population = np.ndarray(shape = (x_size,y_size), dtype = Human)
population_count = len(population) * len(population[0])


for i in range(len(population)):
    for j in range(len(population[i])):
        imm = random.gauss(0.5, 0.1)
        age = random.randint(1, 80)
        population[i][j] = Human(0, age, imm) #add correct distribution
        #population[i][j].age = random.randint(1, 80)
        #population[i][j].immunity = random.randint(0, 100)

#start epidemy

infected = []
dead = []
healed = []

infected_dynamics = []
healed_dynamics = []
dead_dynamics = []

for h in range(100):
    id = random.randint(0, population_count)
    population[id//x_size][id%y_size].virus_state = 1
    infected.append(id)


def spred_virus(id, new_infected):
    spread = random.random()
    person = population[id//x_size][id%y_size]
    p = 0.1 * (1 - person.immunity) 
    if spread < p and person.virus_state == 0:
        population[id//x_size][id%y_size].virus_state = 1
        new_infected.append(id)
        #print ("new virus case")

def random_spread(contacts, new_infected):
    i = 0
    while i < contacts:
        id = random.randint(0, x_size*y_size - 1)
        x = id//x_size
        y = id%y_size
        if population[x][y].virus_state == 0:
            spread = random.random()
            p = 0.001 * (1 - population[x][y].immunity) 
            if spread < p:
                population[x][y].virus_state = 1
                new_infected.append(id)
        i += 1

        

def heal(id):
    x = id//x_size
    y = id%y_size
    if population[x][y].virus_state == 1:
        death = random.random()
        p =  (1 - population[x][y].immunity) * population[x][y].age / 80 / 50
        if death < p:
            population[x][y].virus_state = 3
            infected.remove(id)
            dead.append(id)
        else:
            population[x][y].virus_days += 1
            if population[x][y].virus_days > 15:
                population[x][y].virus_state = 2
                infected.remove(id)
                healed.append(id)

    

virus_img = np.ndarray([x_size, y_size, 3], dtype=np.uint8)
virus_img[:,:] = [255, 255, 255]


if WRITE_VIDEO:
    out = cv2.VideoWriter('project.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 15, (x_size, y_size))

def update_view(video_out = None):   
    for i in range(len(virus_img)):
        for j in range(len(virus_img)):
            if population[i][j].virus_state == 0:
                virus_img[i,j,:] = 255
            elif population[i][j].virus_state == 1:
                virus_img[i,j,1:2] = 0
            elif population[i][j].virus_state == 2:
                virus_img[i,j,0] = 0
                virus_img[i,j,1] = 255
                virus_img[i,j,2] = 0
            elif population[i][j].virus_state == 3:
                virus_img[i,j,:] = 0
    if video_out:               
        video_out.write(virus_img)
    #plt.imshow(virus_img)
    #plt.draw()
    #plt.pause(0.002)

for step in range(500):
    print ("step:", step, "number of infected", len(infected), "healed",len(healed), "dead", len(dead))
    new_infected = []
    for id in infected:
        if population[id//x_size][id%y_size].virus_days < 8:
            for i in range(3):
                for j in range(3):
                    n_id_x = (id//x_size + (i-1))%x_size
                    n_id_y = (id%x_size + j-1)%y_size
                    n_id = n_id_x *x_size + n_id_y 
                    if id != n_id:
                        spred_virus(n_id, new_infected)
            random_spread(50, new_infected)
        heal(id)
        
    for new_id in new_infected:
        infected.append(new_id)

    infected_dynamics.append(len(infected))
    healed_dynamics.append(len(healed))
    dead_dynamics.append(len(dead))

    if len(infected) == 0:
        break
#update picture
    if WRITE_VIDEO:
        update_view(out)

if WRITE_VIDEO:
    out.release()

with open("infected_dynamics.txt", 'w') as f:
    for x in infected_dynamics:
        f.write(str(x) + '\n')

with open("healed_dynamics.txt", 'w') as f:
    for x in healed_dynamics:
        f.write(str(x) + '\n')

with open("dead_dynamics.txt", 'w') as f:
    for x in dead_dynamics:
        f.write(str(x) + '\n')

update_view()
plt.imsave('final_state.png', virus_img)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(50,100))

ax1.plot(infected_dynamics, 'red')
ax1.plot(healed_dynamics, 'green')
ax1.plot(dead_dynamics, 'black')

ax2.imshow(virus_img)
plt.show()
    