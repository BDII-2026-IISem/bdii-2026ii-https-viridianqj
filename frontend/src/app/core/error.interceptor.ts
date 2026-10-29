import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { MessageService } from 'primeng/api';
import { catchError, throwError } from 'rxjs';

import { environment } from '../../environments/environment';

const MESSAGES: Record<number, string> = {
  403: 'No tienes permiso para realizar esta acción.',
  404: 'El registro solicitado no existe.',
  409: 'Hay un conflicto con los datos existentes.',
};

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const messages = inject(MessageService);

  return next(req).pipe(
    catchError((err: HttpErrorResponse) => {
      // 401 lo gestiona el authInterceptor y 400 lo muestra cada formulario.
      if (req.url.startsWith(environment.apiUrl) && err.status !== 401 && err.status !== 400) {
        const detail =
          err.status === 0
            ? 'Sin conexión con el servidor.'
            : err.status >= 500
              ? 'Error interno del servidor.'
              : MESSAGES[err.status];
        if (detail) {
          messages.add({ severity: 'error', summary: `Error ${err.status}`, detail, life: 4000 });
        }
      }
      return throwError(() => err);
    }),
  );
};
