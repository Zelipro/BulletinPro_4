import flet as ft
from Zeli_Dialog import ZeliDialog2
from datetime import datetime
from fpdf import FPDF
import os
from sync_manager import supabase_db

# === CORRECTIF COMPATIBILITÉ LINUX ===
if not hasattr(ft, 'Colors'):
    ft.Colors = ft.colors
# =====================================

global PAGE
def Generation_Bulletin(page, Donner):
    """Génération des bulletins scolaires avec FPDF2 - Compatible PyInstaller"""
    PAGE = page
    Dialog = ZeliDialog2(page)
    
    if Donner.get("role") not in ["admin", "prof"]:
        Dialog.alert_dialog(title="Accès refusé", message="Vous n'avez pas les permissions nécessaires.")
        return
    
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
    
    def init_trimestre_table():
        """Initialise la table Trimestre_moyen_save dans Supabase"""
        try:
            response = supabase_db.client.table("Trimestre_moyen_save").select("*").limit(1).execute()
        except Exception as e:
            print(f"⚠️ Table Trimestre_moyen_save n'existe peut-être pas: {e}")
    
    def calculate_moyenne_matiere(note_interro, note_devoir, note_compo):
        try:
            interro, devoir, compo = float(note_interro), float(note_devoir), float(note_compo)
            return round((((interro + devoir) / 2) + compo) / 2, 2)
        except:
            return 0.0
    
    def calculate_moyenne_generale(notes):
        try:
            total_points, total_coef = 0, 0
            for note in notes:
                moyenne_matiere = calculate_moyenne_matiere(note['note_interrogation'], note['note_devoir'], note['note_composition'])
                coef = float(note['coefficient'])
                total_points += moyenne_matiere * coef
                total_coef += coef
            return round(total_points / total_coef, 2) if total_coef > 0 else 0.0
        except:
            return 0.0
    
    def get_appreciation(moyenne):
        if moyenne >= 18: return "Excellent"
        elif moyenne >= 16: return "Très bien"
        elif moyenne >= 14: return "Bien"
        elif moyenne >= 12: return "Assez bien"
        elif moyenne >= 10: return "Passable"
        elif moyenne >= 8: return "Insuffisant"
        else: return "Très insuffisant"
    
    def get_matiere_info(matiere_nom, etablissement):
        """Récupère les informations complètes d'une matière depuis Supabase"""
        try:
            matiere_search = matiere_nom.strip().lower()
            response = supabase_db.client.table("Matieres")\
                .select("nom, genre")\
                .eq("etablissement", etablissement)\
                .execute()
            
            if response.data:
                for matiere in response.data:
                    if matiere['nom'].strip().lower() == matiere_search:
                        nom_complet = matiere['nom'].strip()
                        genre = matiere['genre'].strip().lower() if matiere['genre'] else ""
                        
                        if any(keyword in genre for keyword in ["scien", "science", "scientifique"]):
                            categorie = "Scientifique"
                        elif any(keyword in genre for keyword in ["litt", "littérature", "littéraire"]):
                            categorie = "Littéraire"
                        elif any(keyword in genre for keyword in ["art", "artistique"]):
                            categorie = "Facultative"
                        else:
                            categorie = "Facultative"
                        
                        return nom_complet, categorie
                
                for matiere in response.data:
                    if matiere_search in matiere['nom'].strip().lower():
                        nom_complet = matiere['nom'].strip()
                        genre = matiere['genre'].strip().lower() if matiere['genre'] else ""
                        
                        if any(keyword in genre for keyword in ["scien", "science", "scientifique"]):
                            categorie = "Scientifique"
                        elif any(keyword in genre for keyword in ["litt", "littérature", "littéraire"]):
                            categorie = "Littéraire"
                        else:
                            categorie = "Facultative"
                        
                        return nom_complet, categorie
            
            return matiere_nom, "Facultative"
        except Exception as e:
            print(f"❌ Erreur get_matiere_info: {e}")
            return matiere_nom, "Facultative"
    
    def calculate_matiere_rank(matiere, classe, moyenne_eleve):
        """Calcule le rang dans une matière"""
        try:
            notes_response = supabase_db.client.table("Notes")\
                .select("matricule, note_interrogation, note_devoir, note_composition")\
                .eq("classe", classe)\
                .eq("matiere", matiere)\
                .execute()
            
            if not notes_response.data:
                return "N/A"
            
            moyennes = []
            for note in notes_response.data:
                moy = calculate_moyenne_matiere(
                    note['note_interrogation'], 
                    note['note_devoir'], 
                    note['note_composition']
                )
                moyennes.append((note['matricule'], moy))
            
            moyennes.sort(key=lambda x: x[1], reverse=True)
            
            for i, (mat, moy) in enumerate(moyennes, 1):
                if abs(moy - moyenne_eleve) < 0.01:
                    return f"{i}er" if i == 1 else f"{i}e"
            
            return "N/A"
        except Exception as e:
            print(f"❌ Erreur calculate_matiere_rank: {e}")
            return "N/A"
    
    def save_trimestre_moyenne(matricule, moyenne, annee_scolaire, periode):
        """Sauvegarde la moyenne du trimestre dans Supabase"""
        try:
            existing = supabase_db.client.table("Trimestre_moyen_save")\
                .select("*")\
                .eq("matricule", matricule)\
                .eq("annee_scolaire", annee_scolaire)\
                .eq("periode", periode)\
                .execute()
            
            data = {
                "matricule": matricule,
                "moyenne": moyenne,
                "annee_scolaire": annee_scolaire,
                "periode": periode
            }
            
            if existing.data:
                supabase_db.client.table("Trimestre_moyen_save")\
                    .update(data)\
                    .eq("matricule", matricule)\
                    .eq("annee_scolaire", annee_scolaire)\
                    .eq("periode", periode)\
                    .execute()
            else:
                supabase_db.client.table("Trimestre_moyen_save")\
                    .insert(data)\
                    .execute()
        except Exception as e:
            print(f"❌ Erreur save_trimestre_moyenne: {e}")
    
    def get_previous_moyennes(matricule, annee_scolaire, periode_actuelle):
        """Récupère les moyennes précédentes"""
        try:
            response = supabase_db.client.table("Trimestre_moyen_save")\
                .select("periode, moyenne")\
                .eq("matricule", matricule)\
                .eq("annee_scolaire", annee_scolaire)\
                .neq("periode", periode_actuelle)\
                .order("id", desc=False)\
                .execute()
            
            return [(row['periode'], row['moyenne']) for row in response.data] if response.data else []
        except Exception as e:
            print(f"❌ Erreur get_previous_moyennes: {e}")
            return []
    
    def load_classes_with_students():
        """Charge les classes avec effectifs"""
        etablissement = Return("etablissement")
        if not etablissement:
            return []
        
        try:
            return supabase_db.get_classes_with_students(etablissement=etablissement)
        except Exception as e:
            print(f"❌ Erreur load_classes_with_students: {e}")
            return []
    
    def load_students_by_class(classe_nom):
        """Charge les élèves d'une classe"""
        etablissement = Return("etablissement")
        if not etablissement:
            return []
        
        try:
            students_data = supabase_db.get_students(etablissement=etablissement, classe=classe_nom)
            return [
                (s['nom'], s['prenom'], s['matricule'], s.get('date_naissance', 'N/A'), s['sexe'], s['classe'])
                for s in students_data
            ]
        except Exception as e:
            print(f"❌ Erreur load_students_by_class: {e}")
            return []
    
    def get_student_notes(matricule, classe):
        """Récupère les notes d'un élève"""
        try:
            notes = supabase_db.get_notes(matricule=matricule, classe=classe)
            return notes
        except Exception as e:
            print(f"❌ Erreur get_student_notes: {e}")
            return []
    
    def get_teacher_by_subject(matiere, etablissement):
        """Récupère le nom COMPLET du professeur d'une matière"""
        try:
            teacher_response = supabase_db.client.table("Teacher")\
                .select("ident")\
                .eq("matiere", matiere)\
                .execute()
            
            if not teacher_response.data:
                return "N/A"
            
            ident = teacher_response.data[0]['ident']
            
            user_response = supabase_db.client.table("User")\
                .select("nom, prenom")\
                .eq("identifiant", ident)\
                .eq("etablissement", etablissement)\
                .execute()
            
            if user_response.data:
                nom = user_response.data[0]['nom']
                prenom = user_response.data[0]['prenom']
                return f"{nom} {prenom[0]}." if prenom else nom
            
            return "N/A"
        except Exception as e:
            print(f"❌ Erreur get_teacher_by_subject: {e}")
            return "N/A"
    
    def calculate_class_rank(moyenne, classe, annee, notes_list):
        """Calcule le rang dans la classe"""
        try:
            students_response = supabase_db.client.table("Notes")\
                .select("matricule")\
                .eq("classe", classe)\
                .execute()
            
            if not students_response.data:
                return "N/A"
            
            matricules = list(set([s['matricule'] for s in students_response.data]))
            
            moyennes = []
            for mat in matricules:
                notes_eleve = supabase_db.get_notes(matricule=mat, classe=classe)
                if notes_eleve:
                    moy = calculate_moyenne_generale(notes_eleve)
                    moyennes.append((mat, moy))
            
            moyennes.sort(key=lambda x: x[1], reverse=True)
            
            for i, (mat, moy) in enumerate(moyennes, 1):
                if abs(moy - moyenne) < 0.01:
                    return f"{i}e" if i > 1 else "1er"
            
            return "N/A"
        except Exception as e:
            print(f"❌ Erreur calculate_class_rank: {e}")
            return "N/A"
    
    def calculate_class_stats(classe):
        """Calcule les statistiques de la classe"""
        try:
            students_response = supabase_db.client.table("Notes")\
                .select("matricule")\
                .eq("classe", classe)\
                .execute()
            
            if not students_response.data:
                return {'plus_forte': 0, 'plus_faible': 0, 'moyenne_classe': 0}
            
            matricules = list(set([s['matricule'] for s in students_response.data]))
            
            moyennes = []
            for mat in matricules:
                notes_eleve = supabase_db.get_notes(matricule=mat, classe=classe)
                if notes_eleve:
                    moy = calculate_moyenne_generale(notes_eleve)
                    moyennes.append(moy)
            
            if moyennes:
                return {
                    'plus_forte': round(max(moyennes), 2),
                    'plus_faible': round(min(moyennes), 2),
                    'moyenne_classe': round(sum(moyennes) / len(moyennes), 2)
                }
            
            return {'plus_forte': 0, 'plus_faible': 0, 'moyenne_classe': 0}
        except Exception as e:
            print(f"❌ Erreur calculate_class_stats: {e}")
            return {'plus_forte': 0, 'plus_faible': 0, 'moyenne_classe': 0}
    
    # ==================== CLASSE FPDF PERSONNALISÉE ====================
    
    class BulletinPDF(FPDF):
        """Classe pour générer des bulletins scolaires avec FPDF2"""
        
        def __init__(self):
            super().__init__()
            self.set_auto_page_break(auto=False)
            self.add_page()
        
        def draw_background(self):
            """Dessine le fond vert menthe du bulletin"""
            self.set_fill_color(212, 232, 212)
            self.rect(0, 0, 210, 297, 'F')
            
            self.set_line_width(0.5)
            self.set_draw_color(102, 102, 102)
            self.rect(5, 5, 200, 287)
        
        def draw_header(self, etablissement, contact, annee, devise, logo_path=None):
            """Dessine l'en-tête du bulletin"""
            if logo_path and os.path.exists(logo_path):
                try:
                    self.image(logo_path, x=93, y=8, w=24)
                except Exception as e:
                    print(f"⚠️ Erreur logo: {e}")
            
            self.set_xy(8, 10)
            self.set_font('Arial', '', 7)
            self.multi_cell(65, 3.5,
                f"MINISTÈRE DES ENSEIGNEMENTS PRIMAIRE,\n"
                f"SECONDAIRE, TECHNIQUE ET DE L'ARTISANAT\n\n"
                f"{etablissement}\n"
                f"{contact}",
                0, 'L')
            
            self.set_xy(137, 10)
            self.set_font('Arial', 'B', 7)
            self.multi_cell(65, 3.5, "RÉPUBLIQUE TOGOLAISE\n", 0, 'R')
            self.set_xy(137, 13.5)
            self.set_font('Arial', '', 7)
            self.multi_cell(65, 3.5, "Travail-Liberté-Patrie\n\n", 0, 'R')
            self.set_xy(137, 20)
            self.set_font('Arial', 'B', 8)
            self.set_text_color(46, 125, 50)
            self.multi_cell(65, 3.5, f"{devise}\n", 0, 'R')
            self.set_text_color(0, 0, 0)
            self.set_xy(137, 27)
            self.set_font('Arial', '', 7)
            self.multi_cell(65, 3.5, f"Année scolaire : {annee}", 0, 'R')
        
        def draw_title(self, periode):
            """Dessine le titre du bulletin"""
            self.set_xy(10, 35)
            self.set_fill_color(76, 175, 80)
            self.set_text_color(255, 255, 255)
            self.set_font('Arial', 'B', 11)
            self.cell(190, 7, f"BULLETIN DE NOTES DU {periode.upper()}", 0, 1, 'C', True)
            self.set_text_color(0, 0, 0)
        
        def draw_student_info(self, classe, effectif, nom, prenom, matricule, date_naissance, sexe):
            """Dessine les informations de l'élève"""
            self.set_xy(10, 44)
            self.set_fill_color(232, 245, 233)
            self.set_draw_color(153, 153, 153)
            self.rect(10, 44, 190, 15, 'DF')
            
            self.set_font('Arial', '', 8)
            self.set_xy(11, 46)
            self.cell(95, 4, f"Classe : {classe}", 0, 0)
            self.cell(94, 4, f"Effectif : {effectif}", 0, 1)
            
            self.set_xy(11, 50)
            self.cell(140, 4, f"NOM ET PRENOMS DE L'ELEVE : {nom} {prenom}", 0, 0)
            self.cell(49, 4, f"Né(e) le : {date_naissance}", 0, 1)
            
            self.set_xy(11, 54)
            self.cell(140, 4, f"N° Mle : {matricule}", 0, 0)
            self.cell(49, 4, f"Sexe : {sexe}", 0, 1)
        
        def draw_notes_table(self, notes_data, start_y=61):
            """Dessine le tableau des notes"""
            self.set_xy(10, start_y)
            
            col_w = [40, 12, 12, 12, 12, 12, 10, 12, 8, 25, 20, 15]
            
            self.set_font('Arial', 'B', 7)
            self.set_fill_color(168, 213, 186)
            self.set_draw_color(102, 102, 102)
            
            headers = ['Matières', 'Inter.', 'Dev.', 'M.Clas', 'Compo.', 'Note /20', 
                      'Coef.', 'Note coef.', 'Rg', 'Professeur', 'Apprécia*', 'Signature']
            
            x_start = 10
            for i, header in enumerate(headers):
                self.set_xy(x_start, start_y)
                self.cell(col_w[i], 8, header, 1, 0, 'C', True)
                x_start += col_w[i]
            
            current_y = start_y + 8
            
            for section_name, notes in notes_data.items():
                self.set_xy(10, current_y)
                self.set_fill_color(232, 245, 233)
                self.set_font('Arial', 'B', 8)
                self.cell(190, 5, section_name, 1, 1, 'L', True)
                current_y += 5
                
                self.set_font('Arial', '', 7)
                for note in notes:
                    self.set_xy(10, current_y)
                    self.cell(col_w[0], 5, note[0][:35], 1, 0, 'L')
                    for i, val in enumerate(note[1:], 1):
                        self.cell(col_w[i], 5, str(val), 1, 0, 'C')
                    current_y += 5
            
            return current_y
        
        def draw_totals(self, totals_data, start_y):
            """Dessine les lignes de totaux"""
            self.set_xy(10, start_y)
            self.set_fill_color(255, 249, 230)
            self.set_font('Arial', 'B', 7)
            
            col_w = [40, 12, 12, 12, 12, 12, 10, 12, 8, 25, 20, 15]
            
            for row_data in totals_data:
                x_pos = 10
                col_index = 0
                
                for text, span in row_data:
                    width = sum(col_w[col_index:col_index + span])
                    self.set_xy(x_pos, start_y)
                    self.cell(width, 5, text, 1, 0, 'C', True)
                    x_pos += width
                    col_index += span
                
                start_y += 5
            
            return start_y
        
        def draw_decision_section(self, appreciation, responsable_type, responsable_nom, 
                                 distinctions, date_actuelle, titulaire_nom, start_y):
            """Dessine la section décisions - SIGNATURES GROUPÉES"""
            section_height = 38
            
            self.set_xy(10, start_y)
            self.set_fill_color(255, 249, 230)
            self.set_draw_color(102, 102, 102)
            self.rect(10, start_y, 190, section_height, 'D')
            
            self.line(105, start_y, 105, start_y + section_height)
            
            # GAUCHE
            self.set_xy(12, start_y + 2)
            self.set_font('Arial', 'B', 8)
            self.cell(90, 4, "DÉCISION DU CONSEIL DES PROFESSEURS", 0, 1)
            
            self.set_xy(12, start_y + 7)
            self.set_font('Arial', 'B', 7)
            self.cell(90, 3, "Distinctions spéciales", 0, 1)
            
            y_pos = start_y + 11
            self.set_font('Arial', '', 7)
            for key, label in [('tableau_honneur', 'Tableau d\'honneur'), 
                              ('encouragement', 'Encouragement'), 
                              ('felicitation', 'Félicitation')]:
                if distinctions.get(key):
                    self.set_xy(12, y_pos)
                    self.cell(90, 3, f"{label}: OUI", 0, 1)
                    y_pos += 3
            
            self.set_xy(12, y_pos + 1)
            self.set_font('Arial', 'B', 7)
            self.cell(90, 3, "APPRECIATION DU CHEF D'ETABLISSEMENT", 0, 1)
            self.set_xy(12, y_pos + 5)
            self.set_font('Arial', '', 7)
            self.multi_cell(90, 3, appreciation, 0, 'L')
            
            # DROITE - SIGNATURES GROUPÉES (CORRIGÉ)
            # 1. TITULAIRE : Label + Espace pour signature + Nom
            self.set_xy(107, start_y + 2)
            self.set_font('Arial', '', 7)
            self.cell(85, 3, "Signature du titulaire de classe", 0, 1, 'C')
            
            # Espace pour la signature (ligne)
            #self.line(107, start_y + 8, 197, start_y + 8)
            
            # Nom du titulaire JUSTE EN DESSOUS
            self.set_xy(107, start_y + 11)
            self.set_font('Arial', 'B', 7)
            self.cell(85, 3, titulaire_nom, 0, 1, 'C')
            
            #Ligne pour faire la separation
            self.line(107, start_y + 17, 197, start_y + 17)
            
            # 2. Date
            self.set_xy(140, start_y + 19)
            self.set_font('Arial', '', 7)
            self.cell(85, 3, f"Lomé le {date_actuelle}", 0, 1, 'C')
            
            # 3. PROVISEUR : Label + Espace pour signature + Nom
            self.set_xy(107, start_y + 20)
            self.set_font('Arial', '', 7)
            self.cell(85, 3, f"Le {responsable_type}", 0, 1, 'C')
            
            # Espace pour la signature (ligne)
            #self.line(107, start_y + 26, 197, start_y + 26)
            
            # Nom du responsable JUSTE EN DESSOUS
            self.set_xy(107, start_y + 29)
            self.set_font('Arial', 'B', 8)
            self.cell(85, 3, responsable_nom, 0, 1, 'C')
        
        def draw_footer(self, date_edition):
            """Dessine le pied de page"""
            self.set_xy(10, 285)
            self.set_font('Arial', '', 7)
            self.set_text_color(102, 102, 102)
            self.cell(190, 4, f"Édité le {date_edition}", 0, 0, 'C')
            self.set_text_color(0, 0, 0)
    
    # ==================== GÉNÉRATION DU BULLETIN ====================
    
    def generate_bulletin_pdf(student, classe, notes, etablissement, annee, appreciation, 
                            moyenne_gen, rang, periode, type_periode, effectif, 
                            devise_etablissement, logo_path, bp_info, type_responsable, titulaire_nom):
        """Génère le PDF du bulletin"""
        try:
            pdf = BulletinPDF()
            pdf.draw_background()
            
            contact = Return("telephone")
            if bp_info and bp_info.strip():
                contact_info = f"{bp_info} Tel : {contact}"
            else:
                contact_info = f"Tel : {contact}"
            
            pdf.draw_header(etablissement, contact_info, annee, devise_etablissement, logo_path)
            pdf.draw_title(periode)
            
            date_naissance = student[3] if len(student) > 3 and student[3] else "N/A"
            pdf.draw_student_info(classe, effectif, student[0], student[1], 
                                 student[2], date_naissance, student[4])
            
            notes_litt, notes_sci, notes_fac = [], [], []
            
            for note in notes:
                matiere_courte = str(note['matiere']).strip()
                matiere_nom_complet, categorie = get_matiere_info(matiere_courte, etablissement)
                moyenne_mat = calculate_moyenne_matiere(note['note_interrogation'], 
                                                        note['note_devoir'], 
                                                        note['note_composition'])
                note_coef = moyenne_mat * float(note['coefficient'])
                prof = get_teacher_by_subject(matiere_courte, etablissement)
                apprec = get_appreciation(moyenne_mat)
                rang_mat = calculate_matiere_rank(matiere_courte, classe, moyenne_mat)
                
                matiere_row = [
                    matiere_nom_complet,
                    f"{note['note_interrogation']}",
                    f"{note['note_devoir']}",
                    f"{note['note_composition']}",
                    f"{note['note_composition']}",
                    f"{moyenne_mat:.2f}",
                    f"{note['coefficient']}",
                    f"{note_coef:.2f}",
                    rang_mat,
                    prof[:20],
                    apprec,
                    ""
                ]
                
                if categorie == "Littéraire":
                    notes_litt.append(matiere_row)
                elif categorie == "Scientifique":
                    notes_sci.append(matiere_row)
                else:
                    notes_fac.append(matiere_row)
            
            notes_data = {}
            if notes_litt:
                notes_data["MATIÈRES LITTÉRAIRES"] = notes_litt
            if notes_sci:
                notes_data["MATIÈRES SCIENTIFIQUES"] = notes_sci
            if notes_fac:
                notes_data["MATIÈRES FACULTATIVES"] = notes_fac
            
            current_y = pdf.draw_notes_table(notes_data, start_y=61)
            
            total_coef = sum(float(n['coefficient']) for n in notes)
            total_points = sum(calculate_moyenne_matiere(n['note_interrogation'], n['note_devoir'], 
                              n['note_composition']) * float(n['coefficient']) for n in notes)
            
            stats = calculate_class_stats(classe)
            moyennes_prec = get_previous_moyennes(student[2], annee, periode)
            moyennes_prec_text = "  ".join([f"{p}: {m:.2f}" for p, m in moyennes_prec])
            
            admin_nom_complet = "Non disponible"
            try:
                response = supabase_db.client.table("User")\
                    .select("nom, prenom")\
                    .eq("etablissement", etablissement)\
                    .eq("titre", "admin")\
                    .limit(1)\
                    .execute()
                
                if response.data:
                    admin_nom_complet = f"{response.data[0]['nom']} {response.data[0]['prenom']}"
            except:
                pass
            
            # TOTAUX CORRIGÉS + MOYENNES PRÉCÉDENTES
            totals_data = [
                [("", 5), ("TOTAL", 1), (f"{int(total_coef)}", 1), (f"{total_points:.2f}", 1), ("", 4)],
                [(f"{periode}:", 2), (f"{moyenne_gen:.2f}", 1), (f"Rg : {rang}", 1), ("Moyennes :", 2), ("", 3), ("Retards : 0 fois", 2), ("", 1)],
                [(f"Moyenne du {type_periode.lower()}", 5), (f"{moyenne_gen:.2f}", 1), (f"Plus forte : {stats['plus_forte']}", 2), ("Absences : 0 H", 3), ("", 1)]
            ]
            
            # TOUJOURS AFFICHER LES MOYENNES PRÉCÉDENTES (même si vide)
            if moyennes_prec and len(moyennes_prec) > 0:
                # Il y a des moyennes précédentes
                totals_data.append([
                    ("Moyennes précédentes", 5), 
                    (moyennes_prec_text, 3), 
                    (f"Plus faible : {stats['plus_faible']}", 3), 
                    ("", 1)
                ])
            else:
                # Pas de moyennes précédentes, mais on affiche quand même la ligne
                totals_data.append([
                    ("Moyennes précédentes", 5), 
                    ("", 3), 
                    (f"Plus faible : {stats['plus_faible']}", 3), 
                    ("", 1)
                ])
            
            totals_data.append([
                ("Décision du conseil de classe", 5), 
                (f"Moyenne classe : {stats['moyenne_classe']}", 6), 
                ("", 1)
            ])
            
            current_y = pdf.draw_totals(totals_data, current_y)
            
            distinctions = {
                'tableau_honneur': moyenne_gen >= 10,
                'encouragement': 12 <= moyenne_gen < 14,
                'felicitation': moyenne_gen >= 14
            }
            
            pdf.draw_decision_section(
                appreciation,
                type_responsable,
                admin_nom_complet,
                distinctions,
                datetime.now().strftime("%d %B %Y"),
                titulaire_nom,
                current_y + 2
            )
            
            pdf.draw_footer(datetime.now().strftime("%d/%m/%Y"))
            
            return pdf
            
        except Exception as e:
            print(f"❌ Erreur generate_bulletin_pdf: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_bulletin_pdf(pdf, filename):
        """Sauvegarde le PDF"""
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            pdf.output(filename)
            print(f"✅ PDF créé: {filename}")
            return True
        except Exception as e:
            print(f"❌ Erreur save_bulletin_pdf: {e}")
            return False
    
    # ==================== INTERFACE UTILISATEUR ====================
    
    def select_periode_and_classe():
        Dialog = ZeliDialog2(PAGE)
        
        Loag1 = Dialog.loading_dialog()
        
        init_trimestre_table()
        type_periode = ft.Dropdown(
            label="Type de période",
            options=[
                ft.dropdown.Option("Trimestre"),
                ft.dropdown.Option("Semestre")
            ],
            value="Trimestre",
            width=250
        )
        periode_dropdown = ft.Dropdown(
            label="Période",
            options=[
                ft.dropdown.Option("Premier Trimestre"),
                ft.dropdown.Option("Deuxième Trimestre"),
                ft.dropdown.Option("Troisième Trimestre")
            ],
            value="Premier Trimestre",
            width=250
        )
        
        def update_periode_options(e):
            if type_periode.value == "Semestre":
                periode_dropdown.options = [
                    ft.dropdown.Option("Premier Semestre"),
                    ft.dropdown.Option("Deuxième Semestre")
                ]
                periode_dropdown.value = "Premier Semestre"
            else:
                periode_dropdown.options = [
                    ft.dropdown.Option("Premier Trimestre"),
                    ft.dropdown.Option("Deuxième Trimestre"),
                    ft.dropdown.Option("Troisième Trimestre")
                ]
                periode_dropdown.value = "Premier Trimestre"
            page.update()
        
        type_periode.on_change = update_periode_options
        annee_field = ft.TextField(
            label="Année scolaire",
            value="2024/2025",
            text_align="center",
            width=250
        )
        devise_field = ft.TextField(
            label="Devise",
            value="DISCIPLINE - TRAVAIL - RÉUSSITE",
            text_align="center",
            width=250
        )
        bp_field = ft.TextField(
            label="BP (Boîte Postale) - Optionnel",
            hint_text="Ex: 04 BP 87 LOME TOGO",
            text_align="center",
            width=250
        )
        
        responsable_dropdown = ft.Dropdown(
            label="Type de responsable",
            hint_text="Sélectionnez",
            options=[
                ft.dropdown.Option("Directeur"),
                ft.dropdown.Option("Proviseur"),
            ],
            value="Proviseur",
            width=250
        )
        
        logo_path_field = ft.TextField(
            label="Logo (optionnel)",
            text_align="center",
            width=250,
            read_only=True
        )
        selected_logo = {"path": None}
        
        def pick_logo(e):
            file_picker = ft.FilePicker(on_result=lambda r: handle_logo_selection(r))
            page.overlay.append(file_picker)
            page.update()
            file_picker.pick_files(
                allowed_extensions=["png", "jpg", "jpeg", "svg"],
                dialog_title="Logo"
            )
        
        def handle_logo_selection(result):
            if result.files:
                selected_logo["path"] = result.files[0].path
                logo_path_field.value = result.files[0].name
                page.update()
        
        def valider_periode(e):
            if not all([type_periode.value, periode_dropdown.value, annee_field.value, devise_field.value, responsable_dropdown.value]):
                Dialog.error_toast("Champs obligatoires manquants")
                return
            Dialog.close_dialog(periode_dialog)
            show_classes_selection(
                type_periode.value,
                periode_dropdown.value,
                annee_field.value,
                devise_field.value,
                selected_logo["path"],
                bp_field.value,
                responsable_dropdown.value
            )
        
        Dialog.close_dialog(Loag1)
        periode_dialog = Dialog.custom_dialog(
            title="📅 Configuration",
            content=ft.Column([
                ft.Icon(ft.Icons.CALENDAR_MONTH, size=50, color=ft.Colors.BLUE),
                ft.Text("Configurez les paramètres", size=14, text_align=ft.TextAlign.CENTER),
                ft.Divider(),
                ft.Text("Période scolaire", size=12, weight=ft.FontWeight.BOLD),
                type_periode,
                periode_dropdown,
                annee_field,
                ft.Divider(),
                ft.Text("Personnalisation", size=12, weight=ft.FontWeight.BOLD),
                devise_field,
                bp_field,
                ft.Divider(),
                ft.Text("Responsable de l'établissement", size=12, weight=ft.FontWeight.BOLD),
                responsable_dropdown,
                ft.Text("💡 Le nom sera récupéré automatiquement", size=10, italic=True, color=ft.Colors.GREY_600),
                ft.Divider(),
                ft.Row([
                    logo_path_field,
                    ft.IconButton(
                        icon=ft.Icons.UPLOAD_FILE,
                        tooltip="Logo",
                        on_click=pick_logo,
                        bgcolor=ft.Colors.BLUE_100
                    )
                ], spacing=5),
                ft.Text("💡 Logo et BP optionnels", size=10, italic=True, color=ft.Colors.GREY_600)
            ], width=450, height=650, spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton(
                    "Annuler",
                    icon=ft.Icons.CLOSE,
                    on_click=lambda e: Dialog.close_dialog(periode_dialog)
                ),
                ft.ElevatedButton(
                    "Suivant",
                    icon=ft.Icons.ARROW_FORWARD,
                    bgcolor=ft.Colors.BLUE,
                    color=ft.Colors.WHITE,
                    on_click=valider_periode
                )
            ]
        )
    
    def show_classes_selection(type_periode, periode, annee_scolaire, devise_etablissement, logo_path, bp_info, type_responsable):
        Dialog = ZeliDialog2(PAGE)
        
        Loag = Dialog.loading_dialog()
        classes = load_classes_with_students()
        
        def create_class_card(classe):
            classe_nom = classe.get('nom') if isinstance(classe, dict) else classe[0]
            effectif = classe.get('effectif', 0) if isinstance(classe, dict) else classe[1]
            
            students_with_notes = 0
            try:
                students_response = supabase_db.client.table("Notes")\
                    .select("matricule")\
                    .eq("classe", classe_nom)\
                    .execute()
                
                if students_response.data:
                    students_with_notes = len(set([s['matricule'] for s in students_response.data]))
            except:
                pass
            
            pourcentage = int((students_with_notes / effectif * 100)) if effectif > 0 else 0
            
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CLASS_, color=ft.Colors.PURPLE, size=40),
                    ft.Text(classe_nom, size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=5),
                    ft.Row([
                        ft.Icon(ft.Icons.PEOPLE, color=ft.Colors.BLUE, size=20),
                        ft.Text(f"{effectif} élève(s)", size=14)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(height=5),
                    ft.Column([
                        ft.Text(f"{students_with_notes}/{effectif} avec notes", size=12, color=ft.Colors.GREY_700),
                        ft.ProgressBar(
                            value=pourcentage / 100,
                            color=ft.Colors.GREEN if pourcentage == 100 else ft.Colors.ORANGE,
                            bgcolor=ft.Colors.GREY_300,
                            height=8
                        ),
                        ft.Text(f"{pourcentage}%", size=12, weight=ft.FontWeight.BOLD)
                    ], spacing=3, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                border=ft.border.all(2, ft.Colors.PURPLE_200),
                border_radius=15,
                padding=20,
                margin=10,
                width=220,
                height=220,
                ink=True,
                on_click=lambda e, c=classe_nom, ef=effectif: ask_titulaire_then_show_students(
                    c, ef, type_periode, periode, annee_scolaire, devise_etablissement, logo_path, bp_info, type_responsable
                )
            )
        
        def ask_titulaire_then_show_students(classe_nom, effectif, type_periode, periode, annee_scolaire, devise_etablissement, logo_path, bp_info, type_responsable):
            """Demande le nom du titulaire avant d'afficher les élèves"""
            titulaire_field = ft.TextField(
                label="Nom complet du titulaire de classe",
                hint_text="Ex: ADOM Jean",
                text_align="left",
                width=400
            )
            
            def valider_titulaire(e):
                if not titulaire_field.value or not titulaire_field.value.strip():
                    Dialog.error_toast("Veuillez saisir le nom du titulaire")
                    return
                Dialog.close_dialog(titulaire_dialog)
                show_student_selection_with_checkboxes(
                    classe_nom, effectif, type_periode, periode, annee_scolaire, 
                    devise_etablissement, logo_path, bp_info, type_responsable, 
                    titulaire_field.value.strip()
                )
            
            titulaire_dialog = Dialog.custom_dialog(
                title=f"👨‍🏫 Titulaire de {classe_nom}",
                content=ft.Column([
                    ft.Icon(ft.Icons.PERSON, size=50, color=ft.Colors.BLUE),
                    ft.Text("Saisissez le nom du titulaire de cette classe", size=14, text_align=ft.TextAlign.CENTER),
                    ft.Divider(),
                    titulaire_field,
                    ft.Text("💡 Ce nom apparaîtra sur tous les bulletins de la classe", size=10, italic=True, color=ft.Colors.GREY_600)
                ], width=450, height=250, spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                actions=[
                    ft.TextButton(
                        "Retour",
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda e: Dialog.close_dialog(titulaire_dialog)
                    ),
                    ft.ElevatedButton(
                        "Valider",
                        icon=ft.Icons.CHECK,
                        bgcolor=ft.Colors.GREEN,
                        color=ft.Colors.WHITE,
                        on_click=valider_titulaire
                    )
                ]
            )
        
        class_cards = [create_class_card(classe) for classe in classes]
        if not class_cards:
            class_cards.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.CLASS_, size=60, color=ft.Colors.GREY_400),
                        ft.Text("Aucune classe disponible", size=16, color=ft.Colors.GREY_600)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=30
                )
            )
        
        Dialog.close_dialog(Loag)
        classes_dialog = Dialog.custom_dialog(
            title=f"📚 Sélection classe - {periode}",
            content=ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.INFO, color=ft.Colors.BLUE),
                            ft.Text(f"Période: {periode} ({annee_scolaire})", size=14, weight=ft.FontWeight.W_500)
                        ], spacing=10),
                        ft.Text(f"Devise: {devise_etablissement}", size=11, italic=True),
                        ft.Text(f"Responsable: {type_responsable}", size=11, italic=True, color=ft.Colors.PURPLE)
                    ]),
                    bgcolor=ft.Colors.BLUE_50,
                    padding=15,
                    border_radius=10
                ),
                ft.Divider(),
                ft.Text("Sélectionnez une classe", size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Container(height=10),
                ft.Container(
                    content=ft.GridView(
                        controls=class_cards,
                        runs_count=2,
                        max_extent=240,
                        child_aspect_ratio=1.0,
                        spacing=10,
                        run_spacing=10
                    ),
                    height=400
                )
            ], width=600, height=600, spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.TextButton(
                    "Retour",
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: (Dialog.close_dialog(classes_dialog), select_periode_and_classe())
                ),
                ft.TextButton(
                    "Fermer",
                    icon=ft.Icons.CLOSE,
                    on_click=lambda e: Dialog.close_dialog(classes_dialog)
                )
            ]
        )
    
    def show_student_selection_with_checkboxes(classe_nom, effectif, type_periode, periode, annee_scolaire, devise_etablissement, logo_path, bp_info, type_responsable, titulaire_nom):
        Dialog = ZeliDialog2(PAGE)
        
        Loag = Dialog.loading_dialog()
        
        students = load_students_by_class(classe_nom)
        etablissement = Return("etablissement")
        
        student_checkboxes = {}
        student_rows = []
        
        for student in students:
            notes = get_student_notes(student[2], classe_nom)
            has_notes = len(notes) > 0
            
            if has_notes:
                moyenne = calculate_moyenne_generale(notes)
                moy_text = f"{moyenne:.2f}/20"
                moy_color = ft.Colors.GREEN if moyenne >= 10 else ft.Colors.ORANGE
            else:
                moy_text = "Aucune note"
                moy_color = ft.Colors.GREY
            
            checkbox = ft.Checkbox(value=False, disabled=not has_notes)
            student_checkboxes[student[2]] = checkbox
            
            row = ft.Container(
                content=ft.Row([
                    checkbox,
                    ft.Container(
                        content=ft.Text(
                            student[0][0].upper(),
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE
                        ),
                        width=35,
                        height=35,
                        border_radius=17.5,
                        bgcolor=ft.Colors.BLUE_400 if 'M' in str(student[4]) else ft.Colors.PINK_400,
                        alignment=ft.alignment.center
                    ),
                    ft.Column([
                        ft.Text(f"{student[0]} {student[1]}", size=13, weight=ft.FontWeight.W_500),
                        ft.Text(f"Mat: {student[2]}", size=10, color=ft.Colors.GREY_700)
                    ], spacing=2, expand=True),
                    ft.Text(moy_text, size=12, color=moy_color, weight=ft.FontWeight.BOLD),
                    ft.Icon(
                        ft.Icons.CHECK_CIRCLE if has_notes else ft.Icons.WARNING,
                        color=ft.Colors.GREEN if has_notes else ft.Colors.ORANGE,
                        size=18
                    )
                ], spacing=10),
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=8
            )
            
            student_rows.append(row)
        
        if not student_rows:
            student_rows.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.PEOPLE, size=60, color=ft.Colors.GREY_400),
                        ft.Text("Aucun élève dans cette classe", size=16, color=ft.Colors.GREY_600)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=30
                )
            )
        
        def toggle_all(e):
            select_all = e.control.value
            for checkbox in student_checkboxes.values():
                if not checkbox.disabled:
                    checkbox.value = select_all
            page.update()
        
        select_all_checkbox = ft.Checkbox(
            label="Sélectionner tous les élèves avec notes",
            value=False,
            on_change=toggle_all
        )
        
        def generate_selected_bulletins(e):
            selected = [matricule for matricule, cb in student_checkboxes.items() if cb.value]
            if not selected:
                Dialog.error_toast("Veuillez sélectionner au moins un élève")
                return
            Dialog.close_dialog(selection_dialog)
            selected_student_data = [s for s in students if s[2] in selected]
            generate_all_bulletins_batch(
                classe_nom, selected_student_data, etablissement, annee_scolaire,
                periode, type_periode, effectif, devise_etablissement, logo_path, bp_info, type_responsable, titulaire_nom
            )
        
        Dialog.close_dialog(Loag)
        selection_dialog = Dialog.custom_dialog(
            title=f"📋 {classe_nom} - Sélection des élèves",
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.INFO, color=ft.Colors.BLUE),
                        ft.Text(f"{periode} ({annee_scolaire}) - Titulaire: {titulaire_nom}", size=13, italic=True)
                    ], spacing=10),
                    bgcolor=ft.Colors.BLUE_50,
                    padding=10,
                    border_radius=5
                ),
                ft.Divider(),
                select_all_checkbox,
                ft.Divider(),
                ft.Container(
                    content=ft.Column(controls=student_rows, spacing=8, scroll=ft.ScrollMode.AUTO),
                    height=350
                )
            ], width=600, height=550, spacing=10),
            actions=[
                ft.TextButton(
                    "Retour",
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: (
                        Dialog.close_dialog(selection_dialog),
                        show_classes_selection(type_periode, periode, annee_scolaire, devise_etablissement, logo_path, bp_info, type_responsable)
                    )
                ),
                ft.ElevatedButton(
                    "Générer les bulletins sélectionnés",
                    icon=ft.Icons.PICTURE_AS_PDF,
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                    on_click=generate_selected_bulletins
                )
            ]
        )
    
    def generate_all_bulletins_batch(classe_nom, students, etablissement, annee, periode, type_periode, effectif, devise_etablissement, logo_path, bp_info, type_responsable, titulaire_nom):
        loading_dialog = Dialog.loading_dialog(
            title="Génération en cours...",
            message=f"Génération de {len(students)} bulletin(s)..."
        )
        
        try:
            # Obtenir le chemin du dossier Documents de l'utilisateur (multi-plateforme)
            if os.name == 'nt':  # Windows
                documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
            else:  # Linux, Mac, Unix
                documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
            
            # Créer le chemin complet : Documents/Bulletins/Classe/Periode
            bulletins_dir = os.path.join(documents_path, "Bulletins", classe_nom, periode.replace(' ', '_'))
            
            # Créer les dossiers si nécessaire
            os.makedirs(bulletins_dir, exist_ok=True)
            
            success_count = 0
            for student in students:
                notes = get_student_notes(student[2], classe_nom)
                if notes:
                    moyenne_gen = calculate_moyenne_generale(notes)
                    rang = calculate_class_rank(moyenne_gen, classe_nom, annee, notes)
                    filename = f"{bulletins_dir}/Bulletin_{student[0]}_{student[1]}.pdf"
                    
                    pdf = generate_bulletin_pdf(
                        student, classe_nom, notes, etablissement, annee,
                        "Bon Travail", moyenne_gen, rang, periode, type_periode, effectif,
                        devise_etablissement, logo_path, bp_info, type_responsable, titulaire_nom
                    )
                    
                    if pdf and save_bulletin_pdf(pdf, filename):
                        save_trimestre_moyenne(student[2], moyenne_gen, annee, periode)
                        success_count += 1
            
            Dialog.close_dialog(loading_dialog)
            success_dialog = Dialog.custom_dialog(
                title="✅ Génération terminée",
                content=ft.Column([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=60),
                    ft.Text(
                        f"{success_count} bulletin(s) générés !",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN
                    ),
                    ft.Text(f"Dossier: {bulletins_dir}", size=13),
                    ft.ElevatedButton(
                        "Ouvrir le dossier",
                        icon=ft.Icons.FOLDER_OPEN,
                        on_click=lambda e: os.startfile(bulletins_dir) if os.name == 'nt' else os.system(f'open "{bulletins_dir}"')
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, width=400, height=250),
                actions=[
                    ft.ElevatedButton(
                        "OK",
                        bgcolor=ft.Colors.GREEN,
                        color=ft.Colors.WHITE,
                        on_click=lambda e: Dialog.close_dialog(success_dialog)
                    )
                ]
            )
        except Exception as ex:
            Dialog.close_dialog(loading_dialog)
            Dialog.error_toast(f"Erreur: {str(ex)}")
            print(f"Erreur: {ex}")
            import traceback
            traceback.print_exc()
    
    select_periode_and_classe()
