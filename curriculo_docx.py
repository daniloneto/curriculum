"""Command line tool to generate DOCX resumes from JSON files."""
from __future__ import annotations

import argparse
import json
import os
import sys

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
    parser = argparse.ArgumentParser(description="Gerar currículo em formato DOCX.")
    parser.add_argument("language", nargs="?", help="Código do idioma (ex: pt, en, es)")
    parser.add_argument("--template", "-t", default="docx", help="Nome do template a ser usado")
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


def build_document(data: dict, template_name: str, selected_lang: str) -> str:
    template_manager = TemplateManager()
    try:
        template = template_manager.get_template(template_name)
    except ValueError:
        print(f"Template '{template_name}' não encontrado. Usando padrão 'docx'.")
        template = template_manager.get_template("docx")

    doc = template.create_document()

    nome = get_field(data, "nome", "name", ["nombre"])
    email = data.get("email", "")
    telefone = get_field(data, "telefone", "phone")
    linkedin = data.get("linkedin", "")

    secoes_key = next((k for k in ["secoes", "sections", "secciones", "sektionen"] if k in data), None)
    if not secoes_key:
        raise ValueError("Formato de arquivo JSON inválido. A chave de seções não foi encontrada.")
    secoes = data[secoes_key]

    template.add_title(doc, nome, email, telefone, linkedin)

    resume_section = next((secoes[k] for k in [
        "resumoProfissional",
        "professionalSummary",
        "resumenProfesional",
        "resumentProfessionnel",
    ] if k in secoes), None)
    if resume_section:
        template.add_section_title(doc, get_section_title(resume_section))
        doc.add_paragraph(get_section_content(resume_section))

    experience_section = next((secoes[k] for k in [
        "experienciaProfissional",
        "workExperience",
        "experienciaLaboral",
        "experienceProfessionnelle",
    ] if k in secoes), None)
    if experience_section:
        template.add_section_title(doc, get_section_title(experience_section))
        for job in get_jobs(experience_section):
            position = get_field(job, "cargo", "position")
            if position:
                doc.add_paragraph(position, style="List Bullet")
            period = get_field(job, "periodo", "period")
            if period:
                doc.add_paragraph(period)
            description_items = next((job[k] for k in ["descricao", "description", "descripcion"] if k in job), [])
            descricao = "".join(f"- {item}\n" for item in description_items)
            if descricao:
                doc.add_paragraph(descricao)

    template.add_page_break(doc)
    skills_section = next((secoes[k] for k in [
        "habilidadesTecnicas",
        "technicalSkills",
        "habilidadesTecnicas",
        "competencesTechniques",
    ] if k in secoes), None)
    if skills_section:
        template.add_section_title(doc, get_section_title(skills_section))
        skills = next((skills_section[k] for k in ["habilidades", "skills", "habilidades", "competences"] if k in skills_section), [])
        for skill in skills:
            skill_name = get_field(skill, "nome", "name")
            skill_level = get_field(skill, "nivel", "level")
            if skill_name and skill_level:
                template.add_skill_bar(doc, skill_name, skill_level)

    certifications_section = next((secoes[k] for k in ["certificacoes", "certifications", "certificaciones", "certifications"] if k in secoes), None)
    if certifications_section:
        template.add_section_title(doc, get_section_title(certifications_section))
        for cert in get_section_list(certifications_section):
            p = doc.add_paragraph()
            p.add_run("🏅 ").bold = True
            p.add_run(cert)

    education_section = next((secoes[k] for k in ["educacao", "education", "educacion", "education"] if k in secoes), None)
    if education_section:
        template.add_section_title(doc, get_section_title(education_section))
        for degree in next((education_section[k] for k in ["formacao", "degrees", "formacion", "diplomes"] if k in education_section), []):
            doc.add_paragraph(degree)

    in_progress_section = next((secoes[k] for k in ["emAndamento", "inProgress", "enProgreso", "enCours"] if k in secoes), None)
    if in_progress_section:
        template.add_section_title(doc, get_section_title(in_progress_section))
        for course in next((in_progress_section[k] for k in ["cursos", "courses", "cursos", "cours"] if k in in_progress_section), []):
            doc.add_paragraph(course)

    output_path = get_field(data, "nomeArquivoSaida", "outputFileName")
    if not output_path:
        output_name = nome.replace(" ", "_") if nome else "Curriculo"
        output_path = f"{output_name}_{selected_lang}.docx"

    doc.save(output_path)
    return output_path


def main() -> None:
    args = parse_args()
    data, lang = load_resume_data(args.language, args.json_file)
    output = build_document(data, args.template, lang)
    print(f"Arquivo salvo como: {output}")


if __name__ == "__main__":
    main()
