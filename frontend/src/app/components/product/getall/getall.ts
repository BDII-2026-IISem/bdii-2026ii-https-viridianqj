import { CurrencyPipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { Button } from 'primeng/button';
import { TableModule } from 'primeng/table';
import { Tag } from 'primeng/tag';

import { ProductI } from '../../../models/business/product';
import { ProductService } from '../../../services/business/product';
import { stateLabel, stateSeverity } from '../../../shared/state-severity';

@Component({
  selector: 'app-getall',
  standalone: true,
  imports: [TableModule, Button, Tag, CurrencyPipe],
  templateUrl: './getall.html',
  styleUrl: './getall.css',
})
export class Getall implements OnInit {
  private readonly service = inject(ProductService);

  readonly items = signal<ProductI[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  readonly severity = stateSeverity;
  readonly label = stateLabel;

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.service.getAll().subscribe({
      next: (data) => {
        this.items.set(data);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('No se pudo cargar productos. Revisa que el backend esté corriendo en el puerto 8000.');
        this.loading.set(false);
      },
    });
  }
}
