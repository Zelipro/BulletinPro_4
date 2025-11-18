import flet as ft
from Zeli_Dialog import ZeliDialog2
import sqlite3
import os
import shutil
from pathlib import Path
from time import sleep

#-------
from stats import Stats
from Prof import Gestion_Prof
from classe import Gestion_Classe
from Matiere import Gestion_Matiere
from Students import Gestion_Eleve,Gestion_Eleve_Liste
from Note import Saisie_Notes
from Bulletin import Generation_Bulletin
from sync_manager import supabase_db
#-----

# === CORRECTIF COMPATIBILITÉ LINUX ===
if not hasattr(ft, 'Colors'):
    ft.Colors = ft.colors
# =====================================

# === CORRECTIF COMPATIBILITÉ LINUX ===
if not hasattr(ft, 'Icons'):
    ft.Icons = ft.icons
# =====================================

#======================= Pour Page 0 =======
#======================             ==============

def Get_on_db_local(mention):
    def User():
        donne = []
        return supabase_db.get_all_users()
    
    dic = {
        "User":User
    }
    
    func = dic.get(mention)
    if not func:
        return []   # return empty list when unknown mention
    return func()

def Submit(page, Ident, Pass): 
    Dialog = ZeliDialog2(page)
    
    Loag = Dialog.loading_dialog()
        
   # )
    def login_success(donner_info, Dial):
        Dialog.close_dialog(Dial)
        page.clean()
        
        # Récupérer sidebar et main_content
        sidebar, main_content = Page1(page, donner_info)
        
        # Ajouter à la page
        page.add(
            ft.Row([
                sidebar,
                main_content,
            ], spacing=0, expand=True)
        )
        page.update()
    
    # ✅ ANCIEN CODE SQLite SUPPRIMÉ
    # ✅ NOUVEAU: Utiliser Supabase directement
    
    # Vérifier créateur
    if Ident.value == "Deg" and Pass.value == "Deg":
        Donner = {
            "ident": "Deg",
            "pass": "Deg",
            "name": "Zeli",
            "role": "creator"
        }
        Dialog.close_dialog(Loag)
        Dial = Dialog.custom_dialog(
            title="Notification",
            content=ft.Column([
                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=60, color=ft.Colors.GREEN_200),
                ft.Text(value="Bienvenue Mon créateur")
            ], height=100, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.ElevatedButton(
                    content=ft.Text(value="Ok", color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.GREEN_300,
                    on_click=lambda e: login_success(Donner, Dial)
                )
            ]
        )
        return
    
    # ✅ NOUVEAU: Connexion via Supabase
    user = supabase_db.login(Ident.value, Pass.value)
    
    if user:
        # ✅ Connexion réussie
        Donner = {
            "ident": user["ident"],
            "pass": user["pass"],
            "name": user["name"],
            "role": user["role"],
            "etablissement": user.get("etablissement"),
            "email": user.get("email"),
            "telephone": user.get("telephone")
        }
        
        Dialog.close_dialog(Loag)
        Dial = Dialog.custom_dialog(
            title="Notification",
            content=ft.Column([
                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=60, color=ft.Colors.GREEN_200),
                ft.Text(value=f"Bienvenue {Ident.value}")
            ], height=100, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.ElevatedButton(
                    content=ft.Text(value="Ok", color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.GREEN_200,
                    on_click=lambda e: login_success(Donner, Dial)
                )
            ]
        )
    else:
        # ✅ Échec connexion
        Dialog.close_dialog(Loag)
        Dial = Dialog.custom_dialog(
            title="Notification",
            content=ft.Column([
                ft.Icon(ft.Icons.ERROR_ROUNDED, size=60, color=ft.Colors.RED_200),
                ft.Text(value="Erreur de connexion")
            ], height=100, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.ElevatedButton(
                    content=ft.Text(value="Ok", color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.RED_200,
                    on_click=lambda e: Dialog.close_dialog(Dial)
                )
            ]
        )

def Page0(page,Donne = None):#page: ft.Page):
    page.title = "Login page"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    #page.bgcolor = "#1a0d2e"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    # Fonction de connexion
    def learn_more_click(e):
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Learn More clicked!", color=ft.Colors.WHITE),
            bgcolor=ft.Colors.BLUE_700,
        )
        page.snack_bar.open = True
        page.update()
    
    # Champs de formulaire
    
    # Panneau gauche - Welcome
    left_panel = ft.Container(
        content=ft.Column([
            # Logo
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text("", size=0),
                        width=8,
                        height=30,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=2,
                    ),
                    ft.Container(width=5),
                    ft.Container(
                        content=ft.Text("", size=0),
                        width=8,
                        height=30,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=2,
                    ),
                ], spacing=0),
                margin=ft.margin.only(bottom=40),
            ),
            
            # Welcome text
            ft.Text(
                "Welcome",
                size=60,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
            ),
            
            ft.Text(
                "On BulletinPro !",
                size=25,
                #weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
            ),
            
            # Ligne d�corative
            ft.Container(
                width=80,
                height=4,
                bgcolor="#ff6b6b",
                border_radius=2,
                margin=ft.margin.only(top=10, bottom=30),
            ),
            
            # Description
            ft.Container(
                content=ft.Text(
                    value = "Simplifiez la gestion académique de votre établissement.Générez des bulletins scolaires professionnels en quelques clics, suivez les performances de vos élèves et concentrez-vous sur l'essentiel : leur réussite éducative.Commencez dès maintenant et transformez votre gestion scolaire !",

                    size=14,
                    color="#b8a7d1",
                    text_align=ft.TextAlign.LEFT,
                ),
                width=350,
                margin=ft.margin.only(bottom=40),
            ),
            
            # Bouton Learn More
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.START,
        spacing=0),
        padding=60,
        alignment=ft.alignment.center_left,
    )
    
    # Ajout d'une fonction pour gérer la visibilité du mot de passe
    def toggle_password_visibility(e):
        Pass.password = not Pass.password
        e.control.icon = ft.Icons.VISIBILITY_OFF if Pass.password else ft.Icons.VISIBILITY
        page.update()
    
    Pass = ft.TextField(
        label="Password",
        hint_text="Password",
        password=True,
        color=ft.Colors.WHITE,
        suffix_icon=ft.IconButton(
            icon=ft.Icons.VISIBILITY_OFF,
            icon_color=ft.Colors.WHITE60,
            on_click=toggle_password_visibility,
            tooltip="Afficher/Masquer le mot de passe"
        ),
    )
    Ident = ft.TextField(
        label =  "User Name",
        hint_text =  "User Name",
        color=ft.Colors.WHITE,
    )
    
    def forgot_password(e):
        Dialog = ZeliDialog2(page)
        Loag = Dialog.loading_dialog()
        # Dans validate_and_search(), remplacer ce bloc (ligne ~333-370) :
        def validate_and_search(e):
            if not all([name_field.value, surname_field.value, email_field.value]):
                error_text.value = "Tous les champs sont obligatoires"
                page.update()
                return
            
            # ✅ NOUVEAU: Récupérer avec Supabase
            try:
                # Rechercher l'utilisateur
                response = supabase_db.client.table("User").select("*")\
                    .ilike("nom", name_field.value)\
                    .ilike("prenom", surname_field.value)\
                    .ilike("email", email_field.value)\
                    .execute()
                
                if response.data:
                    user = response.data[0]  # Dictionnaire !
                    
                    Dialog.custom_dialog(
                        title="Récupération réussie",
                        content=ft.Column([
                            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=50, color=ft.Colors.GREEN),
                            ft.Text("Vos identifiants:"),
                            ft.Container(height=10),
                            ft.Text(f"Identifiant: {user['identifiant']}", size=16),
                            ft.Text(f"Mot de passe: {user['passwords']}", size=16, weight=ft.FontWeight.BOLD),
                        ], height=200, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        actions=[
                            ft.ElevatedButton(
                                text="Ok",
                                bgcolor=ft.Colors.GREEN,
                                color=ft.Colors.WHITE,
                                on_click=lambda e: Dialog.close_dialog(search_dialog)
                            )
                        ]
                    )
                else:
                    error_text.value = "Aucun compte trouvé avec ces informations"
                    page.update()
                    
            except Exception as ex:
                error_text.value = f"Erreur: {str(ex)}"
                page.update()

        def verify_security_answer(answer, correct_answer, dialog, user, error_text):
            if answer == correct_answer:
                Dialog.custom_dialog(
                    title="Identifiants récupérés",
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.LOCK_OPEN, color=ft.Colors.GREEN, size=50),
                            ft.Text("Vos identifiants:"),
                            ft.Text(f"Identifiant: {user[1]}", size=16),
                            ft.Text(f"Mot de passe: {user[2]}", size=16, weight=ft.FontWeight.BOLD)
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    actions=[
                        ft.ElevatedButton("Ok", 
                                        on_click=lambda e: [Dialog.close_dialog(dialog), 
                                                          Dialog.close_dialog(search_dialog)])
                    ]
                )
            else:
                error_text.value = "Réponse incorrecte"
                page.update()

        name_field = ft.TextField(
            label="Nom",
            hint_text="Votre nom",
            width=300,
            text_align=ft.TextAlign.CENTER,
        )
        
        surname_field = ft.TextField(
            label="Prénom",
            hint_text="Votre prénom",
            width=300,
            text_align=ft.TextAlign.CENTER,
        )
        
        email_field = ft.TextField(
            label="Email",
            hint_text="Votre email",
            width=300,
            text_align=ft.TextAlign.CENTER,
        )
        
        error_text = ft.Text(
            value="",
            color=ft.Colors.RED,
            size=12,
        )

        Dialog.close_dialog(Loag)
        search_dialog = Dialog.custom_dialog(
            title="Récupération de mot de passe",
            content=ft.Column(
                [
                    ft.Icon(
                        ft.Icons.PASSWORD_ROUNDED,
                        size=50,
                        color=ft.Colors.BLUE,
                    ),
                    ft.Container(height=10),
                    ft.Text(
                        "Veuillez entrer vos informations",
                        text_align=ft.TextAlign.CENTER,
                        size=14,
                    ),
                    ft.Container(height=20),
                    name_field,
                    surname_field,
                    email_field,
                    error_text,
                ],
                height=400,
                width=400,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            actions=[
                ft.TextButton(
                    text="Annuler",
                    on_click=lambda e: Dialog.close_dialog(search_dialog)
                ),
                ft.ElevatedButton(
                    text="Rechercher",
                    bgcolor=ft.Colors.BLUE,
                    color=ft.Colors.WHITE,
                    on_click=validate_and_search
                ),
            ]
        )

    # Panneau droit - Sign in
    right_panel = ft.Container(
        content=ft.Column([
            # Titre Sign in
            ft.Text(
                "Sign in",
                size=36,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
                text_align=ft.TextAlign.CENTER,
            ),
            
            ft.Container(height=30),
            
            # User Name
            ft.Column([
                Ident,
                ft.Container(height=8),
            ], spacing=0),
            
            ft.Container(height=20),
            
            # Password
            ft.Column([
                Pass,
                ft.Container(height=8),
            ], spacing=0),
            
            ft.Container(height=5),
            
            # Lien "Mot de passe oublié"
            ft.TextButton(
                text = "Mot de passe oublié",
                on_click=forgot_password,
                ),
            ft.Container(height=30),
            ft.Container(
                content=ft.Text(
                    "Submit",
                    size=16,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                width=280,
                height=50,
                bgcolor=None,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.center_left,
                    end=ft.alignment.center_right,
                    colors=["#ff7b54", "#ff5252"],
                ),
                border_radius=25,
                alignment=ft.alignment.center,
                ink=True,
                on_click = lambda e : Submit(page , Ident , Pass),
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=20,
                    color="#ff5252",
                    offset=ft.Offset(0, 5),
                ),
            ),
            
            ft.Container(height=25),
            
            # Social media Icons
            ft.Row([
                ft.IconButton(
                    icon=ft.Icons.FACEBOOK,
                    icon_color=ft.Colors.WHITE,
                    icon_size=22,
                    tooltip="Facebook",
                ),
                ft.IconButton(
                    icon=ft.Icons.CAMERA_ALT,
                    icon_color=ft.Colors.WHITE,
                    icon_size=22,
                    tooltip="Instagram",
                ),
                ft.IconButton(
                    icon=ft.Icons.PUSH_PIN,
                    icon_color=ft.Colors.WHITE,
                    icon_size=22,
                    tooltip="Pinterest",
                ),
            ], 
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=0),
        bgcolor="#3d2f52",
        padding=50,
        border_radius=ft.border_radius.only(top_right=15, bottom_right=15),
        width=400,
        #alignment=ft.alignment.center,
    )
    
    # Conteneur principal avec fond d�coratif
    main_container = ft.Container(
        content=ft.Stack([
            # Formes d�coratives en arri�re-plan
            ft.Container(
                width=400,
                height=400,
                border_radius=200,
                bgcolor="#2d1b47",
                opacity=0.3,
                left=-100,
                top=-100,
            ),
            ft.Container(
                width=300,
                height=300,
                border_radius=150,
                bgcolor="#4a2d6b",
                opacity=0.2,
                right=-50,
                top=100,
            ),
            ft.Container(
                width=200,
                height=200,
                border_radius=100,
                bgcolor="#5c3d7a",
                opacity=0.25,
                left=100,
                bottom=-50,
            ),
            
            # Panneau de login avec effet glassmorphism
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=left_panel,
                        bgcolor="#2d1947",
                        expand=True,
                        border_radius=ft.border_radius.only(top_left=15, bottom_left=15),
                    ),
                    right_panel,
                ], spacing=0),
                width=900,
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=50,
                    color="#000000",
                    offset=ft.Offset(0, 10),
                ),
                border_radius=15,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            ),
        ]),
        alignment=ft.alignment.center,
        expand=True,
    )
    
    # Boutons en haut
    
    # Layout complet
    return ft.Stack([
            main_container,
        ], expand=True)



