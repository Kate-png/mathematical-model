import pygame
import time
import xml.etree.ElementTree as ET
import numexpr as ne
import random as rn

WIDTH = 1200  #ширина окна
HEIGHT = 800  #высота окна
FPS = 100 #частота обновления, кадры в секунду
G = 6.67430/(10**(11)) #гравитационная постоянная 
k = 1_000_000 #метров в пикселе на момент инициализации, масштаб 

w_x = -600_000_000 #координаты угла окна 
w_y = -400_000_000 #на общей карте
atm = 0  #включение и выключение атмосферы
wind = 0 #давление солнечного света
I=83500 #интенстивность излучления звезды
entry=0 #запись в файл


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
        self.real_x = real_x #x координата геометрического центра объекта, м
        self.real_y = real_y #у координата геометрического центра объекта, м
        self.real_r = real_r #радиус, м
        self.m = m #масса, кг
        self.colour = colour #цвет
        self.speed = [0,0] #вектор скорости, м/с
        self.a = [0,0] #вектор ускорения, м/с**2
        self.f = [0,0] #вектор силы гравитационного поля,Н
        self.trace_count = 0 #расчет трека, расстояние между точками
        self.trace = [] #массив точек трека
        self.status = True #статус существования
        self.name = ''  #имя объекта для удобства для записи в файл

        self.s_x = 0 #смещение центра масс по х для планет
        self.s_y = 0 #смещение центра масс по y для планет

    def update(self): #расчет характеристик тел в каждый момент времени
        self.a[0] = ((self.f[0]/self.m)*(vrem_k**2)/FPS**2) #расчет ускорения по 2 закону Ньютона a=F/m
        self.a[1] = ((self.f[1]/self.m)*(vrem_k**2)/FPS**2) #домноженный на поправочный коэффициент

        self.speed[0] +=  self.a[0] #расчет скорости
        self.speed[1] +=  self.a[1] 

        while (self.speed[0]>120000*(vrem_k/FPS) or self.speed[1]>120000*(vrem_k/FPS) or self.speed[0]<-120000*(vrem_k/FPS) or self.speed[1]<-120000*(vrem_k/FPS)):
            self.speed[0]/=2;
            self.speed[1]/=2;#принудительное ограничение скорости

        
        self.real_x += self.speed[0] #расчет координаты
        self.real_y += self.speed[1]


        if self.real_x>1000_000_000_000 or self.real_x<-1000_000_000_000 or self.real_y>1000_000_000_000 or self.real_y<-1000_000_000_000:
            self.status =False #уничтожаем объект при вылете за границу карты


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
                           ) #отрисовка самого объекта по геометрическому центру

       
        pygame.draw.circle(screen,
                           'black',
                           ((self.real_x - w_x + self.s_x)/k, 
                            (self.real_y - w_y + self.s_y)/k),
                           2
                           ) 
        pygame.draw.circle(screen,
                           'white',
                           ((self.real_x - w_x + self.s_x)/k, 
                            (self.real_y - w_y + self.s_y)/k),
                           1
                           ) #отрисовка центра масс (предназначено для планет)

        if atm==1 and self.types==2:
            pygame.draw.circle(screen,
                           self.colour,
                           ((self.real_x - w_x)/k, #вычисление координат места на карте для рисования
                            (self.real_y - w_y)/k),
                           (self.real_r+12000_000)/k,
                           2
                           ) #отрисовка контура атмосферы

        if wind==1 and self.types==1:
            pygame.draw.circle(screen,
                           'white',
                           ((self.real_x - w_x)/k, #вычисление координат места на карте для рисования
                            (self.real_y - w_y)/k),
                           (self.real_r-self.real_r/2)/k,
                           2
                           ) #отрисовка окружности (давление света)



        for i in self.trace:
            pygame.draw.circle(screen,
                           self.colour,
                           ((i[0] - w_x)/k,
                                (i[1] - w_y)/k),
                            1) #отрисовка трека по геометрическому центру



objects = []   #Объектов на карте 




