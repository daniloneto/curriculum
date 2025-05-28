# Sistema de Geração de Currículos Multilíngue com otimização para ATS e Interface Web

Este projeto é um sistema completo para geração de currículos em formato DOCX e PDF a partir de arquivos JSON estruturados ou dados inseridos via interface web. Oferece suporte para múltiplos idiomas, layouts personalizáveis, e uma interface web amigável para cadastro, edição e geração de currículos.

## Recursos

- **Múltiplos formatos**: Geração de currículos em formato DOCX e PDF (Moderno e Otimizado para ATS).
- **Internacionalização**: Suporte para múltiplos idiomas (Português, Inglês, Espanhol) com arquivos JSON dedicados e formulários dinâmicos.
- **Personalização**: Sistema de templates para layouts diferenciados.
- **Interface Web Interativa (Flask & JavaScript)**:
    - **`/generate` (Gerar Currículo)**: Página principal para selecionar idioma, tipo de currículo (Moderno, ATS, DOCX) e gerar o documento. Utiliza dados do `localStorage` (se disponíveis e preenchidos via `/cadastrar`) ou arquivos JSON de exemplo.
    - **`/cadastrar` (Cadastrar/Editar Currículo)**:
        - Permite ao usuário selecionar o idioma desejado.
        - Carrega dinamicamente um formulário com abas, baseado na estrutura do arquivo JSON de schema correspondente ao idioma (e.g., `web/static/schemas/schema_pt.json`).
        - Cada seção principal do schema (como "Resumo Profissional", "Experiência Laboral") é apresentada em uma aba separada.
        - Campos são gerados dinamicamente.
        - Dados inseridos/editados são salvos no `localStorage` do navegador, associados ao idioma selecionado. Esta página serve tanto para cadastro inicial quanto para edição dos dados já presentes no `localStorage`.
    - **`/edit` (Editar JSON do LocalStorage - Avançado)**: Permite a visualização e edição direta do JSON bruto armazenado no `localStorage` para um idioma específico. Útil para ajustes finos ou correções que não são facilmente realizáveis pelo formulário dinâmico.
- **Interface de Linha de Comando (CLI)**: Menu interativo para seleção de idioma, formato e template para geração de currículos via terminal (legado, mas funcional).
- **Design profissional**: 
  - Fontes elegantes e adequadas para currículos
  - Elementos visuais como ícones e indicadores de nível de habilidade (barras ou quadradinhos)
  - Formatação profissional com seções bem definidas
  - Quebras de página automáticas para melhor organização

## Interface Web - CV Generator

Esta interface web fornece uma maneira fácil e intuitiva de cadastrar, editar dados de currículo e gerar PDFs/DOCXs a partir deles.

### Iniciando a Interface Web

Para iniciar a interface web, execute o seguinte comando na raiz do projeto:

```bash
# Certifique-se de que todas as dependências estão instaladas
pip install -r requirements.txt

# Execute o servidor Flask
python ./web/app.py
```

Após executar este comando, abra seu navegador e acesse:
`http://127.0.0.1:5000/`

### Funcionalidades da Interface Web:

- **`/generate` (Gerar Currículo)**:
    - Página principal para geração de documentos.
    - Selecione o idioma.
    - Escolha o tipo de currículo: PDF Moderno, PDF ATS, ou DOCX.
    - Clique em "Gerar". O sistema usará os dados do `localStorage` para o idioma selecionado (se existirem e tiverem sido preenchidos via `/cadastrar`). Caso contrário, pode recorrer a arquivos JSON de exemplo no servidor.
    - O download do arquivo será iniciado automaticamente.

- **`/cadastrar` (Cadastrar ou Editar Dados do Currículo)**:
    - Selecione o idioma para o qual deseja cadastrar ou editar informações.
    - Um formulário dinâmico com abas será apresentado, baseado no schema JSON do idioma.
        - **Exemplo de Abas**: "Dados Pessoais", "Resumo Profissional", "Experiência Laboral", "Habilidades Técnicas", "Educação", "Certificações", etc.
    - Preencha ou modifique os campos conforme necessário.
    - Ao clicar em "Salvar no Navegador", os dados são armazenados/atualizados no `localStorage` do seu navegador, separados por idioma.
    - Esta é a forma principal e recomendada para inserir e manter os dados do seu currículo.

- **`/edit` (Editar JSON Bruto do LocalStorage - Uso Avançado)**:
    - Permite selecionar um idioma.
    - Visualiza e permite editar diretamente a estrutura JSON que está salva no `localStorage` para aquele idioma.
    - Útil para usuários avançados que precisam fazer modificações que o formulário dinâmico não suporta, ou para inspecionar os dados.
    - Requer conhecimento da estrutura JSON esperada pelo sistema.