#===================================    Fin Page 0 ===========================================
    """Récupère les préférences utilisateur"""
def get_user_preference(setting_name, Donner):
    try:
        user = supabase_db.get_user_info(
            identifiant=Donner.get("ident"),
            titre=Donner.get("role")
        )
        if user:
            return user.get(setting_name, "fr")
        return "fr"
    except:
        return "fr"

def User_Config(page, Donner):  # Ajout du paramètre Donner
    """Gestion des préférences utilisateur (mode/langue)
    Maintenant: applique automatiquement les préférences stockées au chargement.
    """
    Dialog = ZeliDialog2(page)

    # --- apply stored preferences immediately on load ---
    try:
        #pref_theme = get_user_preference("theme", Donner)
        #pref_lang = get_user_preference("language", Donner)
        #page.theme_mode = ft.ThemeMode.DARK if pref_theme == "dark" else ft.ThemeMode.LIGHT
        # you can store language on page or Info if needed
        page.update()
    except Exception:
        pass
    
    def save_preferences(theme, language, dialog):
        # Appliquer le thème immédiatement
        page.theme_mode = ft.ThemeMode.DARK if theme == "dark" else ft.ThemeMode.LIGHT
        page.update()
        
        Dialog.alert_dialog(title="Succès", message="Préférences enregistrées!")
        Dialog.close_dialog(dialog)
            
    
    config_dialog = Dialog.custom_dialog(
        title="Préférences",
        content=ft.Column([
            ft.Switch(
                label="Mode sombre",
                value=False #get_user_preference("theme",Donner) == "dark"
            ),
            ft.Container(height=3),
            ft.Dropdown(
                label="Langue",
                options=[
                    ft.dropdown.Option("fr", "Français"),
                    ft.dropdown.Option("en", "English")
                ],
                value=get_user_preference("language",Donner)
            )
        ], width=300, height=200),
        actions=[
            ft.TextButton("Annuler", on_click=lambda e : Dialog.close_dialog(config_dialog)),
            ft.ElevatedButton(
                "Enregistrer",
                on_click=lambda e: save_preferences(
                    "dark" if config_dialog.content.controls[0].value else "light",
                    config_dialog.content.controls[2].value,
                    config_dialog
                )
            )
        ]
    )

