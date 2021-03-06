import matplotlib.pyplot as plt
import numpy as np
import matplotlib.widgets as wdg

class rayon:
    """ 
    Tracé d'un rayon lumineux et détermination des points de contact

    ----------
    x : float
        Abscisse du point d'origine du rayon.
    y : float
        Ordonnée du point d'origine du rayon.
    teta : float
        Angle du rayon par rapport à l'axe des abscisses.
    color : str
        Couleur du rayon.
    direction : bool
        Direction de propagation du rayon (True = vers la droite)
    origine : object
        Origine du rayon (None si provient d'une source)
    """
    def __init__(self,figure, x =0, y=0, teta=0, color = "k", direction = True, origine = None):
        self.x = x  #abscisse d'origine
        self.y =y   #ordonnée d'origine
        self.teta = teta    #angle du rayon par rapport à l'axe des abscisses
        self.color = color  #Couleur du rayon
        self.direction = direction  #Direction du rayon
        self.origine = origine      #Permet de savoir l'origine du rayon (de quel miroir il provient), utile pour le débogage
        
        self.fig, self.ax = figure  #Figure sur laquelle tracer
        
        
        
        if self.direction: #Défini le vecteur x conrrespondant a la direction du rayon
            self.x_array = np.linspace(self.x,self.x+20)
        else:
            self.x_array = np.linspace(self.x, self.x-20)
        
        if origine != None:
            self.color="C1"
        
        
        #On appelle la méthode check() permettant de déterminer si le rayon entre en contact avec un miroir
        self.check()
        
    def trace(self):
        #méthode traçant le rayon
        y = (self.x_array-self.x)*np.tan(self.teta) +self.y #vecteur y
        
        self.ax.plot(self.x_array, y,self.color, alpha = 0.2) #plot
        
    def check(self):
        #Méthode vérifiant si le rayon entre en contact avec un obstacle (dioptre ou miroir)
        def fonction(liste):
            #Fonction prenant en entrée la liste des dioptre de la figure vérifiant si le rayon entre en contact avec un dioptre.
            #Si le rayon va vers la gauche, la liste indiquée sera la liste contenant les dioptre parcourue dans le sens inverse.
            
            for dioptre in liste:   #Pour tous les dioptres
                
                #Résolution de l'équation
                A = 1+(np.tan(self.teta)**2)
                B = -2*dioptre.c -2*self.x*(np.tan(self.teta)**2)+2*self.y*np.tan(self.teta)
                C = (dioptre.c)**2 + (self.x**2)*(np.tan(self.teta)**2) - 2*self.y*self.x*np.tan(self.teta) + (self.y**2) - (dioptre.r**2)

                delta = (B**2)-(4*A*C)
                if delta < 0:
                    continue

                #On choisi la bonne solution en fonction de l'interface rencontrée
                if dioptre.side:
                    X1 = (-B-np.sqrt(delta))/(2*A)
                else:
                    X1 = (-B+np.sqrt(delta))/(2*A)
                Y1 = (X1-self.x)*np.tan(self.teta) +self.y

                #Sécurité pour éviter de créer un deuxième rayon réfléchi au point de départ d'un rayon réfléchi
                if round(X1,1) == round(self.x,1):
                    continue

                #On vérifie si le programme n'as pas choisi la mauvaise solution, et que la solution est bien sur l'interface
                if (Y1 > dioptre.min and Y1 < dioptre.max) and (X1 > np.min(dioptre.xc) and X1 < np.max(dioptre.xc)) and X1 < np.max(self.x_array)  and X1 > np.min(self.x_array):                
                    self.x_array = np.linspace(self.x, X1, 100)
                
                    #On calcul l'angle de la normale en fonction de l'interface rencontrée
                    if dioptre.side:
                        teta_rayon = np.pi - np.arctan(Y1/(dioptre.c-X1))
                    else:
                        teta_rayon = np.arctan(Y1/(X1 - dioptre.c))
                    
                    #Calcul de l'angle entre la normale et le rayon incident
                    beta = (np.pi - teta_rayon + self.teta)
                    
                    #Calcul de l'angle entre la normale et le rayon réfracté
                    alpha = np.arcsin((np.sin(beta)*dioptre.n_left)/dioptre.n_right)
                



                    if (self.direction and dioptre.side) or (not self.direction and not dioptre.side):
                        teta_nouveau = teta_rayon + alpha - np.pi
                    else:
                        teta_nouveau = -alpha + teta_rayon


   
                    #Création d'un rayon réfracté en fonction du point d'impact et de l'angle calculé précédemment
                    lst_ray.append(rayon((self.fig,self.ax),X1,Y1, teta_nouveau, origine = dioptre, direction = self.direction))
        
        #Si le rayon se dirige vers la droite, la liste est parcourue dans son sens normal, sinon dans son sens inverse
        if self.direction:
            fonction(lst_dioptre)
        else:
            fonction(lst_dioptre[::-1])

        for miroir in lst_miroir: #Pour chaque miroir existant
            #Résolution de l'équation
            A = 1+(np.tan(self.teta)**2)
            B = -2*(miroir.x-miroir.r) -2*self.x*(np.tan(self.teta)**2)+2*self.y*np.tan(self.teta)
            C = (miroir.x-miroir.r)**2 + (self.x**2)*(np.tan(self.teta)**2) - 2*self.y*self.x*np.tan(self.teta) + (self.y**2) - (miroir.r**2)

            delta = (B**2)-(4*A*C)

            #Si delta négatif, pas de solution, on passe le tour de boucle
            if delta <0:
                continue
            #Si r>0, la solution est sur la droite du "cercle", sinon elle est sur la gauche du "cercle"
            if miroir.r>0:
                X1 = (-B+np.sqrt(delta))/(2*A)
            else:
                X1 = (-B-np.sqrt(delta))/(2*A)
            Y1 = (X1-self.x)*np.tan(self.teta) +self.y  #Calcul de l'ordonnée du point de contact

            if round(X1) == round(self.x): #Sécurité pour éviter de créer un deuxième rayon réfléchi au point de départ d'un rayon réfléchi
                continue
            
            #On vérifie si le programme n'as pas choisi la mauvaise solution, et que la solution est bien sur le miroir
            if Y1 < miroir.max and Y1 > miroir.min and (((self.direction == False) and (self.x > miroir.x)) or ((self.direction == True) and (self.x < miroir.x)))  and round(X1,1) >= round(np.min(miroir.xc),1) and round(X1,1) <= round(np.max(miroir.xc),1) and ((X1 <= max(self.x_array) and self.direction) or (X1 >= min(self.x_array) and self.direction == False)):
                self.x_array = np.linspace(self.x,X1,100)  #On créé le vecteur x entre le point de départ et d'arrivée
                teta_rayon = np.arcsin(Y1/miroir.r)        #On calcule l'angle de la normale
                teta_nouveau = -np.pi + 2*teta_rayon -self.teta    #On calcule l'angle du rayon réfléchi

     
                teta_nouveau = (teta_nouveau + np.pi) % (2 * np.pi) - np.pi #transforme la valeur de l'angle entre -pi/2,pi/2
                if abs(teta_nouveau) > np.pi/2 : #On définit la direction du rayon en fonction de son angle   and abs(teta_nouveau) < 3*np.pi/2
                    direction = False
                else:
                    direction = True
                #On créé un nouveau rayon (réfléchi) en fonction du point de contact avec le miroir, l'angle et sa direction
                lst_ray.append(rayon((self.fig,self.ax),X1,Y1, teta_nouveau, origine = miroir, direction = direction))


                
       
        self.trace()    #On trace le rayon incident

