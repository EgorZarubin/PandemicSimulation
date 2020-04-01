import random
import numpy as np
import matplotlib.pyplot as plt
import cv2

print ("Pandemic simulation")

class Human:
    virus_state = 0
    virus_days = 0
    age = 30    
    immunitet = 50

    def __init__(self, virus_state, age, immunitet):
        self.virus_state = virus_state
        self.age = age
        self.immunitet = immunitet

#init population
x_size = 500
y_size = 500
population = np.ndarray(shape = (x_size,y_size), dtype = Human)
population_count = len(population) * len(population[0])


for i in range(len(population)):
    for j in range(len(population[i])):
        population[i][j] = Human(0, random.randint(1, 80), random.randint(0, 100)) #add correct distribution
        #population[i][j].age = random.randint(1, 80)
        #population[i][j].immunitet = random.randint(0, 100)

#start epidemy
infected = []
dead = 0
healed = 0

for h in range(100):
    id = random.randint(0, population_count)
    population[id//x_size][id%y_size].virus_state = 1
    infected.append(id)


def spred_virus(id, new_infected):
    spread = random.randint(0,100)
    person = population[id//x_size][id%y_size]
    spread *= (100 - person.immunitet) / 100 
    if spread > 50 and person.virus_state == 0:
        population[id//x_size][id%y_size].virus_state = 1
        new_infected.append(id)
        #print ("new virus case")
        

def heal(id, healed, dead):
    if population[id//x_size][id%y_size].virus_state == 1:
        death = random.randint(0, 1000)
        death *= population[id//x_size][id%y_size].age / 80
        if death > 900:
            population[id//x_size][id%y_size].virus_state = 3
            infected.remove(id)
            dead += 1
        else:
            population[id//x_size][id%y_size].virus_days += 1
            if population[id//x_size][id%y_size].virus_days > 15:
                population[id//x_size][id%y_size].virus_state = 2
                if id in infected:
                    infected.remove(id)
                else:
                    print("warning: id", id)
                healed += 1

    return healed, dead



#epydemi step
plt.figure(figsize=(10,10))
virus_img = np.ndarray([x_size, y_size, 3], dtype=np.uint8)
virus_img[:,:] = [255, 255, 255]
plt.imshow(virus_img)

out = cv2.VideoWriter('project.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 15, (x_size, y_size))

def update_view(video_out):   
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
                        
    video_out.write(virus_img)
    #plt.imshow(virus_img)
    #plt.draw()
    #plt.pause(0.002)

for step in range(500):
    print ("step:", step, "number of infected", len(infected), "healed",healed, "dead", dead)
    new_infected = []
    for id in infected:
        if population[id//x_size][id%y_size].virus_days < 5:
            for i in range(3):
                for j in range(3):
                    n_id_x = (id//x_size + (i-1))%x_size
                    n_id_y = (id%x_size + j-1)%y_size
                    n_id = n_id_x *x_size + n_id_y 
                    if id != n_id:
                        spred_virus(n_id, new_infected)
        healed, dead = heal(id, healed, dead)
    for new_id in new_infected:
        infected.append(new_id)
    if len(infected) == 0:
        break
#update picture
    update_view(out)

out.release()

    