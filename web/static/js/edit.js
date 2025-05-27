// JavaScript para a página de edição
document.addEventListener('DOMContentLoaded', function() {
    const languageSelect = document.getElementById('language-select');
    const jsonEditor = document.getElementById('json-editor');
    const saveButton = document.getElementById('save-button');
    const formatButton = document.getElementById('format-button');
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
    
    // Inicializar o validador de schema
    try {
        ajv = new Ajv({allErrors: true});
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
        
        // Limpar highlight anterior, se existir
        if (hoverMarker) {
            hoverMarker.clear();
            hoverMarker = null;
        }
        
        // Criar tooltip
        const keyText = event.target.textContent;
        tooltipElement = document.createElement('div');
        tooltipElement.className = 'CodeMirror-hover';
        tooltipElement.textContent = 'Chave JSON: ' + keyText;
        
        // Posicionar tooltip
        const rect = event.target.getBoundingClientRect();
        tooltipElement.style.top = (rect.top - 25) + 'px';
        tooltipElement.style.left = rect.left + 'px';
        
        document.body.appendChild(tooltipElement);
        
        // Destacar o par chave-valor atual
        const pos = cm.coordsChar({left: rect.left, top: rect.top}, "page");
        const token = cm.getTokenAt(pos);
        if (token && token.type && token.type.includes('property')) {
            const line = pos.line;
            const startChar = token.start;
            const lineText = cm.getLine(line);
            
            // Encontrar o fim do valor correspondente (pode estar em várias linhas)
            let endLine = line;
            let endChar = lineText.length;
            let searchLine = line;
            let braceCount = 0;
            let foundColon = false;
            
            // Percorrer caracteres para encontrar o final do valor
            while (searchLine < cm.lineCount()) {
                const lineContent = cm.getLine(searchLine);
                for (let i = (searchLine === line ? token.end : 0); i < lineContent.length; i++) {
                    const char = lineContent[i];
                    if (!foundColon && char === ':') {
                        foundColon = true;
                    } else if (foundColon) {
                        if (char === '{' || char === '[') braceCount++;
                        else if (char === '}' || char === ']') braceCount--;
                        else if ((char === ',' || char === '}' || char === ']') && braceCount <= 0) {
                            endLine = searchLine;
                            endChar = i;
                            searchLine = cm.lineCount(); // Sair do loop externo
                            break;
                        }
                    }
                }
                searchLine++;
            }
            
            // Criar marker para destacar o par chave-valor
            hoverMarker = cm.markText(
                {line: line, ch: startChar},
                {line: endLine, ch: endChar},
                {className: 'json-pair-highlight', css: 'background-color: rgba(255,255,255,0.1); border-radius: 3px;'}
            );
        }
    });
    
    // Remover o tooltip quando o mouse sair
    editor.on("mouseout", function() {
        if (tooltipElement) {
            document.body.removeChild(tooltipElement);
            tooltipElement = null;
        }
        
        if (hoverMarker) {
            hoverMarker.clear();
            hoverMarker = null;
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
            formatButton.disabled = true;
        }
    });
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
                
                let errorHtml = '<div class="validation-error">';
                errorHtml += '<strong>Erros de validação:</strong>';
                errorHtml += '<pre>';
                
                // Formatar mensagens de erro
                validateFn.errors.forEach((error, index) => {
                    const path = error.instancePath || '';
                    const property = error.params.missingProperty ? `"${error.params.missingProperty}"` : 
                                    error.params.additionalProperty ? `"${error.params.additionalProperty}"` : '';
                    const message = error.message || '';
                    
                    errorHtml += `${index + 1}. ${path} ${property} ${message}\n`;
                    
                    // Tentar encontrar a linha correspondente ao erro
                    highlightErrorInEditor(path, property, error);
                });
                
                errorHtml += '</pre></div>';
                validationResults.innerHTML = errorHtml;
                validationResults.style.display = 'block';
            }
        } catch (e) {
            showAlert('Erro ao validar JSON: ' + e.message, 'danger');
        }
    });
    
    // Função para buscar o conteúdo do JSON    function fetchJsonContent(language) {
        // Mostrar indicador de carregamento
        editor.setValue('Carregando...');
        editor.setOption('readOnly', true);
        saveButton.disabled = true;
        formatButton.disabled = true;
        validateButton.disabled = true;
        validationResults.style.display = 'none';
        
        // Carregar o schema correspondente ao idioma
        fetch(`/static/schemas/schema_${language}.json`)
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
                    formatButton.disabled = false;
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
                formatButton.disabled = true;
                validateButton.disabled = true;
            });
                isCompactView = false;
                
                // Executar o linting
                setTimeout(() => {
                    editor.performLint();
                }, 100);
            }
        })
        .catch(error => {
            showAlert('Erro ao carregar o arquivo: ' + error, 'danger');
            editor.setValue('');
            editor.setOption('readOnly', true);
            saveButton.disabled = true;
            formatButton.disabled = true;
            toggleViewButton.disabled = true;
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
    
    // Formatar JSON quando o botão for clicado
    formatButton.addEventListener('click', function() {
        try {
            const content = editor.getValue();
            const jsonObj = JSON.parse(content);
            const prettyJson = JSON.stringify(jsonObj, null, 2);
            editor.setValue(prettyJson);
            showAlert('JSON formatado com sucesso!', 'success');
            updateJsonStats();
        } catch (e) {
            showAlert('Erro ao formatar JSON: ' + e.message, 'danger');
        }
    });
    
    // Salvar o JSON quando o botão for clicado
    saveButton.addEventListener('click', function() {
        const jsonContent = editor.getValue();
        
        if (!currentLanguage || !jsonContent) {
            showAlert('Selecione um idioma e insira o conteúdo JSON', 'danger');
            return;
        }
        
        // Verificar se o JSON é válido
        try {
            JSON.parse(jsonContent);
        } catch (e) {
            showAlert('JSON inválido: ' + e.message, 'danger');
            return;
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

    // Adicionar atalho de teclado para formatar o JSON (Ctrl+Shift+F)
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'F') {
            e.preventDefault();
            if (!formatButton.disabled) {
                formatButton.click();
            }
        }
    });
});
