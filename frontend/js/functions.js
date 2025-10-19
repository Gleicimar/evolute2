const MenuMobile = document.getElementById('menu_mov');

MenuMobile.addEventListener('click', () => {
  const Menu = document.querySelector('.menu');
  if (Menu.classList.contains('active')) {
    Menu.classList.remove('active');
  } else {
    Menu.classList.add('active');
    }
 });