def New_admin(page,Donner):
    Dialog = ZeliDialog2(page)
    
    def Verif_ident_in(Ident , passs):
        return supabase_db.login(Ident, passs)
        
    def save_admin(fields, dialog):
        new_admin = {
            "identifiant" : fields[0],
            "passwords" : fields[1],
            "nom" : fields[2],
            "prenom" : fields[3],
            "email" : fields[4],
            "telephone" : fields[5],
            "etablissement" : fields[6],
            "titre" : "admin"
        }
        
        new = supabase_db.create_user(new_admin)
        if not new[0]:
            Dialog.error_toast(f"❌ Erreur create_user: {new[1]}")
            return
        
        dialg2 = Dialog.custom_dialog(
                title="",
                content=ft.Column(
                    [
                        ft.Icon(
                           ft.Icons.CHECK_CIRCLE,
                           size = 60,
                           color = ft.Colors.GREEN
                        ),
                        ft.Container(height=2),
                        ft.Text(
                            value = "Succès",
                            weight=ft.FontWeight.BOLD,
                            size = 30,
                            color=ft.Colors.GREEN
                        ),
                        ft.Text(
                            value = f"""admin créé avec succès!
                                \nIdentifiant: {fields[0]}
                                \nMot de passe: {fields[1]}"""
                        )
                    ],
                    height=250,
                    width=400,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                actions=[
                    ft.ElevatedButton(
                        text = "Ok",
                        width=100,
                        bgcolor=ft.Colors.GREEN,
                        color=ft.Colors.WHITE,
                        on_click=lambda e : Dialog.close_dialog(dialg2)
                    )
                ]
            )
        Dialog.close_dialog(dialog)
        
    fields = [
        ft.TextField(label="Nom admin",text_align="center"),
        ft.TextField(label="Prénom admin",text_align="center"),
        ft.TextField(label="Email admin",text_align="center"),
        ft.TextField(label="Téléphone admin",text_align="center"),
        ft.TextField(label="Nom École",text_align="center"),
    ]
    
    def valider(e, dialog, fields):
        error = False
        for field in fields:
            if not field.value:
                field.error_text = "Champ requis"
                error = True
        
        if error:
            page.update()
            return
        else:
            Name = fields[0].value
            Prenom = fields[1].value
            Etablisement = fields[4].value
            Ident = f"{Prenom[0]}{Name}".upper()
            Pass = f"{Prenom.lower()}@admin_{len(Name)+len(Prenom)}_{Etablisement.replace(' ','').lower()}"

            Result = False #J'ai mise false ici car il y a deja autre chose qui ca se charger de la faire dans la fonction sync_manager
            if not Result:
                save_admin([Ident,Pass] + [elmt.value for elmt in fields], dialog)
            else:
                Dialog.error_toast("Cet utilisateur existe déjà")
                page.update()
        
    dialog = Dialog.custom_dialog(
        title="Nouvel administrateur",
        content=ft.Column([
            ft.Text("Ajouter un administrateur", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            *fields,
        ], width=400, height=400, scroll=ft.ScrollMode.AUTO),
        actions=[
            ft.TextButton("Annuler", on_click=lambda e: Dialog.close_dialog(dialog)),
            ft.ElevatedButton(
                "Valider",
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE,
                on_click=lambda e: valider(e, dialog, fields)
            )
        ]
    )

def Setting(page, Donner=None):
    Dialog = ZeliDialog2(page)
    Loag = Dialog.loading_dialog(
        title="Chargement",
        message="Veuillez patienter pendant le chargement des paramètres..."
    )
    # Définir les informations par défaut pour le créateur
    if not Donner:
        Donner = {
            "ident": "Deg",
            "role": "creator",
            "pass": None,
            "name": "Développeur"
        }
    
    def Return(Ident):
        """Récupère une information depuis la table User"""
        Tous = supabase_db.get_user_info(identifiant=Ident,titre=Donner.get("role"))
        
        return Tous if Tous else None
    
    def save_settings(fields_dict, dial, theme_value, lang_value):
        """Enregistre les paramètres selon le type d'utilisateur"""
        Loag2 = Dialog.loading_dialog(
            title="Enregistrement",
            message="Veuillez patienter pendant l'enregistrement des paramètres..."
        )
        # Déterminer le thème
        theme = "dark" if theme_value else "light"
        
        if Donner.get("role") == "creator":
            # Créer la table Dev_Preferences si elle n'existe pas
            Dialog.close_dialog(Loag2)
            Dialog.alert_dialog("You don't have here a Table for this ")
            
        else:
            # Pour admin et prof
            # Récupérer les données actuelles
            Tous = Return(Donner.get("ident"))
            
            if not Tous:
                Dialog.close_dialog(Loag2)
                Dialog.error_toast("Utilisateur non trouvé")
                return
            
            # Mettre à jour les informations
            update = {
                "identifiant" : Donner.get("ident"),
                "passwords" : fields_dict["password"].value,
                "nom" : fields_dict["nom"].value,
                "prenom" : fields_dict["prenom"].value,
                "email" :  fields_dict["email"].value,
                "telephone" :  fields_dict["telephone"].value,
                "etablissement" : fields_dict["etablissement"].value,
                "titre" : Donner.get("role"),
                "theme" : theme,
                "language" : lang_value,
            }
            
            upd = supabase_db.update_user(Donner.get("ident"),update)
            if not upd:
                Dialog.close_dialog(Loag2)
                Dialog.error_toast("Erreur lors de l'eenregistrement")
                return
                
            # Appliquer le thème immédiatement
            page.theme_mode = ft.ThemeMode.DARK if theme == "dark" else ft.ThemeMode.LIGHT
            page.update()
            
            Dialog.close_dialog(Loag2)
            Dialog.alert_dialog(
                title="Succès",
                message="Paramètres enregistrés avec succès!"
            )
            
            Dialog.close_dialog(dial)
            
    
    def toggle_password_visibility(e, password_field, icon_button):
        """Basculer la visibilité du mot de passe"""
        password_field.password = not password_field.password
        icon_button.icon = ft.Icons.VISIBILITY_OFF if password_field.password else ft.Icons.VISIBILITY
        page.update()
    
    def enable_password_edit(e, password_field):
        """Activer l'édition du mot de passe"""
        password_field.read_only = False
        password_field.border_color = ft.Colors.BLUE
        page.update()
    
    # Récupérer les préférences actuelles
    current_theme = "Dark" #get_user_preference("theme", Donner)
    current_lang = "fr" #get_user_preference("language", Donner)
    
    # Créer l'onglet Système (commun à tous)
    theme_switch = ft.Switch(
        label="Mode sombre",
        value=current_theme == "dark",
        on_change=lambda e: page.update(),
    )
    
    lang_dropdown = ft.Dropdown(
        label="Langue",
        value=current_lang,
        options=[
            ft.dropdown.Option("fr", "Français"),
            ft.dropdown.Option("en", "English")
        ],
        on_change=lambda e: page.update(),
    )
    
    system_tab = ft.Tab(
        text="Système",
        icon=ft.Icons.SETTINGS,
        content=ft.Container(
            content=ft.Column([
                ft.Text("Préférences du système", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                theme_switch,
                lang_dropdown,
            ], spacing=15),
            padding=20,
        )
    )
    
    # Liste des onglets
    tabs_list = [system_tab]
    fields_dict = {}
    
    # Ajouter l'onglet Profil seulement pour admin et prof
    if Donner.get("role") in ["admin", "prof"]:
        # Champs pour le profil
        ident_field = ft.TextField(
            label="Identifiant",
            value=Donner.get("ident"),
            read_only=True,
            disabled=True,
            text_align="center"
        )
        
        # Récupérer les données utilisateur
        user_data = supabase_db.get_user_info(identifiant=Donner.get("ident"),titre = Donner.get("role"))
        if not user_data:
            Dialog.error_toast("Erreur d'obtention des données utilisateur")
            return 
        #print(user_data)
        # Boutons pour le mot de passe
        visibility_button = ft.IconButton(
            icon=ft.Icons.VISIBILITY_OFF,
            icon_color=ft.Colors.GREY_600,
            tooltip="Afficher/Masquer"
        )
        
        password_field = ft.TextField(
            label="Mot de passe",
            value=user_data.get("passwords", "") if user_data else "",
            password=True,
            read_only=True,
            text_align="center",
            suffix=visibility_button,
            prefix=ft.IconButton(
                icon=ft.Icons.EDIT,
                icon_color=ft.Colors.BLUE,
                tooltip="Modifier",
                on_click=lambda e: enable_password_edit(e, password_field)
            )
        )
        
        # Lier l'événement de visibilité
        visibility_button.on_click = lambda e: toggle_password_visibility(e, password_field, visibility_button)
        
        nom_field = ft.TextField(
            label="Nom",
            value=user_data.get("nom", "") if user_data else "",
            text_align="center",
            capitalization=ft.TextCapitalization.WORDS
        )
        
        prenom_field = ft.TextField(
            label="Prénom",
            value=user_data.get("prenom", "") if user_data else "",
            text_align="center",
            capitalization=ft.TextCapitalization.WORDS
        )
        
        email_field = ft.TextField(
            label="Email",
            value=user_data.get("email", "") if user_data else "",
            text_align="center",
            keyboard_type=ft.KeyboardType.EMAIL
        )
        
        telephone_field = ft.TextField(
            label="Téléphone",
            value=user_data.get("telephone", "") if user_data else "",
            text_align="center",
            keyboard_type=ft.KeyboardType.PHONE
        )
        
        etablissement_field = ft.TextField(
            label="Établissement",
            value=user_data.get("etablissement", "") if user_data else "",
            read_only=True,
            disabled=True,
            text_align="center"
        )
        
        # Stocker les champs dans le dictionnaire
        fields_dict = {
            "password": password_field,
            "nom": nom_field,
            "prenom": prenom_field,
            "email": email_field,
            "telephone": telephone_field,
            "etablissement": etablissement_field
        }
        
        # Créer l'onglet Profil
        profile_tab = ft.Tab(
            text="Profil",
            icon=ft.Icons.PERSON,
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Informations personnelles", size=16, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ident_field,
                    password_field,
                    nom_field,
                    prenom_field,
                    email_field,
                    telephone_field,
                    etablissement_field,
                ], spacing=15, scroll=ft.ScrollMode.AUTO),
                padding=20,
            )
        )
        
        tabs_list.insert(0, profile_tab)  # Insérer en premier
    
    # Créer le contenu avec onglets
    settings_content = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=tabs_list,
        expand=True,
    )
    
    Dialog.close_dialog(Loag)
    # Créer le dialog
    dial = Dialog.custom_dialog(
        title=f"⚙️ Paramètres - {Donner.get('name', 'Utilisateur')}",
        content=ft.Container(
            content=settings_content,
            width=450,
            height=400,
        ),
        actions=[
            ft.TextButton(
                "Annuler",
                icon=ft.Icons.CLOSE,
                on_click=lambda e: Dialog.close_dialog(dial)
            ),
            ft.ElevatedButton(
                "Enregistrer",
                icon=ft.Icons.SAVE,
                bgcolor=ft.Colors.GREEN,
                color=ft.Colors.WHITE,
                on_click=lambda e: save_settings(
                    fields_dict,
                    dial,
                    theme_switch.value,
                    lang_dropdown.value
                )
            )
        ]
    )



