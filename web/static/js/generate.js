// JavaScript para a página de geração de PDF
document.addEventListener('DOMContentLoaded', function() {
    // Obter elementos do DOM
    const languageSelect = document.getElementById('language-select');
    const formatOptions = document.querySelectorAll('.format-option');
    const generateButton = document.getElementById('generate-button');
    const alertBox = document.getElementById('alert-box');
    const downloadLinkContainer = document.getElementById('download-link-container');
    const downloadLink = document.getElementById('download-link');
    
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
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showAlert(data.error, 'danger');
            } else {
                showAlert('Arquivo gerado com sucesso!', 'success');
                
                // Exibir o link para download
                downloadLink.href = data.download_url;
                downloadLink.textContent = `Baixar ${data.filename}`;
                downloadLinkContainer.style.display = 'block';
                
                // Fazer o download automaticamente
                setTimeout(function() {
                    window.location = data.download_url;
                }, 1000);
            }
        })
        .catch(error => {
            showAlert('Erro ao gerar o arquivo: ' + error, 'danger');
        })
        .finally(() => {
            // Restaurar o botão
            generateButton.innerHTML = 'Gerar';
            generateButton.disabled = false;
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
    
    // Inicializar o estado do botão
    updateGenerateButton();
});
