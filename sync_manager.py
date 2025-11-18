"""
supabase_manager.py - Gestionnaire Supabase pour remplacer SQLite
Installation requise: pip install supabase
"""

from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from datetime import datetime
import os

# === CORRECTIF COMPATIBILITÉ LINUX ===
if not hasattr(ft, 'Colors'):
    ft.Colors = ft.colors
# =====================================

# === CORRECTIF COMPATIBILITÉ LINUX ===
if not hasattr(ft, 'Icons'):
    ft.Icons = ft.icons
# =====================================

class SupabaseManager:
    """Gestionnaire unique pour toutes les opérations Supabase"""
    
    def __init__(self):
        # Récupérer depuis variables d'environnement ou config
        self.url = os.getenv("SUPABASE_URL", "https://fumkblfluoswkcegpape.supabase.co")
        self.key = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ1bWtibGZsdW9zd2tjZWdwYXBlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIwOTIyODgsImV4cCI6MjA3NzY2ODI4OH0.9s8cpr-jxaoqAZdBhUKlSHsjrqX-2zFr14y11RipmVA")
        
        self.client: Client = create_client(self.url, self.key)
        self.current_user = None
    
        # ============ AUTHENTIFICATION ============
    
    def login(self, identifiant: str, password: str) -> Optional[Dict]:
        """
        Connexion utilisateur
        Retourne: dict avec infos user ou None
        """
        try:
            response = self.client.table("User").select("*").eq("identifiant", identifiant).eq("passwords", password).execute()
            
            if response.data and len(response.data) > 0:
                user = response.data[0]
                self.current_user = user
                return {
                    "ident": user["identifiant"],
                    "pass": user["passwords"],
                    "name": user["nom"],
                    "role": user["titre"],
                    "etablissement": user["etablissement"],
                    "email": user.get("email"),
                    "telephone": user.get("telephone")
                }
            return None
        except Exception as e:
            print(f"❌ Erreur login: {e}")
            return None
    
    def get_user_info(self, identifiant: str, titre: str):# -> Optional[Dict]:
        """Récupère les infos d'un utilisateur"""
        try:
            response = self.client.table("User").select("*").eq("identifiant", identifiant).eq("titre", titre).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Erreur get_user_info: {e}")
            return None
    
        # ============ USERS (ADMINS & PROFS) ============
    
    def get_all_users(self, titre: Optional[str] = None, etablissement: Optional[str] = None) :#-> List[Dict]:
        """
        Récupère tous les utilisateurs
        Peut filtrer par titre (admin/prof) et/ou établissement
        """
        try:
            query = self.client.table("User").select("*")
            
            if titre:
                query = query.eq("titre", titre)
            if etablissement:
                query = query.eq("etablissement", etablissement)
            
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"❌ Erreur get_all_users: {e}")
            return []
    
    def create_user(self, user_data: Dict):# -> bool:
        """
        Crée un nouvel utilisateur (admin ou prof)
        user_data doit contenir: identifiant, passwords, nom, prenom, email, telephone, etablissement, titre
        """
        try:
            # Vérifier si l'utilisateur existe déjà
            existing = self.client.table("User").select("*").eq("identifiant", user_data["identifiant"]).execute()
            
            if existing.data:
                print("⚠️ Utilisateur existe déjà")
                return {False , "Utilisateur existe déjà"}
            
            # Créer l'utilisateur
            response = self.client.table("User").insert(user_data).execute()
            return {True , "Success"}
        except Exception as e:
            print(f"❌ Erreur create_user: {e}")
            return {False , e}
    
    def update_user(self, identifiant: str, updates: Dict) :#-> bool:
        """Met à jour un utilisateur"""
        try:
            response = self.client.table("User").update(updates).eq("identifiant", identifiant).execute()
            return True
        except Exception as e:
            print(f"❌ Erreur update_user: {e}")
            return False
    
    def delete_user(self, identifiant: str, titre: str) :#-> bool:
        """Supprime un utilisateur"""
        try:
            response = self.client.table("User").delete().eq("identifiant", identifiant).eq("titre", titre).execute()
            return True
        except Exception as e:
            print(f"❌ Erreur delete_user: {e}")
            return False
    
    # ============ TEACHERS ============
    
    def get_teachers(self, etablissement: str) :#-> List[Dict]:
        """Récupère tous les enseignants d'un établissement"""
        return self.get_all_users(titre="prof", etablissement=etablissement)
    
    def create_teacher(self, nom: str, prenom: str, email: str, telephone: str, 
                      matiere: str, etablissement: str) : # -> Optional[Dict]:
        """
        Crée un enseignant et son entrée Teacher
        Retourne les identifiants générés
        """
        try:
            # Générer identifiant et mot de passe
            ident = f"{prenom[0]}{nom}".upper().replace(" ", "")
            password = f"{prenom[0].lower()}@prof_{etablissement[:4]}_{len(nom) + len(prenom)}"
            
            # Créer dans User
            user_data = {
                "identifiant": ident,
                "passwords": password,
                "nom": nom,
                "prenom": prenom,
                "email": email,
                "telephone": telephone,
                "etablissement": etablissement,
                "titre": "prof"
            }
            
            if not self.create_user(user_data):
                return None
            
            # Créer dans Teacher
            teacher_data = {
                "ident": ident,
                "pass": password,
                "matiere": matiere
            }
            
            response = self.client.table("Teacher").insert(teacher_data).execute()
            
            return {
                "identifiant": ident,
                "password": password
            }
        except Exception as e:
            print(f"❌ Erreur create_teacher: {e}")
            return None
    
    def get_teacher_subject(self, identifiant: str) :#-> Optional[str]:
        """Récupère la matière d'un enseignant"""
        try:
            response = self.client.table("Teacher").select("matiere").eq("ident", identifiant).execute()
            return response.data[0]["matiere"] if response.data else None
        except Exception as e:
            print(f"❌ Erreur get_teacher_subject: {e}")
            return None
    
    def update_Teacher(self, identifiant: str, updates: Dict) :#-> bool:
        """Met à jour un utilisateur"""
        try:
            response = self.client.table("Teacher").update(updates).eq("identifiant", identifiant).execute()
            return True
        except Exception as e:
            print(f"❌ Erreur update_user: {e}")
            return False
    
    def delete_Teacher(self, identifiant: str) :#-> bool:
        """Supprime un utilisateur"""
        try:
            response = self.client.table("Teacher").delete().eq("identifiant", identifiant).execute()
            return True
        except Exception as e:
            print(f"❌ Erreur delete_user: {e}")
            return False
    # ============ STUDENTS (ÉLÈVES) ============
    
    def get_students(self, etablissement: str, classe: Optional[str] = None) :#-> List[Dict]:
        """
        Récupère les élèves d'un établissement
        Peut filtrer par classe
        """
        try:
            query = self.client.table("Students").select("*").eq("etablissement", etablissement)
            
            if classe:
                query = query.eq("classe", classe)
            
            response = query.order("nom", desc=False).execute()
            return response.data
        except Exception as e:
            print(f"❌ Erreur get_students: {e}")
            return []
    
    def create_student(self, student_data: Dict) :#-> bool:
        """
        Crée un élève
        student_data: nom, prenom, matricule, date_naissance, sexe, classe, etablissement
        """
        try:
            # Vérifier si existe
            existing = self.client.table("Students").select("*").eq("matricule", student_data["matricule"]).eq("etablissement", student_data["etablissement"]).execute()
            
            if existing.data:
                print("⚠️ Élève existe déjà")
                return False
            
            response = self.client.table("Students").insert(student_data).execute()
            return True
        except Exception as e:
            print(f"❌ Erreur create_student: {e}")
            return False
    
    def update_student(self, matricule: str, etablissement: str, updates: Dict) :#-> bool:
        """Met à jour un élève"""
        try:
            response = self.client.table("Students").update(updates).eq("matricule", matricule).eq("etablissement", etablissement).execute()
            return True
        except Exception as e:
            print(f"❌ Erreur update_student: {e}")
            return False
    
    def delete_student(self, matricule: str, etablissement: str) :#-> bool:
        """Supprime un élève"""
        try:
            response = self.client.table("Students").delete().eq("matricule", matricule).eq("etablissement", etablissement).execute()
            return True
        except Exception as e:
            print(f"❌ Erreur delete_student: {e}")
            return False
    
    # ============ MATIÈRES ============
    
    def get_matieres(self, etablissement: str) :#-> List[Dict]:
        """Récupère les matières d'un établissement"""
        try:
            response = self.client.table("Matieres").select("*").eq("etablissement", etablissement).order("nom", desc=False).execute()
            return response.data
        except Exception as e:
            print(f"❌ Erreur get_matieres: {e}")
            return []
    
    def create_matiere(self, nom: str, genre: str, etablissement: str) :#-> bool:
        """Crée une matière"""
        try:
            # Vérifier si existe
            existing = self.client.table("Matieres").select("*").eq("nom", nom).eq("etablissement", etablissement).execute()
            
            if existing.data:
                print("⚠️ Matière existe déjà")
                return False
            
            matiere_data = {
                "nom": nom,
                "genre": genre,
                "etablissement": etablissement
            }
            
            response = self.client.table("Matieres").insert(matiere_data).execute()
            return True
        except Exception as e:
            print(f"❌ Erreur create_matiere: {e}")
            return False
    
    def update_matiere(self, old_nom: str, etablissement: str, new_nom: str, new_genre: str) :#-> bool:
        """Met à jour une matière"""
        try:
            updates = {
                "nom": new_nom,
                "genre": new_genre
            }
            response = self.client.table("Matieres").update(updates).eq("nom", old_nom).eq("etablissement", etablissement).execute()
            return True
        except Exception as e:
            print(f"❌ Erreur update_matiere: {e}")
            return False
    
    # ============ CLASSES ============
    
    def get_classes(self, etablissement: str) :#-> List[Dict]:
        """Récupère les classes d'un établissement"""
        try:
            response = self.client.table("Class").select("*").eq("etablissement", etablissement).order("nom", desc=False).execute()
            return response.data
        except Exception as e:
            print(f"❌ Erreur get_classes: {e}")
            return []
    
    def get_classes_with_students(self, etablissement: str) :#-> List[Dict]:
        """Récupère les classes avec leur effectif"""
        try:
            # Récupérer toutes les classes distinctes depuis Students
            response = self.client.table("Students").select("classe").eq("etablissement", etablissement).execute()
            
            if not response.data:
                return []
            
            # Compter les effectifs
            classes_dict = {}
            for row in response.data:
                classe = row["classe"]
                classes_dict[classe] = classes_dict.get(classe, 0) + 1
            
            return [{"nom": classe, "effectif": effectif} for classe, effectif in classes_dict.items()]
        except Exception as e:
            print(f"❌ Erreur get_classes_with_students: {e}")
            return []
    
    def create_class(self, nom: str, etablissement: str) :#-> bool:
        """Crée une classe"""
        try:
            # Vérifier si existe
            existing = self.client.table("Class").select("*").eq("nom", nom).eq("etablissement", etablissement).execute()
            
            if existing.data:
                print("⚠️ Classe existe déjà")
                return [False , "Classe existe déjà"]
            
            class_data = {
                "nom": nom,
                "etablissement": etablissement
            }
            
            response = self.client.table("Class").insert(class_data).execute()
            return [True , "Success"]
        except Exception as e:
            print(f"❌ Erreur create_class: {e}")
            return [False , e]
    
    # ============ NOTES ============
    
    def get_notes(self, matricule: Optional[str] = None, classe: Optional[str] = None, 
                  matiere: Optional[str] = None) :#-> List[Dict]:
        """
        Récupère les notes
        Peut filtrer par matricule, classe et/ou matière
        """
        try:
            query = self.client.table("Notes").select("*")
            
            if matricule:
                query = query.eq("matricule", matricule)
            if classe:
                query = query.eq("classe", classe)
            if matiere:
                query = query.eq("matiere", matiere)
            
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"❌ Erreur get_notes: {e}")
            return []
    
    def create_or_update_note(self, note_data: Dict) :#-> bool:
        """
        Crée ou met à jour une note
        note_data: classe, matricule, matiere, coefficient, note_interrogation, 
                  note_devoir, note_composition, moyenne, date_saisie
        """
        try:
            # Vérifier si existe
            existing = self.client.table("Notes").select("*").eq("matricule", note_data["matricule"]).eq("matiere", note_data["matiere"]).eq("classe", note_data["classe"]).execute()
            
            if existing.data:
                # UPDATE
                response = self.client.table("Notes").update(note_data).eq("matricule", note_data["matricule"]).eq("matiere", note_data["matiere"]).eq("classe", note_data["classe"]).execute()
            else:
                # INSERT
                response = self.client.table("Notes").insert(note_data).execute()
            
            return True
        except Exception as e:
            print(f"❌ Erreur create_or_update_note: {e}")
            return False
    
    def delete_note(self, matricule: str, matiere: str, classe: str) :#-> bool:
        """Supprime une note"""
        try:
            response = self.client.table("Notes").delete().eq("matricule", matricule).eq("matiere", matiere).eq("classe", classe).execute()
            return True
        except Exception as e:
            print(f"❌ Erreur delete_note: {e}")
            return False
    
    # ============ UTILITAIRES ============
    
    def search_students(self, etablissement: str, search_term: str) :#-> List[Dict]:
        """Recherche d'élèves par nom, prénom ou matricule"""
        try:
            # Supabase ne supporte pas le LIKE avec OR, donc on fait plusieurs requêtes
            students = self.get_students(etablissement)
            
            search_lower = search_term.lower()
            filtered = [
                s for s in students
                if search_lower in s["nom"].lower() 
                or search_lower in s["prenom"].lower() 
                or search_lower in s["matricule"].lower()
            ]
            
            return filtered
        except Exception as e:
            print(f"❌ Erreur search_students: {e}")
            return []
    
    def get_student_with_notes(self, matricule: str, classe: str) :#-> Optional[Dict]:
        """Récupère un élève avec toutes ses notes"""
        try:
            # Récupérer l'élève
            student_response = self.client.table("Students").select("*").eq("matricule", matricule).execute()
            
            if not student_response.data:
                return None
            
            student = student_response.data[0]
            
            # Récupérer ses notes
            notes = self.get_notes(matricule=matricule, classe=classe)
            
            return {
                "student": student,
                "notes": notes
            }
        except Exception as e:
            print(f"❌ Erreur get_student_with_notes: {e}")
            return None


# ============ INSTANCE GLOBALE ============
supabase_db = SupabaseManager()


# ============ FONCTIONS HELPER POUR REMPLACER LES ANCIENNES ============

def Return(ident_type: str, user_info: Dict) :#-> List:
    """
    Fonction de compatibilité pour remplacer l'ancienne fonction Return
    """
    if ident_type == "etablissement":
        return [[user_info.get("etablissement")]]
    elif ident_type == "telephone":
        return [[user_info.get("telephone")]]
    elif ident_type == "email":
        return [[user_info.get("email")]]
    return []


