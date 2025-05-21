# Sistema de Geração de Currículos Multilíngue

Este projeto é um sistema completo para geração de currículos em formato DOCX e PDF a partir de arquivos JSON estruturados, com suporte para múltiplos idiomas e layouts personalizáveis. O sistema permite criar currículos profissionais rapidamente em diversos formatos e idiomas.

## Recursos

- **Múltiplos formatos**: Geração de currículos em formato DOCX e PDF
- **Internacionalização**: Suporte para múltiplos idiomas com detecção automática
- **Personalização**: Sistema de templates para layouts diferenciados
- **Interface amigável**: Menu interativo para seleção de idioma, formato e template
- **Design profissional**: 
  - Fontes elegantes e adequadas para currículos
  - Elementos visuais como ícones e indicadores de nível de habilidade (barras ou quadradinhos)
  - Formatação profissional com seções bem definidas
  - Quebras de página automáticas para melhor organização

## Requisitos

### Pré-requisitos
- Python 3.6 ou superior
- pip (gerenciador de pacotes do Python)

### Bibliotecas
- **Para formato DOCX**: python-docx
- **Para formato PDF**: ReportLab

## Instalação

1. Clone este repositório:
```bash
git clone https://github.com/daniloneto/cv-generator.git
cd cv-generator
```

2. Instale as dependências necessárias:
```bash
pip install python-docx reportlab
```

## Uso

### Método Recomendado: Interface Interativa

A maneira mais simples de usar o sistema é através do menu interativo:

```bash
python cv-generator.py
```

Este comando inicia um assistente que permite escolher:
1. O idioma do currículo (baseado nos arquivos JSON disponíveis)
2. O formato de saída (PDF ou DOCX)
3. O template de layout desejado (padrão ou personalizado)

### Uso via Linha de Comando

Para usuários avançados, é possível executar os scripts diretamente com parâmetros:

Para gerar o currículo em formato DOCX:
```bash
python curriculo_docx.py [CÓDIGO_IDIOMA] [--template NOME_TEMPLATE]
```

Para gerar o currículo em formato PDF:
```bash
python curriculo_pdf.py [CÓDIGO_IDIOMA] [--template NOME_TEMPLATE]
```

#### Parâmetros:
- `CÓDIGO_IDIOMA`: Código de 2 letras do idioma (pt, en, es, etc.)
- `--template NOME_TEMPLATE`: (Opcional) Nome do template a ser utilizado

#### Exemplos:
```bash
python curriculo_docx.py pt                    # Português com template padrão
python curriculo_pdf.py en                     # Inglês com template padrão
python curriculo_pdf.py pt --template moderno  # Português com template moderno
```

Se nenhum código de idioma for especificado, o sistema usará o português como padrão (se disponível).

## Sistema de Templates

O sistema permite personalizar completamente o layout do currículo através de templates. Cada template define o estilo visual e a organização dos elementos.

### Templates Disponíveis

| Nome | Formato | Descrição |
|------|---------|-----------|
| **pdf** | PDF | Template padrão para formato PDF com layout clássico |
| **docx** | DOCX | Template padrão para formato DOCX |
| **moderno** | PDF | Design contemporâneo com cores modernas e quadradinhos para níveis de habilidade |

### Como Funcionam os Templates

Os templates são módulos Python armazenados na pasta `templates/` que seguem a convenção de nomenclatura:
- `template_<formato>.py` para templates padrão
- `template_<formato>_<estilo>.py` para variações de estilo

Cada template deve implementar funções específicas para renderização do documento:

#### Para templates PDF:
- `get_styles()`: Define os estilos de texto e elementos
- `add_title()`: Adiciona cabeçalho com informações pessoais
- `add_section_title()`: Formata títulos de seção
- `add_skill_bar()`: Renderiza indicadores de nível de habilidade
- `add_page_break()`: Insere quebra de página
- `create_document()`: Configura o documento PDF

#### Para templates DOCX:
- `add_title()`: Formata título e dados de contato
- `add_section_title()`: Formata títulos de seção
- `add_skill_bar()`: Cria representação visual para níveis de habilidade
- `add_page_break()`: Insere quebra de página
- `create_document()`: Configura o documento DOCX

### Criando Novos Templates

Você pode criar seus próprios templates simplesmente adicionando um novo arquivo na pasta `templates/` implementando as funções necessárias. O sistema detectará automaticamente o novo template e o disponibilizará na interface de seleção.

## Estrutura de Dados

