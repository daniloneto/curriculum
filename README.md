"# Sistema de Geração de Currículos Multilíngue

Este projeto é um sistema completo para geração de currículos em formato DOCX e PDF a partir de arquivos JSON estruturados, com suporte para múltiplos idiomas. Fique livre para incrementar o script.

## Recursos

- Geração de currículos em formato DOCX e PDF
- Suporte para múltiplos idiomas
- Detecção automática de idiomas disponíveis
- Interface de linha de comando para seleção de idioma e formato
- Fonte profissional
- Elementos visuais como ícones e barras de nível de habilidade
- Formatação profissional com seções claras
- Quebras de página automáticas para melhor organização

## Requisitos

### Para o formato DOCX
- Python 3.6+
- python-docx

### Para o formato PDF
- Python 3.6+
- ReportLab

## Instalação

1. Clone este repositório:
```bash
git clone https://github.com/daniloneto/curriculum.git
cd curriculum
```

2. Instale as dependências:
```bash
pip install python-docx reportlab
```

## Uso

### Interface de Linha de Comando

A maneira mais fácil de usar o sistema é através da interface de linha de comando:

```bash
python gerar_curriculo.py
```

Este comando exibirá um menu interativo que permite escolher:
1. O idioma do currículo (baseado nos arquivos JSON disponíveis)
2. O formato de saída (PDF ou DOCX)

### Uso Manual

Também é possível executar os scripts diretamente, especificando o código do idioma:

Para gerar o currículo em formato DOCX:
```bash
python curriculo_docx.py [CÓDIGO_IDIOMA]
```

Para gerar o currículo em formato PDF:
```bash
python curriculo_pdf.py [CÓDIGO_IDIOMA]
```

Exemplos:
```bash
python curriculo_docx.py pt  # Português
python curriculo_pdf.py en   # Inglês
python curriculo_docx.py es  # Espanhol
```

Se nenhum código de idioma for especificado, o sistema usará o português como padrão (se disponível).

## Estrutura de Dados

Os dados do currículo são armazenados em arquivos JSON com a convenção de nomenclatura `curriculo_XX.json`, onde `XX` é o código do idioma (por exemplo, `pt`, `en`, `es`, etc.).

Cada arquivo JSON deve incluir um campo `languageName` para identificar o nome do idioma na interface de usuário:

### Estrutura básica comum a todos os idiomas:

```json
{
  "languageName": "Nome do idioma na própria língua",
  
  // Informações pessoais (os nomes das chaves podem variar por idioma)
  "nome": "Nome Completo",  // ou "name", "nombre", etc.
  "email": "email@exemplo.com",
  "telefone": "xx-xxxx-xxxx",  // ou "phone", "telefono", etc.
  "linkedin": "https://linkedin.com/in/usuario",
  
  // Seções do currículo (os nomes das chaves podem variar por idioma)
  "secoes": {  // ou "sections", "secciones", etc.
    // Várias seções com estrutura específica para cada idioma
  },
  
  // Nome do arquivo de saída
  "nomeArquivoSaida": "Curriculo_Nome_Completo.docx"  // ou "outputFileName", etc.
}
```

### Exemplos para diferentes idiomas:

#### Português (`curriculo_pt.json`):
```json
{
  "languageName": "Português",
  "nome": "Nome Completo",
  "email": "email@exemplo.com",
  "telefone": "xx-xxxx-xxxx",
  "linkedin": "https://linkedin.com/in/usuario",
  "secoes": {
    "resumoProfissional": { ... },
    "experienciaProfissional": { ... },
    "habilidadesTecnicas": { ... },
    "certificacoes": { ... },
    "educacao": { ... },
    "emAndamento": { ... }
  },
  "nomeArquivoSaida": "Curriculo_Nome_Completo.docx"
}
```

#### Inglês (`curriculo_en.json`):
```json
{
  "languageName": "English",
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "xx-xxxx-xxxx",
  "linkedin": "https://linkedin.com/in/user",
  "sections": {
    "professionalSummary": { ... },
    "workExperience": { ... },
    "technicalSkills": { ... },
    "certifications": { ... },
    "education": { ... },
    "inProgress": { ... }
  },
  "outputFileName": "Resume_Full_Name.docx"
}
```

#### Espanhol (`curriculo_es.json`):
```json
{
  "languageName": "Español",
  "nombre": "Nombre Completo",
  "email": "email@ejemplo.com",
  "telefono": "xx-xxxx-xxxx",
  "linkedin": "https://linkedin.com/in/usuario",
  "secciones": {
    "resumenProfesional": { ... },
    "experienciaLaboral": { ... },
    "habilidadesTecnicas": { ... },
    "certificaciones": { ... },
    "educacion": { ... },
    "enProgreso": { ... }
  },
  "nombreArchivoSalida": "Curriculum_Nombre_Completo.docx"
}
```

## Arquivos do Projeto

- `curriculo_docx.py`: Script para geração de currículo em formato DOCX
- `curriculo_pdf.py`: Script para geração de currículo em formato PDF
- `gerar_curriculo.py`: Interface de linha de comando para geração de currículos
- `curriculo_pt.json`: Dados do currículo em português
- `curriculo_en.json`: Dados do currículo em inglês
- `curriculo_es.json`: Dados do currículo em espanhol (exemplo)

## Adicionando Novos Idiomas

Para adicionar um novo idioma:

1. Crie um novo arquivo JSON seguindo a convenção `curriculo_XX.json`, onde XX é o código do idioma.
2. Inclua o campo `languageName` com o nome do idioma na própria língua.
3. Estruture as seções do currículo de acordo com as convenções do idioma, mas mantenha a estrutura hierárquica geral.
4. Os scripts detectarão automaticamente o novo idioma e o incluirão nas opções disponíveis.

## Notas Sobre a Implementação

- A seção "Habilidades Técnicas" sempre começa em uma nova página
- O sistema detecta automaticamente os idiomas disponíveis baseados nos arquivos JSON presentes no diretório
- A implementação usa uma estratégia de fallback, tentando várias chaves possíveis para cada campo, o que permite flexibilidade nas estruturas JSON entre diferentes idiomas