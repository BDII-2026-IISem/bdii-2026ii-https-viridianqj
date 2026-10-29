import { Injectable, computed, signal } from '@angular/core';

export interface TokenPair {
  access: string;
  refresh: string;
  tokenType: string;
  accessExpiresIn: number;
}

export interface SessionUser {
  id: number;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  avatar: string | null;
  status: string;
}

const STORAGE_KEY = 'brasago.session.v1';

@Injectable({ providedIn: 'root' })
export class SessionStore {
  private readonly _tokens = signal<TokenPair | null>(this.restore());
  private readonly _user = signal<SessionUser | null>(null);

  readonly tokens = this._tokens.asReadonly();
  readonly user = this._user.asReadonly();
  readonly isAuthenticated = computed(() => this._tokens() !== null);

  accessToken(): string | null {
    return this._tokens()?.access ?? null;
  }

  refreshToken(): string | null {
    return this._tokens()?.refresh ?? null;
  }

  saveTokens(pair: TokenPair): void {
    this._tokens.set(pair);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(pair));
    } catch {
      // Sin almacenamiento disponible: la sesión dura solo mientras la pestaña esté abierta.
    }
  }

  setUser(user: SessionUser): void {
    this._user.set(user);
  }

  clear(): void {
    this._tokens.set(null);
    this._user.set(null);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      // Sin almacenamiento disponible: nada que limpiar.
    }
  }

  private restore(): TokenPair | null {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? (JSON.parse(raw) as TokenPair) : null;
    } catch {
      return null;
    }
  }
}