Os dados do currículo são armazenados em arquivos JSON com a convenção `curriculo_XX.json`, onde `XX` é o código do idioma (pt, en, es, etc.).

### Estrutura Básica

Cada arquivo JSON deve incluir:

```json
{
  "languageName": "Nome do idioma na própria língua",
  
  // Informações pessoais
  "nome": "Nome Completo",  // ou "name", "nombre", etc.
  "email": "email@exemplo.com",
  "telefone": "+XX XX XXXXX-XXXX",  // ou "phone", "telefono", etc.
  "linkedin": "https://linkedin.com/in/usuario",
  
  // Seções do currículo
  "secoes": {  // ou "sections", "secciones", etc.
    // Várias seções específicas para cada idioma
  },
  
  // Nome do arquivo de saída
  "nomeArquivoSaida": "Curriculo_Nome_Completo"  // ou "outputFileName", etc.
}
```

### Exemplos por Idioma

<details>
<summary><b>🇧🇷 Português (curriculo_pt.json)</b></summary>

```json
{
  "languageName": "Português",
  "nome": "Nome Completo",
  "email": "email@exemplo.com",
  "telefone": "+55 11 98765-4321",
  "linkedin": "https://linkedin.com/in/usuario",
  "secoes": {
    "resumoProfissional": { /* conteúdo */ },
    "experienciaProfissional": { /* conteúdo */ },
    "habilidadesTecnicas": { /* conteúdo */ },
    "certificacoes": { /* conteúdo */ },
    "educacao": { /* conteúdo */ },
    "emAndamento": { /* conteúdo */ }
  },
  "nomeArquivoSaida": "Curriculo_Nome_Completo"
}
```
</details>

<details>
<summary><b>🇺🇸 Inglês (curriculo_en.json)</b></summary>

```json
{
  "languageName": "English",
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "+1 555-123-4567",
  "linkedin": "https://linkedin.com/in/user",
  "sections": {
    "professionalSummary": { /* content */ },
    "workExperience": { /* content */ },
    "technicalSkills": { /* content */ },
    "certifications": { /* content */ },
    "education": { /* content */ },
    "inProgress": { /* content */ }
  },
  "outputFileName": "Resume_Full_Name"
}
```
</details>

<details>
<summary><b>🇪🇸 Espanhol (curriculo_es.json)</b></summary>

```json
{
  "languageName": "Español",
  "nombre": "Nombre Completo",
  "email": "email@ejemplo.com",
  "telefono": "+34 612 345 678",
  "linkedin": "https://linkedin.com/in/usuario",
  "secciones": {
    "resumenProfesional": { /* contenido */ },
    "experienciaLaboral": { /* contenido */ },
    "habilidadesTecnicas": { /* contenido */ },
    "certificaciones": { /* contenido */ },
    "educacion": { /* contenido */ },
    "enProgreso": { /* contenido */ }
  },
  "nombreArchivoSalida": "Curriculum_Nombre_Completo"
}
```
</details>

## Estrutura do Projeto

```
curriculum/
├── curriculo_docx.py       # Gerador de formato DOCX
├── curriculo_pdf.py        # Gerador de formato PDF
├── cv-generator.py      # Interface interativa
├── curriculo_pt.json       # Dados em português
├── curriculo_en.json       # Dados em inglês
├── curriculo_es.json       # Dados em espanhol
└── templates/              # Diretório de templates
    ├── __init__.py         # Gerenciador de templates
    ├── template_pdf.py     # Template padrão para PDF
    ├── template_docx.py    # Template padrão para DOCX
    └── template_pdf_moderno.py  # Template moderno para PDF
```

## Adicionando Novos Idiomas

Para adicionar suporte a um novo idioma:

1. Crie um arquivo JSON seguindo o padrão `curriculo_XX.json` (onde XX é o código do idioma)
2. Inclua o campo `languageName` com o nome do idioma na própria língua
3. Estruture as seções do currículo conforme as convenções desse idioma
4. O sistema detectará automaticamente o novo idioma na próxima execução

## Notas Técnicas

- O sistema implementa um mecanismo de "fallback" para campos, permitindo diferentes estruturas JSON entre idiomas
- A seção "Habilidades Técnicas" é automaticamente iniciada em uma nova página
- O template moderno utiliza quadradinhos para representar os níveis de habilidade técnica
- Todas as quebras de página são gerenciadas automaticamente para garantir um layout profissional

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
- Adicionar novos templates
- Implementar suporte a novos idiomas
- Melhorar a formatação dos documentos gerados
- Estender a funcionalidade do sistema

## Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.