class source:
    """ 
    Créé un nombre déterminé de rayon lumineux suivant plusieurs conditions
    Permet de créer une source à l'infinie ou non.

    ----------
    x : float
        Abscisse du point d'origine des rayons.
    y : float
        Ordonnée du point d'origine des rayon.
    angle : float
        Angle d'ouverture de la source lorsque la source n'est pas à l'infinie.
    N : int
        Nombre de rayons
    inf : bool
        Source à l'infinie ou non.
    height : str
        Hauteur de répartition des rayons lorsque la source est considérée à l'infinie.
    """
    def __init__(self,figure, x, y, angle, N, inf = False, height = 0):
        self.figure = figure    #Figure sur laquelle tracer
        self.x = x              #Position x,y de la source
        self.y = y
        self.alpha = angle      #Demie angle d'ouverture de la source
        self.N = N              #Nombre de rayon créés par la source
        self.infiny = inf       #Source à l'infinie
        self.height = height    #Hauteur de création des rayons en mode infini

        self.create_ray()

    def create_ray(self):
        lst_angle = np.linspace(-self.alpha, self.alpha, self.N)    #Liste des angles pour chaque rayon de la source

        if self.infiny: #Si la source est à l'infini
            for y in np.linspace(-self.height/2, self.height/2, self.N):
                lst_ray.append(rayon(self.figure, self.x, y, 0))    #Création d'un rayon d'angle 0rad
        else:
            for angle in lst_angle:
                lst_ray.append(rayon(self.figure, self.x, self.y, angle)) #Sinon on trace un rayon avec l'angle correspondant


    
