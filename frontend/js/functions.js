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

const API_URL = 'http://127.0.0.1/projetos/Duoempresa/frontend/'; //Subtituir pela url do vercel ou heroku quando for fazer o deploy

//enviar formulário

//selicionar o formulário
const form = document.getElementById('contactForm');

//escutar evento de envio do formulário

form.addEventListener('submit', async(e)=> {
  e.preventDefault(); //impedir o comportamento padrão de recarregar a página

  //Pegar os dados do formulário
  const nome = form.nome.value;
  const email = form.email.value;
  const mensagem = form.mensagem.value;

  //Botao de enivo mostrar que está enviando
  const botaoEnviar = form.querySelector('input[type="submit"]');
  botaoEnviar.value = 'Enviando...';
  botaoEnviar.disabled = true;

  //Enviar os dados para a API
  try {
    //enviar os dados  do formulário para a API
    const  response = await fetch(`${API_URL}/contato.html`, {
      method: 'POST',
      headers: {
        'Content-type': 'application/json',
      },
      body: JSON.stringify({ nome, email, mensagem }),
    })
    if(response.ok) {
      alert('Mensagem enviada com sucesso!');
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
