import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Drawer } from 'primeng/drawer';
import { Toast } from 'primeng/toast';

import { SessionStore } from './core/session';
import { Aside } from './components/layout/aside/aside';
import { Footer } from './components/layout/footer/footer';
import { Header } from './components/layout/header/header';
import { AuthService } from './services/auth';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, Header, Aside, Footer, Drawer, Toast],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App implements OnInit {
  readonly session = inject(SessionStore);
  private readonly auth = inject(AuthService);

  readonly mobileOpen = signal(false);
  readonly sidebarCollapsed = signal(false);

  ngOnInit(): void {
    // Tras recargar (F5) hay tokens guardados pero no el usuario: se vuelve a pedir el perfil.
    if (this.session.isAuthenticated() && !this.session.user()) {
      this.auth.refreshSession().subscribe({ error: () => this.session.clear() });
    }
  }

  // En escritorio colapsa o muestra el menú lateral; en móvil abre el drawer.
  onMenuToggle(): void {
    if (window.matchMedia('(min-width: 1024px)').matches) {
      this.sidebarCollapsed.update((v) => !v);
    } else {
      this.mobileOpen.set(true);
    }
  }

  closeMenu(): void {
    this.mobileOpen.set(false);
  }
}
