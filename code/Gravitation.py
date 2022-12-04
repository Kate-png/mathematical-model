import pygame
import time
import xml.etree.ElementTree as ET
import numexpr as ne
import random as rn

WIDTH = 1200  #������ ����
HEIGHT = 800  #������ ����
FPS = 100 #������� ����������, ����� � �������
G = 6.67430/(10**(11)) #�������������� ���������� 
k = 1_000_000 #������ � ������� �� ������ �������������, ������� 

w_x = -600_000_000 #���������� ���� ���� 
w_y = -400_000_000 #�� ����� �����
atm = 0  #��������� � ���������� ���������
wind = 0 #�������� ���������� �����
I=83500 #�������������� ���������� ������
entry=0 #������ � ����


vrem_k = 1 # ����������� ��������� ������� �� ������, 1 - �������� �����, 


pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT)) #������������� ����
pygame.display.set_caption("Gravitation") #�������� ���������
clock = pygame.time.Clock()
font = pygame.font.SysFont('arial', 26) #����� � ������
text_FPS = font.render('FPS: '+str(FPS), True,'white') #������ ������� ���������� �� ������
text_vrem_k = font.render('Time: x'+str(vrem_k), True,'white') #������ ��������� ������� �� ������
                
class Objects(): #������ ���� ��������
    def __init__(self,types,real_x,real_y,real_r,m,colour):
        self.types = types; #��� ������������ �������: ������ = 1, ������� = 2 ��� �������� = 3
        self.real_x = real_x #x ���������� ��������������� ������ �������, �
        self.real_y = real_y #� ���������� ��������������� ������ �������, �
        self.real_r = real_r #������, �
        self.m = m #�����, ��
        self.colour = colour #����
        self.speed = [0,0] #������ ��������, �/�
        self.a = [0,0] #������ ���������, �/�**2
        self.f = [0,0] #������ ���� ��������������� ����,�
        self.trace_count = 0 #������ �����, ���������� ����� �������
        self.trace = [] #������ ����� �����
        self.status = True #������ �������������
        self.name = ''  #��� ������� ��� �������� ��� ������ � ����

        self.s_x = 0 #�������� ������ ���� �� � ��� ������
        self.s_y = 0 #�������� ������ ���� �� y ��� ������

    def update(self): #������ ������������� ��� � ������ ������ �������
        self.a[0] = ((self.f[0]/self.m)*(vrem_k**2)/FPS**2) #������ ��������� �� 2 ������ ������� a=F/m
        self.a[1] = ((self.f[1]/self.m)*(vrem_k**2)/FPS**2) #����������� �� ����������� �����������

        self.speed[0] +=  self.a[0] #������ ��������
        self.speed[1] +=  self.a[1] 

        while (self.speed[0]>120000*(vrem_k/FPS) or self.speed[1]>120000*(vrem_k/FPS) or self.speed[0]<-120000*(vrem_k/FPS) or self.speed[1]<-120000*(vrem_k/FPS)):
            self.speed[0]/=2;
            self.speed[1]/=2;#�������������� ����������� ��������

        
        self.real_x += self.speed[0] #������ ����������
        self.real_y += self.speed[1]


        if self.real_x>1000_000_000_000 or self.real_x<-1000_000_000_000 or self.real_y>1000_000_000_000 or self.real_y<-1000_000_000_000:
            self.status =False #���������� ������ ��� ������ �� ������� �����


        # ����������:
        self.trace_count += (self.speed[0]**2+self.speed[1]**2)**0.5 #������ ��� ����������� ����� ������� ��������
        if self.trace_count/k >= 5: #������� ��������� ����� �����
            self.trace_count = 0
            self.trace.append((self.real_x,
                                self.real_y))
        if len(self.trace)>1000: #����������� ����� �����: ���� ������ ����� � ����� �������� 1000,
            self.trace.pop(0)   #������� ��������� 
            
    def draw(self): #���������
        pygame.draw.circle(screen,
                           self.colour,
                           ((self.real_x - w_x)/k, #���������� ��������� ����� �� ����� ��� ���������
                            (self.real_y - w_y)/k),
                           self.real_r/k
                           ) #��������� ������ ������� �� ��������������� ������

       
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
                           ) #��������� ������ ���� (������������� ��� ������)

        if atm==1 and self.types==2:
            pygame.draw.circle(screen,
                           self.colour,
                           ((self.real_x - w_x)/k, #���������� ��������� ����� �� ����� ��� ���������
                            (self.real_y - w_y)/k),
                           (self.real_r+12000_000)/k,
                           2
                           ) #��������� ������� ���������

        if wind==1 and self.types==1:
            pygame.draw.circle(screen,
                           'white',
                           ((self.real_x - w_x)/k, #���������� ��������� ����� �� ����� ��� ���������
                            (self.real_y - w_y)/k),
                           (self.real_r-self.real_r/2)/k,
                           2
                           ) #��������� ���������� (�������� �����)



        for i in self.trace:
            pygame.draw.circle(screen,
                           self.colour,
                           ((i[0] - w_x)/k,
                                (i[1] - w_y)/k),
                            1) #��������� ����� �� ��������������� ������



objects = []   #�������� �� ����� 




tree = ET.parse("data.xml")
Ob=tree.findall('ObjectList/Object')
#���������� � xml-����� ������ � �������������� ����������� � ��������������� � ������ ��� ������
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




#������

#p = Objects(1,0,0,696_000_000,1.9891*10**30,'yellow')
#objects.append(p)


#�����:
#p = Objects(2,-149.6*10**9,0,6371000,5.9722*10**24,'blue')
#objects.append(p)
#objects[1].speed[1]+= 29782.77*(vrem_k/FPS)

#����:
#p = Objects(2,-149.6*10**9+363104000,0,1737100,7.35*10**22,'grey')
#objects.append(p)
#p.speed[1] = 1080*(vrem_k/FPS)
#objects[2].speed[1]+= 29782.77*(vrem_k/FPS)


#�������, ������� ��������� �� ������������� ������
#p = Objects(3,69.6*10**9,30*10**9,6_371_000,5.9722*10**24,'brown')
#objects.append(p)
#objects[3].speed[1]+= 27782.77*(vrem_k/FPS)

#������
#p=Objects(2, -778_570_000_000,0,71492000,1.8986*10**27,'orange')
#objects.append(p)
#objects[4].speed[1]+= 13070*(vrem_k/FPS)

#�������� 
#p=Objects(3, -149.6*10**9+123104000,149.6*10**9+1231040000, 463500, 9.393*10**20,'green')
#objects.append(p)
#objects[5].speed[0]+=3000*(vrem_k/FPS)
#objects[5].speed[1]+= 29782.77*(vrem_k/FPS)