tree = ET.parse("data.xml")
Ob=tree.findall('ObjectList/Object')
#Считывание с xml-файла данных с автоматическим вычислением и преобразованием в нужный тип данных
for i in range(len(Ob)):
    p = Objects(int(Ob[i].find('Type').text),
                float(ne.evaluate(Ob[i].find('CoordinateX').text)),
                float(ne.evaluate(Ob[i].find('CoordinateY').text)),
                float(ne.evaluate(Ob[i].find('Radius').text)),
                float(ne.evaluate(Ob[i].find('Weight').text)),
                Ob[i].find('Colour').text)
    objects.append(p)
    objects[i].speed[0]+=float(ne.evaluate(Ob[i].find('SpeedX').text))*(vrem_k/FPS)
    objects[i].speed[1]+= float(ne.evaluate(Ob[i].find('SpeedY').text))*(vrem_k/FPS)
    objects[i].name = Ob[i].find('Name').text;









    #objects[i].speed[0]+=Ob[i].find('SpeedX').text*(vrem_k/FPS)
    #objects[i].speed[1]+= Ob[i].find('SpeedY').text*(vrem_k/FPS)

    #print(Ob[i].find('Type').text)




#Солнце

#p = Objects(1,0,0,696_000_000,1.9891*10**30,'yellow')
#objects.append(p)


#Земля:
#p = Objects(2,-149.6*10**9,0,6371000,5.9722*10**24,'blue')
#objects.append(p)
#objects[1].speed[1]+= 29782.77*(vrem_k/FPS)

#Луна:
#p = Objects(2,-149.6*10**9+363104000,0,1737100,7.35*10**22,'grey')
#objects.append(p)
#p.speed[1] = 1080*(vrem_k/FPS)
#objects[2].speed[1]+= 29782.77*(vrem_k/FPS)


#Планета, которая вращается по эллиптической орбите
#p = Objects(3,69.6*10**9,30*10**9,6_371_000,5.9722*10**24,'brown')
#objects.append(p)
#objects[3].speed[1]+= 27782.77*(vrem_k/FPS)

#Юпитер
#p=Objects(2, -778_570_000_000,0,71492000,1.8986*10**27,'orange')
#objects.append(p)
#objects[4].speed[1]+= 13070*(vrem_k/FPS)

