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
pip install -r requirements.txt
```

Isso instalará todas as bibliotecas necessárias para o funcionamento do sistema, incluindo:
- python-docx: Para geração de arquivos DOCX
- reportlab: Para geração de arquivos PDF
- flask: Para a interface web
- Outras bibliotecas auxiliares

## Gerenciamento de Dependências

O projeto utiliza várias bibliotecas Python para funcionar corretamente. Todas as dependências estão listadas no arquivo `requirements.txt` na raiz do projeto. 

### Principais dependências

1. **Para geração de documentos**:
   - `python-docx`: Manipulação de arquivos DOCX
   - `reportlab`: Criação de PDFs
   - `pillow`: Processamento de imagens para os PDFs

2. **Para a interface web**:
   - `flask`: Framework web
   - `flask-cors`: Suporte a CORS para a API
   - `jsonschema`: Validação de JSON

### Atualizando dependências

Se você precisar atualizar as dependências ou adicionar novas bibliotecas:

1. Adicione a biblioteca ao arquivo `requirements.txt`
2. Execute o comando:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

### Ambientes virtuais

Para evitar conflitos com outras aplicações Python, é recomendável utilizar um ambiente virtual:

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

# Instalar dependências no ambiente virtual
pip install -r requirements.txt
```

## Uso

### Método Recomendado: Interface Interativa

A maneira mais simples de usar o sistema é através do menu interativo:

```bash
python cv-generator.py
```

Este comando inicia um assistente que permite escolher:
1. O idioma do currículo (baseado nos arquivos JSON disponíveis)
2. O formato de saída (PDF, DOCX, ou PDF otimizado para ATS)
3. Para PDFs regulares, há uma opção adicional para otimização ATS
4. O template de layout desejado (padrão ou personalizado)

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

Para gerar o currículo em formato PDF otimizado para ATS:
```bash
python curriculo_pdf_ats.py [CÓDIGO_IDIOMA] [--template NOME_TEMPLATE]
```

#### Parâmetros:
- `CÓDIGO_IDIOMA`: Código de 2 letras do idioma (pt, en, es, etc.)
- `--template NOME_TEMPLATE`: (Opcional) Nome do template a ser utilizado

#### Exemplos:
```bash
python curriculo_docx.py pt                     # Português com template padrão
python curriculo_pdf.py en                      # Inglês com template padrão
python curriculo_pdf.py pt --template pdf_moderno # Português com template moderno
python curriculo_pdf_ats.py pt                  # Português com template ATS
```

Se nenhum código de idioma for especificado, o sistema usará o português como padrão (se disponível).

### Interface Web

Para uma experiência mais amigável, você pode iniciar a interface web:

```bash
# Certifique-se de que todas as dependências estão instaladas
pip install -r requirements.txt

# navegue até a pasta web e execute:
cd web
python app.py
```

Após executar este comando, acesse http://localhost:5000 no seu navegador para utilizar a interface web.

A interface web oferece duas funcionalidades principais:

1. **Edição de Arquivos JSON**: Permite selecionar e editar qualquer arquivo de currículo em formato JSON.
   - Selecione o idioma desejado no menu dropdown
   - Edite o conteúdo do JSON
   - Clique em "Salvar" para salvar as alterações

2. **Geração de Currículos**: Permite gerar facilmente currículos em diferentes formatos.
   - Selecione o idioma desejado
   - Escolha o formato (PDF, PDF otimizado para ATS, ou DOCX)
   - Clique em "Gerar" para criar o arquivo
   - O download do arquivo será iniciado automaticamente

Esta interface simplifica o processo de edição e geração de currículos, especialmente para usuários menos familiarizados com linha de comando.

## Sistema de Templates

O sistema permite personalizar completamente o layout do currículo através de templates. Cada template define o estilo visual e a organização dos elementos.

### Templates Disponíveis

| Nome | Formato | Descrição |
|------|---------|-----------|
| **pdf** | PDF | Template padrão para formato PDF com layout clássico |
| **docx** | DOCX | Template padrão para formato DOCX |
| **pdf_moderno** | PDF | Design contemporâneo com cores modernas e quadradinhos para níveis de habilidade |
| **pdf_ats** | PDF | Otimizado para Applicant Tracking Systems (ATS) brasileiros |

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

## Template ATS Otimizado

O template ATS (Applicant Tracking System) foi desenvolvido especificamente para maximizar a compatibilidade com sistemas de rastreamento de currículos utilizados por empresas brasileiras durante processos seletivos.

### O que é um ATS?

ATS (Applicant Tracking System) é um software usado por recrutadores para organizar, pesquisar e filtrar currículos de candidatos. Estes sistemas geralmente:

- Analisam o texto do currículo procurando palavras-chave relevantes
- Classificam candidatos com base na correspondência com os requisitos da vaga
- Podem rejeitar automaticamente currículos que não atendem a critérios mínimos

### Recursos do Template ATS

| Característica | Benefício |
|----------------|-----------|
| **Estrutura simplificada** | Facilita a leitura por sistemas automatizados |
| **Formatação limpa** | Evita elementos visuais complexos que podem confundir o ATS |
| **Palavras-chave destacadas** | Aumenta a chance de reconhecimento pelo sistema |
| **Seção dedicada de palavras-chave** | Garante que termos importantes sejam detectados |
| **Rotulagem explícita** | Identifica claramente cada seção (ex: "Cargo:", "Empresa:", "Período:") |
| **Níveis de habilidade textuais** | Usa descrições em vez de representações visuais para níveis |

### Como usar o Template ATS

