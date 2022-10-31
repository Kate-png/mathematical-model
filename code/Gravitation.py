import pygame
import time

WIDTH = 1200  #ширина окна
HEIGHT = 800  #высота окна
FPS = 100 #частота обновления, кадры в секунду
G = 6.67430/(10**(11)) #гравитационная постоянная 
k = 1_000_000 #метров в пикселе на момент инициализации, масштаб 

w_x = -600_000_000 #координаты угла окна 
w_y = -400_000_000 #на общей карте

vrem_k = 1 # коэффициент ускорения времени на начало, 1 - реальное время, 

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT)) #инициализация окна
pygame.display.set_caption("Gravitation") #название программы
clock = pygame.time.Clock()
font = pygame.font.SysFont('arial', 26) #шрифт и размер
text_FPS = font.render('FPS: '+str(FPS), True,'white') #запись частоты обновления на экране
text_vrem_k = font.render('Time: x'+str(vrem_k), True,'white') #запись ускорения времени на экране
                
class Objects(): #спрайт всех объектов
    def __init__(self,types,real_x,real_y,real_r,m,colour):
        self.types = types; #тип ксомического объекта: звезда = 1, планета = 2 или астероид = 3
        self.real_x = real_x #x координата центра объекта, м
        self.real_y = real_y #у координата центра объекта, м
        self.real_r = real_r #радиус, м
        self.m = m #масса, кг
        self.colour = colour #цвет
        self.speed = [0,0] #вектор скорости, м/с
        self.a = [0,0] #вектор ускорения, м/с**2
        self.f = [0,0] #вектор силы гравитационного поля,Н
        self.trace_count = 0 #расчет трека, расстояние между точками
        self.trace = [] #массив точек трека
        self.status = True #статус существования

    def update(self): #расчет характеристик тел в каждый момент времени
        self.a[0] = ((self.f[0]/self.m)*(vrem_k**2)/FPS**2) #расчет ускорения по 2 закону Ньютона a=F/m
        self.a[1] = ((self.f[1]/self.m)*(vrem_k**2)/FPS**2) #домноженный на поправочный коэффициент

        self.speed[0] +=  self.a[0] #расчет скорости
        self.speed[1] +=  self.a[1] 
        
        self.real_x += self.speed[0] #расчет координаты
        self.real_y += self.speed[1]




        # траектория:
        self.trace_count += (self.speed[0]**2+self.speed[1]**2)**0.5 #каждый раз добавляется длина вектора скорости
        if self.trace_count/k >= 5: #частота появления точек трека
            self.trace_count = 0
            self.trace.append((self.real_x,
                                self.real_y))
        if len(self.trace)>1000: #регулировка длины трека: если массив точек в треке превысит 1000,
            self.trace.pop(0)   #удаляем последний 
            
    def draw(self): #отрисовка
        pygame.draw.circle(screen,
                           self.colour,
                           ((self.real_x - w_x)/k, #вычисление координат места на карте для рисования
                            (self.real_y - w_y)/k),
                           self.real_r/k
                           ) #отрисовка самого объекта
        for i in self.trace:
            pygame.draw.circle(screen,
                           self.colour,
                           ((i[0] - w_x)/k,
                                (i[1] - w_y)/k),
                            1) #отрисовка трека

objects = []   #Объектов на карте     


#Солнце
p = Objects(1,0,0,696_000_000,1.9891*10**30,'yellow')
objects.append(p)


#Земля:
p = Objects(2,-149.6*10**9,0,6371000,5.9722*10**24,'blue')
objects.append(p)
objects[1].speed[1]+= 29782.77*(vrem_k/FPS)

#Луна:
p = Objects(2,-149.6*10**9+363104000,0,1737100,7.35*10**22,'grey')
objects.append(p)
p.speed[1] = 1080*(vrem_k/FPS)
objects[2].speed[1]+= 29782.77*(vrem_k/FPS)


#Планета, которая вращается по эллиптической орбите
p = Objects(2,69.6*10**9,30*10**9,6_371_000,5.9722*10**24,'brown')
objects.append(p)
objects[3].speed[1]+= 27782.77*(vrem_k/FPS)

#Юпитер
p=Objects(2, -778_570_000_000,0,71492000,1.8986*10**27,'orange')
objects.append(p)
objects[4].speed[1]+= 13070*(vrem_k/FPS)

#Астероид 
p=Objects(3, -149.6*10**9+123104000,149.6*10**9+123104000, 463500, 9.393*10**20,'green')
objects.append(p)
objects[5].speed[0]+=3000*(vrem_k/FPS)
objects[5].speed[1]+= 29782.77*(vrem_k/FPS)


