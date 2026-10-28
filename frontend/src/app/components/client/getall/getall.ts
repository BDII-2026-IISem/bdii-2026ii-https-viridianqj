import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Button } from 'primeng/button';
import { Dialog } from 'primeng/dialog';
import { InputText } from 'primeng/inputtext';
import { Select } from 'primeng/select';
import { TableModule } from 'primeng/table';
import { Tag } from 'primeng/tag';

import { ClientI } from '../../../models/business/client';
import { ClientService } from '../../../services/business/client';
import { stateLabel, stateSeverity } from '../../../shared/state-severity';

@Component({
  selector: 'app-getall',
  standalone: true,
  imports: [ReactiveFormsModule, TableModule, Button, Tag, Dialog, InputText, Select],
  templateUrl: './getall.html',
  styleUrl: './getall.css',
})
export class Getall implements OnInit {
  private readonly service = inject(ClientService);
  private readonly fb = inject(FormBuilder);

  readonly items = signal<ClientI[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  readonly search = signal('');
  readonly filtered = computed(() => {
    const q = this.search().trim().toLowerCase();
    if (!q) return this.items();
    return this.items().filter((c) =>
      [c.name, c.email ?? '', c.phone ?? ''].some((v) => v.toLowerCase().includes(q)),
    );
  });

  readonly dialogOpen = signal(false);
  readonly editing = signal<ClientI | null>(null);
  readonly saving = signal(false);
  readonly formError = signal<string | null>(null);

  readonly severity = stateSeverity;
  readonly label = stateLabel;

  readonly documentTypes = [
    { label: 'Cédula de ciudadanía', value: 'CC' },
    { label: 'Cédula de extranjería', value: 'CE' },
    { label: 'Tarjeta de identidad', value: 'TI' },
    { label: 'NIT', value: 'NIT' },
    { label: 'Pasaporte', value: 'PASAPORTE' },
  ];

  readonly form = this.fb.nonNullable.group({
    documentType: ['CC', Validators.required],
    documentNumber: ['', [Validators.required, Validators.maxLength(30)]],
    name: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(150)]],
    phone: ['', Validators.maxLength(30)],
    email: ['', [Validators.email, Validators.maxLength(150)]],
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
        this.error.set('No se pudo cargar clientes. Revisa que el backend esté corriendo en el puerto 8000.');
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
    this.form.reset({ documentType: 'CC', documentNumber: '', name: '', phone: '', email: '' });
    this.dialogOpen.set(true);
  }

  openEdit(client: ClientI): void {
    this.editing.set(client);
    this.formError.set(null);
    this.form.reset({
      documentType: client.documentType,
      documentNumber: client.documentNumber,
      name: client.name,
      phone: client.phone ?? '',
      email: client.email ?? '',
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
      documentType: v.documentType,
      documentNumber: v.documentNumber.trim(),
      name: v.name.trim(),
      phone: v.phone.trim() || null,
      email: v.email.trim() || null,
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

  remove(client: ClientI): void {
    if (!confirm(`¿Dar de baja a ${client.name}? El registro se conserva como inactivo.`)) return;
    this.service.remove(client.id).subscribe({
      next: () => this.load(),
      error: () => this.error.set('No se pudo dar de baja el cliente.'),
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