class miroir:
    """ 
    Créé un miroir sphérique concave ou convexe

    ----------
    fig : matplotlib figure
        Figure sur laquelle tracer le miroir.
    x : float
        Abscisse du point d'origine des rayons.
    r : float
        Rayon du miroir.
    diametre : float
        Angle d'ouverture du miroir
    color : str
        Couleur du miroir
    """
    def __init__(self,fig, x =0, r = 10, diametre = np.pi/3, color ="k"):
        self.x = x       #position du miroir sur l'axe des abscisses
        self.diametre = diametre     #demi-diamètre d'ouverture
        self.r = r              #Rayon du miroir
        self.color = color      #Couleur du miroir
        self.fig, self.ax = fig  #Figure sur laquelle tracer le miroir

        self.max = int  #Initialisation des variables max et min
        self.min = int

        self.test = False

        self.trace()    #On trace le miroir

    def trace(self):
        teta = np.linspace(-self.diametre, self.diametre,1000)   #Vecteur teta correspondant à l'angle de chaque point du cercle par rapport à l'axe des x
        
        self.xc = self.r*np.cos(teta) - self.r + self.x #array des x
        self.yc = self.r*np.sin(teta)   #array des y

        #Calcul de la hauteur max et min du miroir
        self.max = np.max(self.yc)
        self.min = -self.max
        
        self.ax.plot(self.xc, self.yc, color = self.color) #tracé du miroir
        #self.ax.plot(self.x - self.r, 0,marker = "o", color = self.color) #Tracé du centre du miroir


class sous_dioptre:
    """ 
    Créé une interface d'une lentille bi-concave ou bi-convexe.
    Voir class dioptre.

    ----------
    fig : matplotlib figure
        Figure sur laquelle tracer le dioptre.
    centre : float
        centre du cercle
    r : float
        Rayon du cercle.
    n_left : float
        indice de réfraction à gauche de l'interface
    n_right : float
        indice de réfraction à droite de l'interface
    side : bool
        côté concave de la lentille
    color : str
        Couleur du miroir
    """
    def __init__(self, fig, centre, r, teta, n_left, n_right, side, color = "red"):
        self.fig, self.ax = fig
        self.color = color #Couleur du dioptre

        self.side = side #permet de savoir quel côté du cercle est tracé de manière à choisir la bonne solution de l'équation (true = gauche)

        self.r = r #rayon du cercle
        self.c = centre #centre du cercle
        self.teta = teta #array contenant les angles nécessaires au tracé des dioptres
        self.n_left = n_left #indice de réfraction à gauche de la surface
        self.n_right = n_right #indice de réfraction à droite de la surface

        self.trace() #Appel de la méthode trace pour tracer la surface

    def trace(self):
        self.xc = self.r*np.cos(self.teta)+self.c #array des x
        self.yc = self.r*np.sin(self.teta)   #array des y

        self.ax.plot(self.xc, self.yc, color = self.color) #tracé

        #Calcul de la hauteur max et min du dioptre (utile pour la condition dans la méthode check des rayons)
        self.max = np.max(self.yc)
        self.min = -self.max

