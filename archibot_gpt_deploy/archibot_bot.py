
import re
import json
from typing import List, Dict
import fitz  # PyMuPDF
import webbrowser

class Archibot:
    def __init__(self):
        self.sections_order = [
            "Conditions générales",
            "Revêtements extérieurs",
            "Approvisionnement",
            "Béton",
            "Charpente",
            "Solins"
        ]
        self.materials_keywords = [
            "Galvalume", "Maibec", "fibrociment", "bois", "aluminium", "acier",
            "zinc", "HMP", "KYNAR 500", "HYLAR 5000", "Harrywood", "MS1", "Bellara",
            "agway", "ideal revêtement", "Alutech", "panfab", "Norwood", "acier galvanisé",
            "acier prépeint", "panneau composite", "panneau métallique", "bardage", "solin",
            "garniture", "moulure", "revêtement", "Revêtements muraux métalliques",
            "Panneaux composites en aluminium", "Revêtements muraux en métal", "Solins et garnitures en métal"
        ]
        self.spec_keywords = [
            "calibre", "épaisseur", "norme", "CSA", "ASTM", "installation",
            "Z275", "G90", "dimensions", "vis", "rivets", "clips de fixation",
            "ASTM A653", "ASTM A755", "ASTM B209", "CSA S16", "CSA S136",
            "CAN/CGSB 93.3", "CAN/CGSB 1.108", "ULC S102", "ULC S134", "AAMA 508",
            "AAMA 2603", "AAMA 2605", "épaisseur minimale", "revêtement"
        ]
        self.critical_mentions = [
            "à valider", "obligatoire", "certifié", "conformité", "architecte",
            "conformité aux normes", "rapports d’essai", "certifications",
            "responsabilités d’ingénieur", "inspections terrain",
            "dessins d’atelier", "calculs d’ingénieur", "fiches techniques",
            "échantillons", "garanties", "instructions de mise en œuvre",
            "Documents et échantillons à soumettre", "Étanchéité des joints",
            "nettoyage de fin de travaux", "dégagement des accès",
            "conformité aux règlements municipaux", "travaux à réaliser en période hivernale",
            "coût des permis", "garantie contractuelle", "nettoyage après exécution",
            "déneigement", "instructions aux soumissionnaires", "calendrier des travaux",
            "visite des lieux", "addenda", "transmission de la soumission",
            "description des étapes des travaux", "solutions de remplacement",
            "période de validité des soumissions", "adjudication du contrat",
            "permis de construction", "marché à prix forfaitaire", "maître d’ouvrage",
            "maître d’œuvre", "supervision du projet", "réunions hebdomadaires du chantier",
            "gestion des équipements fournis par le client", "BSDQ", "Tango",
            "conditions générales du devis", "responsabilités de l'entrepreneur",
            "portée des travaux", "membre AERMQ", "condition d'hiver",
            "horaire jour", "horaire soir", "horaire nuit"
        ]

    def extract_and_highlight_sections(self, pdf_path: str):
        doc = fitz.open(pdf_path)
        for section in self.sections_order:
            section_doc = fitz.open()
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if section.lower() in text.lower():
                    new_page = section_doc.new_page(width=page.rect.width, height=page.rect.height)
                    new_page.show_pdf_page(new_page.rect, doc, page_num)

            if section_doc.page_count == 0:
                continue

            for page in section_doc:
                self.highlight_keyword(page, section, (1, 1, 0))  # Jaune

            filename = f"{section.replace(' ', '_')}_annoté.pdf"
            section_doc.save(filename)
            section_doc.close()
            webbrowser.open(filename)
        doc.close()

    def highlight_keyword(self, page, keyword, color):
        text_instances = page.search_for(keyword, quads=True)
        for inst in text_instances:
            highlight = page.add_highlight_annot(inst.rect)
            highlight.set_colors(stroke=color, fill=color)
            highlight.update()

    def analyze(self, pdf_text: str) -> Dict:
        sections = self.split_sections(pdf_text)
        results = []
        todo_list = []

        for section_title, section_text in sections.items():
            section_data = {
                "SECTION": section_title,
                "STATUT": "OK",
                "IMPACT": "",
                "LIEN": "",
                "Résumé": "",
            }

            material_found = self.search_keywords(section_text, self.materials_keywords)
            spec_found = self.search_keywords(section_text, self.spec_keywords)
            critical_found = self.search_keywords(section_text, self.critical_mentions)

            summary_parts = []
            if material_found:
                summary_parts.append(f"Matériaux : {', '.join(material_found)}")
            if spec_found:
                summary_parts.append(f"Spécifications : {', '.join(spec_found)}")
            if critical_found:
                section_data["STATUT"] = "À valider"
                section_data["IMPACT"] = "Attention"
                summary_parts.append(f"Mentions critiques : {', '.join(critical_found)}")
                todo_list.extend([f"Valider : {m}" for m in critical_found])

            section_data["Résumé"] = "; ".join(summary_parts)
            results.append(section_data)

        return {
            "résumé": "Analyse complète du devis selon les sections clés.",
            "résultats": results,
            "to-do": todo_list
        }

    def split_sections(self, text: str) -> Dict[str, str]:
        section_regex = '|'.join([re.escape(sec) for sec in self.sections_order])
        matches = list(re.finditer(f'({section_regex})', text, re.IGNORECASE))

        sections = {}
        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            section_title = match.group(1)
            sections[section_title] = text[start:end].strip()

        return sections

    def search_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Return keywords found in ``text``.

        Each keyword is treated as a literal string. Prior implementation used
        ``re.search`` directly with the keyword, which interprets characters
        such as ``.`` or ``/`` as regular expression meta characters. This
        caused false positives or failed matches for specifications like
        ``"CAN/CGSB 93.3"``. To avoid this we escape each keyword before
        searching.
        """

        return [kw for kw in keywords if re.search(re.escape(kw), text, re.IGNORECASE)]

def analyze_devis(text: str) -> Dict:
    bot = Archibot()
    return bot.analyze(text)