### Tecnologias da Interface Web

#### Backend
- **Flask**: Framework web leve e flexível para Python.
- **Flask-CORS**: Extensão para lidar com Cross-Origin Resource Sharing.
- **JSONSchema**: Para validação de estruturas JSON (usado pelos schemas em `web/static/schemas/`).

#### Frontend
- **HTML5/CSS3**: Para a estrutura e estilo da interface.
- **JavaScript (ES6+)**: Para interatividade, manipulação do DOM, chamadas AJAX e gerenciamento do `localStorage`.
    - `cadastro.js`: Lógica principal da página `/cadastrar` (geração de formulário, abas, salvamento no localStorage).
    - `storage.js`: Funções utilitárias para interagir com o `localStorage`.
    - `generate.js`: Lógica da página `/` (geração de currículos).
    - `edit.js`: Lógica da página `/edit` (edição do JSON bruto do localStorage).
- **CodeMirror**: Editor de código com syntax highlighting, usado na página `/edit` para visualização/edição do JSON bruto.
- **Fetch API**: Para comunicação assíncrona com o backend (se necessário, ex: carregar schemas).

### Estrutura de Dados no LocalStorage

Os dados inseridos através da página `/cadastrar` são armazenados no `localStorage` do navegador. Cada idioma tem uma entrada separada, geralmente usando uma chave como `cvData_pt`, `cvData_en`, etc. O conteúdo é uma string JSON que espelha a estrutura esperada pelos scripts geradores de currículo.

---

## Requisitos

### Pré-requisitos
- Python 3.6 ou superior
- pip (gerenciador de pacotes do Python)

### Bibliotecas
- **Para formato DOCX**: `python-docx`
- **Para formato PDF**: `ReportLab`
- **Para interface web**: `Flask`, `Flask-CORS`
- **Utilitários**: `Pillow` (para imagens em PDF), `jsonschema` (para validação de schemas JSON)

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

Isso instalará todas as bibliotecas necessárias para o funcionamento do sistema, incluindo `python-docx`, `reportlab`, `flask`, `flask-cors`, `pillow`, `jsonschema`.

## Gerenciamento de Dependências

O projeto utiliza várias bibliotecas Python para funcionar corretamente. Todas as dependências estão listadas no arquivo `requirements.txt` na raiz do projeto. 

### Principais dependências

1. **Para geração de documentos**:
   - `python-docx`: Manipulação de arquivos DOCX
   - `reportlab`: Criação de PDFs
   - `pillow`: Processamento de imagens para os PDFs (se houver imagens nos templates)

2. **Para a interface web**:
   - `flask`: Framework web
   - `flask-cors`: Suporte a CORS para a API
   - `jsonschema`: Validação dos schemas JSON que definem a estrutura dos formulários dinâmicos

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

### Método Recomendado: Interface Web
Acesse `http://127.0.0.1:5000/` após iniciar o servidor com `python ./web/app.py`.
- Use a página `/cadastrar` para inserir e editar os dados do seu currículo.
- Use a página `/` (Gerar Currículo) para selecionar o idioma, formato e gerar o documento.
- Use a página `/edit` para edições avançadas do JSON armazenado no navegador.

### Método Legado: Interface Interativa (CLI)

A maneira mais simples de usar o sistema é através do menu interativo:

```bash
python cv-generator.py
```

Este comando inicia um assistente que permite escolher:
1. O idioma do currículo (baseado nos arquivos JSON disponíveis)
2. O formato de saída (PDF, DOCX, ou PDF otimizado para ATS)
3. Para PDFs regulares, há uma opção adicional para otimização ATS
4. O template de layout desejado (padrão ou personalizado)

### Uso via Linha de Comando (Legado)

Para usuários avançados, é possível executar os scripts diretamente com parâmetros:

Para gerar o currículo em formato DOCX:
```bash
python ./curriculo_docx.py [CÓDIGO_IDIOMA] [--template NOME_TEMPLATE]
```

Para gerar o currículo em formato PDF:
```bash
python ./curriculo_pdf.py [CÓDIGO_IDIOMA] [--template NOME_TEMPLATE]
```

Para gerar o currículo em formato PDF otimizado para ATS:
```bash
python ./curriculo_pdf_ats.py [CÓDIGO_IDIOMA] [--template NOME_TEMPLATE]
```

#### Parâmetros:
- `CÓDIGO_IDIOMA`: Código de 2 letras do idioma (pt, en, es, etc.)
- `--template NOME_TEMPLATE`: (Opcional) Nome do template a ser utilizado

