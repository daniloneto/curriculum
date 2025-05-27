// JavaScript para a página de geração de PDF
document.addEventListener('DOMContentLoaded', function() {
    // Obter elementos do DOM
    const languageSelect = document.getElementById('language-select');
    const formatOptions = document.querySelectorAll('.format-option');
    const generateButton = document.getElementById('generate-button');
    const alertBox = document.getElementById('alert-box');
    const downloadLinkContainer = document.getElementById('download-link-container');
    const downloadLink = document.getElementById('download-link');
    const debugInfo = document.getElementById('debug-info');
    const debugOutput = document.getElementById('debug-output');
    
    // Mostrar área de debug em ambiente de desenvolvimento (verificar usando URL)
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    if (isLocalhost) {
        debugInfo.style.display = 'block';
    }
    
    // Log para depuração
    console.log('Opções de formato encontradas:', formatOptions.length);
    formatOptions.forEach((opt, index) => {
        console.log(`Opção ${index + 1}:`, opt.textContent.trim(), 'data-format:', opt.dataset.format, 'data-template:', opt.dataset.template);
    });
    
    let selectedFormat = null;
    let selectedTemplate = null;
    
    // Selecionar um formato quando clicado
    formatOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Desmarcar todas as opções
            formatOptions.forEach(opt => opt.classList.remove('selected'));
            
            // Marcar a opção selecionada
            this.classList.add('selected');
            
            // Armazenar o formato e o template selecionados
            selectedFormat = this.dataset.format;
            selectedTemplate = this.dataset.template || null;
            
            // Habilitar o botão de geração
            updateGenerateButton();
        });
    });
    
    // Atualizar o estado do botão de geração
    function updateGenerateButton() {
        if (languageSelect.value && selectedFormat) {
            generateButton.disabled = false;
        } else {
            generateButton.disabled = true;
        }
    }
    
    // Atualizar o botão quando o idioma mudar
    languageSelect.addEventListener('change', updateGenerateButton);
      // Gerar o PDF quando o botão for clicado
    generateButton.addEventListener('click', function() {
        const selectedLanguage = languageSelect.value;
        
        if (!selectedLanguage || !selectedFormat) {
            showAlert('Selecione um idioma e um formato', 'danger');
            return;
        }
        
        // Log para depuração
        console.log('Gerando currículo:', {
            language: selectedLanguage,
            format: selectedFormat,
            template: selectedTemplate
        });
        
        // Mostrar indicador de carregamento
        generateButton.innerHTML = '<span class="loading"></span> Gerando...';
        generateButton.disabled = true;
        
        // Esconder o link de download existente
        downloadLinkContainer.style.display = 'none';
        
        // Enviar a solicitação para gerar o PDF
        fetch('/generate_pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                language: selectedLanguage,
                format: selectedFormat,
                template: selectedTemplate
            })
        })        .then(response => {
            // Registrar informações sobre a resposta para depuração
            if (debugOutput) {
                addDebugInfo('Resposta do servidor:', {
                    status: response.status,
                    statusText: response.statusText
                });
            }
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (debugOutput) {
                addDebugInfo('Dados de resposta:', data);
            }
            
            if (data.error) {
                showAlert(data.error, 'danger');
            } else {
                showAlert('Arquivo gerado com sucesso!', 'success');
                
                // Log para depuração
                console.log('Resposta do servidor:', data);
                  // Exibir o link para download
                downloadLink.href = data.download_url;
                downloadLink.textContent = `Baixar ${data.filename}`;
                downloadLinkContainer.style.display = 'block';
                
                // Log adicional para depuração
                console.log('URL de download:', data.download_url);
                console.log('Nome do arquivo:', data.filename);
                  // Fazer o download automaticamente
                setTimeout(function() {
                    console.log('Redirecionando para:', data.download_url);
                    if (debugOutput) {
                        addDebugInfo('Iniciando download:', {
                            url: data.download_url,
                            filename: data.filename
                        });
                    }
                    
                    // Usar um link temporário para garantir o download
                    const tempLink = document.createElement('a');
                    tempLink.href = data.download_url;
                    tempLink.setAttribute('download', data.filename);
                    tempLink.setAttribute('target', '_blank');
                    document.body.appendChild(tempLink);
                    tempLink.click();
                    document.body.removeChild(tempLink);
                    
                    // Verificar se o arquivo existe via API de depuração (apenas em localhost)
                    if (isLocalhost) {
                        setTimeout(function() {
                            fetch(`/debug/file_exists/${data.filename}`)
                                .then(response => response.json())
                                .then(fileInfo => {
                                    addDebugInfo('Informações do arquivo:', fileInfo);
                                })
                                .catch(error => {
                                    addDebugInfo('Erro ao verificar arquivo:', error.message);
                                });
                        }, 500);
                    }
                    
                    // Fallback: se o método acima não funcionar, redirecionar diretamente
                    setTimeout(function() {
                        if (debugOutput) {
                            addDebugInfo('Usando fallback de download', { url: data.download_url });
                        }
                        window.location.href = data.download_url;
                    }, 1000);
                }, 1000);
            }
        })        .catch(error => {
            console.error('Erro na requisição:', error);
            showAlert('Erro ao gerar o arquivo: ' + error, 'danger');
            if (debugOutput) {
                addDebugInfo('Erro na requisição:', {
                    message: error.message,
                    stack: error.stack
                });
            }
        })
        .finally(() => {
            // Restaurar o botão
            generateButton.innerHTML = 'Gerar';
            generateButton.disabled = false;
        });
    });
    
    // Função para adicionar informações de depuração
    function addDebugInfo(label, data) {
        if (debugOutput) {
            const timestamp = new Date().toLocaleTimeString();
            let content = typeof data === 'object' ? JSON.stringify(data, null, 2) : data;
            debugOutput.innerHTML += `[${timestamp}] ${label}\n${content}\n\n`;
            debugOutput.scrollTop = debugOutput.scrollHeight;
        }
    }
    
    // Função para exibir alertas
    function showAlert(message, type) {
        alertBox.innerHTML = message;
        alertBox.className = `alert alert-${type}`;
        alertBox.style.display = 'block';
        
        // Adicionar à área de debug
        addDebugInfo('Alerta:', { type, message });
        
        // Esconder a mensagem após 5 segundos
        setTimeout(function() {
            alertBox.style.display = 'none';
        }, 5000);
    }
    
    // Inicializar o estado do botão
    updateGenerateButton();
});
