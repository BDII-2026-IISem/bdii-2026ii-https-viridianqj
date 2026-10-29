import { Component, OnInit, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Toast } from 'primeng/toast';

import { SessionStore } from './core/session';
import { Aside } from './components/layout/aside/aside';
import { Footer } from './components/layout/footer/footer';
import { Header } from './components/layout/header/header';
import { AuthService } from './services/auth';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, Header, Aside, Footer, Toast],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App implements OnInit {
  readonly session = inject(SessionStore);
  private readonly auth = inject(AuthService);

  ngOnInit(): void {
    // Tras recargar (F5) hay tokens guardados pero no el usuario: se vuelve a pedir el perfil.
    if (this.session.isAuthenticated() && !this.session.user()) {
      this.auth.profile().subscribe({ error: () => this.session.clear() });
    }
  }
}
