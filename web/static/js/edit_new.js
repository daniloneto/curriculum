// JavaScript para a página de edição
document.addEventListener('DOMContentLoaded', function() {      const languageSelect = document.getElementById('language-select');
    const jsonEditor = document.getElementById('json-editor');
    const saveButton = document.getElementById('save-button');
    const syncButton = document.getElementById('sync-button');
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
        validateButton.disabled = true;
        validationResults.style.display = 'none';
        
        // Limpar marcadores de erro
        clearErrorMarkers();
        
        // Verificar se temos o currículo no localStorage
        const storedResume = getStoredResume(language);
        
        if (storedResume) {
            console.log(`Currículo para ${language} carregado do localStorage`);
            handleJsonLoaded(storedResume);
            
            // Carregar o schema para validação
            loadSchemaForLanguage(language);
            
            // Verificar diferenças com a versão do servidor
            checkServerDifferences(language);
            
            return;
        }
            
        // Se não encontrou no localStorage, carregar do servidor
        fetch('/get_json_content', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ language: language })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showAlert(data.error, 'danger');
                editor.setValue('');
            } else {
                // Salvar no localStorage para uso futuro
                storeResume(language, data.content);
                handleJsonLoaded(data.content);
                
                // Carregar o schema para validação
                loadSchemaForLanguage(language);
            }
        })
        .catch(error => {
            showAlert('Erro ao carregar o arquivo: ' + error, 'danger');
            editor.setValue('');
            editor.setOption('readOnly', true);
            saveButton.disabled = true;
            validateButton.disabled = true;        });
    }
    
    // Função para carregar o schema para um idioma
    function loadSchemaForLanguage(language) {
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
            })
            .catch(error => {
                console.error(`Erro ao carregar schema para ${language}:`, error);
                showAlert(`Erro ao carregar schema para validação: ${error}`, 'warning');
            });
    }
      // Função para processar o JSON carregado
    function handleJsonLoaded(content) {
        // Formatar o JSON para exibição
        const prettyJson = JSON.stringify(content, null, 2);
        editor.setValue(prettyJson);                    
        editor.setOption('readOnly', false);
        saveButton.disabled = false;
        syncButton.disabled = false;
        validateButton.disabled = false;
        
        // Executar o linting
        setTimeout(() => {
            editor.performLint();
        }, 100);
        
        updateJsonStats();
    }

    // Função para atualizar estatísticas do JSON
    function updateJsonStats() {
        try {
            const jsonContent = editor.getValue();
            if (!jsonContent.trim()) {
                jsonStats.textContent = 'Vazio';
                return;
            }
            
            const parsed = JSON.parse(jsonContent);
            const bytes = new TextEncoder().encode(jsonContent).length;
            const formattedSize = bytes < 1024 
                ? `${bytes} bytes` 
                : `${(bytes / 1024).toFixed(1)} KB`;
            
            // Contar chaves de primeiro nível
            const topLevelKeys = Object.keys(parsed).length;
            
            jsonStats.textContent = `${formattedSize} | ${topLevelKeys} chaves`;
        } catch (e) {
            jsonStats.textContent = 'JSON inválido';
        }
    }
    
    // Função para limpar marcadores de erro
    function clearErrorMarkers() {
        // Limpar marcadores de erro anteriores
        for (let marker of errorMarkers) {
            marker.clear();
        }
        errorMarkers = [];
        
        // Limpar área de resultados de validação
        if (validationResults) {
            validationResults.innerHTML = '';
            validationResults.style.display = 'none';
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
            const parsedJson = JSON.parse(jsonContent);
            
            // Salvar no localStorage
            if (storeResume(currentLanguage, parsedJson)) {
                showAlert('JSON salvo com sucesso no navegador!', 'success');
            } else {
                showAlert('Erro ao salvar no navegador.', 'danger');
            }
        } catch (e) {
            showAlert('JSON inválido: ' + e.message, 'danger');
            return;
        }
    });
      // Sincronizar com o servidor quando o botão for clicado
    syncButton.addEventListener('click', function() {
        if (!currentLanguage) {
            showAlert('Selecione um idioma para sincronizar', 'danger');
            return;
        }
        
        // Verificar se temos o currículo no localStorage
        const storedResume = getStoredResume(currentLanguage);
        
        if (!storedResume) {
            showAlert('Nenhum currículo encontrado para sincronizar', 'danger');
            return;
        }
        
        // Mostrar indicador de carregamento
        syncButton.innerHTML = '<span class="loading"></span> Sincronizando...';
        syncButton.disabled = true;
        
        // Enviar o JSON para o servidor
        fetch('/save_json', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                language: currentLanguage,
                content: storedResume
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showAlert(`Erro ao sincronizar: ${data.error}`, 'danger');
            } else {
                showAlert('JSON sincronizado com sucesso com o servidor!', 'success');
                
                // Resetar o estilo do botão de sincronização
                syncButton.classList.remove('btn-warning');
                syncButton.textContent = 'Sincronizar com Servidor';
            }
        })
        .catch(error => {
            showAlert('Erro ao sincronizar: ' + error, 'danger');
        })
        .finally(() => {
            syncButton.disabled = false;
        });    });


    // Limpar erro quando idioma mudar
    languageSelect.addEventListener('change', function() {
        clearErrorMarkers();
    });
    
    // Função para exibir alertas
    function showAlert(message, type, timeout) {
        alertBox.innerHTML = message;
        alertBox.className = `alert alert-${type}`;
        alertBox.style.display = 'block';
        
        // Esconder a mensagem após 5 segundos
        setTimeout(function() {
            alertBox.style.display = 'none';
        }, timeout || 5000);
    }
    
    // Verificar diferenças entre versões locais e do servidor
    function checkServerDifferences(language) {
        // Buscar a versão do servidor para comparação
        fetch('/get_json_content', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ language: language })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Erro ao verificar diferenças:', data.error);
                return;
            }
            
            // Verificar se a versão local é diferente da do servidor
            const storedResume = getStoredResume(language);
            if (storedResume && isLocalDifferentFromServer(language, data.content)) {
                // Atualizar o estilo do botão de sincronização para indicar diferenças
                syncButton.classList.add('btn-warning');
                syncButton.innerHTML = 'Sincronizar <span class="badge badge-light">!</span>';
                
                // Mostrar uma dica sobre as diferenças
                showAlert('Existem diferenças entre sua versão local e a do servidor. Clique em "Sincronizar" para atualizar.', 'warning', 10000);
            } else {
                syncButton.classList.remove('btn-warning');
                syncButton.textContent = 'Sincronizar com Servidor';
            }
        })
        .catch(error => {
            console.error('Erro ao verificar diferenças:', error);
        });
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

    // Exportar currículos quando o botão for clicado
    const exportButton = document.getElementById('export-button');
    exportButton.addEventListener('click', function() {
        if (downloadStoredData()) {
            showAlert('Currículos exportados com sucesso!', 'success');
        } else {
            showAlert('Erro ao exportar currículos.', 'danger');
        }
    });
    
    // Importar currículos quando o botão for clicado
    const importButton = document.getElementById('import-button');
    const importFile = document.getElementById('import-file');
    
    importButton.addEventListener('click', function() {
        importFile.click();
    });
    
    importFile.addEventListener('change', function() {
        if (this.files.length === 0) return;
        
        const file = this.files[0];
        const reader = new FileReader();
        
        reader.onload = function(e) {
            try {
                const importData = JSON.parse(e.target.result);
                
                if (importStoredData(importData)) {
                    showAlert('Currículos importados com sucesso!', 'success');
                    
                    // Recarregar o idioma atual, se houver
                    if (currentLanguage) {
                        fetchJsonContent(currentLanguage);
                    }
                } else {
                    showAlert('Erro ao importar currículos. Formato inválido.', 'danger');
                }
            } catch (e) {
                showAlert('Erro ao importar arquivo: ' + e.message, 'danger');
            }
            
            // Limpar o input
            importFile.value = '';
        };
        
        reader.readAsText(file);
    });
});
