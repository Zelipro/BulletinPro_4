import flet as ft
from Zeli_Dialog import ZeliDialog2
from sync_manager import supabase_db


def Gestion_Matiere(page, Donner):
    """Gestion des matières - Version Supabase complète"""
    Dialog = ZeliDialog2(page)
    
    Loag = Dialog.loading_dialog(
        title = "Chagement des matieres",
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
    
    def Get_all():
        """Récupère toutes les matières depuis Supabase"""
        etablissement = Return("etablissement")
        if not etablissement:
            return []
        
        try:
            matieres = supabase_db.get_matieres(etablissement=etablissement)
            # Convertir en tuples pour compatibilité
            return [(m['nom'], m['genre'], m['etablissement']) for m in matieres]
        except Exception as e:
            Dialog.error_toast(f"Erreur de chargement: {e}")
            return []
    
    def edit_matiere(matiere):
        """Modifie une matière"""
        Loag2 = Dialog.loading_dialog()
        def save():
            try:
                etablissement = Return("etablissement")
                if not etablissement:
                    Dialog.error_toast("Erreur de récupération de l'établissement")
                    return
                
                if not non_field.value or not non_field.value.strip():
                    non_field.error_text = "Ce champ est obligatoire"
                    page.update()
                    return
                
                if not genre_field.value:
                    genre_field.error_text = "Sélectionnez un genre"
                    page.update()
                    return
                
                # Mettre à jour via Supabase
                success = supabase_db.update_matiere(
                    old_nom=matiere[0],
                    etablissement=etablissement,
                    new_nom=non_field.value.strip(),
                    new_genre=genre_field.value
                )
                
                if not success:
                    Dialog.error_toast("Cette matière existe déjà")
                    return
                
                Dialog.info_toast("Modification effectuée avec succès !")
                Dialog.close_dialog(diag)
                Gestion_Matiere(page, Donner)
                
            except Exception as e:
                Dialog.error_toast(f"Erreur de modification: {e}")
        
        non_field = ft.TextField(
            label="Intitulé de la matière",
            value=matiere[0],
            text_align="center"
        )
        genre_field = ft.Dropdown(
            label="Genre",
            hint_text="Sélection du genre",
            value=matiere[1],
            options=[
                ft.dropdown.Option("Scientifique", leading_icon=ft.Icons.SCIENCE),
                ft.dropdown.Option("Littérature", leading_icon=ft.Icons.PAGES_ROUNDED),
                ft.dropdown.Option("Art", leading_icon=ft.Icons.ART_TRACK_ROUNDED),
            ]
        )
        
        Dialog.close_dialog(Loag2)
        diag = Dialog.custom_dialog(
            title="Modification de matière",
            content=ft.Column([
                non_field,
                genre_field
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, height=120),
            actions=[
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CLOSE, color="white"),
                        ft.Text(value="Annuler", color="white")
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor="red",
                    on_click=lambda e: Dialog.close_dialog(diag),
                    width=100,
                ),
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SAVE, color="white"),
                        ft.Text(value="Enregistrer", color="white")
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor="green",
                    width=120,
                    on_click=lambda e: save()
                ),
            ]
        )
    
    def add_matiere():
        """Ajoute une nouvelle matière"""
        Loag1 = Dialog.loading_dialog()
        def save():
            try:
                etablissement = Return("etablissement")
                if not etablissement:
                    Dialog.error_toast("Erreur de récupération de l'établissement")
                    return
                
                if not non_field.value or not non_field.value.strip():
                    non_field.error_text = "Ce champ est obligatoire"
                    page.update()
                    return
                
                if not genre_field.value:
                    genre_field.error_text = "Sélectionnez un genre"
                    page.update()
                    return
                
                # Créer via Supabase
                success = supabase_db.create_matiere(
                    nom=non_field.value.strip(),
                    genre=genre_field.value,
                    etablissement=etablissement
                )
                
                if not success:
                    Dialog.error_toast("Cette matière existe déjà")
                    return
                
                Dialog.info_toast("Matière ajoutée avec succès !")
                Dialog.close_dialog(diag)
                Gestion_Matiere(page, Donner)
                
            except Exception as e:
                Dialog.error_toast(f"Erreur d'ajout: {e}")
        
        non_field = ft.TextField(
            label="Intitulé de la matière",
            text_align="center"
        )
        genre_field = ft.Dropdown(
            label="Genre",
            hint_text="Sélection du genre",
            options=[
                ft.dropdown.Option("Scientifique", leading_icon=ft.Icons.SCIENCE),
                ft.dropdown.Option("Littérature", leading_icon=ft.Icons.PAGES_ROUNDED),
                ft.dropdown.Option("Art", leading_icon=ft.Icons.ART_TRACK_ROUNDED),
            ]
        )
        Dialog.close_dialog(Loag1)
        diag = Dialog.custom_dialog(
            title="Ajout de matière",
            content=ft.Column([
                non_field,
                genre_field
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, height=120),
            actions=[
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CLOSE, color="white"),
                        ft.Text(value="Annuler", color="white")
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor="red",
                    on_click=lambda e: Dialog.close_dialog(diag),
                    width=100,
                ),
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SAVE, color="white"),
                        ft.Text(value="Enregistrer", color="white")
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor="green",
                    width=120,
                    on_click=lambda e: save()
                ),
            ]
        )
    
    def create_matiere_card(matiere):
        """Crée une carte pour une matière"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    f"{matiere[0]}",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(f"Domaine : {matiere[1]}", size=15),
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.EDIT,
                        tooltip="Modifier",
                        icon_color=ft.Colors.GREEN,
                        on_click=lambda e, t=matiere: edit_matiere(t)
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=ft.border_radius.only(top_right=20, bottom_left=20),
            padding=20,
            margin=10,
            width=280,
            height=200,
        )
    
    # Chargement des matières
    matieres = Get_all()
    matiere_cards = [create_matiere_card(matiere) for matiere in matieres]
    
    # Si aucune matière
    if not matiere_cards:
        matiere_cards = [
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SCHOOL, size=60, color=ft.Colors.GREY_400),
                    ft.Text("Aucune matière trouvée", size=16, color=ft.Colors.GREY_600),
                    ft.Text("Cliquez sur 'Ajouter' pour commencer", size=12, color=ft.Colors.GREY_500),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=30
            )
        ]
    
    # Dialog principal
    Dialog.close_dialog(Loag)
    main_dialog = Dialog.custom_dialog(
        title=f"📚 Liste des matières ({len(matieres)})",
        content=ft.Column([
            ft.Row([
                ft.Column(
                    controls=matiere_cards,
                    scroll=ft.ScrollMode.AUTO,
                    height=330,
                    width=350,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ], scroll=ft.ScrollMode.AUTO),
            ft.Container(expand=True),
            ft.Divider(),
            ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE),
                    ft.Text("Ajouter une matière", color=ft.Colors.WHITE),
                ], spacing=8),
                bgcolor=ft.Colors.GREEN_700,
                on_click=lambda e: add_matiere(),
            )
        ], width=450, height=450, spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        actions=[
            ft.TextButton("Fermer", icon=ft.Icons.CLOSE, on_click=lambda e: Dialog.close_dialog(main_dialog))
        ]
    )