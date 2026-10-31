import { Directive, TemplateRef, ViewContainerRef, effect, inject, input } from '@angular/core';

import { SessionStore } from '../../core/session';

// Muestra el elemento solo si la sesión tiene el permiso ("MÉTODO /api/recurso/").
// Se vuelve a evaluar cada vez que cambian los permisos de la sesión.
@Directive({ selector: '[appHasPermission]' })
export class HasPermission {
  private readonly session = inject(SessionStore);
  private readonly template = inject(TemplateRef<unknown>);
  private readonly container = inject(ViewContainerRef);

  readonly appHasPermission = input.required<string>();

  constructor() {
    effect(() => {
      // Leer el signal aquí garantiza que el effect se reejecute al cambiar permisos.
      this.session.permissions();
      const allowed = this.session.canPermission(this.appHasPermission());

      this.container.clear();
      if (allowed) {
        this.container.createEmbeddedView(this.template);
      }
    });
  }
}
