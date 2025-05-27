// JavaScript para a página de edição
document.addEventListener('DOMContentLoaded', function() {    
    const languageSelect = document.getElementById('language-select');
    const jsonEditor = document.getElementById('json-editor');
    const saveButton = document.getElementById('save-button');
    // Remover referência ao formatButton
    const validateButton = document.getElementById('validate-button');    
    const alertBox = document.getElementById('alert-box');
    const jsonStats = document.getElementById('json-stats');
    const cursorInfo = document.getElementById('cursor-info');
    const validationResults = document.getElementById('validation-results');
    let editor; // Variável para o editor CodeMirror
    let currentLanguage = '';    
    let hoverMarker = null;
    let tooltipElement = null;
    let currentSchema = null;
    let ajv = null;
    let validateFn = null;
    let errorMarkers = [];
    
    // Inicializar o validador de schema
    try {
        // Ajv 6.x tem uma sintaxe diferente da 8.x
        ajv = new Ajv({allErrors: true, verbose: true, jsonPointers: true});
    } catch (e) {
        console.error("Erro ao inicializar validador AJV:", e);
    }
    
    // Inicializar o editor CodeMirror
    editor = CodeMirror(document.getElementById('codemirror-editor'), {
        mode: { name: "javascript", json: true },
        theme: "dracula",
        lineNumbers: true,
        lineWrapping: true,
        matchBrackets: true,
        autoCloseBrackets: true,
        tabSize: 2,
        gutters: ["CodeMirror-lint-markers", "CodeMirror-linenumbers", "CodeMirror-foldgutter"],
        lint: {
            esversion: 11,
            asi: true
        },
        readOnly: true,        
        extraKeys: {
            "Ctrl-Space": "autocomplete",
            "Ctrl-Q": function(cm) { cm.foldCode(cm.getCursor()); },
            "Alt-F": "findPersistent",
            "Ctrl-F": "findPersistent",
            // Remover atalho de formatação
            "Ctrl-Shift-V": function(cm) { validateJson(); },
        },
        styleActiveLine: true,
        foldGutter: true,
        indentWithTabs: false,
        indentUnit: 2,
        highlightSelectionMatches: {showToken: /\w/, annotateScrollbar: true},
        scrollbarStyle: "overlay"
    });

    // Adicionar o evento de hover para mostrar tooltips nas chaves JSON
    editor.on("mouseover", function(cm, event) {
        if (!event.target.classList.contains('cm-property')) return;
        
        // Limpar tooltip anterior, se existir
        if (tooltipElement) {
            document.body.removeChild(tooltipElement);
            tooltipElement = null;
        }
        
        // Obter a chave sob o cursor
        const pos = cm.coordsChar({left: event.clientX, top: event.clientY});
        const token = cm.getTokenAt(pos);
        if (!token.type || !token.type.includes('property')) return;
        
        const key = token.string.replace(/"/g, '');
        
        // Encontrar o valor correspondente (isso é simplificado e pode não funcionar para estruturas complexas)
        try {
            const json = JSON.parse(cm.getValue());
            let description = '';
            
            // Se temos um schema, verificar se há descrição para esta chave
            if (currentSchema && currentSchema.properties && currentSchema.properties[key]) {
                description = currentSchema.properties[key].description || '';
            } else if (key.length > 0) {
                // Caso contrário, tentar determinar o tipo do valor
                const value = json[key];
                const type = Array.isArray(value) ? 'array' : typeof value;
                description = `Tipo: ${type}`;
                
                // Para arrays, mostrar o tamanho
                if (Array.isArray(value)) {
                    description += `, ${value.length} item(s)`;
                }
            }
            
            // Criar tooltip
            tooltipElement = document.createElement('div');
            tooltipElement.className = 'CodeMirror-hover';
            tooltipElement.textContent = description || key;
            
            // Posicionar tooltip
            const coords = cm.charCoords(pos);
            tooltipElement.style.left = (coords.left) + 'px';
            tooltipElement.style.top = (coords.top - 25) + 'px';
            
            document.body.appendChild(tooltipElement);
        } catch (e) {
            // Se não conseguir analisar o JSON, não mostrar nada
            return;
        }
    });
    
    // Remover tooltip quando o mouse sair do editor
    editor.on("mouseout", function() {
        if (tooltipElement) {
            document.body.removeChild(tooltipElement);
            tooltipElement = null;
        }
    });
    
    // Atualizar o valor do textarea quando o editor mudar
    editor.on('change', function() {
        jsonEditor.value = editor.getValue();
        updateJsonStats();
    });
    
    // Carregar o conteúdo do JSON quando um idioma for selecionado
    languageSelect.addEventListener('change', function() {
        currentLanguage = languageSelect.value;        
        if (currentLanguage) {
            fetchJsonContent(currentLanguage);
        } else {
            editor.setValue('');
            editor.setOption('readOnly', true);
            saveButton.disabled = true;
            // Remover formatButton.disabled = true;
            validateButton.disabled = true;
            validationResults.style.display = 'none';
        }
    });
    
    // Função para buscar o conteúdo do JSON
    function fetchJsonContent(language) {        
        // Mostrar indicador de carregamento
        editor.setValue('Carregando...');
        editor.setOption('readOnly', true);
        saveButton.disabled = true;
        // Remover formatButton.disabled = true;
        validateButton.disabled = true;
        validationResults.style.display = 'none';
        
        // Limpar marcadores de erro
        clearErrorMarkers();            
        // Carregar o schema correspondente ao idioma
        fetch(`/schemas/${language}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Schema não encontrado para o idioma ${language}`);
                }
                return response.json();
            })
            .then(schema => {
                currentSchema = schema;
                
                // Compilar o validador
                if (ajv) {
                    try {
                        validateFn = ajv.compile(schema);
                        console.log(`Schema para ${language} carregado com sucesso`);
                    } catch (e) {
                        console.error(`Erro ao compilar schema para ${language}:`, e);
                        showAlert(`Erro ao compilar schema para validação: ${e.message}`, 'danger');
                    }
                }
                
                // Agora buscar o conteúdo do JSON
                return fetch('/get_json_content', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ language: language })
                });
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showAlert(data.error, 'danger');
                    editor.setValue('');
                } else {
                    // Formatar o JSON para exibição
                    const prettyJson = JSON.stringify(data.content, null, 2);
                    editor.setValue(prettyJson);                    
                    editor.setOption('readOnly', false);
                    saveButton.disabled = false;
                    // Remover formatButton.disabled = false;
                    validateButton.disabled = false;
                    
                    // Executar o linting
                    setTimeout(() => {
                        editor.performLint();
                    }, 100);
                    
                    updateJsonStats();
                }
            })
            .catch(error => {
                showAlert('Erro ao carregar o arquivo: ' + error, 'danger');
                editor.setValue('');
                editor.setOption('readOnly', true);
                saveButton.disabled = true;
                // Remover formatButton.disabled = true;
                validateButton.disabled = true;
            });
    }
    
    // Atualizar estatísticas do JSON
    function updateJsonStats() {
        try {
            const content = editor.getValue();
            const jsonObj = JSON.parse(content);
            
            // Contar propriedades de primeiro nível
            const topLevelProps = Object.keys(jsonObj).length;
            
            // Contar total de propriedades recursivamente
            let totalProps = 0;
            let nestedObjects = 0;
            let nestedArrays = 0;
            
            function countProps(obj) {
                if (Array.isArray(obj)) {
                    nestedArrays++;
                    obj.forEach(item => {
                        if (typeof item === 'object' && item !== null) {
                            countProps(item);
                        }
                    });
                } else if (typeof obj === 'object' && obj !== null) {
                    const keys = Object.keys(obj);
                    totalProps += keys.length;
                    
                    keys.forEach(key => {
                        if (typeof obj[key] === 'object' && obj[key] !== null) {
                            nestedObjects++;
                            countProps(obj[key]);
                        }
                    });
                }
            }
            
            countProps(jsonObj);
            
            jsonStats.innerHTML = `Propriedades: ${topLevelProps} (total: ${totalProps}) | Objetos: ${nestedObjects} | Arrays: ${nestedArrays}`;
        } catch (e) {
            jsonStats.innerHTML = 'JSON inválido';
        }
    }
    
    // Atualizar informações da posição do cursor
    editor.on('cursorActivity', function() {
        const cursor = editor.getCursor();
        const token = editor.getTokenAt(cursor);
        const lineContent = editor.getLine(cursor.line);
        
        // Identificar o tipo de token sob o cursor
        let tokenType = 'texto';
        if (token.type) {
            if (token.type.includes('property')) tokenType = 'chave';
            else if (token.type.includes('string')) tokenType = 'texto';
            else if (token.type.includes('number')) tokenType = 'número';
            else if (token.type.includes('atom') && (token.string === 'true' || token.string === 'false')) tokenType = 'booleano';
            else if (token.type.includes('atom') && token.string === 'null') tokenType = 'nulo';
            else if (token.type.includes('bracket')) tokenType = token.string === '{' || token.string === '}' ? 'objeto' : 'array';
        }
        
        // Adicionar classes especiais para null e boolean (para colorir diferente)
        if (tokenType === 'booleano') {
            editor.addOverlay({
                token: function(stream) {
                    if (stream.match(/true|false/, true)) return "json-boolean";
                    stream.next();
                    return null;
                }
            });
        } else if (tokenType === 'nulo') {
            editor.addOverlay({
                token: function(stream) {
                    if (stream.match(/null/, true)) return "json-null";
                    stream.next();
                    return null;
                }
            });
        }
        
        cursorInfo.innerHTML = `Linha: ${cursor.line + 1}, Coluna: ${cursor.ch + 1} | Tipo: ${tokenType}`;
    });
    
    // Manter apenas a função de validação
    function validateJson() {
        const editor = window.editor;
        const jsonContent = editor.getValue();
        const selectedLanguage = document.getElementById('language-select').value;
        
        // Verificar se um idioma está selecionado
        if (!selectedLanguage) {
            showAlert("Por favor, selecione um idioma primeiro.");
            return;
        }
        
        try {
            // Tentar analisar o JSON
            const parsedJson = JSON.parse(jsonContent);
            
            // Limpar erros anteriores
            clearErrorMarkers();
            
            // Buscar o schema de validação para este idioma
            fetch(`/schemas/${selectedLanguage}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(schema => {
                    console.log("Schema carregado:", schema);
                    
                    // Validar com Ajv
                    const ajv = new Ajv({allErrors: true});
                    const validate = ajv.compile(schema);
                    const valid = validate(parsedJson);
                    
                    const validateButton = document.getElementById('validate-button');
                    
                    if (valid) {
                        validateButton.classList.add('valid');
                        validateButton.classList.remove('invalid');
                        showValidationResults([], true);
                    } else {
                        validateButton.classList.add('invalid');
                        validateButton.classList.remove('valid');
                        showValidationResults(validate.errors, false);
                    }
                })
                .catch(error => {
                    console.error("Erro ao buscar schema:", error);
                    showAlert("Schema de validação não disponível para este idioma");
                });
        } catch (e) {
            console.error("Erro ao analisar JSON:", e);
            showAlert("JSON inválido: " + e.message);
        }
    }
    
    // Validar JSON contra o schema
    validateButton.addEventListener('click', function() {
        try {
            const content = editor.getValue();
            const jsonObj = JSON.parse(content);
            
            // Limpar marcadores de erro anteriores
            clearErrorMarkers();
            
            // Verificar se temos o validador e o schema
            if (!validateFn || !currentSchema) {
                showAlert('Schema de validação não disponível para este idioma', 'danger');
                return;
            }
            
            // Executar a validação
            const valid = validateFn(jsonObj);
              if (valid) {
                // JSON válido de acordo com o schema
                validationResults.innerHTML = '<div class="validation-success">O JSON é válido e atende a todos os requisitos do schema.</div>';
                validationResults.style.display = 'block';
                validateButton.classList.add('valid');
                validateButton.classList.remove('invalid');
                
                // Limpar mensagem após alguns segundos
                setTimeout(() => {
                    validationResults.style.display = 'none';
                    validateButton.classList.remove('valid');
                }, 5000);
            } else {
                // JSON inválido - mostrar erros
                validateButton.classList.add('invalid');
                validateButton.classList.remove('valid');
                
                const errors = validateFn.errors || [];
                
                let errorHtml = '<div class="validation-error">';
                errorHtml += `<div><span class="error-count">${errors.length}</span><strong>Erro${errors.length > 1 ? 's' : ''} de validação encontrado${errors.length > 1 ? 's' : ''}:</strong></div>`;
                
                // Formatar mensagens de erro
                errors.forEach((error, index) => {
                    const path = error.instancePath || '';
                    const property = error.params.missingProperty ? `"${error.params.missingProperty}"` : 
                                    error.params.additionalProperty ? `"${error.params.additionalProperty}"` : '';
                    const message = error.message || '';
                    
                    // Determinar o tipo de erro
                    let errorType = 'Erro';
                    if (error.keyword === 'required') errorType = 'Obrigatório';
                    else if (error.keyword === 'type') errorType = 'Tipo Inválido';
                    else if (error.keyword === 'format') errorType = 'Formato';
                    else if (error.keyword === 'pattern') errorType = 'Padrão';
                    else if (error.keyword === 'enum') errorType = 'Valor';
                    else if (error.keyword === 'additionalProperties') errorType = 'Prop. Adicional';
                    
                    // Formatar o caminho para facilitar a leitura
                    const displayPath = path.replace(/^\//, '').replace(/\//g, '.') || 'raiz';
                    
                    errorHtml += `<div class="error-detail">
                        <span class="error-type">${errorType}</span>
                        <strong>${displayPath}</strong> ${property ? `propriedade: ${property}` : ''} 
                        <span>${message}</span>
                    </div>`;
                    
                    // Tentar encontrar a linha correspondente ao erro
                    highlightErrorInEditor(path, property, error);
                });
                
                errorHtml += '</div>';
                validationResults.innerHTML = errorHtml;
                validationResults.style.display = 'block';
            }
        } catch (e) {
            showAlert('Erro ao validar JSON: ' + e.message, 'danger');
        }
    });
      // Função para limpar marcadores de erro
    function clearErrorMarkers() {
        errorMarkers.forEach(marker => marker.clear());
        errorMarkers = [];
        
        // Limpar todos os marcadores do gutter
        for (let i = 0; i < editor.lineCount(); i++) {
            editor.setGutterMarker(i, 'CodeMirror-lint-markers', null);
        }
        
        validateButton.classList.remove('valid', 'invalid');
        validationResults.style.display = 'none';
    }
      // Função para destacar erros no editor
    function highlightErrorInEditor(path, property, error) {
        try {
            const content = editor.getValue();
            const lines = content.split('\n');
            
            // Caminho normalizado para pesquisa
            const searchPath = path.replace(/^\//, '').replace(/\//g, '.');
            const searchProperty = property.replace(/"/g, '');
            
            let found = false;
            
            // Primeiro, tentar uma correspondência exata do caminho
            if (searchPath || searchProperty) {
                for (let i = 0; i < lines.length; i++) {
                    const line = lines[i];
                    
                    // Verificar se a linha contém o caminho ou propriedade
                    const containsPath = searchPath && line.includes(`"${searchPath.split('.').pop()}"`);
                    const containsProperty = searchProperty && line.includes(`"${searchProperty}"`);
                    
                    if (containsPath || containsProperty) {
                        // Marcar a linha com erro
                        const marker = editor.markText(
                            {line: i, ch: 0},
                            {line: i, ch: line.length},
                            {className: 'cm-error-line'}
                        );
                        
                        errorMarkers.push(marker);
                        
                        // Adicionar marcador no gutter
                        const errorMarkerElement = document.createElement('div');
                        errorMarkerElement.className = 'cm-error-marker';
                        errorMarkerElement.title = error.message || 'Erro de validação';
                        editor.setGutterMarker(i, 'CodeMirror-lint-markers', errorMarkerElement);
                        
                        // Se for o primeiro erro, rolar para ele
                        if (errorMarkers.length === 1) {
                            editor.scrollIntoView({line: Math.max(0, i-2), ch: 0}, 100);
                        }
                        
                        found = true;
                        break;
                    }
                }
            }
            
            // Se não encontrou por correspondência exata, tente encontrar seções relevantes
            if (!found && error.keyword === 'required') {
                const parentPath = searchPath.split('.').slice(0, -1).join('.');
                
                for (let i = 0; i < lines.length; i++) {
                    const line = lines[i];
                    
                    // Verificar se a linha corresponde ao objeto pai onde falta a propriedade
                    if (parentPath && line.includes(`"${parentPath.split('.').pop()}"`)) {
                        // Encontrar o escopo do objeto (abertura e fechamento de chaves)
                        let openBraces = 0;
                        let closeBraces = 0;
                        let startLine = i;
                        let endLine = i;
                        
                        // Procurar a abertura de chaves
                        for (let j = i; j < lines.length; j++) {
                            if (lines[j].includes('{')) {
                                openBraces++;
                                endLine = j;
                                break;
                            }
                        }
                        
                        // Procurar o fechamento correspondente
                        for (let j = endLine + 1; j < lines.length; j++) {
                            if (lines[j].includes('{')) openBraces++;
                            if (lines[j].includes('}')) closeBraces++;
                            
                            if (openBraces === closeBraces) {
                                endLine = j;
                                break;
                            }
                        }
                        
                        // Marcar todo o objeto
                        const marker = editor.markText(
                            {line: startLine, ch: 0},
                            {line: endLine, ch: lines[endLine].length},
                            {className: 'cm-error-line'}
                        );
                        
                        errorMarkers.push(marker);
                        
                        // Rolar para o início do objeto
                        if (errorMarkers.length === 1) {
                            editor.scrollIntoView({line: Math.max(0, startLine-2), ch: 0}, 100);
                        }
                        
                        found = true;
                        break;
                    }
                }
            }
            
            // Se ainda não encontrou, tente outras estratégias
            if (!found) {
                // Para erros de tipo, tente encontrar o valor com tipo incorreto
                if (error.keyword === 'type') {
                    const fieldName = searchPath.split('.').pop();
                    
                    for (let i = 0; i < lines.length; i++) {
                        if (lines[i].includes(`"${fieldName}"`)) {
                            // Marcar a linha
                            const marker = editor.markText(
                                {line: i, ch: 0},
                                {line: i, ch: lines[i].length},
                                {className: 'cm-error-line'}
                            );
                            
                            errorMarkers.push(marker);
                            
                            if (errorMarkers.length === 1) {
                                editor.scrollIntoView({line: Math.max(0, i-2), ch: 0}, 100);
                            }
                            
                            break;
                        }
                    }
                }
            }
        } catch (e) {
            console.error('Erro ao destacar erro no editor:', e);
        }
    }
    
    // Salvar o JSON quando o botão for clicado
    saveButton.addEventListener('click', function() {
        const jsonContent = editor.getValue();
        
        if (!currentLanguage || !jsonContent) {
            showAlert('Selecione um idioma e insira o conteúdo JSON', 'danger');
            return;
        }
        
        // Verificar se o JSON é válido
        try {
            const jsonObj = JSON.parse(jsonContent);
            
            // Validar contra o schema
            if (validateFn) {
                const valid = validateFn(jsonObj);
                if (!valid) {
                    const shouldProceed = confirm('O JSON contém erros de validação. Deseja salvar mesmo assim?');
                    if (!shouldProceed) {
                        validateButton.click(); // Mostrar erros
                        return;
                    }
                }
            }
            
            // Enviar o JSON para o servidor
            fetch('/save_json', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    language: currentLanguage,
                    content: jsonContent
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showAlert(data.error, 'danger');
                } else {
                    showAlert(data.message, 'success');
                }
            })
            .catch(error => {
                showAlert('Erro ao salvar o arquivo: ' + error, 'danger');
            });
        } catch (e) {
            showAlert('JSON inválido: ' + e.message, 'danger');
            return;
        }
    });   
   

    // Limpar erro quando idioma mudar
    languageSelect.addEventListener('change', function() {
        clearErrorMarkers();
    });
    
    // Função para exibir alertas
    function showAlert(message, type) {
        alertBox.innerHTML = message;
        alertBox.className = `alert alert-${type}`;
        alertBox.style.display = 'block';
        
        // Esconder a mensagem após 5 segundos
        setTimeout(function() {
            alertBox.style.display = 'none';
        }, 5000);
    }
    
    // Trigger change event to load JSON if language is pre-selected
    if (languageSelect.value) {
        languageSelect.dispatchEvent(new Event('change'));
    }

    // Remover o atalho de teclado para formatar o JSON (Ctrl+Shift+F)
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'V') {
            e.preventDefault();
            if (!validateButton.disabled) {
                validateButton.click();
            }
        }
    });
});
