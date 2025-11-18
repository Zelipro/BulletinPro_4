import flet as ft
from Zeli_Dialog import ZeliDialog2
from sync_manager import supabase_db


def Gestion_Classe(page, Donner):
    """Gestion des classes - Version Supabase complète"""
    Dialog = ZeliDialog2(page)
    
    #Pour la passiance
    Pasiance = Dialog.loading_dialog("Chargement des données...")
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
    
    def search_students(students, search_term):
        """Filtre les élèves selon le terme de recherche"""
        if not search_term:
            return students
        
        search_term = search_term.lower().strip()
        filtered = []
        
        for student in students:
            if isinstance(student, dict):
                nom = str(student.get('nom', '')).lower()
                prenom = str(student.get('prenom', '')).lower()
                matricule = str(student.get('matricule', '')).lower()
            else:
                nom = str(student[0]).lower()
                prenom = str(student[1]).lower()
                matricule = str(student[2]).lower()
            
            if (search_term in nom or search_term in prenom or search_term in matricule):
                filtered.append(student)
        
        return filtered
    
    def show_class_details(classe_nom, effectif):
        """Affiche les détails d'une classe avec la liste des élèves"""
        etablissement = Return("etablissement")
        if not etablissement:
            Dialog.error_toast("Impossible de récupérer l'établissement")
            return
        
        try:
            all_students_raw = supabase_db.get_students(
                etablissement=etablissement,
                classe=classe_nom
            )
            all_students = [
                (s['nom'], s['prenom'], s['matricule'], s.get('date_naissance', 'N/A'), s['sexe'], s['classe'])
                for s in all_students_raw
            ]
        except Exception as e:
            Dialog.error_toast(f"Erreur chargement élèves: {e}")
            return
        
        students_container = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=10)
        
        def update_student_list(search_term=""):
            filtered_students = search_students(all_students, search_term)
            students_container.controls.clear()
            
            if not filtered_students:
                students_container.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.SEARCH_OFF, size=50, color=ft.Colors.GREY_400),
                            ft.Text("Aucun élève trouvé", size=16, color=ft.Colors.GREY_600),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                        padding=30
                    )
                )
            else:
                for student in filtered_students:
                    students_container.controls.append(create_student_row(student))
            page.update()
        
        def on_search_change(e):
            update_student_list(e.control.value)
        
        search_field = ft.TextField(
            hint_text="Rechercher par nom, prénom ou matricule...",
            prefix_icon=ft.Icons.SEARCH,
            border_color=ft.Colors.BLUE_200,
            focused_border_color=ft.Colors.BLUE_500,
            on_change=on_search_change,
            width=450,
        )
        
        update_student_list()
        
        detail_dialog = Dialog.custom_dialog(
            title=f"📚 Classe {classe_nom} - {len(all_students)} élève(s)",
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.Icons.PEOPLE, color=ft.Colors.BLUE, size=30),
                                ft.Text(f"{effectif}", size=20, weight=ft.FontWeight.BOLD),
                                ft.Text("Élèves", size=12, color=ft.Colors.GREY_600),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                            padding=10, border=ft.border.all(1, ft.Colors.BLUE_200), border_radius=10,
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.Icons.MALE, color=ft.Colors.GREEN, size=30),
                                ft.Text(f"{sum(1 for s in all_students if 'M' in str(s[4]))}", size=20, weight=ft.FontWeight.BOLD),
                                ft.Text("Garçons", size=12, color=ft.Colors.GREY_600),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                            padding=10, border=ft.border.all(1, ft.Colors.GREEN_200), border_radius=10,
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.Icons.FEMALE, color=ft.Colors.PINK, size=30),
                                ft.Text(f"{sum(1 for s in all_students if 'F' in str(s[4]))}", size=20, weight=ft.FontWeight.BOLD),
                                ft.Text("Filles", size=12, color=ft.Colors.GREY_600),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                            padding=10, border=ft.border.all(1, ft.Colors.PINK_200), border_radius=10,
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_AROUND, spacing=10),
                    padding=10, bgcolor=ft.Colors.BLUE_50, border_radius=10,
                ),
                ft.Divider(),
                search_field,
                ft.Divider(),
                ft.Container(content=students_container, height=300, width=450),
            ], width=500, height=550, spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.TextButton("Fermer", icon=ft.Icons.CLOSE, on_click=lambda e: Dialog.close_dialog(detail_dialog))
            ]
        )
    
    def create_student_row(student):
        """Crée une ligne pour afficher un élève"""
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(student[0][0].upper(), size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    width=40, height=40, border_radius=20,
                    bgcolor=ft.Colors.BLUE_400 if 'M' in str(student[4]) else ft.Colors.PINK_400,
                    alignment=ft.alignment.center,
                ),
                ft.Column([
                    ft.Text(f"{student[0]} {student[1]}", size=15, weight=ft.FontWeight.W_500),
                    ft.Row([
                        ft.Icon(ft.Icons.TAG, size=14, color=ft.Colors.GREY_600),
                        ft.Text(f"Matricule: {student[2]}", size=12, color=ft.Colors.GREY_700),
                        ft.Text("|", color=ft.Colors.GREY_400),
                        ft.Icon(
                            ft.Icons.MALE if 'M' in str(student[4]) else ft.Icons.FEMALE,
                            size=14,
                            color=ft.Colors.BLUE_400 if 'M' in str(student[4]) else ft.Colors.PINK_400
                        ),
                        ft.Text(student[4], size=12, color=ft.Colors.GREY_700),
                    ], spacing=5),
                ], spacing=2, expand=True),
                ft.IconButton(
                    icon=ft.Icons.INFO_OUTLINE,
                    icon_color=ft.Colors.BLUE,
                    tooltip="Voir détails",
                    on_click=lambda e, s=student: show_student_detail(s)
                ),
            ], spacing=10),
            padding=10, border=ft.border.all(1, ft.Colors.GREY_300), border_radius=8, ink=True,
        )
    
    def show_student_detail(student):
        """Affiche les détails complets d'un élève"""
        detail_student_dialog = Dialog.custom_dialog(
            title=f"👤 Détails - {student[0]} {student[1]}",
            content=ft.Column([
                ft.Divider(),
                create_info_row("Nom:", student[0]),
                create_info_row("Prénom:", student[1]),
                create_info_row("Matricule:", student[2]),
                create_info_row("Date de naissance:", student[3]),
                create_info_row("Sexe:", student[4]),
                create_info_row("Classe:", student[5]),
                ft.Divider(),
            ], width=400, height=300, scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.START, spacing=10),
            actions=[
                ft.TextButton("Fermer", icon=ft.Icons.CLOSE, icon_color=ft.Colors.RED, on_click=lambda e: Dialog.close_dialog(detail_student_dialog))
            ]
        )
    
    def add_class():
        """Ajoute une nouvelle classe"""
        def save(d):
            Loag = Dialog.loading_dialog("Enregistrement en cours...")
            etabl = Return("etablissement")
            if not etabl:
                Dialog.close_dialog(Loag)
                Dialog.error_toast("Erreur de récupération de l'établissement")
                return
            
            if not Classe_field.value or not Classe_field.value.strip():
                Dialog.close_dialog(Loag)
                Classe_field.error_text = "Ce champ est obligatoire"
                page.update()
                return
            
            success = supabase_db.create_class(nom=Classe_field.value.strip(), etablissement=etabl)
            
            if not success:
                Dialog.close_dialog(Loag)
                Dialog.error_toast("Erreur : Cette classe existe déjà")
                return
            
            Dialog.close_dialog(Loag)
            Dialog.info_toast("Classe ajoutée avec succès !")
            Dialog.close_dialog(d)
            Gestion_Classe(page, Donner)
        
        def Close(d):
            Dialog.close_dialog(d)
        
        Classe_field = ft.TextField(label="Classe", hint_text="Ex: Terminal C")
        
        diag = Dialog.custom_dialog(
            title="Nouvelle Classe",
            content=ft.Column([Classe_field, ft.Divider()], height=80),
            actions=[
                ft.ElevatedButton(icon=ft.Icons.CLOSE, icon_color="white", text="Annuler", color="white", bgcolor="red", on_click=lambda e: Close(diag)),
                ft.ElevatedButton(icon=ft.Icons.SAVE, icon_color="white", text="Enregistrer", color="white", bgcolor="green", on_click=lambda e: save(diag)),
            ]
        )
    
    def Close_see(diag):
        Dialog.close_dialog(diag)
        Gestion_Classe(page, Donner)
        
    def see(): #Pour voir toutes les classes
        Loag2 = Dialog.loading_dialog("Chargement des classes...")
        etablissement = Return("etablissement")
        
        if not etablissement:
            Dialog.close_dialog(Loag2)
            Dialog.error_toast("Impossible de récupérer l'établissement")
            return
        
        classes = supabase_db.get_classes(etablissement=etablissement)
        controls = []
        if not classes:
            controls = [
                ft.Icon(ft.Icons.CLASS_, size=60, color=ft.Colors.GREY_400),
                ft.Text("Aucune classe trouvée", size=16, color=ft.Colors.GREY_600),
                ft.Text("Verfifier votre connection et réessayez", size=12, color=ft.Colors.RED, text_align=ft.TextAlign.CENTER),
            ]
            #return
        else:
            for classe in classes:
                if isinstance(classe, dict):
                    classe_nom = classe.get("nom")
                else:
                    classe_nom = classe[0]
                
                controls.append(
                    ft.Text(classe_nom, size=15)
                    )
        class_list_container = ft.Column(
            scroll=ft.ScrollMode.AUTO, 
            spacing=10,
            width=450,
            height=400,
            controls=controls
        )
        
        Dialog.close_dialog(Loag2)
        
        detail_dialog = Dialog.custom_dialog(
            title="📚 Toutes les Classes",
            content=ft.Column([
                class_list_container
            ], width=500, height=450, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.TextButton("Fermer", icon=ft.Icons.CLOSE, on_click=lambda e: Close_see(detail_dialog))
            ]
        )
        
    def create_info_row(label, value):
        """Crée une ligne d'information"""
        return ft.Row([
            ft.Text(label, size=15, weight=ft.FontWeight.BOLD, width=150),
            ft.Text(str(value or "N/A"), size=15, selectable=True, expand=True),
        ], spacing=10)
    
    def create_class_card(classe):
        """Crée une carte pour une classe"""
        if isinstance(classe, dict):
            classe_nom = classe.get("nom")
            effectif = classe.get("effectif", 0)
        else:
            classe_nom = classe[0]
            effectif = classe[1] if len(classe) > 1 else 0
        
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.CLASS_, color=ft.Colors.GREEN, size=40),
                ft.Text(classe_nom, size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Container(height=5),
                ft.Row([
                    ft.Icon(ft.Icons.PEOPLE, color=ft.Colors.BLUE, size=20),
                    ft.Text(f"{effectif} élève(s)", size=14),
                ], alignment=ft.MainAxisAlignment.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8, alignment=ft.MainAxisAlignment.CENTER),
            border=ft.border.all(2, ft.Colors.GREEN_200), border_radius=15, padding=20, margin=10,
            width=200, height=180, ink=True,
            on_click=lambda e, c=classe_nom, ef=effectif: show_class_details(c, ef),
        )
    
    etablissement = Return("etablissement")
    if not etablissement:
        Dialog.close_dialog(Pasiance)
        Dialog.error_toast("Impossible de récupérer l'établissement")
        return
    
    classes = supabase_db.get_classes_with_students(etablissement=etablissement)
    class_cards = [create_class_card(classe) for classe in classes]
    
    if not class_cards:
        Dialog.close_dialog(Pasiance)
        class_cards = [
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CLASS_, size=60, color=ft.Colors.GREY_400),
                    ft.Text("Aucune classe trouvée", size=16, color=ft.Colors.GREY_600),
                    ft.Text("Les classes sont créées automatiquement lors de l'ajout d'élèves", size=12, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=30
            )
        ]
    
    Dialog.close_dialog(Pasiance)
    main_dialog = Dialog.custom_dialog(
        title=f"📚 Gestion des Classes ({len(classes)} classe(s))",
        content=ft.Column([
            ft.Text("Cliquez sur une classe pour voir ses élèves", size=14, color=ft.Colors.GREY_600, italic=True),
            ft.Text("Ici seul les classes qui ont au moins une élèves peuvent se faire voir", size=14, color=ft.Colors.RED, italic=True),
            ft.Divider(),
            ft.Row([
                ft.Column(
                    controls=[ft.GridView(controls=class_cards, runs_count=2)],
                    scroll=ft.ScrollMode.AUTO, height=350, width=450, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ], scroll=ft.ScrollMode.AUTO),
            ft.Divider(),
            ft.Row([
                ft.ElevatedButton(icon=ft.Icons.ADD, text="Ajouter une Classe", on_click=lambda e: add_class()),
                ft.ElevatedButton(icon=ft.Icons.VISIBILITY, text="Voir Toutes les Classes", on_click=lambda e: see()),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
        ], width=500, height=650, spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        actions=[
            ft.TextButton("Fermer", icon=ft.Icons.CLOSE, on_click=lambda e: Dialog.close_dialog(main_dialog))
        ]
    )