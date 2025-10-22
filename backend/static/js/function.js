document.querySelectorAll('.delete-link').forEach(link => {
    link.addEventListener('click', function(event) {
        event.preventDefault();
        if (!confirm('Tem certeza que deseja deletar este lead?')) return;

        const leadId = this.dataset.leadId;
        const clickedLink = this;  // 🔹 guarda referência ao link

        fetch(`/dashboard/deletar_lead/${leadId}`, { method: 'POST' })
        .then(response => {
            if (response.ok) {
                clickedLink.remove(); // 🔹 usa a referência correta
            } else {
                alert('Erro ao deletar lead.');
            }
        })
        .catch(error => console.error(error));
    });
});
