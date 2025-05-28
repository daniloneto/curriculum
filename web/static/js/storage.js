/**
 * Gerenciador de armazenamento local para os arquivos de currículo
 */

// Prefixo para as chaves do localStorage
const STORAGE_PREFIX = 'cv_generator_';

// Chave para armazenar a lista de idiomas disponíveis
const LANGUAGES_KEY = `${STORAGE_PREFIX}languages`;

/**
 * Verifica se o idioma já está armazenado no localStorage
 * @param {string} langCode - Código do idioma (pt, en, es)
 * @returns {boolean} - true se o idioma estiver armazenado, false caso contrário
 */
function isLanguageStored(langCode) {
    return localStorage.getItem(`${STORAGE_PREFIX}${langCode}`) !== null;
}

/**
 * Armazena o currículo no localStorage
 * @param {string} langCode - Código do idioma (pt, en, es)
 * @param {Object} curriculoData - Dados do currículo
 */
function storeResume(langCode, curriculoData) {
    try {
        localStorage.setItem(`${STORAGE_PREFIX}${langCode}`, JSON.stringify(curriculoData));

        // Atualiza a lista de idiomas disponíveis
        updateAvailableLanguages(langCode, curriculoData.languageName);
        
        return true;
    } catch (error) {
        console.error(`Erro ao armazenar currículo ${langCode}:`, error);
        return false;
    }
}

/**
 * Recupera o currículo do localStorage
 * @param {string} langCode - Código do idioma (pt, en, es)
 * @returns {Object|null} - Dados do currículo ou null se não existir
 */
function getStoredResume(langCode) {
    try {
        const data = localStorage.getItem(`${STORAGE_PREFIX}${langCode}`);
        return data ? JSON.parse(data) : null;
    } catch (error) {
        console.error(`Erro ao recuperar currículo ${langCode}:`, error);
        return null;
    }
}

/**
 * Atualiza a lista de idiomas disponíveis no localStorage
 * @param {string} langCode - Código do idioma (pt, en, es)
 * @param {string} langName - Nome do idioma na própria língua
 */
function updateAvailableLanguages(langCode, langName) {
    try {
        // Recuperar a lista atual
        let languages = getAvailableLanguages();
        
        // Adicionar ou atualizar o idioma
        languages[langCode] = { name: langName };
        
        // Salvar a lista atualizada
        localStorage.setItem(LANGUAGES_KEY, JSON.stringify(languages));
    } catch (error) {
        console.error('Erro ao atualizar a lista de idiomas:', error);
    }
}

/**
 * Obtém a lista de idiomas disponíveis no localStorage
 * @returns {Object} - Objeto com os idiomas disponíveis {langCode: {name: string}}
 */
function getAvailableLanguages() {
    try {
        const data = localStorage.getItem(LANGUAGES_KEY);
        return data ? JSON.parse(data) : {};
    } catch (error) {
        console.error('Erro ao recuperar lista de idiomas:', error);
        return {};
    }
}

/**
 * Inicializa o armazenamento local com os templates padrão
 * @param {Object} defaultTemplates - Templates padrão {langCode: curriculoData}
 */
function initializeStorage(defaultTemplates) {
    // Verificar se já existem dados armazenados
    const storedLanguages = getAvailableLanguages();
    const hasStoredData = Object.keys(storedLanguages).length > 0;
    
    if (!hasStoredData && defaultTemplates) {
        console.log('Inicializando armazenamento local com templates padrão');
        
        // Armazenar cada template
        for (const [langCode, data] of Object.entries(defaultTemplates)) {
            storeResume(langCode, data);
        }
    }
}

/**
 * Limpa todos os dados do currículo armazenados
 */
function clearAllStoredData() {
    try {
        const languages = getAvailableLanguages();
        
        // Remover cada currículo
        for (const langCode of Object.keys(languages)) {
            localStorage.removeItem(`${STORAGE_PREFIX}${langCode}`);
        }
        
        // Remover a lista de idiomas
        localStorage.removeItem(LANGUAGES_KEY);
        
        return true;
    } catch (error) {
        console.error('Erro ao limpar dados armazenados:', error);
        return false;
    }
}

/**
 * Exporta todos os currículos armazenados para um arquivo JSON
 * @returns {Object} Objeto com todos os currículos armazenados
 */
function exportAllStoredData() {
    try {
        const languages = getAvailableLanguages();
        const exportData = {
            languages: languages,
            curricula: {}
        };
        
        // Adicionar cada currículo ao objeto de exportação
        for (const langCode of Object.keys(languages)) {
            const curriculumData = getStoredResume(langCode);
            if (curriculumData) {
                exportData.curricula[langCode] = curriculumData;
            }
        }
        
        return exportData;
    } catch (error) {
        console.error('Erro ao exportar dados armazenados:', error);
        return null;
    }
}

/**
 * Importa currículos de um arquivo JSON exportado anteriormente
 * @param {Object} importData - Dados exportados anteriormente
 * @returns {boolean} - true se a importação foi bem-sucedida, false caso contrário
 */
function importStoredData(importData) {
    try {
        if (!importData || !importData.curricula) {
            return false;
        }
        
        // Importar cada currículo
        for (const [langCode, data] of Object.entries(importData.curricula)) {
            if (data) {
                storeResume(langCode, data);
            }
        }
        
        return true;
    } catch (error) {
        console.error('Erro ao importar dados:', error);
        return false;
    }
}

/**
 * Exporta os dados para um arquivo JSON para download
 */
function downloadStoredData() {
    const exportData = exportAllStoredData();
    if (!exportData) {
        return false;
    }
    
    // Criar um blob com os dados
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    // Criar um link para download
    const a = document.createElement('a');
    a.href = url;
    a.download = 'curriculos_exportados.json';
    document.body.appendChild(a);
    a.click();
    
    // Limpar
    setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, 0);
    
    return true;
}

/**
 * Verifica se a versão local difere da versão no servidor
 * @param {string} langCode - Código do idioma
 * @param {Object} serverData - Dados do servidor
 * @returns {boolean} - true se as versões são diferentes, false caso contrário
 */
function isLocalDifferentFromServer(langCode, serverData) {
    const localData = getStoredResume(langCode);
    if (!localData || !serverData) {
        return false;
    }
    
    // Comparar as versões usando JSON stringificado
    return JSON.stringify(localData) !== JSON.stringify(serverData);
}
