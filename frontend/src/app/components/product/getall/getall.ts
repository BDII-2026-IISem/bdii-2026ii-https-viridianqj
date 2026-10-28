import { CurrencyPipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Button } from 'primeng/button';
import { Dialog } from 'primeng/dialog';
import { InputNumber } from 'primeng/inputnumber';
import { InputText } from 'primeng/inputtext';
import { TableModule } from 'primeng/table';
import { Tag } from 'primeng/tag';

import { ProductI } from '../../../models/business/product';
import { ProductService } from '../../../services/business/product';
import { stateLabel, stateSeverity } from '../../../shared/state-severity';

@Component({
  selector: 'app-getall',
  standalone: true,
  imports: [ReactiveFormsModule, TableModule, Button, Tag, Dialog, InputText, InputNumber, CurrencyPipe],
  templateUrl: './getall.html',
  styleUrl: './getall.css',
})
export class Getall implements OnInit {
  private readonly service = inject(ProductService);
  private readonly fb = inject(FormBuilder);

  readonly items = signal<ProductI[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  readonly search = signal('');
  readonly filtered = computed(() => {
    const q = this.search().trim().toLowerCase();
    if (!q) return this.items();
    return this.items().filter((p) =>
      [p.sku, p.name, p.description ?? ''].some((v) => v.toLowerCase().includes(q)),
    );
  });

  readonly dialogOpen = signal(false);
  readonly editing = signal<ProductI | null>(null);
  readonly saving = signal(false);
  readonly formError = signal<string | null>(null);

  readonly severity = stateSeverity;
  readonly label = stateLabel;

  readonly form = this.fb.nonNullable.group({
    sku: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(50)]],
    name: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(150)]],
    description: ['', Validators.maxLength(255)],
    price: [0, [Validators.required, Validators.min(0)]],
  });

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

  onSearch(event: Event): void {
    this.search.set((event.target as HTMLInputElement).value);
  }

  openCreate(): void {
    this.editing.set(null);
    this.formError.set(null);
    this.form.reset({ sku: '', name: '', description: '', price: 0 });
    this.dialogOpen.set(true);
  }

  openEdit(product: ProductI): void {
    this.editing.set(product);
    this.formError.set(null);
    this.form.reset({
      sku: product.sku,
      name: product.name,
      description: product.description ?? '',
      price: Number(product.price),
    });
    this.dialogOpen.set(true);
  }

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const v = this.form.getRawValue();
    const payload = {
      sku: v.sku.trim(),
      name: v.name.trim(),
      description: v.description.trim() || null,
      price: v.price.toFixed(2),
    };

    const current = this.editing();
    const request = current
      ? this.service.update(current.id, payload)
      : this.service.create(payload);

    this.saving.set(true);
    this.formError.set(null);
    request.subscribe({
      next: () => {
        this.saving.set(false);
        this.dialogOpen.set(false);
        this.load();
      },
      error: (err: HttpErrorResponse) => {
        this.saving.set(false);
        this.formError.set(this.describe(err));
      },
    });
  }

  remove(product: ProductI): void {
    if (!confirm(`¿Dar de baja el producto ${product.name}? El registro se conserva como inactivo.`)) return;
    this.service.remove(product.id).subscribe({
      next: () => this.load(),
      error: () => this.error.set('No se pudo dar de baja el producto.'),
    });
  }

  private describe(err: HttpErrorResponse): string {
    const body = err.error;
    if (body && typeof body === 'object') {
      return Object.entries(body)
        .map(([campo, msgs]) => `${campo}: ${Array.isArray(msgs) ? msgs.join(' ') : msgs}`)
        .join(' · ');
    }
    return 'No se pudo guardar. Revisa que el backend esté corriendo.';
  }
}