#Астероид 
#p=Objects(3, -149.6*10**9+123104000,149.6*10**9+1231040000, 463500, 9.393*10**20,'green')
#objects.append(p)
#objects[5].speed[0]+=3000*(vrem_k/FPS)
#objects[5].speed[1]+= 29782.77*(vrem_k/FPS)


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


        if event.type == pygame.KEYDOWN:
            if pygame.key.get_pressed()[pygame.K_1]:#включаем и выключаем отображение атмосферы
                if(atm==0):
                    atm=1
                else:
                    atm=0


            if pygame.key.get_pressed()[pygame.K_2]:#включаем и выключаем давление света
                if(wind==0):
                    wind=1
                else:
                    wind=0


            if pygame.key.get_pressed()[pygame.K_RETURN]:#включаем и выключаем запись в файл
                if(entry==0):
                    entry=1
                else:
                    entry=0


            if pygame.key.get_pressed()[pygame.K_UP]:  #изменяем ускорение времени 
                    vrem_k *= 10 #увеличение в 10 раз 
                    for i in objects:
                        i.speed[0]*=10
                        i.speed[1]*=10
                    text_vrem_k = font.render('Time: x'+str(vrem_k), True,'white') #пишем множитель времени
            if pygame.key.get_pressed()[pygame.K_DOWN]:  #изменяем ускорение времени 
                    vrem_k /= 10 #уменьшение в 10 раз 
                    for i in objects:
                        i.speed[0]/=10
                        i.speed[1]/=10
                    text_vrem_k = font.render('Time: x'+str(vrem_k), True,'white') #пишем множитель времени
                
                


            
        if event.type == pygame.MOUSEBUTTONDOWN:
            #Найдём место на реальной карте,
            #куда хочет попасть пользователь:
            xx = event.pos[0] #положение курсора по х в окне 
            yy = event.pos[1] #положение курсора по y в окне
            jump_x = w_x + xx*k #положение курсора по х на реальной карте
            jump_y = w_y + yy*k  #положение курсора по y на реальной карте





            if event.button == 3:#задаем вручную центр масс
                for ball in objects:
                    if ((jump_x-ball.real_x)**2+(jump_y-ball.real_y)**2)**0.5<ball.real_r and ball.types==2:#если курсор попадает в планету
                       ball.s_x =  jump_x-ball.real_x #вычисляем смещение центра по x и по y
                       ball.s_y =  jump_y-ball.real_y


            
            if event.button == 4:  #уменьшение масштаба (приближение)
               if k>100_000:
                    k = k*0.85


               w_x = jump_x - xx*k #обновляем положение угла окна на реальной карте
               w_y = jump_y - yy*k

            if event.button == 2:

                #добавление рандомной планеты
                q=Objects(2,jump_x,jump_y,rn.uniform(100000, 5000000),rn.uniform(1, 5)*10**rn.randint(25, 30),'purple')
                objects.append(q)
                q.speed[0] = rn.uniform(-100000000, 100000000)
                q.speed[1] = rn.uniform(-100000000, 100000000)
                q.name = 'Planet'+str(rn.randint(10, 1000))
                
            if event.button == 5:  #увеличение масштаба (отдаление)
               if k<100_000_000_0:
                    k = k/0.85

               w_x = jump_x - xx*k
               w_y = jump_y - yy*k



                        
            
                
        if event.type == pygame.MOUSEMOTION: #перемещение карты
            if pygame.mouse.get_pressed()[0] == True:
                w_x -= event.rel[0]*k #обновляем положение угла окна на реальной карте 
                w_y -= event.rel[1]*k #по относительному смещению положения курсора
            
    collisions = [] #массив индексов объектов, которые вошли в коллизию


    #считаем действующие силы на каждое тело
    for i in range(len(objects)): #цикл по длине массива объектов
        for j in range(i+1,len(objects)): #выбираем второй объект, не совпадающий с первым
            dx = (objects[j].real_x+objects[j].s_x)-(objects[i].real_x+objects[i].s_x) #проекция расстояния между двумя объектами (центрами масс) по x
            dy = (objects[j].real_y+objects[j].s_y)-(objects[i].real_y+objects[i].s_y) #проекция расстояния между двумя объектами (центрами масс) по y
            d = (dx**2+dy**2)**0.5 #действительное расстояние
            ff = G*objects[i].m*objects[j].m/d**2 #закон всемирного тяготения
            
            if wind==1 and objects[i].types==1:
                fw = I/299_792_458*(1-0.1+0.9)*2*3.141592*objects[j].real_r #расчет силы давления света, действующего на объект
                if objects[j].types!=1:
                    objects[j].f[0] += dx*fw/d #коррекция сил
                    objects[j].f[1] += dy*fw/d
            


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
            if t1.real_r > t2.real_r: #устанавливаем тип,цвет и имя большего объекта
                c = t1.colour
                tp = t1.types
                nm = t1.name
            else:
                c = t2.colour
                tp = t2.types
                nm = t2.name
                
            t = Objects(tp,(t1.real_x*t1.m+t2.real_x*t2.m)/(t1.m+t2.m), #новые координаты по 
                            (t1.real_y*t1.m+t2.real_y*t2.m)/(t1.m+t2.m), #среднему арифметическому взвешенному
                            (t1.real_r**3+t2.real_r**3)**(1/3), #увеличиваем радиус
                            t1.m + t2.m, #складываем массу
                            c)
            t.speed[0] = (t1.m*t1.speed[0]+t2.m*t2.speed[0])/(t1.m+t2.m) #скорости после абсолютно неупругого удара по х
            t.speed[1] = (t1.m*t1.speed[1]+t2.m*t2.speed[1])/(t1.m+t2.m) #скорости после абсолютно неупругого удара по y
            t.name = nm;
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
    if entry==1:
        screen.blit(font.render('Rec', True,'red'), (150, 10)) #уведомление о записи в файл
    pygame.display.update()

    if entry==1:
    #записываем в файл весь массив траектории, если ее еще нет, то текущие координаты.
        f = open('Coords.txt', 'w') #открываем файл на запись 
        for ball in objects:
            f.write(" \n" + ball.name + ": \n")
            if len(ball.trace)>0:
                for i in range(len(ball.trace)):
                  f.write(str(ball.trace[i][0]) + "  "+ str(ball.trace[i][1]) + "\n")
            else:
                f.write(str(ball.real_x) + "  "+ str(ball.real_y) + "\n")
        f.close()#закрываем файл записи

pygame.quit()