tick = 0
tm = time.time()
running = True
while running:
    
    clock.tick(FPS) #������������� ����������� � ������������ �������� ����� ������� (�� ����� 100 ������ � �������)
    tick+=1
    if tick == 100:
        tick = 0
        text_FPS = font.render('FPS: '+str(int((100/(time.time() - tm)))), True,
                  'white') #��������� � ����� �������� �������� �������
        
        tm = time.time()
        
    #��������� �������
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #����� �� ���������
            running = False


        if event.type == pygame.KEYDOWN:
            if pygame.key.get_pressed()[pygame.K_1]:#�������� � ��������� ����������� ���������
                if(atm==0):
                    atm=1
                else:
                    atm=0


            if pygame.key.get_pressed()[pygame.K_2]:#�������� � ��������� �������� �����
                if(wind==0):
                    wind=1
                else:
                    wind=0


            if pygame.key.get_pressed()[pygame.K_RETURN]:#�������� � ��������� ������ � ����
                if(entry==0):
                    entry=1
                else:
                    entry=0


            if pygame.key.get_pressed()[pygame.K_UP]:  #�������� ��������� ������� 
                    vrem_k *= 10 #���������� � 10 ��� 
                    for i in objects:
                        i.speed[0]*=10
                        i.speed[1]*=10
                    text_vrem_k = font.render('Time: x'+str(vrem_k), True,'white') #����� ��������� �������
            if pygame.key.get_pressed()[pygame.K_DOWN]:  #�������� ��������� ������� 
                    vrem_k /= 10 #���������� � 10 ��� 
                    for i in objects:
                        i.speed[0]/=10
                        i.speed[1]/=10
                    text_vrem_k = font.render('Time: x'+str(vrem_k), True,'white') #����� ��������� �������
                
                


            
        if event.type == pygame.MOUSEBUTTONDOWN:
            #����� ����� �� �������� �����,
            #���� ����� ������� ������������:
            xx = event.pos[0] #��������� ������� �� � � ���� 
            yy = event.pos[1] #��������� ������� �� y � ����
            jump_x = w_x + xx*k #��������� ������� �� � �� �������� �����
            jump_y = w_y + yy*k  #��������� ������� �� y �� �������� �����





            if event.button == 3:#������ ������� ����� ����
                for ball in objects:
                    if ((jump_x-ball.real_x)**2+(jump_y-ball.real_y)**2)**0.5<ball.real_r and ball.types==2:#���� ������ �������� � �������
                       ball.s_x =  jump_x-ball.real_x #��������� �������� ������ �� x � �� y
                       ball.s_y =  jump_y-ball.real_y


            
            if event.button == 4:  #���������� �������� (�����������)
               if k>100_000:
                    k = k*0.85


               w_x = jump_x - xx*k #��������� ��������� ���� ���� �� �������� �����
               w_y = jump_y - yy*k

            if event.button == 2:

                #���������� ��������� �������
                q=Objects(2,jump_x,jump_y,rn.uniform(100000, 5000000),rn.uniform(1, 5)*10**rn.randint(25, 30),'purple')
                objects.append(q)
                q.speed[0] = rn.uniform(-100000000, 100000000)
                q.speed[1] = rn.uniform(-100000000, 100000000)
                q.name = 'Planet'+str(rn.randint(10, 1000))
                
            if event.button == 5:  #���������� �������� (���������)
               if k<100_000_000_0:
                    k = k/0.85

               w_x = jump_x - xx*k
               w_y = jump_y - yy*k



                        
            
                
        if event.type == pygame.MOUSEMOTION: #����������� �����
            if pygame.mouse.get_pressed()[0] == True:
                w_x -= event.rel[0]*k #��������� ��������� ���� ���� �� �������� ����� 
                w_y -= event.rel[1]*k #�� �������������� �������� ��������� �������
            
    collisions = [] #������ �������� ��������, ������� ����� � ��������


    #������� ����������� ���� �� ������ ����
    for i in range(len(objects)): #���� �� ����� ������� ��������
        for j in range(i+1,len(objects)): #�������� ������ ������, �� ����������� � ������
            dx = (objects[j].real_x+objects[j].s_x)-(objects[i].real_x+objects[i].s_x) #�������� ���������� ����� ����� ��������� (�������� ����) �� x
            dy = (objects[j].real_y+objects[j].s_y)-(objects[i].real_y+objects[i].s_y) #�������� ���������� ����� ����� ��������� (�������� ����) �� y
            d = (dx**2+dy**2)**0.5 #�������������� ����������
            ff = G*objects[i].m*objects[j].m/d**2 #����� ���������� ���������
            
            if wind==1 and objects[i].types==1:
                fw = I/299_792_458*(1-0.1+0.9)*2*3.141592*objects[j].real_r #������ ���� �������� �����, ������������ �� ������
                if objects[j].types!=1:
                    objects[j].f[0] += dx*fw/d #��������� ���
                    objects[j].f[1] += dy*fw/d
            


            objects[i].f[0] += dx*ff/d #�������� ���� �� � ��� ������� �������
            objects[i].f[1] += dy*ff/d #�������� ���� �� y ��� ������� �������


            objects[j].f[0] -= dx*ff/d #�������� ���� �� � ��� ������� �������
            objects[j].f[1] -= dy*ff/d #�������� ���� �� y ��� ������� �������

            if objects[i].real_r > d - objects[j].real_r: #��������, �� ����������� �� �������
                collisions.append((i,j))
                
    #���������� ������������:
    for i in collisions:
        t1 = objects[i[0]]
        t2 = objects[i[1]]
        if t1.status and t2.status:
            t1.status = False #���������� �������
            t2.status = False
            if t1.real_r > t2.real_r: #������������� ���,���� � ��� �������� �������
                c = t1.colour
                tp = t1.types
                nm = t1.name
            else:
                c = t2.colour
                tp = t2.types
                nm = t2.name
                
            t = Objects(tp,(t1.real_x*t1.m+t2.real_x*t2.m)/(t1.m+t2.m), #����� ���������� �� 
                            (t1.real_y*t1.m+t2.real_y*t2.m)/(t1.m+t2.m), #�������� ��������������� �����������
                            (t1.real_r**3+t2.real_r**3)**(1/3), #����������� ������
                            t1.m + t2.m, #���������� �����
                            c)
            t.speed[0] = (t1.m*t1.speed[0]+t2.m*t2.speed[0])/(t1.m+t2.m) #�������� ����� ��������� ���������� ����� �� �
            t.speed[1] = (t1.m*t1.speed[1]+t2.m*t2.speed[1])/(t1.m+t2.m) #�������� ����� ��������� ���������� ����� �� y
            t.name = nm;
            objects.append(t)
    


    tt = [] #��������� � ������ ������ �� �������, ������� ����������
    for ball in objects: 
        if ball.status:
            tt.append(ball)
    objects = tt #��������� ����������� ������ �������� (��������� ��������������)
            
    for ball in objects:
        ball.update()
        ball.f = [0,0] #��������� � ���������� ����

        
    #������
    screen.fill('black')
    
    for ball in objects:
        ball.draw()
        
    screen.blit(text_FPS, (10, 10)) #��������� ��� �� ������
    screen.blit(text_vrem_k, (10, 30)) #��������� ��������� �������
    if entry==1:
        screen.blit(font.render('Rec', True,'red'), (150, 10)) #����������� � ������ � ����
    pygame.display.update()

    if entry==1:
    #���������� � ���� ���� ������ ����������, ���� �� ��� ���, �� ������� ����������.
        f = open('Coords.txt', 'w') #��������� ���� �� ������ 
        for ball in objects:
            f.write(" \n" + ball.name + ": \n")
            if len(ball.trace)>0:
                for i in range(len(ball.trace)):
                  f.write(str(ball.trace[i][0]) + "  "+ str(ball.trace[i][1]) + "\n")
            else:
                f.write(str(ball.real_x) + "  "+ str(ball.real_y) + "\n")
        f.close()#��������� ���� ������

pygame.quit()