#### Exemplos:
```bash
python ./curriculo_docx.py pt                     # Português com template padrão
python ./curriculo_pdf.py en                      # Inglês com template padrão
python ./curriculo_pdf.py pt --template pdf_moderno # Português com template moderno
python ./curriculo_pdf_ats.py pt                  # Português com template ATS
```

Se nenhum código de idioma for especificado, os scripts de linha de comando usarão o português como padrão (se o `curriculo_pt.json` existir na raiz).

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

## Estrutura de Dados dos Arquivos JSON (Usados como fallback ou exemplos)

Os dados do currículo podem ser fornecidos por arquivos JSON com a convenção `curriculo_XX.json` na raiz do projeto, onde `XX` é o código do idioma (pt, en, es, etc.). Estes arquivos são usados como fallback pela interface web se não houver dados no `localStorage`, e são a fonte primária para os scripts de linha de comando.

A interface web utiliza **schemas JSON** (localizados em `web/static/schemas/`) para definir a estrutura dos formulários dinâmicos na página `/cadastrar`. Estes schemas podem ser similares em estrutura aos arquivos `curriculo_XX.json`, mas servem a um propósito diferente (definição de formulário vs. dados concretos).

## Estrutura do Projeto

```
cv-generator/
├── curriculo_docx.py       # Gerador DOCX (CLI)
├── curriculo_pdf.py        # Gerador PDF Moderno (CLI)
├── curriculo_pdf_ats.py    # Gerador PDF ATS (CLI)
├── cv-generator.py         # Interface interativa (CLI)
├── requirements.txt        # Lista de dependências Python
├── curriculo_pt.json       # Dados de exemplo em Português
├── curriculo_en.json       # Dados de exemplo em Inglês
├── curriculo_es.json       # Dados de exemplo em Espanhol
├── LICENSE
├── README.md
├── render.yaml
├── wsgi.py                   # Para deploy com Gunicorn
├── templates/              # Templates Python para geradores de documentos
│   ├── __init__.py
│   ├── template_docx.py
│   ├── template_pdf.py
│   ├── template_pdf_moderno.py
│   └── template_pdf_ats.py
└── web/                    # Interface web (Flask)
    ├── app.py              # Aplicação Flask principal
    ├── static/             # Arquivos estáticos
    │   ├── css/
    │   │   └── styles.css
    │   ├── js/
    │   │   ├── cadastro.js   # Lógica da página /cadastrar
    │   │   ├── storage.js    # Utilitários para localStorage
    │   │   ├── generate.js   # Lógica da página / (gerar)
    │   │   └── edit.js       # Lógica da página /edit (JSON bruto)
    │   └── schemas/        # Schemas JSON para formulários dinâmicos
    │       ├── schema_pt.json
    │       ├── schema_en.json
    │       └── schema_es.json
    └── templates/          # Templates HTML (Jinja2)
        ├── base.html
        ├── cadastrar.html  # cadastro/edição via formulário
        ├── edit.html       # Para edição do JSON bruto
        └── generate.html   # Página principal para seleção e geração
```

## Adicionando Novos Idiomas

1.  **Para a Interface Web (`/cadastrar` e `/`):**
    *   Crie um novo arquivo de schema JSON em `web/static/schemas/`, por exemplo, `schema_fr.json` para Francês. Este arquivo define os campos e seções para o formulário dinâmico.
    *   Atualize a lógica em `web/app.py` e nos JavaScripts (`cadastro.js`, `generate.js`) para reconhecer o novo idioma e carregar o schema correspondente.
    *   Forneça traduções para os rótulos da interface, se necessário.

2.  **Para os Scripts de Linha de Comando (Legado) e Fallback da Web:**
    *   Crie um arquivo de dados JSON na raiz do projeto, seguindo o padrão `curriculo_XX.json` (e.g., `curriculo_fr.json`).
    *   Inclua o campo `languageName` com o nome do idioma na própria língua.
    *   Estruture as seções do currículo conforme as convenções desse idioma e os campos esperados pelos scripts `curriculo_*.py`.

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
- Adicionar novos templates de documentos (`templates/`)
- Melhorar os schemas de formulário (`web/static/schemas/`)
- Implementar suporte a novos idiomas (schemas, arquivos JSON de exemplo, e atualizações nos scripts)
- Melhorar a formatação dos documentos gerados
- Estender a funcionalidade do sistema (CLI ou Web)

![Screenshot_22](https://github.com/user-attachments/assets/50d8d192-a68d-46ee-a5ba-79cf012e1616)

## Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
