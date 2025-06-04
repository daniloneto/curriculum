"""Generate PDF resumes from JSON data."""
from __future__ import annotations

import argparse
import json
import os
import sys

from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.units import inch
from templates import TemplateManager
from utils import (
    get_available_languages,
    get_field,
    get_jobs,
    get_section_content,
    get_section_list,
    get_section_title,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gerar currículo em formato PDF.")
    parser.add_argument("language", nargs="?", help="Código do idioma (ex: pt, en, es)")
    parser.add_argument("--template", "-t", default="pdf", help="Nome do template a ser usado")
    parser.add_argument("--json-file", help="Caminho para um arquivo JSON personalizado", default=None)
    return parser.parse_args()


def load_resume_data(language: str | None, json_file: str | None) -> tuple[dict, str]:
    available_languages = get_available_languages()
    default_lang = "pt" if "pt" in available_languages else next(iter(available_languages), None)
    selected_lang = default_lang
    if language and language.lower() in available_languages:
        selected_lang = language.lower()

    if not selected_lang and not json_file:
        print("Erro: Não foram encontrados arquivos de idioma válidos.")
        sys.exit(1)

    if json_file:
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data, selected_lang or "pt"

    json_file_path = available_languages[selected_lang]["file"]
    with open(json_file_path, "r", encoding="utf-8") as file:
        return json.load(file), selected_lang


def build_pdf(data: dict, template_name: str, selected_lang: str) -> str:
    template_manager = TemplateManager()
    try:
        template = template_manager.get_template(template_name)
    except ValueError:
        print(f"Template '{template_name}' não encontrado. Usando padrão 'pdf'.")
        template = template_manager.get_template("pdf")

    pdf_filename = get_field(data, "nomeArquivoSaida", "outputFileName")
    nome = get_field(data, "nome", "name", ["nombre"])
    if not pdf_filename:
        base = nome.replace(" ", "_") if nome else "Curriculo"
        pdf_filename = f"{base}_{selected_lang}.pdf"
    if not pdf_filename.lower().endswith(".pdf"):
        pdf_filename = os.path.splitext(pdf_filename)[0] + ".pdf"

    doc = template.create_document(pdf_filename)
    styles = template.get_styles()
    elements: list = []

    email = data.get("email", "")
    telefone = get_field(data, "telefone", "phone")
    linkedin = data.get("linkedin", "")

    template.add_title(elements, nome, email, telefone, linkedin, styles)

    secoes_key = next((k for k in ["secoes", "sections", "secciones", "sektionen"] if k in data), None)
    if not secoes_key:
        raise ValueError("Formato de arquivo JSON inválido. A chave de seções não foi encontrada.")
    secoes = data[secoes_key]

    resume_section = next((secoes[k] for k in [
        "resumoProfissional",
        "professionalSummary",
        "resumenProfesional",
        "resumentProfessionnel",
    ] if k in secoes), None)
    if resume_section:
        template.add_section_title(elements, get_section_title(resume_section), styles)
        elements.append(Paragraph(get_section_content(resume_section), styles["normal"]))
        elements.append(Spacer(1, 0.1 * inch))

    experience_section = next((secoes[k] for k in [
        "experienciaProfissional",
        "workExperience",
        "experienciaLaboral",
        "experienceProfessionnelle",
    ] if k in secoes), None)
    if experience_section:
        template.add_section_title(elements, get_section_title(experience_section), styles)
        for job in get_jobs(experience_section):
            position = get_field(job, "cargo", "position")
            if position:
                elements.append(Paragraph(f"• {position}", styles["bullet"]))
            period = get_field(job, "periodo", "period")
            if period:
                elements.append(Paragraph(period, styles["normal"]))
            description_content = next((job[k] for k in ["descricao", "description", "descripcion"] if k in job), None)
            processed = []
            if isinstance(description_content, str):
                processed = [s.strip() for s in description_content.split("\n") if s.strip()]
            elif isinstance(description_content, list):
                processed = [str(item).strip() for item in description_content if str(item).strip()]
            for item_text in processed:
                elements.append(Paragraph(f"- {item_text}", styles["bullet"]))
            elements.append(Spacer(1, 0.1 * inch))

    template.add_page_break(elements)
    skills_section = next((secoes[k] for k in ["habilidadesTecnicas", "technicalSkills", "competencesTechniques"] if k in secoes), None)
    if skills_section:
        template.add_section_title(elements, get_section_title(skills_section), styles)
        skills = next((skills_section[k] for k in ["habilidades", "skills", "competencias", "competences"] if k in skills_section), [])
        for skill in skills:
            skill_name = get_field(skill, "name", "nome", ["nombre"])
            skill_level_str = get_field(skill, "level", "nivel")
            if skill_name and skill_level_str:
                try:
                    template.add_skill_bar(elements, skill_name, styles, int(skill_level_str))
                except ValueError:
                    print(f"Aviso: Nível de habilidade inválido para '{skill_name}'. Pulando.")
        elements.append(Spacer(1, 0.1 * inch))

    certifications_section = next((secoes[k] for k in ["certificacoes", "certifications", "certificaciones", "certifications"] if k in secoes), None)
    if certifications_section:
        template.add_section_title(elements, get_section_title(certifications_section), styles)
        for cert in get_section_list(certifications_section):
            elements.append(Paragraph(f"🏅 {cert}", styles["normal"]))
        elements.append(Spacer(1, 0.1 * inch))

    education_section = next((secoes[k] for k in ["educacao", "education", "educacion", "education"] if k in secoes), None)
    if education_section:
        template.add_section_title(elements, get_section_title(education_section), styles)
        for degree in next((education_section[k] for k in ["formacao", "degrees", "formacion", "diplomes"] if k in education_section), []):
            elements.append(Paragraph(degree, styles["normal"]))
        elements.append(Spacer(1, 0.1 * inch))

    in_progress_section = next((secoes[k] for k in ["emAndamento", "inProgress", "enProgreso", "enCours"] if k in secoes), None)
    if in_progress_section:
        template.add_section_title(elements, get_section_title(in_progress_section), styles)
        for course in next((in_progress_section[k] for k in ["cursos", "courses", "cursos", "cours"] if k in in_progress_section), []):
            elements.append(Paragraph(course, styles["normal"]))

    doc.build(elements)
    return pdf_filename


def main() -> None:
    args = parse_args()
    data, lang = load_resume_data(args.language, args.json_file)
    output = build_pdf(data, args.template, lang)
    print(f"Arquivo PDF salvo como: {output}")


if __name__ == "__main__":
    main()