class dioptre:
    """ 
    Créé deux interfaces sous_dioptre par rapports aux paramètres de la lentille.

    ----------
    fig : matplotlib figure
        Figure sur laquelle tracer le dioptre.
    x : float
        centre de la lentille
    r : float
        Rayon du cercle.
    s : float
        distance entre le centre de la lentille et les sommets des cercles
    n : float
        indice de réfraction de la lentille
    type : str
        type de la lentille (convergent ou divergent)
    color : str
        Couleur du miroir
    """
    def __init__(self,fig, x, r, s,n,type = "convergent",  color = "darkturquoise"):
        self.fig = fig

        self.x = x  #Centre de la lentille
        self.r = r  #Rayon des dioptres
        self.s = s  #Distance entre le centre de la lentille et les sommets des dioptres
        self. n = n #Indice de réfraction de la lentille
        self.color = color  #Couleur de la lentille
        self.type = type    #Type de lentille
        
        #Si l'utilisateur ne rentre pas un bon type de lentille, le programme reporte une erreur
        if self.type not in ["convergent", "divergent"]:
            raise ValueError("{} is not a valid lens type".format(self.type))

        #Appel de la méthode correspondant au type de lentille pour tracer les interfaces de la bonne manière
        if self.type == "convergent":
            self.convergent()
        else:
            self.divergent()

    def convergent(self):
        diametre = np.arccos((self.r-self.s)/self.r)

        c1 = self.x + self.r - self.s #Centre du premier cercle
        c2 = self.x + self.s - self.r #Centre du deuxieme cercle


        teta1 = np.linspace(-diametre, diametre, 100)   #Vecteurs contenant les angles nécessaires au tracé
        teta2 = np.linspace(-diametre+np.pi, diametre+np.pi, 100)

        #Création des deux surfaces
        lst_dioptre.append(sous_dioptre(fig, c1, self.r, teta2, 1, self.n, True, color = self.color))
        lst_dioptre.append(sous_dioptre(fig, c2, self.r, teta1, self.n, 1, False, color = self.color))

    def divergent(self):
        diametre = np.arccos((self.r-self.s)/self.r)    #angle d'ouverture maximale

        c1 = self.x + self.s + self.r   #Centre du premier cercle
        c2 = self.x - self.s - self.r   #Centre du deuxieme cercle

        teta1 = np.linspace(-diametre, diametre, 1000)  #Vecteurs contenant les angles nécessaires au tracé
        teta2 = np.linspace(-diametre+np.pi, diametre+np.pi, 1000)

        #Création des deux surfaces
        lst_dioptre.append(sous_dioptre(fig, c2, self.r, teta1, 1,self.n, False, color = self.color))
        lst_dioptre.append(sous_dioptre(fig, c1, self.r, teta2,self.n, 1, True, color = self.color))
        
        

       

        


    
if __name__ == "__main__":
    fig = plt.subplots()  #Création de la figure

    #Limites, grille, ratio des axes..
    fig[1].set_xlim(-20,20)
    fig[1].set_ylim(-15,15)
    fig[1].grid(True)
    fig[1].set_aspect("equal")

    #Listes vides que l'on va remplir par les objets
    lst_ray = []
    lst_miroir = []
    lst_source = []
    lst_dioptre = []    #Cette liste n'est pas a remplir par l'utilisateur, c'est le programme qui la rempli automatiquement
    
    #On créé les objets miroir et source que l'on ajoute dans la liste correspondant
    lst_miroir.append(miroir(x = 15, r=-15, diametre = np.pi/4, fig = fig, color = "blue")) 
    
    dioptre(fig, 0, 12,0.5,1.38, type = "divergent")
    
    lst_source.append(source(fig,-10, 0,np.pi/12, 100, inf = True, height = 4))

    

    plt.show()



