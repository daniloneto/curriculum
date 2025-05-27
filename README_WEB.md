# Interface Web - CV Generator

Esta interface web fornece uma maneira fácil e intuitiva de editar arquivos JSON de currículo e gerar PDFs/DOCXs a partir deles.

## Iniciando a Interface Web

Para iniciar a interface web, execute o seguinte comando no terminal:

```bash
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

## Estrutura de Arquivos

- `web/`: Pasta contendo a interface web
  - `app.py`: Arquivo principal da aplicação web
  - `templates/`: Contém os templates HTML
    - `base.html`: Template base com a estrutura comum
    - `edit.html`: Página de edição de JSON
    - `generate.html`: Página de geração de currículos
  - `static/`: Contém arquivos estáticos
    - `css/styles.css`: Estilos da interface
    - `js/`: Scripts JavaScript
      - `edit.js`: Funcionalidades da página de edição
      - `generate.js`: Funcionalidades da página de geração

## Suporte e Dúvidas

Em caso de problemas ou dúvidas:
1. Verifique se todos os arquivos estão na estrutura correta
2. Certifique-se de que todas as dependências Python estão instaladas
3. Consulte o README principal do projeto para mais informações
