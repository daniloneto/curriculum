// JavaScript para a página de cadastro de currículo
document.addEventListener('DOMContentLoaded', function() {
    // Elementos DOM
    const languageSelect = document.getElementById('language-select');
    const formContainer = document.getElementById('form-container');
    const curriculoForm = document.getElementById('curriculo-form');
    const saveButton = document.getElementById('save-button');
    const resetButton = document.getElementById('reset-button');
    const alertBox = document.getElementById('alert-box');
      // Variáveis de estado
    let currentLanguage = '';
    let curriculoData = null;
    let formSections = {};
    let dynamicLists = {};
    
    // Função para formatar o nome de um campo para exibição
    function getFormattedFieldName(key) {
        // Adicionar espaços antes das letras maiúsculas e capitalizar a primeira letra
        return key
            .replace(/([A-Z])/g, ' $1') // Adicionar espaço antes das maiúsculas (para camelCase)
            .replace(/^./, str => str.toUpperCase()) // Capitalizar a primeira letra
            .replace(/_/g, ' ') // Substituir underscores por espaços
            .replace(/\./g, ' ') // Substituir pontos por espaços
            .trim(); // Remover espaços extras
    }
    
    // Função para formatar o nome da seção
    function getFormattedSectionName(key) {
        // Converter camelCase para formato legível
        return key
            .replace(/([A-Z])/g, ' $1') // Inserir espaço antes de cada letra maiúscula
            .replace(/^./, str => str.toUpperCase()) // Capitalizar a primeira letra
            .replace(/_/g, ' ') // Substituir underscores por espaços
            .trim(); // Remover espaços extras
    }
    
    // Carregar o currículo quando o idioma for selecionado
    languageSelect.addEventListener('change', function() {
        currentLanguage = languageSelect.value;
        
        if (!currentLanguage) {
            formContainer.style.display = 'none';
            return;
        }
        
        // Verificar se existe um currículo no localStorage
        const storedResume = getStoredResume(currentLanguage);
        
        if (storedResume) {
            curriculoData = storedResume;
            showAlert(`Currículo em ${getLanguageName(currentLanguage)} carregado.`, 'success');
        } else {
            // Se não existir, tentar carregar do servidor
            fetchCurriculoData(currentLanguage);
            return;
        }
        
        // Gerar o formulário com os dados carregados
        generateForm(curriculoData);
        formContainer.style.display = 'block';
    });
    
    // Salvar o currículo quando o botão for clicado
    saveButton.addEventListener('click', function() {
        if (validateForm()) {
            // Atualizar o objeto de dados com os valores do formulário
            updateCurriculoDataFromForm();
            
            // Salvar no localStorage
            if (storeResume(currentLanguage, curriculoData)) {
                showAlert(`Currículo em ${getLanguageName(currentLanguage)} salvo com sucesso!`, 'success');
            } else {
                showAlert('Erro ao salvar currículo.', 'danger');
            }
        } else {
            showAlert('Por favor, preencha todos os campos obrigatórios.', 'danger');
        }
    });
    
    // Limpar o formulário quando o botão for clicado
    resetButton.addEventListener('click', function() {
        if (confirm('Deseja limpar todos os campos? As alterações não salvas serão perdidas.')) {
            generateForm(curriculoData); // Recarregar o formulário com os dados originais
        }
    });
    
    // Função para buscar os dados do currículo do servidor
    function fetchCurriculoData(language) {
        // Mostrar indicador de carregamento
        showAlert('Carregando currículo...', 'warning');
        
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
                formContainer.style.display = 'none';
            } else {
                curriculoData = data.content;
                
                // Salvar no localStorage para uso futuro
                storeResume(language, curriculoData);
                
                // Gerar o formulário
                generateForm(curriculoData);
                formContainer.style.display = 'block';
                
                showAlert(`Currículo em ${getLanguageName(language)} carregado do servidor.`, 'success');
            }
        })
        .catch(error => {
            showAlert('Erro ao carregar o currículo: ' + error, 'danger');
            formContainer.style.display = 'none';
        });
    }    // Função para gerar o formulário dinamicamente com abas
    function generateForm(data) {
        // Limpar o formulário existente
        curriculoForm.innerHTML = '';
        formSections = {};
        dynamicLists = {};
        
        // Criar container para as abas
        const tabsContainer = document.createElement('div');
        tabsContainer.className = 'tabs';
        
        // Criar container para o conteúdo das abas
        const tabsContentContainer = document.createElement('div');
        tabsContentContainer.className = 'tabs-content';
        
        // Adicionar primeira aba para informações pessoais
        const pessoalTab = document.createElement('div');
        pessoalTab.className = 'tab active';
        pessoalTab.dataset.target = 'tab-pessoal';
        pessoalTab.textContent = 'Informações Pessoais'; // Consider localizing this if needed
        tabsContainer.appendChild(pessoalTab);
        
        // Adicionar container para o conteúdo da aba de informações pessoais
        const pessoalContent = document.createElement('div');
        pessoalContent.id = 'tab-pessoal';
        pessoalContent.className = 'tab-content active';
        
        // Seção de informações pessoais
        const pessoalSection = createSection('Informações Pessoais'); // Consider localizing
        
        // Processar todos os campos de nível superior (exceto secoes e sections)
        for (const [key, value] of Object.entries(data)) {
            // Ignorar campos de estrutura complexa que serão processados separadamente
            if (key === 'secoes' || key === 'sections' || key === 'secciones') continue;
            
            // Determinar o tipo de campo com base no valor
            let fieldType = 'text';
            let required = key === 'nome' || key === 'name' || key === 'email' || key === 'languageName';
            
            if (typeof value === 'object' && !Array.isArray(value)) {
                // Ignorar objetos complexos por enquanto
                continue;
            } else if (Array.isArray(value)) {
                // Ignorar arrays por enquanto
                continue;
            } else if (typeof value === 'boolean') {
                fieldType = 'checkbox';
            } else if (key.includes('email')) {
                fieldType = 'email';
            } else if (key.includes('telefone') || key.includes('phone') || key.includes('celular')) {
                fieldType = 'tel';
            } else if (key.includes('url') || key.includes('website') || key.includes('linkedin')) {
                fieldType = 'url';
            } else if (key.includes('data') || key.includes('date')) {
                fieldType = 'date';
            }
            
            // Criar um label mais amigável
            const label = getFormattedFieldName(key);
            
            // Adicionar o campo ao formulário
            addFormField(pessoalSection, key, label, value, fieldType, required);
        }
        
        pessoalContent.appendChild(pessoalSection);
        tabsContentContainer.appendChild(pessoalContent);
        
        // Processar as seções do currículo em abas separadas
        if (data.secoes) { // Portuguese
            processGenericSectionsInTabs(data.secoes, 'secoes', tabsContainer, tabsContentContainer);
        } else if (data.sections) { // English
            processGenericSectionsInTabs(data.sections, 'sections', tabsContainer, tabsContentContainer);
        } else if (data.secciones) { // Spanish
            processGenericSectionsInTabs(data.secciones, 'secciones', tabsContainer, tabsContentContainer);
        }
        
        // Adicionar as abas e o conteúdo ao formulário
        curriculoForm.appendChild(tabsContainer);
        curriculoForm.appendChild(tabsContentContainer);
        
        // Adicionar evento de clique para as abas
        setupTabNavigation();
    }
    // REMOVE OLD processSecoesInTabs and processSectionsInTabs
    // The old functions processSecoesInTabs (approx lines 203-305) and 
    // processSectionsInTabs (approx lines 308-410) will be replaced by the new function below.

    // Função para processar seções genéricas do currículo em abas
    function processGenericSectionsInTabs(sectionsData, topLevelKey, tabsContainer, tabsContentContainer) {
        Object.entries(sectionsData).forEach(([sectionKey, sectionItemData], index) => {
            // Use 'titulo' (Portuguese/Spanish) or 'title' (English)
            const title = sectionItemData.titulo || sectionItemData.title || getFormattedSectionName(sectionKey);

            const tab = document.createElement('div');
            tab.className = 'tab';
            tab.dataset.target = `tab-${sectionKey}`; // Use sectionKey for target ID consistency
            tab.textContent = title;
            tabsContainer.appendChild(tab);

            const tabContent = document.createElement('div');
            tabContent.id = `tab-${sectionKey}`; // Match dataset.target
            tabContent.className = 'tab-content';

            const sectionElement = createSection(title);
            formSections[sectionKey] = sectionElement;

            // Primeiro, processar campos simples da seção
            for (const [key, value] of Object.entries(sectionItemData)) {
                if (key === 'titulo' || key === 'title' || typeof value === 'object') continue;

                const fieldKey = `${topLevelKey}.${sectionKey}.${key}`;
                const label = getFormattedFieldName(key);
                addFormField(sectionElement, fieldKey, label, value, 'text', false);
            }

            // Depois, processar estruturas mais complexas
            for (const [key, value] of Object.entries(sectionItemData)) {
                if (key === 'titulo' || key === 'title') continue;

                if (typeof value === 'object') {
                    if (Array.isArray(value)) { // É uma lista/array
                        const listKey = `${topLevelKey}.${sectionKey}.${key}`;
                        const label = getFormattedFieldName(key);

                        if (value.length > 0) {
                            if (typeof value[0] === 'string') {
                                createSimpleDynamicList(sectionElement, listKey, label, value);
                            } else if (typeof value[0] === 'object') {
                                const fields = extractFieldsFromObject(value[0]); // extractFieldsFromObject is generic
                                createDynamicList(sectionElement, listKey, label, value, fields);
                            }
                        } else { // Array vazio - tentar determinar o tipo baseado no nome
                            const simpleListKeys = ['lista', 'formacao', 'certificacoes', 'idiomas', 'list', 'items', 'education', 'languages', 'habilidadeslist', 'skillslist', 'cursos', 'courses', 'publications', 'publicacoes', 'referencias', 'references'];
                            if (simpleListKeys.includes(key.toLowerCase())) { // check common keys for simple lists
                                createSimpleDynamicList(sectionElement, listKey, label, []);
                            } else {
                                const fields = guessFieldsFromSectionName(sectionKey, key); // guessFieldsFromSectionName uses sectionKey
                                createDynamicList(sectionElement, listKey, label, [], fields);
                            }
                        }
                    } else { // É um objeto (sub-seção)
                        const subSectionContainerKey = `${topLevelKey}.${sectionKey}.${key}`;
                        const subSectionDiv = document.createElement('div');
                        subSectionDiv.className = 'sub-section';

                        const subTitleElement = document.createElement('h4');
                        subTitleElement.textContent = getFormattedFieldName(key);
                        subSectionDiv.appendChild(subTitleElement);

                        for (const [subKey, subValue] of Object.entries(value)) {
                            if (typeof subValue !== 'object') { // Simple field in sub-object
                                const fieldKey = `${subSectionContainerKey}.${subKey}`;
                                const label = getFormattedFieldName(subKey);
                                const fieldType = (subKey.toLowerCase() === 'texto' || subKey.toLowerCase() === 'descricao' || subKey.toLowerCase() === 'text' || subKey.toLowerCase() === 'description' || subKey.toLowerCase().includes('content')) ? 'textarea' : 'text';
                                addFormField(subSectionDiv, fieldKey, label, subValue, fieldType, false);
                            } else if (Array.isArray(subValue)) { // Array within sub-object
                                const listKey = `${subSectionContainerKey}.${subKey}`;
                                const label = getFormattedFieldName(subKey);
                                if (subValue.length > 0) {
                                    if (typeof subValue[0] === 'string') {
                                        createSimpleDynamicList(subSectionDiv, listKey, label, subValue);
                                    } else if (typeof subValue[0] === 'object') {
                                        const fields = extractFieldsFromObject(subValue[0]);
                                        createDynamicList(subSectionDiv, listKey, label, subValue, fields);
                                    }
                                } else { // Empty array in sub-object, default to simple list
                                    createSimpleDynamicList(subSectionDiv, listKey, label, []);
                                }
                            }
                        }
                        sectionElement.appendChild(subSectionDiv);
                    }
                }
            }
            tabContent.appendChild(sectionElement);
            tabsContentContainer.appendChild(tabContent);
        });
    }
    
    // Configurar a navegação entre as abas
    function setupTabNavigation() {
        const tabs = document.querySelectorAll('.tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                // Remover classe active de todas as abas e conteúdos
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                
                // Adicionar classe active na aba clicada
                this.classList.add('active');
                
                // Mostrar o conteúdo correspondente
                const targetId = this.dataset.target;
                const targetContent = document.getElementById(targetId);
                if (targetContent) {
                    targetContent.classList.add('active');
                }
            });
        });
    }
    
    // Função para validar o formulário
    function validateForm() {
        const requiredFields = curriculoForm.querySelectorAll('[required]');
        let valid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                valid = false;
                
                // Destacar o campo
                field.style.borderColor = '#dc3545';
                
                // Adicionar evento para remover destaque quando o campo for preenchido
                field.addEventListener('input', function() {
                    if (this.value.trim()) {
                        this.style.borderColor = '';
                        this.classList.remove('is-invalid');
                    }
                }, { once: true });
            } else {
                field.style.borderColor = '';
                field.classList.remove('is-invalid');
            }
        });
        
        return valid;
    }
      // Função para atualizar o objeto de dados com os valores do formulário
    function updateCurriculoDataFromForm() {
        // Processamento recursivo para atualizar o objeto de dados
        const formInputs = curriculoForm.querySelectorAll('input, textarea, select');
        
        formInputs.forEach(input => {
            if (!input.hasAttribute('data-key')) return;
            
            const key = input.getAttribute('data-key');
            let value = input.type === 'checkbox' ? input.checked : input.value;
            
            // Ignorar inputs que pertencem a listas dinâmicas - eles serão processados separadamente
            if (key.includes('[') && key.includes(']')) return;
            
            // Converter para tipo apropriado
            if (input.type === 'number') {
                value = parseFloat(value);
            }
            
            // Definir o valor no objeto usando o caminho aninhado
            setNestedValue(curriculoData, key, value);
        });
        
        // Atualizar listas dinâmicas
        Object.keys(dynamicLists).forEach(key => {
            const listData = dynamicLists[key];
            
            // Extrair os valores da lista e atualizá-los no objeto
            if (listData.simple) {
                // Lista simples (array de strings)
                const items = [];
                const listItems = listData.list.querySelectorAll('.dynamic-list-item');
                
                listItems.forEach(item => {
                    const input = item.querySelector('input, textarea');
                    if (input && input.value.trim()) {
                        items.push(input.value.trim());
                    }
                });
                
                // Definir no objeto
                setNestedValue(curriculoData, key, items);
            } else {
                // Lista complexa (array de objetos)
                const items = [];
                const listItems = listData.list.querySelectorAll('.dynamic-list-item');
                
                listItems.forEach(item => {
                    const obj = {};
                    const itemIndex = parseInt(item.getAttribute('data-index'));
                    
                    // Buscar todos os campos deste item
                    const itemInputs = item.querySelectorAll('input, textarea, select');
                    
                    itemInputs.forEach(input => {
                        if (!input.hasAttribute('data-key')) return;
                        
                        const inputKey = input.getAttribute('data-key');
                        // Extrair o nome do campo do final da chave (após o último ponto)
                        const fieldName = inputKey.split('.').pop().replace(/\[\d+\]\./, '');
                        let value = input.type === 'checkbox' ? input.checked : input.value;
                        
                        // Converter para tipo apropriado
                        if (input.type === 'number') {
                            value = parseFloat(value);
                        }
                        
                        obj[fieldName] = value;
                    });
                    
                    if (Object.keys(obj).length > 0) {
                        items.push(obj);
                    }
                });
                
                // Definir no objeto
                setNestedValue(curriculoData, key, items);
            }
        });
    }
    
    // Função auxiliar para definir um valor em um caminho aninhado
    function setNestedValue(obj, path, value) {
        // Manipular caminhos simples e complexos
        const parts = path.split('.');
        let current = obj;
        
        // Navegar até o objeto pai
        for (let i = 0; i < parts.length - 1; i++) {
            const part = parts[i];
            
            // Verificar se é um array com índice
            if (part.includes('[') && part.includes(']')) {
                const arrName = part.substring(0, part.indexOf('['));
                const index = parseInt(part.match(/\[(\d+)\]/)[1]);
                
                if (!current[arrName]) current[arrName] = [];
                if (!current[arrName][index]) current[arrName][index] = {};
                
                current = current[arrName][index];
            } else {
                if (!current[part]) current[part] = {};
                current = current[part];
            }
        }
        
        // Definir o valor na propriedade final
        const lastPart = parts[parts.length - 1];
        
        // Verificar se é um array com índice
        if (lastPart.includes('[') && lastPart.includes(']')) {
            const arrName = lastPart.substring(0, lastPart.indexOf('['));
            const index = parseInt(lastPart.match(/\[(\d+)\]/)[1]);
            
            if (!current[arrName]) current[arrName] = [];
            current[arrName][index] = value;
        } else {
            current[lastPart] = value;
        }
    }
    
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
    
    // Função para obter o nome do idioma
    function getLanguageName(langCode) {
        switch (langCode) {
            case 'pt': return 'Português';
            case 'en': return 'Inglês';
            case 'es': return 'Espanhol';
            default: return langCode.toUpperCase();
        }
    }
    
    // Extrair campos de um objeto exemplo para criar uma lista dinâmica
    function extractFieldsFromObject(obj) {
        if (!obj) return [];
        
        return Object.keys(obj).map(key => {
            const value = obj[key];
            let type = 'text';
            
            // Determinar o tipo com base no valor ou nome do campo
            if (typeof value === 'boolean') {
                type = 'checkbox';
            } else if (key.includes('email')) {
                type = 'email';
            } else if (key.includes('telefone') || key.includes('phone')) {
                type = 'tel';
            } else if (key.includes('url') || key.includes('website') || key.includes('linkedin')) {
                type = 'url';
            } else if (key.includes('data') || key.includes('date')) {
                type = 'date';
            } else if (key.includes('descricao') || key.includes('description') || 
                       key.includes('texto') || key.includes('text') ||
                       key.includes('atividades') || key.includes('activities')) {
                type = 'textarea';
            }
            
            return {
                key: key,
                label: getFormattedFieldName(key),
                type: type,
                required: key === 'nome' || key === 'name' || key === 'empresa' || key === 'cargo' || 
                          key === 'company' || key === 'position' || key === 'title'
            };
        });
    }
    
    // Função para adivinhar campos com base no nome da seção
    function guessFieldsFromSectionName(sectionName, listName) {
        // Campos padrão para diferentes tipos de seções
        if (sectionName === 'experienciaProfissional' || sectionName === 'empregos' || 
            sectionName === 'experience' || sectionName === 'workExperience' || 
            listName === 'empregos' || listName === 'jobs') {
            return [
                { key: 'empresa', label: 'Empresa', required: true },
                { key: 'cargo', label: 'Cargo', required: true },
                { key: 'periodo', label: 'Período', required: true },
                { key: 'descricao', label: 'Descrição', type: 'textarea', required: true }
            ];
        } else if (sectionName === 'educacao' || sectionName === 'education' || 
                   listName === 'formacao' || listName === 'education') {
            return [
                { key: 'curso', label: 'Curso', required: true },
                { key: 'instituicao', label: 'Instituição', required: true },
                { key: 'periodo', label: 'Período', required: true },
                { key: 'descricao', label: 'Descrição', type: 'textarea', required: false }
            ];
        } else if (sectionName === 'projetos' || sectionName === 'projects' || 
                  listName === 'projetos' || listName === 'projects') {
            return [
                { key: 'nome', label: 'Nome', required: true },
                { key: 'descricao', label: 'Descrição', type: 'textarea', required: true },
                { key: 'tecnologias', label: 'Tecnologias', required: false },
                { key: 'link', label: 'Link', type: 'url', required: false }
            ];
        } else if (sectionName === 'habilidades' || sectionName === 'skills' || 
                  listName === 'categorias' || listName === 'categories') {
            return [
                { key: 'nome', label: 'Nome da Categoria', required: true },
                { key: 'habilidades', label: 'Habilidades (separadas por vírgula)', type: 'textarea', required: true }
            ];
        }
        
        // Campos genéricos para qualquer outro tipo de seção
        return [
            { key: 'nome', label: 'Nome', required: true },
            { key: 'descricao', label: 'Descrição', type: 'textarea', required: false }
        ];
    }
    
    // Função para criar uma seção do formulário
    function createSection(title) {
        const section = document.createElement('div');
        section.className = 'form-section';
        
        const heading = document.createElement('h3');
        heading.textContent = title;
        section.appendChild(heading);
        
        return section;
    }
    
    // Função para adicionar um campo ao formulário
    function addFormField(section, key, label, value, type = 'text', required = false) {
        const formGroup = document.createElement('div');
        formGroup.className = 'form-group' + (required ? ' required' : '');
        
        const fieldLabel = document.createElement('label');
        fieldLabel.setAttribute('for', key);
        fieldLabel.textContent = label;
        formGroup.appendChild(fieldLabel);
        
        let input;
        if (type === 'textarea') {
            input = document.createElement('textarea');
            input.className = 'form-control';
        } else {
            input = document.createElement('input');
            input.className = 'form-control';
            input.type = type;
        }
        
        input.id = key;
        input.name = key;
        input.value = value;
        input.setAttribute('data-key', key);
        if (required) {
            input.required = true;
        }
        
        formGroup.appendChild(input);
        section.appendChild(formGroup);
        
        return input;
    }
    
    // Função para criar uma lista dinâmica (array de objetos)
    function createDynamicList(section, key, label, items, fields) {
        const container = document.createElement('div');
        container.className = 'dynamic-list-container';
        
        const listLabel = document.createElement('label');
        listLabel.textContent = label;
        container.appendChild(listLabel);
        
        const list = document.createElement('ul');
        list.className = 'dynamic-list';
        list.id = key + '-list';
        container.appendChild(list);
        
        // Adicionar cada item existente
        if (items && items.length) {
            items.forEach((item, index) => {
                addDynamicListItem(list, key, item, fields, index);
            });
        }
        
        // Botão para adicionar novos itens
        const addButton = document.createElement('button');
        addButton.className = 'btn add-item-btn';
        addButton.textContent = 'Adicionar ' + label.replace(/s$/, ''); // Remover plural, se existir
        addButton.type = 'button';
        addButton.addEventListener('click', function() {
            // Criar um item vazio
            const newItem = {};
            fields.forEach(field => {
                newItem[field.key] = '';
            });
            
            // Adicionar à lista
            const newIndex = list.children.length;
            addDynamicListItem(list, key, newItem, fields, newIndex);
        });
        
        container.appendChild(addButton);
        section.appendChild(container);
        
        // Armazenar referência para facilitar a atualização
        dynamicLists[key] = {
            list: list,
            fields: fields
        };
        
        return container;
    }
    
    // Função para adicionar um item a uma lista dinâmica
    function addDynamicListItem(list, key, item, fields, index) {
        const listItem = document.createElement('li');
        listItem.className = 'dynamic-list-item';
        listItem.setAttribute('data-index', index);
        
        // Criar campos para cada propriedade do item
        fields.forEach(field => {
            const fieldKey = `${key}[${index}].${field.key}`;
            addFormField(listItem, fieldKey, field.label, item[field.key] || '', field.type || 'text', field.required);
        });
        
        // Botões de ação
        const controls = document.createElement('div');
        controls.className = 'dynamic-list-controls';
        
        // Botão remover
        const removeButton = document.createElement('button');
        removeButton.className = 'btn btn-danger btn-sm';
        removeButton.textContent = 'Remover';
        removeButton.type = 'button';
        removeButton.addEventListener('click', function() {
            list.removeChild(listItem);
            // Reindexar os itens restantes
            reindexDynamicList(list, key, fields);
        });
        
        controls.appendChild(removeButton);
        listItem.appendChild(controls);
        list.appendChild(listItem);
    }
    
    // Função para criar uma lista dinâmica simples (array de strings)
    function createSimpleDynamicList(section, key, label, items) {
        const container = document.createElement('div');
        container.className = 'dynamic-list-container';
        
        const listLabel = document.createElement('label');
        listLabel.textContent = label;
        container.appendChild(listLabel);
        
        const list = document.createElement('ul');
        list.className = 'dynamic-list';
        list.id = key + '-list';
        container.appendChild(list);
        
        // Adicionar cada item existente
        if (items && items.length) {
            items.forEach((item, index) => {
                addSimpleListItem(list, key, item, index);
            });
        }
        
        // Botão para adicionar novos itens
        const addButton = document.createElement('button');
        addButton.className = 'btn add-item-btn';
        addButton.textContent = 'Adicionar ' + label.replace(/s$/, ''); // Remover plural, se existir
        addButton.type = 'button';
        addButton.addEventListener('click', function() {
            // Adicionar à lista
            const newIndex = list.children.length;
            addSimpleListItem(list, key, '', newIndex);
        });
        
        container.appendChild(addButton);
        section.appendChild(container);
        
        // Armazenar referência para facilitar a atualização
        dynamicLists[key] = {
            list: list,
            simple: true
        };
        
        return container;
    }
    
    // Função para adicionar um item a uma lista simples
    function addSimpleListItem(list, key, value, index) {
        const listItem = document.createElement('li');
        listItem.className = 'dynamic-list-item';
        listItem.setAttribute('data-index', index);
        
        // Campo para o valor
        const fieldKey = `${key}[${index}]`;
        addFormField(listItem, fieldKey, 'Valor', value, 'text', true);
        
        // Botões de ação
        const controls = document.createElement('div');
        controls.className = 'dynamic-list-controls';
        
        // Botão remover
        const removeButton = document.createElement('button');
        removeButton.className = 'btn btn-danger btn-sm';
        removeButton.textContent = 'Remover';
        removeButton.type = 'button';
        removeButton.addEventListener('click', function() {
            list.removeChild(listItem);
            // Reindexar os itens restantes
            reindexSimpleList(list, key);
        });
        
        controls.appendChild(removeButton);
        listItem.appendChild(controls);
        list.appendChild(listItem);
    }
    
    // Função para reindexar uma lista dinâmica após remoção de itens
    function reindexDynamicList(list, key, fields) {
        const items = list.querySelectorAll('.dynamic-list-item');
        items.forEach((item, newIndex) => {
            item.setAttribute('data-index', newIndex);
            
            // Atualizar os ids e names de todos os campos
            fields.forEach(field => {
                const input = item.querySelector(`[data-key^="${key}["][data-key$="].${field.key}"]`);
                if (input) {
                    const newKey = `${key}[${newIndex}].${field.key}`;
                    input.id = newKey;
                    input.name = newKey;
                    input.setAttribute('data-key', newKey);
                }
            });
        });
    }
    
    // Função para reindexar uma lista simples após remoção de itens
    function reindexSimpleList(list, key) {
        const items = list.querySelectorAll('.dynamic-list-item');
        items.forEach((item, newIndex) => {
            item.setAttribute('data-index', newIndex);
            
            // Atualizar os ids e names de todos os campos
            const input = item.querySelector(`[data-key^="${key}["]`);
            if (input) {
                const newKey = `${key}[${newIndex}]`;
                input.id = newKey;
                input.name = newKey;
                input.setAttribute('data-key', newKey);
            }
        });
    }
});
