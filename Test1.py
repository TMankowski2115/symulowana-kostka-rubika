from ursina import *
import time
import random
import datetime



class Timer:
    def __init__(self):
        self.wlacznik=False
        self.poczatek=0
        self.koncowy_czas=0
    
    def start(self):
        self.wlacznik=True
        self.poczatek= time.time()
    
    def stop(self):
        self.wlacznik=False
    
    
    def podaj_czas(self):
        if self.wlacznik==True:
            self.koncowy_czas= time.time()- self.poczatek
            return time.time()- self.poczatek
        else:
            return self.koncowy_czas
    def pauzowanie(self):
        if self.wlacznik==True:
                self.stop()
        
        else:
                self.start()


class Gra(Ursina):
    def __init__(self):
        super().__init__()
        # tryb
        # 1 - ruch
        # 2 - ułóż
        # 3 - cofnij
        # 4 - mieszaj 
        self.RUCH = 1
        self.ULOZ = 2
        self.COFNIJ = 3
        self.MIESZAJ =4
        self.rotation_direction = 1
        window.fullscreen = False
        Entity(model='sphere', scale=10000, texture='Zenek1', double_sided=True)
        EditorCamera()
        
        camera.world_position = (0, 0, -15)
        self.load_game()
        
        self.wykonane_ruchy=[]
        self.stoper= Timer()
        
        self.Licznik_Czasu=Button(text="Mierz czas", color=color.red, scale=.13, position = (0.45, -0.4), on_click= self.stoper.pauzowanie)
        self.Cofanie=Button(text="Cofnij ruch", color=color.red, scale=.13, position = (0.60, -0.4), on_click= self.cofnij_ruch)
        self.Ukladanie=Button(text="Ulóż kostkę!", color=color.red, scale=.13, position = (0.75, -0.4), on_click= self.uloz_kostke)
        self.Losowanie=Button(text="Pomieszaj!", color=color.red, scale=.13, position = (0.45, -0.25), on_click= self.pomieszaj_kostke)
        self.czas= Text(text=f"Twój czas: 0.0 sekund", color= color.red, position=(-0.50, 0.4), size=.05)
        self.Zapisz=Button(text="Zapisz", color=color.red, scale=.13, position=(0.6, -0.25), on_click=self.zapisz_ruchy_do_pliku)
        self.Zapisz=Button(text="Wczytaj", color=color.red, scale=.13, position=(0.75, -0.25), on_click=self.wczytaj_ruchy_z_pliku)
        self.update()

     
            
    
     

    def zapisz_ruchy_do_pliku(self):
        with open("zapis.txt", 'w') as plik:
            for i in self.wykonane_ruchy:
                plik.write(f'{i}\n')
     
    def wczytaj_ruchy_z_pliku(self):
        self.uloz_kostke()
        with open("zapis.txt", 'r') as plik:
            for i in plik:
                self.wykonane_ruchy.append(i.strip())
            self.uloz_kostke_zostaw_liste()


    
    def update(self):
        twoj_czas= self.stoper.podaj_czas()
        self.czas.text= f'Twój czas: {twoj_czas:.2f} sekund'
        invoke(self.update, delay=0.1)
      
    def pomieszaj_kostke(self):
        liczba_przemieszan= random.randint(15, 25)
        lista_kolorow=['BIALA', 'ZOLTA', 'CZERWONA', 'POMARANCZOWA', 'NIEBIESKA', 'ZIELONA']
        lista_kierunkow= [-90, 90]
        for i in range(0, liczba_przemieszan):
            strona= random.choice(lista_kolorow)
            kierunek= random.choice(lista_kierunkow)
            self.obroc_kostke(strona, kierunek, self.MIESZAJ)

    def cofnij_ruch(self):
        
       
        if len(self.wykonane_ruchy)!=0:
            stronka=self.wykonane_ruchy[-2]
            kierunek=int(self.wykonane_ruchy[-1])
            self.obroc_kostke(stronka, -kierunek, self.COFNIJ)
            self.wykonane_ruchy.pop()
            self.wykonane_ruchy.pop()
            
    def uloz_kostke_zostaw_liste(self):

        if len(self.wykonane_ruchy)!=0:

            
            for i in range(int(len(self.wykonane_ruchy)/2)):
                stronka=self.wykonane_ruchy[2*i]
                kierunek=int(self.wykonane_ruchy[2*i+1])
                self.obroc_kostke(stronka, kierunek, self.ULOZ)

    def uloz_kostke(self):

        if len(self.wykonane_ruchy)!=0:

            
            while len(self.wykonane_ruchy)>0:
                    stronka=self.wykonane_ruchy[-2]
                    kierunek=int(self.wykonane_ruchy[-1])
                    self.obroc_kostke(stronka, -kierunek, self.ULOZ)
                    self.wykonane_ruchy.pop()
                    self.wykonane_ruchy.pop()
                    

                
    def load_game(self):
        self.stworz_pozycje_kosteczek()
        self.poboczne = [Entity(model='rubik', texture='Cube', position = pos) for pos in self.SIDE_POSITIONS]
        self.main_cube = Entity(model='rubik', collider='box', texture= 'Chess_Board')
        self.osie_obrotu = {'ZIELONA': 'x', 'NIEBIESKA': 'x', 'BIALA': 'y', 'ZOLTA': 'y', 'CZERWONA': 'z', 'POMARANCZOWA': 'z'}
        self.krawedzie_kostki = {'ZIELONA': self.LEFT, 'ZOLTA': self.BOTTOM, 'NIEBIESKA': self.RIGHT, 'CZERWONA': self.FACE, 'POMARANCZOWA': self.BACK, 'BIALA': self.TOP}
        self.animation_time = 0.5
        self.tworzenie_hitboxow()
        self.blokada_ruchu =False
        self.spectator_mode= True
        
        
        self.opcje = Text( origin = (0, 16), color= color.red)
        self.zmien_tryb_gry()
       
      
    def obroc_kostke(self, nazwa_strony, stopnie, tryb):
        if tryb==1 or tryb==4: #zwykly ruch / #ruch mieszania (bez animacji)
            self.blokada_ruchu = True
            cube_positions= self.krawedzie_kostki[nazwa_strony]
            os_obrotu = self.osie_obrotu[nazwa_strony]
            stopnie= stopnie
            self.zmien_nadrzedna()
            for cube in self.poboczne:
                if cube.position in cube_positions:
                    cube.parent= self.main_cube
                    if tryb == 1:
                        eval(f'self.main_cube.animate_rotation_{os_obrotu}({stopnie}, duration = self.animation_time)')
                    elif tryb ==4:
                        exec(f'self.main_cube.rotation_{os_obrotu} = {stopnie}')
            invoke(self.blokada_ruchu_gracza, delay= self.animation_time + 0.1)                            
            self.wykonane_ruchy.append(nazwa_strony)
            self.wykonane_ruchy.append(stopnie)
        elif tryb==2: #dla ukladania calej
            cube_positions= self.krawedzie_kostki[nazwa_strony]
            os_obrotu = self.osie_obrotu[nazwa_strony]
            stopnie= stopnie
            self.zmien_nadrzedna()
            for cube in self.poboczne:
                if cube.position in cube_positions:
                    cube.parent= self.main_cube
                    exec(f'self.main_cube.rotation_{os_obrotu} = {stopnie}')
        elif tryb==3: #dla cofania
            cube_positions= self.krawedzie_kostki[nazwa_strony]
            os_obrotu = self.osie_obrotu[nazwa_strony]
            stopnie= stopnie
            self.zmien_nadrzedna()
            for cube in self.poboczne:
                if cube.position in cube_positions:
                    cube.parent= self.main_cube
                    eval(f'self.main_cube.animate_rotation_{os_obrotu}({stopnie}, duration = 0.1)')

    def blokada_ruchu_gracza(self):
        self.blokada_ruchu = not self.blokada_ruchu

    def zmien_tryb_gry(self):
        self.spectator_mode= not self.spectator_mode
        wiadomosc = dedent(f"{'TRYB SWOBODNY' if self.spectator_mode==True else 'TRYB UKLADANIA'}" f" zmiana trybu- środkowy przycisk myszy").strip()
        self.opcje.text = wiadomosc

    def zmien_nadrzedna(self):
        for cube in self.poboczne:
            if cube.parent == self.main_cube:
                world_pose, world_rot = round(cube.world_position, 1), cube.world_rotation
                cube.parent= scene
                cube.position, cube.rotation = world_pose, world_rot
        self.main_cube.rotation = 0 

    def stworz_hitboxa(self, nazwa, pozycja, skala):
        self.hitbox = Entity(name=nazwa, position=pozycja, model='rubik', scale= skala, collider= 'box', visible=False)

    def tworzenie_hitboxow(self):
        self.LG= self.stworz_hitboxa("czerwony_LG", pozycja=(-1, 1 , -1.5), skala=(1, 1, 0.1))
        self.PG= self.stworz_hitboxa("czerwony_PG", pozycja=(1, 1 , -1.5), skala=(1, 1, 0.1))
        self.LD= self.stworz_hitboxa("czerwony_LD", pozycja=(-1,-1 , -1.5), skala=(1, 1, 0.1))
        self.PD= self.stworz_hitboxa("czerwony_PD", pozycja=(1, -1 , -1.5), skala=(1, 1, 0.1))
        self.LG= self.stworz_hitboxa("zielony_LG", pozycja=(-1.5, 1 , 1), skala=(0.1, 1, 1))
        self.PG= self.stworz_hitboxa("zielony_PG", pozycja=(-1.5, 1 , -1), skala=(0.1, 1, 1))
        self.LD= self.stworz_hitboxa("zielony_LD", pozycja=(-1.5, -1 , 1), skala=(0.1, 1, 1))
        self.PD= self.stworz_hitboxa("zielony_PD", pozycja=(-1.5, -1 , -1), skala=(0.1, 1, 1))
        self.LG= self.stworz_hitboxa("niebieski_LG", pozycja=(1.5, 1 , -1), skala=(0.1, 1, 1))
        self.PG= self.stworz_hitboxa("niebieski_PG", pozycja=(1.5, 1 , 1), skala=(0.1, 1, 1))
        self.LD= self.stworz_hitboxa("niebieski_LD", pozycja=(1.5, -1 , -1), skala=(0.1, 1, 1))
        self.PD= self.stworz_hitboxa("niebieski_PD", pozycja=(1.5, -1 , 1), skala=(0.1, 1, 1))
        self.LG= self.stworz_hitboxa("pomaranczowy_LG", pozycja=(1, 1 , 1.5), skala=(1, 1, 0.1))
        self.PG= self.stworz_hitboxa("pomaranczowy_PG", pozycja=(-1, 1 , 1.5), skala=(1, 1, 0.1))
        self.LD= self.stworz_hitboxa("pomaranczowy_LD", pozycja=(1,-1 , 1.5), skala=(1, 1, 0.1))
        self.PD= self.stworz_hitboxa("pomaranczowy_PD", pozycja=(-1, -1 , 1.5), skala=(1, 1, 0.1))
        self.LG= self.stworz_hitboxa("void_1", pozycja=(0, 0 , 0), skala=(3, 3, 0.1))
        self.LG= self.stworz_hitboxa("void_2", pozycja=(0, 0 , 0), skala=(3, 0.1, 3))
        self.LG= self.stworz_hitboxa("void_3", pozycja=(0, 0 , 0), skala=(0.1, 3, 3))
        self.LG= self.stworz_hitboxa("void_4", pozycja=(0, 1.5 , 0), skala=(3, 0.1, 3))
        self.LG= self.stworz_hitboxa("void_5", pozycja=(0, -1.5 , 0), skala=(3, 0.1, 3))
        # self.GORNY= self.stworz_hitboxa("GORA", pozycja= (0, 0.99, 0),  skala=(3, 1, 3))
        # self.DOLNY= self.stworz_hitboxa("DOL", pozycja= (0, -0.99, 0),  skala=(3, 1, 3))
        # self.LEWY= self.stworz_hitboxa("LEWA", pozycja= (-0.99, 0, 0),  skala=(1, 3, 3))
        # self.PRAWY= self.stworz_hitboxa("PRAWA", pozycja= (0.99, 0, 0),  skala=(1, 3, 3))
        # self.PRZOD= self.stworz_hitboxa("PRZOD", pozycja= (0, 0, -0.99),  skala=(3, 3, 1))
        # self.TYL= self.stworz_hitboxa("TYL", pozycja= (0, 0, 0.99),  skala=(3, 3, 1))

    def input(self, key):
        super().input(key)

        if key in 'mouse1 mouse3' and self.blokada_ruchu==False and self.spectator_mode==False:
            
            stopnie = 90

            for kontakt in mouse.collisions:
                    nazwa_strony= kontakt.entity.name
                    if ((key== 'mouse1' or key=='mouse3') and nazwa_strony in 'void_1 void_2 void_3 void_4 void_5'):
                        break

                    if ((key== 'mouse1' or key=='mouse3') and nazwa_strony in 'czerwony_LG czerwony_PG czerwony_LD czerwony_PD'):

                        if (key=='mouse1' and nazwa_strony =='czerwony_LG'):
                            self.obroc_kostke('ZIELONA', stopnie, self.RUCH)
                        elif (key=='mouse1' and nazwa_strony =='czerwony_LD'):
                            self.obroc_kostke('ZIELONA', -stopnie, self.RUCH)
                        elif (key=='mouse1' and nazwa_strony =='czerwony_PG'):
                            self.obroc_kostke('NIEBIESKA', stopnie, self.RUCH)
                        elif (key=='mouse1' and nazwa_strony =='czerwony_PD'):
                            self.obroc_kostke('NIEBIESKA', -stopnie, self.RUCH)
                        elif (key=='mouse3' and nazwa_strony =='czerwony_PG'):
                            self.obroc_kostke('BIALA', -stopnie, self.RUCH)
                        elif (key=='mouse3' and nazwa_strony =='czerwony_LG'):
                            self.obroc_kostke('BIALA', stopnie, self.RUCH)
                        elif (key=='mouse3' and nazwa_strony =='czerwony_PD'):
                            self.obroc_kostke('ZOLTA', -stopnie, self.RUCH)
                        elif (key=='mouse3' and nazwa_strony =='czerwony_LD'):
                            self.obroc_kostke('ZOLTA', stopnie, self.RUCH)
                        
                        break
                    elif ((key== 'mouse1' or key=='mouse3') and nazwa_strony in 'zielony_LG zielony_PG zielony_LD zielony_PD'):
                        if (key=='mouse1' and nazwa_strony =='zielony_LG'):
                            self.obroc_kostke('POMARANCZOWA', stopnie, self.RUCH)
                        elif (key=='mouse1' and nazwa_strony =='zielony_LD'):
                            self.obroc_kostke('POMARANCZOWA', -stopnie, self.RUCH)
                        elif (key=='mouse1' and nazwa_strony =='zielony_PG'):
                            self.obroc_kostke('CZERWONA', stopnie, self.RUCH)
                        elif (key=='mouse1' and nazwa_strony =='zielony_PD'):
                            self.obroc_kostke('CZERWONA', -stopnie, self.RUCH)
                        elif (key=='mouse3' and nazwa_strony =='zielony_PG'):
                            self.obroc_kostke('BIALA', -stopnie, self.RUCH)
                        elif (key=='mouse3' and nazwa_strony =='zielony_LG'):
                            self.obroc_kostke('BIALA', stopnie, self.RUCH)
                        elif (key=='mouse3' and nazwa_strony =='zielony_PD'):
                            self.obroc_kostke('ZOLTA', -stopnie, self.RUCH)
                        elif (key=='mouse3' and nazwa_strony =='zielony_LD'):
                            self.obroc_kostke('ZOLTA', stopnie, self.RUCH)

                        break
                    elif ((key== 'mouse1' or key=='mouse3') and nazwa_strony in 'pomaranczowy_LG pomaranczowy_PG pomaranczowy_LD pomaranczowy_PD'):
                        if (key=='mouse1' and nazwa_strony =='pomaranczowy_LG'):
                            self.obroc_kostke('NIEBIESKA', -stopnie, self.RUCH)
                        elif (key=='mouse1' and nazwa_strony =='pomaranczowy_LD'):
                            self.obroc_kostke('NIEBIESKA', stopnie, self.RUCH)
                        elif (key=='mouse1' and nazwa_strony =='pomaranczowy_PG'):
                            self.obroc_kostke('ZIELONA', -stopnie, self.RUCH)
                        elif (key=='mouse1' and nazwa_strony =='pomaranczowy_PD'):
                            self.obroc_kostke('ZIELONA', stopnie, self.RUCH)
                        elif (key=='mouse3' and nazwa_strony =='pomaranczowy_PG'):
                            self.obroc_kostke('BIALA', -stopnie, self.RUCH)
                        elif (key=='mouse3' and nazwa_strony =='pomaranczowy_LG'):
                            self.obroc_kostke('BIALA', stopnie, self.RUCH)
                        elif (key=='mouse3' and nazwa_strony =='pomaranczowy_PD'):
                            self.obroc_kostke('ZOLTA', -stopnie, self.RUCH)
                        elif (key=='mouse3' and nazwa_strony =='pomaranczowy_LD'):
                            self.obroc_kostke('ZOLTA', stopnie, self.RUCH)

                        break
                    elif ((key== 'mouse1' or key=='mouse3') and nazwa_strony in 'niebieski_LG niebieski_PG niebieski_LD niebieski_PD'):
                        if (key=='mouse1' and nazwa_strony =='niebieski_LG'):
                            self.obroc_kostke('CZERWONA', -stopnie, self.RUCH)
                        elif (key=='mouse1' and nazwa_strony =='niebieski_LD'):
                            self.obroc_kostke('CZERWONA', stopnie, self.RUCH)
                        elif (key=='mouse1' and nazwa_strony =='niebieski_PG'):
                            self.obroc_kostke('POMARANCZOWA', -stopnie, self.RUCH)
                        elif (key=='mouse1' and nazwa_strony =='niebieski_PD'):
                            self.obroc_kostke('POMARANCZOWA', stopnie, self.RUCH)
                        elif (key=='mouse3' and nazwa_strony =='niebieski_PG'):
                            self.obroc_kostke('BIALA', -stopnie, self.RUCH)
                        elif (key=='mouse3' and nazwa_strony =='niebieski_LG'):
                            self.obroc_kostke('BIALA', stopnie, self.RUCH)
                        elif (key=='mouse3' and nazwa_strony =='niebieski_PD'):
                            self.obroc_kostke('ZOLTA', -stopnie, self.RUCH)
                        elif (key=='mouse3' and nazwa_strony =='niebieski_LD'):
                            self.obroc_kostke('ZOLTA', stopnie, self.RUCH)
                        break


            

        if key == 'mouse2':
            self.zmien_tryb_gry()
               
    def stworz_pozycje_kosteczek(self):
        self.LEFT = {Vec3(-1, y, z) for y in range(-1, 2) for z in range(-1, 2)}
        self.BOTTOM = {Vec3(x, -1, z) for x in range(-1, 2) for z in range(-1, 2)}
        self.FACE = {Vec3(x, y, -1) for x in range(-1, 2) for y in range(-1, 2)}
        self.BACK = {Vec3(x, y, 1) for x in range(-1, 2) for y in range(-1, 2)}
        self.RIGHT = {Vec3(1, y, z) for y in range(-1, 2) for z in range(-1, 2)}
        self.TOP = {Vec3(x, 1, z) for x in range(-1, 2) for z in range(-1, 2)}
        #self.SIDE_POSITIONS = self.BOTTOM |self.BACK 
        self.SIDE_POSITIONS = self.LEFT | self.BOTTOM | self.FACE | self.BACK | self.RIGHT | self.TOP     
     


if __name__ == '__main__':
    app = Gra()
    app.run()
    
   


