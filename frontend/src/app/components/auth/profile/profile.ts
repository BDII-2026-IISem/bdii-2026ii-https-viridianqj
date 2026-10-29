import { Component, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Button } from 'primeng/button';

import { SessionStore } from '../../../core/session';
import { AuthService } from '../../../services/auth';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [Button],
  templateUrl: './profile.html',
  styleUrl: './profile.css',
})
export class Profile {
  readonly session = inject(SessionStore);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  readonly loggingOut = signal(false);

  logout(): void {
    this.loggingOut.set(true);
    this.auth.logout().subscribe({
      complete: () => this.leave(),
      error: () => this.leave(),
    });
  }

  private leave(): void {
    this.session.clear();
    this.loggingOut.set(false);
    this.router.navigate(['/login']);
  }
}