#===== Gestion des eleves ============

#Dans la fonction studnets
    
#====================================

def get_authorized_items(role):
    if role == "creator":
        return [
            {"icon": ft.Icons.ADMIN_PANEL_SETTINGS, "text": "Gestion admin", "color": ft.Colors.RED,
             "desc": "Ajouter/Gérer les administrateurs", "route": "/admin", "fonct": New_admin},
            {"icon": ft.Icons.SETTINGS, "text": "Configuration", "color": ft.Colors.BROWN,
             "desc": "Paramètres système", "route": "/settings", "fonct": Setting},
            {"icon": ft.Icons.BAR_CHART, "text": "Statistiques", "color": ft.Colors.INDIGO,
             "desc": "Analyses et graphiques", "route": "/stats", "fonct": Stats},
        ]
    elif role == "admin":
        return [
            {"icon": ft.Icons.PERSON, "text": "Gestion Enseignants", "color": ft.Colors.TEAL,
             "desc": "Gérer l'équipe pédagogique", "route": "/teachers", "fonct": Gestion_Prof},
            {"icon": ft.Icons.PEOPLE_ALT, "text": "Gestion Élèves", "color": ft.Colors.BLUE,
             "desc": "Ajouter/Gérer les élèves", "route": "/students", "fonct": Gestion_Eleve},
            {"icon": ft.Icons.SUBJECT, "text": "Matières", "color": ft.Colors.ORANGE,
             "desc": "Configuration des matières", "route": "/subjects", "fonct": Gestion_Matiere},
            {"icon": ft.Icons.CLASS_, "text": "Classes", "color": ft.Colors.GREEN,
             "desc": "Organisation des classes", "route": "/classes", "fonct": Gestion_Classe},
            {"icon": ft.Icons.SETTINGS, "text": "Paramètres", "color": ft.Colors.BROWN,
             "desc": "Configuration", "route": "/settings", "fonct": Setting},
            {"icon": ft.Icons.BAR_CHART, "text": "Statistiques", "color": ft.Colors.INDIGO,
             "desc": "Analyses", "route": "/stats", "fonct": Stats},
            {"icon": ft.Icons.ASSESSMENT, "text": "Bulletins", "color": ft.Colors.PURPLE,
             "desc": "Génération bulletins", "route": "/reports", "fonct": Generation_Bulletin},
        ]
    else:  # Enseignant
        return None

