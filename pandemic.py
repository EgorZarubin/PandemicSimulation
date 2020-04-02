import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image
import cv2

print ("Pandemic simulation")

WRITE_VIDEO = True
x_size = 500
y_size = 500

class Human:
    virus_state = 0
    virus_days = 0
    age = 30    
    immunity = 50

    def __init__(self, virus_state, age, immunity):
        self.virus_state = virus_state
        self.age = age
        self.immunity = immunity


def init_population(x, y):
    
    population = np.ndarray(shape = (x, y), dtype = Human)
    
    for i in range(len(population)):
        for j in range(len(population[i])):
            imm = random.gauss(0.5, 0.1)
            age = random.randint(1, 80)
            population[i][j] = Human(0, age, imm) #add correct distribution
            #population[i][j].age = random.randint(1, 80)
            #population[i][j].immunity = random.randint(0, 100)
    
    return population

#start epidemy

def start_epidemy(population, n):
    infected = []
    population_count = x_size*y_size
    for h in range(n):
        id = random.randint(0, population_count)
        population[id//x_size][id%y_size].virus_state = 1
        infected.append(id)
    return infected



def spred_virus(population, id, new_infected):
    spread = random.random()
    person = population[id//x_size][id%y_size]
    p = 0.1 * (1 - person.immunity) 
    if spread < p and person.virus_state == 0:
        population[id//x_size][id%y_size].virus_state = 1
        new_infected.append(id)
        #print ("new virus case")

def random_spread(population, contacts, new_infected):
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

def heal(population, id, infected, healed, dead):
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

def update_view(population, virus_img, video_out = None):   
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

def virus_step(step, population, infected, healed, dead, infected_dynamics, healed_dynamics, dead_dynamics, virus_img = 0, video_out = 0):
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
                        spred_virus(population, n_id, new_infected)
            random_spread(population, 50, new_infected)
        heal(population, id, infected, healed, dead)
        
    for new_id in new_infected:
        infected.append(new_id)

    infected_dynamics.append(len(infected))
    healed_dynamics.append(len(healed))
    dead_dynamics.append(len(dead))

    #update picture
    if WRITE_VIDEO:
        update_view(population, virus_img, video_out)


def main():    
    population = init_population(x_size, y_size)

    infected = start_epidemy(population, 100)
    dead = []
    healed = []

    infected_dynamics = []
    healed_dynamics = []
    dead_dynamics = []

    
    virus_img = np.ndarray([x_size, y_size, 3], dtype=np.uint8)

    virus_img[:,:] = [255, 255, 255]


    if WRITE_VIDEO:
        out = cv2.VideoWriter('project.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 15, (x_size, y_size))

        for step in range(500):
            virus_step(step, population, 
                       infected, healed, dead,
                       infected_dynamics, healed_dynamics,dead_dynamics, virus_img = virus_img, video_out=out)
            if len(infected) == 0:
                break
        out.release()
    
    else: 
        for step in range(500):
            virus_step(step, population,
                       infected, healed, dead,
                       infected_dynamics, healed_dynamics,dead_dynamics)
            if len(infected) == 0:
                break

    with open("infected_dynamics.txt", 'w') as f:
        for x in infected_dynamics:
            f.write(str(x) + '\n')

    with open("healed_dynamics.txt", 'w') as f:
        for x in healed_dynamics:
            f.write(str(x) + '\n')

    with open("dead_dynamics.txt", 'w') as f:
        for x in dead_dynamics:
            f.write(str(x) + '\n')

    update_view(population, virus_img)
    plt.imsave('final_state.png', virus_img)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(50,100))

    ax1.plot(infected_dynamics, 'red')
    ax1.plot(healed_dynamics, 'green')
    ax1.plot(dead_dynamics, 'black')

    ax2.imshow(virus_img)
    plt.show()
    

if __name__ == "__main__":
    main()
    