Você pode gerar um currículo otimizado para ATS de duas maneiras:

1. **Via interface interativa:**
   ```bash
   python cv-generator.py
   ```
   E então selecione o formato PDF e o template "pdf_ats".

2. **Via linha de comando:**
   ```bash
   python curriculo_pdf_ats.py [CÓDIGO_IDIOMA]
   ```

### Melhores Práticas para ATS

Para maximizar suas chances com sistemas ATS:

1. **Use palavras-chave relevantes** extraídas diretamente da descrição da vaga
2. **Mantenha formatos de data consistentes** (ex: MM/AAAA - MM/AAAA)
3. **Evite cabeçalhos e rodapés** com informações importantes
4. **Use seções padrão** reconhecíveis (Experiência, Habilidades, Educação)
5. **Inclua nomes de tecnologias e ferramentas** específicas mencionadas na vaga
6. **Evite abreviações** pouco comuns ou siglas não explicadas

O template ATS deste sistema implementa automaticamente muitas dessas práticas, mas lembre-se de adaptar o conteúdo do seu currículo para cada vaga.

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
cv-generator/
├── curriculo_docx.py       # Gerador de formato DOCX
├── curriculo_pdf.py        # Gerador de formato PDF
├── curriculo_pdf_ats.py    # Gerador de PDF otimizado para ATS
├── cv-generator.py         # Interface interativa de linha de comando
├── requirements.txt        # Lista de dependências do projeto
├── curriculo_pt.json       # Dados em português
├── curriculo_en.json       # Dados em inglês
├── curriculo_es.json       # Dados em espanhol
├── templates/              # Diretório de templates para geração de documentos
│   ├── __init__.py         # Gerenciador de templates
│   ├── template_pdf.py     # Template padrão para PDF
│   ├── template_docx.py    # Template padrão para DOCX
│   ├── template_pdf_moderno.py  # Template moderno para PDF
│   └── template_pdf_ats.py # Template otimizado para ATS
└── web/                    # Interface web
    ├── app.py              # Aplicação Flask principal
    ├── static/             # Arquivos estáticos
    │   ├── css/            # Estilos CSS
    │   │   └── styles.css  # Folha de estilos principal
    │   ├── js/             # Scripts JavaScript
    │   │   ├── edit_new.js # Funções para edição de JSON
    │   │   └── generate.js # Funções para geração de currículos
    │   └── schemas/        # Schemas JSON para validação
    │       ├── schema_pt.json
    │       ├── schema_en.json
    │       └── schema_es.json
    └── templates/          # Templates HTML
        ├── base.html       # Template base com estrutura comum
        ├── edit.html       # Página de edição de JSON
        └── generate.html   # Página de geração de currículos
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

![Screenshot_22](https://github.com/user-attachments/assets/50d8d192-a68d-46ee-a5ba-79cf012e1616)

# Interface Web - CV Generator

Esta interface web fornece uma maneira fácil e intuitiva de editar arquivos JSON de currículo e gerar PDFs/DOCXs a partir deles.

## Iniciando a Interface Web

Para iniciar a interface web, execute o seguinte comando no terminal:

```bash
# Certifique-se de que todas as dependências estão instaladas
pip install -r requirements.txt

# Navegue até a pasta web e execute:
cd web
python app.py
```

Após executar este comando, abra seu navegador e acesse:
http://localhost:5000 ou http://127.0.0.1:5000

## Funcionalidades

A interface web possui duas funcionalidades principais:

### 1. Edição de Arquivos JSON

Na página de edição, você pode:

- Selecionar um arquivo JSON de currículo para editar através do menu dropdown
- Visualizar e editar o conteúdo completo do JSON em um editor de texto
- Salvar as alterações feitas no arquivo

Dicas para edição:
- Mantenha a estrutura JSON intacta para evitar erros de formatação
- Não remova campos-chave como "languageName", "nome", etc.
- Você pode adicionar novos campos conforme necessário, seguindo a estrutura existente

### 2. Geração de Currículos

Na página de geração, você pode:

- Selecionar o idioma do currículo (baseado nos arquivos JSON disponíveis)
- Escolher o formato desejado:
  - PDF (diferentes estilos disponíveis)
  - PDF otimizado para ATS (Applicant Tracking Systems)
  - DOCX (documento Word)
- Gerar o currículo com um clique
- O arquivo será gerado e baixado automaticamente

## Tecnologias da Interface Web

A interface web utiliza as seguintes tecnologias:

### Backend
- **Flask**: Framework web leve e flexível para Python
- **Flask-CORS**: Extensão para lidar com Cross-Origin Resource Sharing
- **JSONSchema**: Para validação de estruturas JSON

### Frontend
- **HTML5/CSS3**: Para a estrutura e estilo da interface
- **JavaScript (ES6+)**: Para interatividade
- **CodeMirror**: Editor de código usado para editar os arquivos JSON
- **Fetch API**: Para comunicação com o backend

### Recursos
- **Edição de JSON com syntax highlighting**: Facilita a visualização e edição do conteúdo
- **Validação em tempo real**: Verifica erros de sintaxe JSON
- **Visualização instantânea**: Prévia do documento gerado
- **Interface responsiva**: Adaptável a diferentes tamanhos de tela

## Personalização da Interface Web

Você pode personalizar a interface web editando os seguintes arquivos:

- **`web/static/css/styles.css`**: Para mudar o visual da interface
- **`web/templates/*.html`**: Para modificar a estrutura HTML
- **`web/static/js/*.js`**: Para alterar o comportamento JavaScript

## Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
