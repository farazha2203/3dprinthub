(function () {
  function installCommandCenterLink() {
    var navbar = document.getElementById('navbar-nav');
    if (!navbar || document.getElementById('phase50-command-center-link')) return;

    var item = document.createElement('li');
    item.className = 'nav-item';
    item.id = 'phase50-command-center-link';
    item.innerHTML = '<a class="nav-link menu-link" href="/admin/command-center/">' +
      '<i class="ri-bank-line"></i><span>مرکز مالی و بازرگانی</span>' +
      '<span class="badge bg-warning-subtle text-warning ms-auto">50.A</span></a>';

    var firstDashboard = navbar.querySelector('.nav-item');
    if (firstDashboard && firstDashboard.nextSibling) {
      navbar.insertBefore(item, firstDashboard.nextSibling);
    } else {
      navbar.appendChild(item);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', installCommandCenterLink, { once: true });
  } else {
    installCommandCenterLink();
  }
})();