tick = 0
tm = time.time()
running = True
while running:
    clock.tick(FPS) #устанавливаем желательную и максимальную задержку между циклами (не более 100 кадров в секунду)
    tick+=1
    if tick == 100:
        tick = 0
        text_FPS = font.render('FPS: '+str(int((100/(time.time() - tm)))), True,
                  'white') #вычисляем и пишем реальную задержку времени
        
        tm = time.time()
        
    #обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #выход из программы
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            #Найдём место на реальной карте,
            #куда хочет попасть пользователь:
            xx = event.pos[0] #положение курсора по х в окне 
            yy = event.pos[1] #положение курсора по y в окне
            jump_x = w_x + xx*k #положение курсора по х на реальной карте
            jump_y = w_y + yy*k  #положение курсора по y на реальной карте
            
            if event.button == 4:  #уменьшение масштаба (приближение)
               if k>100_000:
                    k = k*0.85


               w_x = jump_x - xx*k #обновляем положение угла окна на реальной карте
               w_y = jump_y - yy*k
                
            if event.button == 5:  #увеличение масштаба (отдаление)
               if k<100_000_000_0:
                    k = k/0.85

               w_x = jump_x - xx*k
               w_y = jump_y - yy*k


            if event.button == 3: #изменяем ускорение времени 
                if vrem_k == 1_000_0000:
                    vrem_k = 1 #сброс
                    for i in objects:
                        i.speed[0]/=100_00000
                        i.speed[1]/=100_00000
                else:
                    vrem_k *= 10 #увеличение в 10 раз 
                    for i in objects:
                        i.speed[0]*=10
                        i.speed[1]*=10
                        
                text_vrem_k = font.render('Time: x'+str(vrem_k), True,'white') #пишем множитель времени
                
        if event.type == pygame.MOUSEMOTION: #перемещение карты
            if pygame.mouse.get_pressed()[0] == True:
                w_x -= event.rel[0]*k #обновляем положение угла окна на реальной карте 
                w_y -= event.rel[1]*k #по относительному смещению положения курсора
            
    collisions = [] #массив индексов объектов, которые вошли в коллизию


    #считаем действующие силы на каждое тело
    for i in range(len(objects)): #цикл по длине массива объектов
        for j in range(i+1,len(objects)): #выбираем второй объект, не совпадающий с первым
            dx = objects[j].real_x-objects[i].real_x #проекция расстояния между двумя объектами (центрами) по x
            dy = objects[j].real_y-objects[i].real_y #проекция расстояния между двумя объектами (центрами) по y
            d = (dx**2+dy**2)**0.5 #действительное расстояние
            ff = G*objects[i].m*objects[j].m/d**2 #закон всемирного тяготения
            
            objects[i].f[0] += dx*ff/d #проекция силы на х для первого объекта
            objects[i].f[1] += dy*ff/d #проекция силы на y для первого объекта

            objects[j].f[0] -= dx*ff/d #проекция силы на х для второго объекта
            objects[j].f[1] -= dy*ff/d #проекция силы на y для второго объекта

            if objects[i].real_r > d - objects[j].real_r: #проверка, не столкнулись ли объекты
                collisions.append((i,j))
                
    #обработаем столкновения:
    for i in collisions:
        t1 = objects[i[0]]
        t2 = objects[i[1]]
        if t1.status and t2.status:
            t1.status = False #уничтожаем объекты
            t2.status = False
            if t1.real_r > t2.real_r: #устанавливаем тип и цвет большего объекта
                c = t1.colour
                tp = t1.types
            else:
                c = t2.colour
                tp = t2.types
                
            t = Objects(tp,(t1.real_x*t1.m+t2.real_x*t2.m)/(t1.m+t2.m), #новые координаты по 
                            (t1.real_y*t1.m+t2.real_y*t2.m)/(t1.m+t2.m), #среднему арифметическому взвешенному
                            (t1.real_r**3+t2.real_r**3)**(1/3), #увеличиваем радиус
                            t1.m + t2.m, #складываем массу
                            c)
            t.speed[0] = (t1.m*t1.speed[0]+t2.m*t2.speed[0])/(t1.m+t2.m) #скорости после абсолютно неупругого удара по х
            t.speed[1] = (t1.m*t1.speed[1]+t2.m*t2.speed[1])/(t1.m+t2.m) #скорости после абсолютно неупругого удара по y
            objects.append(t)
    


    tt = [] #добавляем в массив только те объекты, которые существуют
    for ball in objects: 
        if ball.status:
            tt.append(ball)
    objects = tt #обновляем изначальный массив объектов (выкидывая несуществующие)
            
    for ball in objects:
        ball.update()
        ball.f = [0,0] #обновляем и сбрасываем силу
        
    #рисуем
    screen.fill('black')
    
    for ball in objects:
        ball.draw()
        
    screen.blit(text_FPS, (10, 10)) #положение фпс на экране
    screen.blit(text_vrem_k, (10, 30)) #положение множителя времени
    pygame.display.update()
pygame.quit()
