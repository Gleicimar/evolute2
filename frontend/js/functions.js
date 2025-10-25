
// Cole no seu arquivo JS
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});


const MenuMobile = document.getElementById('menu_mov');

MenuMobile.addEventListener('click', () => {
  const Menu = document.querySelector('.menu');
  if (Menu.classList.contains('active')) {
    Menu.classList.remove('active');
  } else {
    Menu.classList.add('active');
    }
 });


/**********chamada da Api */
const API_URL = "https://evolute2.onrender.com";
//  const API_URL = 'http://127.0.0.1:5000'; //Subtituir pela url do vercel ou heroku quando for fazer o deploy

//enviar formulário

//selecionar o formulário
const form = document.getElementById('contactForm');

//escutar evento de envio do formulário

form.addEventListener('submit', async(e)=> {
  e.preventDefault(); //impedir o comportamento padrão de recarregar a página

  //Pegar os dados do formulário
  const nome = form.nome.value.trim();
  const email = form.email.value.trim();
  const mensagem = form.mensagem.value.trim();

  //Botao de enivo mostrar que está enviando
  const botaoEnviar = form.querySelector('input[type="submit"]');
  botaoEnviar.value = 'Enviando...';
  botaoEnviar.disabled = true;

  //Enviar os dados para a API
  try {
    if (!nome || !email || !mensagem) {
      alert('Por favor, preencha todos os campos.');
      botaoEnviar.disabled = false;
      botaoEnviar.value = 'Enviar Mensagem';
      return;
}
    //enviar os dados  do formulário para a API
    const  response = await fetch(`${API_URL}/api/leads`, {
      method: 'POST',
      headers: {
        'Content-type': 'application/json',
      },
      body: JSON.stringify({
        nome: nome,
        email: email,
        mensagem: mensagem
      }),
    })
    if(response.ok) {
      alert('Mensagem enviada com sucesso! :)');

      form.reset();
    }else {
      alert('Erro ao enviar a mensagem. Tente novamente mais tarde.');
    }
  } catch (error) {
    console.error('Erro:', error);
    alert('Erro ao enviar a mensagem. Tente novamente mais tarde.');
  } finally{
    botaoEnviar.disabled = false;
    botaoEnviar.value = 'Enviar Mensagem';
  }
});

/**********fim chamada da Api */
