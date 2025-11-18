import flet as ft
from Zeli_Dialog import ZeliDialog2
import sqlite3
import os
import shutil
from pathlib import Path
from time import sleep
from sync_manager import supabase_db

def Gestion_Eleve(page, Donner , view_only=False):
    Dialog = ZeliDialog2(page)
    Loag = Dialog.loading_dialog(
        title = "Chagergement en cours ..."
    )
    def Return(Ident):
        """Récupère une information depuis Supabase"""
        try:
            user = supabase_db.get_user_info(
                identifiant=Donner.get("ident"),
                titre=Donner.get("role")
            )
            if not user:
                Dialog.error_toast("Erreur de récupération des informations utilisateur")
                return None
            return user.get(Ident.lower())
        except Exception as e:
            Dialog.error_toast(f"Erreur: {e}")
            return None
    
    def load_student():
        """Charge la liste de tous les eleves de l'établissement"""
        Etat = Return("etablissement")
        
        Students = supabase_db.get_students(etablissement=Etat)
        if not Students:
            Dialog.error_toast("Aucun élève trouvé ou erreur de chargement")
            return []
        return [
            (
                student.get("nom"),
                student.get("prenom"),
                student.get("matricule"),
                student.get("date_naissance"),
                student.get("sexe"),
                student.get("classe"),
                student.get("etablissement"),
            )
            for student in Students
        ]
    
    def add_student():
        """Ajoute un nouvel enseignant"""
        Loag2 = Dialog.loading_dialog()
        # Champs de saisie
        nom_field = ft.TextField(
            label="Nom",
            hint_text="Entrez le nom",
            autofocus=True,
            capitalization=ft.TextCapitalization.WORDS
        )
        prenom_field = ft.TextField(
            label="Prénom",
            hint_text="Entrez le prénom",
            capitalization=ft.TextCapitalization.WORDS
        )
        matricule_field = ft.TextField(
            label="matricule",
            hint_text="XXXXX",
            keyboard_type=ft.KeyboardType.NUMBER
        )
        borndate_field = ft.TextField(
            label="date_naissance",
            hint_text="31/10/2025",
            keyboard_type=ft.KeyboardType.PHONE
        )
        sexe_dropdown = ft.Dropdown(
            label="Sexe",
            hint_text="Sélectionnez le sexe",
            options=[
                ft.dropdown.Option("Masculin(M)",leading_icon=ft.Icons.MAN),
                ft.dropdown.Option("Feminin(F)",leading_icon=ft.Icons.WOMAN),

            ]
        )
        
        Etat = Return("etablissement")
        Menu = supabase_db.get_classes(etablissement=Etat)
        
        if not Menu:
            Menu = []
        else: # Estraction des noms 
            Menu2 = []
            for elmt in Menu:
                Menu2.append(ft.dropdown.Option(elmt.get("nom")))
            Menu = Menu2 
            #print(Menu)
            #Dialog.error_toast("Aucune classe trouvée. Veuillez d'abord ajouter une classe.")
            #return
        
        
        classe_dropdown = ft.Dropdown(
            label="classe",
            hint_text="Sélectionnez la classe",
            options=Menu,
        )
        
        def clear_errors():
            """Efface tous les messages d'erreur"""
            for field in [nom_field, prenom_field, matricule_field, borndate_field, sexe_dropdown , classe_dropdown]:
                field.error_text = None
            page.update()
        
        def validate_fields():
            """Valide tous les champs"""
            is_valid = True
            
            # Validation des champs texte
            for field in [nom_field, prenom_field, matricule_field, borndate_field, sexe_dropdown , classe_dropdown]:
                if not field.value or not field.value.strip():
                    field.error_text = "Ce champ est obligatoire"
                    is_valid = False
                else:
                    field.error_text = None
            page.update()
            return is_valid
        
        def save_student(e):
            """Enregistre l'enseignant"""
            Loag3 = Dialog.loading_dialog()
            clear_errors()
            
            if not validate_fields():
                return
            
            new = {
                "nom": nom_field.value.strip(),
                "prenom": prenom_field.value.strip(),
                "matricule": matricule_field.value.strip(),
                "date_naissance": borndate_field.value.strip(),
                "sexe": sexe_dropdown.value.strip(),
                "classe": classe_dropdown.value.strip(),
                "etablissement": Return("etablissement"),
            }
            save = supabase_db.create_student(new)
            if not save:
                Dialog.close_dialog(Loag3)
                Dialog.error_toast("Erreur lors de l'ajout de l'élève")
                return
            
            Dialog.close_dialog(Loag3)
            Dialog.info_toast(message="Eleve ajouté avec success !")
            Gestion_Eleve(page , Donner , False)
        
        # Dialog principal d'ajout
        Dialog.close_dialog(Loag2)
        DIag2 = Dialog.custom_dialog(
            title="➕ Nouvel Eleve",
            content=ft.Column([
                nom_field,
                prenom_field,
                matricule_field,
                borndate_field,
                sexe_dropdown,
                classe_dropdown,
            ],
            width=400,
            height=350,
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            actions=[
                ft.TextButton(
                    "Annuler",
                    icon=ft.Icons.CLOSE,
                    on_click=lambda e: Dialog.close_dialog(DIag2)
                ),
                ft.ElevatedButton(
                    "Enregistrer",
                    icon=ft.Icons.SAVE,
                    bgcolor=ft.Colors.GREEN,
                    color=ft.Colors.WHITE,
                    on_click=save_student
                ),
            ]
        )
    
    def show_details(student):
        """Affiche les détails d'un eleve"""
        detail_dialog = Dialog.custom_dialog(
            title=f"📋 Détails - {student[0]} {student[1]}",
            content=ft.Column([
                ft.Divider(),
                create_info_row("Nom:", student[0]),
                create_info_row("Prénom:", student[1]),
                create_info_row("matricule:", student[2]),
                create_info_row("date_naissance:", student[3]),
                create_info_row("sexe:", student[4]),
                create_info_row("classe:", student[5]),
                ft.Divider(),
            ],
            width=450,
            height=350,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=10,
            ),
            actions=[
                ft.TextButton(
                    "Fermer",
                    icon=ft.Icons.CLOSE,
                    icon_color=ft.Colors.RED,
                    on_click=lambda e: Dialog.close_dialog(detail_dialog)
                )
            ]
        )
    
    def create_info_row(label, value):
        """Crée une ligne d'information"""
        return ft.Row([
            ft.Text(label, size=15, weight=ft.FontWeight.BOLD, width=150),
            ft.Text(str(value or "N/A"), size=15, selectable=True, expand=True),
        ], spacing=10)
    
    def edit_student(student):
        """Modifie un eleve"""
        name_field = ft.TextField(label="Non", value=student[0])
        prenom_field = ft.TextField(label="Prénom", value=student[1])
        matricule_field = ft.TextField(label="matricule", value=student[2], read_only=True, disabled=True)
        borndate_field = ft.TextField(label="date_naissance", value=student[3])
        sexe_field = ft.TextField(label="sexe", value=student[4])
        classe_field = ft.TextField(label="classe", value=student[5])
        etabl_field = ft.TextField(label="classe", value=student[6], read_only=True, disabled=True)
        
        
        def save_changes(e, dialog):
            """Enregistre les modifications"""
            new = {
                "nom": name_field.value,
                "prenom": prenom_field.value,
                "matricule": matricule_field.value,
                "date_naissance": borndate_field.value,
                "sexe": sexe_field.value,
                "classe": classe_field.value,
                "etablissement": etabl_field.value,
            }
            save = supabase_db.update_student(matricule =matricule_field.value,etablissement = etabl_field.value, updates = new)
            if not save:
                Dialog.error_toast("Erreur lors de la mise à jour de l'élève")
                return
            
            Dialog.info_toast("Modifications enregistrées !")
            Dialog.close_dialog(dialog)
            refresh_display()
        
        edit_dialog = Dialog.custom_dialog(
            title=f"✏️ Modifier - {student[0]} {student[1]}",
            content=ft.Column([
                name_field,
                prenom_field,
                borndate_field,
                sexe_field,
                classe_field,
                matricule_field,
                etabl_field,
            ],
            width=400,
            height=380,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
            ),
            actions=[
                ft.TextButton(
                    "Annuler",
                    on_click=lambda e: Dialog.close_dialog(edit_dialog)
                ),
                ft.ElevatedButton(
                    "Enregistrer",
                    bgcolor=ft.Colors.BLUE,
                    color=ft.Colors.WHITE,
                    on_click=lambda e: save_changes(e, edit_dialog)
                )
            ]
        )
    
    def confirm_delete(student):
        """Demande confirmation avant suppression"""
        confirm_dialog = Dialog.custom_dialog(
            title="⚠️ Confirmation de suppression",
            content=ft.Column([
                ft.Icon(ft.Icons.WARNING_ROUNDED, color=ft.Colors.RED, size=50),
                ft.Text(
                    "Êtes-vous sûr de vouloir supprimer cet eleve?",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    f"Eleve: {student[3]} {student[4]}",
                    size=14,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    "⚠️ Cette action est irréversible !",
                    color=ft.Colors.RED,
                    size=12,
                    italic=True,
                    text_align=ft.TextAlign.CENTER
                )
            ],
            width=400,
            height=220,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
            ),
            actions=[
                ft.TextButton(
                    "Annuler",
                    on_click=lambda e: Dialog.close_dialog(confirm_dialog)
                ),
                ft.ElevatedButton(
                    "Supprimer",
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                    icon=ft.Icons.DELETE_FOREVER,
                    on_click=lambda e: execute_delete(student, confirm_dialog)
                )
            ]
        )
    
    def execute_delete(student, dialog):
        """Exécute la suppression"""
        delect = supabase_db.delete_student(
            matricule=student[2],
            etablissement=student[6]
        )
        if not delect:
            Dialog.error_toast("Erreur lors de la suppression de l'élève")
            return

    def refresh_display():
        """Rafraîchit l'affichage de la liste"""
        Dialog.close_dialog(main_dialog)
        # Réouvre le dialog avec les données à jour
        Gestion_Eleve(page, Donner, Dialog)
    
    def create_student_card(student):
        """Crée une carte pour un enseignant"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    f"{student[0]} {student[1]}",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(f"Classe :{student[5]}", size = 15),
                ft.Text(f"Matricue :{student[2]}", size=15),
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.INFO,
                        tooltip="Détails",
                        icon_color=ft.Colors.BLUE,
                        on_click=lambda e, t=student: show_details(t)
                    ),
                    ft.IconButton(
                        icon=ft.Icons.EDIT,
                        tooltip="Modifier",
                        icon_color=ft.Colors.GREEN,
                        on_click=lambda e, t=student: edit_student(t)
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        tooltip="Supprimer",
                        icon_color=ft.Colors.RED,
                        on_click=lambda e, t=student: confirm_delete(t)
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8
            ),
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=ft.border_radius.only(top_right=20, bottom_left=20),
            padding=20,
            margin=10,
            
            width=280,
            height=200,
            #bgcolor=ft.Colors.ON_SURFACE_VARIANT,
        )
    
    # Chargement des enseignants
    students = load_student()
    student_cards = [create_student_card(student) for student in students]
    
    # Si aucun enseignant
    if not student_cards:
        student_cards = [
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SCHOOL, size=60, color=ft.Colors.GREY_400),
                    ft.Text(
                        "Aucun Eleve trouvé",
                        size=16,
                        color=ft.Colors.GREY_600
                    ),
                    ft.Text(
                        "Cliquez sur 'Ajouter' pour commencer",
                        size=12,
                        color=ft.Colors.GREY_500
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
                ),
                padding=30
            )
        ]
    
    # Dialog principal
    Dialog.close_dialog(Loag)
    main_dialog = Dialog.custom_dialog(
        title=f"👨‍🏫 Liste des élèves ({len(students)})",
        content=ft.Column([
            ft.Row(
                [
                    ft.Column(
                        controls=student_cards,
                        scroll=ft.ScrollMode.AUTO,
                        height=330,
                        width = 350,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    )
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
            ft.Container(expand=True),
            ft.Divider(),
            ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE),
                    ft.Text("Ajouter un élève", color=ft.Colors.WHITE),
                ], spacing=8),
                bgcolor=ft.Colors.GREEN_700,
                on_click=lambda e: add_student(),
            )
        ],
        width=450,
        height=450,
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        actions=[
            ft.TextButton(
                "Fermer",
                icon=ft.Icons.CLOSE,
                on_click=lambda e: Dialog.close_dialog(main_dialog)
            )
        ]
    )
    

def Gestion_Eleve_Liste(page, Donner):
    Dialog = ZeliDialog2(page)

    def Return(Ident):
        """Récupère une information depuis Supabase"""
        try:
            user = supabase_db.get_user_info(
                identifiant=Donner.get("ident"),
                titre=Donner.get("role")
            )
            if not user:
                Dialog.error_toast("Erreur de récupération des informations utilisateur")
                return None
            return user.get(Ident.lower())
        except Exception as e:
            Dialog.error_toast(f"Erreur: {e}")
            return None
    
    def load_student():
        """Charge la liste de tous les eleves de l'établissement"""
        Etat = Return("etablissement")
        
        if not Etat:
            return []
        
        student = supabase_db.get_students(etablissement=Etat)
        if not student:
            Dialog.error_toast("Aucun élève trouvé ou erreur de chargement")
            return []
        return [
            (
                stud.get("nom"),
                stud.get("prenom"),
                stud.get("matricule"),
                stud.get("date_naissance"),
                stud.get("sexe"),
                stud.get("classe"),
                stud.get("etablissement"),
            )
            for stud in student
        ]
        
    
    def Close(d):
        d.open = False
        page.update()
        Gestion_Eleve_Liste(page, Donner)
        
    def create_info_row(label, value):
        """Crée une ligne d'information"""
        return ft.Row([
            ft.Text(label, size=15, weight=ft.FontWeight.BOLD, width=150),
            ft.Text(str(value or "N/A"), size=15, selectable=True, expand=True),
        ], spacing=10)
                      
    def show_details(student):
        """Affiche les détails d'un eleve"""
        detail_dialog = Dialog.custom_dialog(
            title=f"📋 Détails - {student[0]} {student[1]}",
            content=ft.Column([
                ft.Divider(),
                create_info_row("Nom:", student[0]),
                create_info_row("Prénom:", student[1]),
                create_info_row("matricule:", student[2]),
                create_info_row("date_naissance:", student[3]),
                create_info_row("sexe:", student[4]),
                create_info_row("classe:", student[5]),
                ft.Divider(),
            ],
            width=450,
            height=350,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=10,
            ),
            actions=[
                ft.TextButton(
                    "Fermer",
                    icon=ft.Icons.CLOSE,
                    icon_color=ft.Colors.RED,
                    on_click=lambda e: Close(detail_dialog)
                )
            ]
        )
    def create_student_card(student):
        """Crée une carte pour un enseignant"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    f"{student[0]} {student[1]}",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(f"Classe :{student[5]}", size = 15),
                ft.Text(f"Matricue :{student[2]}", size=15),
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.INFO,
                        tooltip="Détails",
                        icon_color=ft.Colors.BLUE,
                        on_click=lambda e, t=student: show_details(t)
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8
            ),
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=ft.border_radius.only(top_right=20, bottom_left=20),
            padding=20,
            margin=10,
            
            width=280,
            height=200,
            #bgcolor=ft.Colors.ON_SURFACE_VARIANT,
        )
        
    # Chargement des enseignants
    students = load_student()
    student_cards = [create_student_card(student) for student in students]
    
    # Si aucun enseignant
    if not student_cards:
        student_cards = [
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SCHOOL, size=60, color=ft.Colors.GREY_400),
                    ft.Text(
                        "Aucun Eleve trouvé",
                        size=16,
                        color=ft.Colors.GREY_600
                    ),
                    ft.Text(
                        "Cliquez sur 'Ajouter' pour commencer",
                        size=12,
                        color=ft.Colors.GREY_500
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
                ),
                padding=30
            )
        ]
    
    # Dialog principal
    main_dialog = Dialog.custom_dialog(
        title=f"👨‍🏫 Liste des élèves ({len(students)})",
        content=ft.Column([
            ft.Row(
                [
                    ft.Column(
                        controls=student_cards,
                        scroll=ft.ScrollMode.AUTO,
                        height=330,
                        width = 350,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    )
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
            ft.Container(expand=True),
        ],
        width=450,
        height=450,
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        actions=[
            ft.TextButton(
                "Fermer",
                icon=ft.Icons.CLOSE,
                on_click=lambda e: Dialog.close_dialog(main_dialog)
            )
        ]
    )
    