def Page1(page, Donner = None):
    page.title = "Bulletin Pro"
    page.padding = 0
    #page.theme_mode = ft.ThemeMode.LIGHT
    
    def logOut():
        page.clean()
        page.add(Page0(page))
        page.update()
        
    if not Donner:
        Info = {
            "ident": "Deg",
            "name": "Zeli",
            "role": "creator"
        }
    else:
        Info = Donner
    User_Config(page, Info)
    # Get authorized menu items and cards based on role
    dashboard_cards = get_authorized_items(Info.get("role", "Teacher"))
    
    if not dashboard_cards:
        Dialog = ZeliDialog2(page)
        Dialog.alert_dialog(title = "Error" , message="Vous n'etes pas autorisé a venir ici !\nUtilisez plutôt l'application") 
        logOut()
        return
    
    # Create menu items from dashboard cards
    menu_items = [{"icon": ft.Icons.HOME, "text": "Accueil", "route": "/"}]
    menu_items.extend([
        {"icon": card["icon"], "text": card["text"], "route": card["route"]}
        for card in dashboard_cards
    ])

    # Create card widgets
    cards = []
    for card in dashboard_cards:
        cards.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(card["icon"], color=card["color"], size=40),
                    ft.Text(card["text"], 
                            #color=ft.Colors.BLACK,
                           size=16, 
                           weight=ft.FontWeight.W_500,
                           text_align=ft.TextAlign.CENTER),
                    ft.Container(height=5),
                    ft.Text(card["desc"],
                           #color=ft.Colors.GREY_700,
                           size=12,
                           text_align=ft.TextAlign.CENTER),
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
                alignment=ft.MainAxisAlignment.CENTER),
                #bgcolor=ft.Colors.WHITE,
                width=200,
                height=180,
                border_radius=15,
                padding=20,
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                alignment=ft.alignment.center,
                on_click=lambda e, f=card["fonct"]: f(page,Donner),  # Appel de la fonction associée
                ink=True,
            )
        )

    # Main content with role indication
    main_content = ft.Container(
        #bgcolor = ft.Colors.DARK_BLUE,
        content=ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text("Tableau de Bord", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            f"Bienvenue {Info.get('name', 'admin')} ({Info.get('role', 'Teacher')})", 
                            size=16, 
                            color=ft.Colors.GREY_700
                        ),
                    ]),
                    ft.Container(expand=True),
                    ft.CircleAvatar(
                        content=ft.Text(
                            (Donner['name'][0] if Donner else 'A').upper(),
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                        bgcolor=ft.Colors.BLUE,
                        radius=20,
                    ),
                ]),
                padding=20,
                #bgcolor=ft.Colors.WHITE,
            ),
            # Search bar
            ft.Container(
                content=ft.TextField(
                    hint_text="Search",
                    prefix_icon=ft.Icons.SEARCH,
                    border_color=ft.Colors.GREY_300,
                    filled=True,
                    #bgcolor=ft.Colors.WHITE,
                ),
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
            ),
            # Dashboard cards grid
            ft.Container(
                content=ft.GridView(
                    controls=cards,
                    runs_count=4,
                    max_extent=250,
                    child_aspect_ratio=1.1,
                    spacing=20,
                    run_spacing=20,
                    padding=20,
                ),
                expand=True,
            ),
        ]),
        #bgcolor="#f5f5f5",
        expand=True,
    )
    
    # Sidebar
    sidebar = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.SCHOOL, color=ft.Colors.WHITE),
                    ft.Text("SCHOOL", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                ]),
                padding=20,
                ink  = True,
                on_click= lambda e : logOut()
            ),
            ft.Divider(height=1, ),#color=ft.Colors.WHITE24),
            *[
                ft.Container(
                    content=ft.Row([
                        ft.Icon(item["icon"], color=ft.Colors.WHITE70, size=20),
                        ft.Text(item["text"], color=ft.Colors.WHITE70, size=14),
                    ]),
                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                    on_click=lambda e, route=item["route"]: page.go(route),
                )
                for item in menu_items
            ],
        ]),
        width=250,
        bgcolor="#2c3e50",
        padding=ft.padding.only(top=10),
    )
    
    return sidebar,main_content


def update_language(lang_code):
    """Met à jour les traductions de l'interface"""
    # TODO: Implémenter le système de traduction
    pass

"""def main(page: ft.Page):
    # Layout
    Donner = {
            "ident": "EATIKPO",
            "pass" : "e@prof_12",
            "name": "ATIKPO",
            "role": "prof"
    }
    Main = Page1(page,Donner)
    page.add(
        ft.Row([
            Main[0],
            Main[1],
        ], spacing=0, expand=True)
    )

ft.app(target=main)"""

def main(page : ft.Page):
    #from sync_manager import sync_manager
    #sync_manager.init_local_tables()
    
    page.add(
        Page0(page)
    )
    
ft.app(target=main)
