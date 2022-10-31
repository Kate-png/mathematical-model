import pygame
import time

WIDTH = 1200  #������ ����
HEIGHT = 800  #������ ����
FPS = 100 #������� ����������, ����� � �������
G = 6.67430/(10**(11)) #�������������� ���������� 
k = 1_000_000 #������ � ������� �� ������ �������������, ������� 

w_x = -600_000_000 #���������� ���� ���� 
w_y = -400_000_000 #�� ����� �����

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
        self.real_x = real_x #x ���������� ������ �������, �
        self.real_y = real_y #� ���������� ������ �������, �
        self.real_r = real_r #������, �
        self.m = m #�����, ��
        self.colour = colour #����
        self.speed = [0,0] #������ ��������, �/�
        self.a = [0,0] #������ ���������, �/�**2
        self.f = [0,0] #������ ���� ��������������� ����,�
        self.trace_count = 0 #������ �����, ���������� ����� �������
        self.trace = [] #������ ����� �����
        self.status = True #������ �������������

    def update(self): #������ ������������� ��� � ������ ������ �������
        self.a[0] = ((self.f[0]/self.m)*(vrem_k**2)/FPS**2) #������ ��������� �� 2 ������ ������� a=F/m
        self.a[1] = ((self.f[1]/self.m)*(vrem_k**2)/FPS**2) #����������� �� ����������� �����������

        self.speed[0] +=  self.a[0] #������ ��������
        self.speed[1] +=  self.a[1] 
        
        self.real_x += self.speed[0] #������ ����������
        self.real_y += self.speed[1]




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
                           ) #��������� ������ �������
        for i in self.trace:
            pygame.draw.circle(screen,
                           self.colour,
                           ((i[0] - w_x)/k,
                                (i[1] - w_y)/k),
                            1) #��������� �����

objects = []   #�������� �� �����     


#������
p = Objects(1,0,0,696_000_000,1.9891*10**30,'yellow')
objects.append(p)


#�����:
p = Objects(2,-149.6*10**9,0,6371000,5.9722*10**24,'blue')
objects.append(p)
objects[1].speed[1]+= 29782.77*(vrem_k/FPS)

#����:
p = Objects(2,-149.6*10**9+363104000,0,1737100,7.35*10**22,'grey')
objects.append(p)
p.speed[1] = 1080*(vrem_k/FPS)
objects[2].speed[1]+= 29782.77*(vrem_k/FPS)


#�������, ������� ��������� �� ������������� ������
p = Objects(2,69.6*10**9,30*10**9,6_371_000,5.9722*10**24,'brown')
objects.append(p)
objects[3].speed[1]+= 27782.77*(vrem_k/FPS)

#������
p=Objects(2, -778_570_000_000,0,71492000,1.8986*10**27,'orange')
objects.append(p)
objects[4].speed[1]+= 13070*(vrem_k/FPS)

#�������� 
p=Objects(3, -149.6*10**9+123104000,149.6*10**9+123104000, 463500, 9.393*10**20,'green')
objects.append(p)
objects[5].speed[0]+=3000*(vrem_k/FPS)
objects[5].speed[1]+= 29782.77*(vrem_k/FPS)


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
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            #����� ����� �� �������� �����,
            #���� ����� ������� ������������:
            xx = event.pos[0] #��������� ������� �� � � ���� 
            yy = event.pos[1] #��������� ������� �� y � ����
            jump_x = w_x + xx*k #��������� ������� �� � �� �������� �����
            jump_y = w_y + yy*k  #��������� ������� �� y �� �������� �����
            
            if event.button == 4:  #���������� �������� (�����������)
               if k>100_000:
                    k = k*0.85


               w_x = jump_x - xx*k #��������� ��������� ���� ���� �� �������� �����
               w_y = jump_y - yy*k
                
            if event.button == 5:  #���������� �������� (���������)
               if k<100_000_000_0:
                    k = k/0.85

               w_x = jump_x - xx*k
               w_y = jump_y - yy*k


            if event.button == 3: #�������� ��������� ������� 
                if vrem_k == 1_000_0000:
                    vrem_k = 1 #�����
                    for i in objects:
                        i.speed[0]/=100_00000
                        i.speed[1]/=100_00000
                else:
                    vrem_k *= 10 #���������� � 10 ��� 
                    for i in objects:
                        i.speed[0]*=10
                        i.speed[1]*=10
                        
                text_vrem_k = font.render('Time: x'+str(vrem_k), True,'white') #����� ��������� �������
                
        if event.type == pygame.MOUSEMOTION: #����������� �����
            if pygame.mouse.get_pressed()[0] == True:
                w_x -= event.rel[0]*k #��������� ��������� ���� ���� �� �������� ����� 
                w_y -= event.rel[1]*k #�� �������������� �������� ��������� �������
            
    collisions = [] #������ �������� ��������, ������� ����� � ��������


    #������� ����������� ���� �� ������ ����
    for i in range(len(objects)): #���� �� ����� ������� ��������
        for j in range(i+1,len(objects)): #�������� ������ ������, �� ����������� � ������
            dx = objects[j].real_x-objects[i].real_x #�������� ���������� ����� ����� ��������� (��������) �� x
            dy = objects[j].real_y-objects[i].real_y #�������� ���������� ����� ����� ��������� (��������) �� y
            d = (dx**2+dy**2)**0.5 #�������������� ����������
            ff = G*objects[i].m*objects[j].m/d**2 #����� ���������� ���������
            
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
            if t1.real_r > t2.real_r: #������������� ��� � ���� �������� �������
                c = t1.colour
                tp = t1.types
            else:
                c = t2.colour
                tp = t2.types
                
            t = Objects(tp,(t1.real_x*t1.m+t2.real_x*t2.m)/(t1.m+t2.m), #����� ���������� �� 
                            (t1.real_y*t1.m+t2.real_y*t2.m)/(t1.m+t2.m), #�������� ��������������� �����������
                            (t1.real_r**3+t2.real_r**3)**(1/3), #����������� ������
                            t1.m + t2.m, #���������� �����
                            c)
            t.speed[0] = (t1.m*t1.speed[0]+t2.m*t2.speed[0])/(t1.m+t2.m) #�������� ����� ��������� ���������� ����� �� �
            t.speed[1] = (t1.m*t1.speed[1]+t2.m*t2.speed[1])/(t1.m+t2.m) #�������� ����� ��������� ���������� ����� �� y
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
    pygame.display.update()
pygame.quit()
