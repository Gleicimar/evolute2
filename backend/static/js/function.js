document.querySelectorAll('.delete-link').forEach(link => {
    link.addEventListener('click', function(event) {
        event.preventDefault();
        if (!confirm('Tem certeza que deseja deletar este lead?')) return;

        const leadId = this.dataset.leadId;
        const clickedLink = this;  // 🔹 guarda referência ao link

        fetch(`/painel/deletar_lead/${leadId}`, { method: 'POST' })
        .then(response => {
            if (response.ok) {// 🔹 verifica se a resposta foi bem-sucedida
                clickedLink.remove(); // 🔹 usa a referência correta
            } else {
                alert('Erro ao deletar lead.');
            }
        })
        .catch(error => console.error(error));
    });
});


 // Dark Mode Toggle
    function toggleDarkMode() {
      document.body.classList.toggle('dark-mode');
      const icon = document.getElementById('theme-icon');

      if (document.body.classList.contains('dark-mode')) {
        icon.className = 'fas fa-sun';
        localStorage.setItem('darkMode', 'enabled');
      } else {
        icon.className = 'fas fa-moon';
        localStorage.setItem('darkMode', 'disabled');
      }
    }

    // Load saved theme
    if (localStorage.getItem('darkMode') === 'enabled') {
      document.body.classList.add('dark-mode');
      document.getElementById('theme-icon').className = 'fas fa-sun';
    }