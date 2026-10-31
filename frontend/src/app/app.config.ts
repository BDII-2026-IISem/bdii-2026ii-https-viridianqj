import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideRouter, withComponentInputBinding, withInMemoryScrolling } from '@angular/router';
import { providePrimeNG } from 'primeng/config';
import { ConfirmationService, MessageService } from 'primeng/api';
import Aura from '@primeuix/themes/aura';
import { definePreset } from '@primeuix/themes';

import { routes } from './app.routes';
import { authInterceptor } from './core/auth.interceptor';
import { errorInterceptor } from './core/error.interceptor';
import { primengLicense } from '../environments/primeng-license';

// Paleta tomada del logo: rojo-naranja de fuego como color principal.
const BrasaGoPreset = definePreset(Aura, {
  semantic: {
    primary: {
      50: '#fff4ef',
      100: '#ffe4d6',
      200: '#ffc4a8',
      300: '#ff9a70',
      400: '#f87045',
      500: '#e8502a',
      600: '#c43d1d',
      700: '#9e2f17',
      800: '#7a2514',
      900: '#5a1c10',
      950: '#32100a',
    },
  },
});

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(
      routes,
      withComponentInputBinding(),
      withInMemoryScrolling({ scrollPositionRestoration: 'top' }),
    ),
    provideHttpClient(withInterceptors([authInterceptor, errorInterceptor])),
    providePrimeNG({
      license: primengLicense,
      inputVariant: 'outlined',
      ripple: true,
      theme: {
        preset: BrasaGoPreset,
        options: { darkModeSelector: '.app-dark', cssLayer: { name: 'primeng', order: 'theme, base, primeng, utilities' } },
      },
    }),
    ConfirmationService,
    MessageService,
  ],
};
