import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Button } from 'primeng/button';
import { Dialog } from 'primeng/dialog';
import { InputText } from 'primeng/inputtext';
import { Select } from 'primeng/select';
import { TableModule } from 'primeng/table';
import { Tag } from 'primeng/tag';
import { HasPermission } from '../../../../shared/directives/has-permission';
import { RecordStatus, STATUS_OPTIONS } from '../../../../models/security/status';
import { HttpVerb, ResourceI, ResourcePayload } from '../../../../models/security/resource';
import { ResourceApi } from '../../../../services/security/resource-api';
import { stateLabel, stateSeverity } from '../../../../shared/state-severity';

const VERB_OPTIONS: { label: string; value: HttpVerb }[] = [
  { label: 'GET', value: 'GET' },
  { label: 'POST', value: 'POST' },
  { label: 'PUT', value: 'PUT' },
  { label: 'PATCH', value: 'PATCH' },
  { label: 'DELETE', value: 'DELETE' },
];

@Component({
  selector: 'app-resource-list',
  standalone: true,
  imports: [HasPermission, ReactiveFormsModule, TableModule, Button, Tag, Dialog, InputText, Select],
  templateUrl: './resource-list.html',
  styleUrl: './resource-list.css',
})
export class ResourceList implements OnInit {
  private readonly service = inject(ResourceApi);
  private readonly fb = inject(FormBuilder);

  readonly statusOptions = STATUS_OPTIONS;
  readonly verbOptions = VERB_OPTIONS;
  readonly stateLabel = stateLabel;
  readonly stateSeverity = stateSeverity;

  readonly items = signal<ResourceI[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly search = signal('');
  readonly filtered = computed(() => {
    const q = this.search().trim().toLowerCase();
    return q
      ? this.items().filter((r) => r.route.toLowerCase().includes(q) || r.method.toLowerCase().includes(q))
      : this.items();
  });

  readonly dialogOpen = signal(false);
  readonly editing = signal<ResourceI | null>(null);
  readonly saving = signal(false);
  readonly formError = signal<string | null>(null);

  readonly form = this.fb.nonNullable.group({
    method: ['GET' as HttpVerb, Validators.required],
    route: ['', [Validators.required, Validators.pattern(/^\/api\/.+/), Validators.maxLength(200)]],
    status: ['ACTIVE' as RecordStatus, Validators.required],
  });

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.service.getAll().subscribe({
      next: (rows) => {
        this.items.set(rows);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('No se pudieron cargar los recursos.');
        this.loading.set(false);
      },
    });
  }

  openCreate(): void {
    this.editing.set(null);
    this.formError.set(null);
    this.form.reset({ method: 'GET', route: '/api/', status: 'ACTIVE' });
    this.dialogOpen.set(true);
  }

  openEdit(res: ResourceI): void {
    this.editing.set(res);
    this.formError.set(null);
    this.form.reset({ method: res.method, route: res.route, status: res.status as RecordStatus });
    this.dialogOpen.set(true);
  }

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const v = this.form.getRawValue();
    const payload: ResourcePayload = { method: v.method, route: v.route.trim(), status: v.status };
    const current = this.editing();
    const request = current ? this.service.update(current.id, payload) : this.service.create(payload);

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

  remove(res: ResourceI): void {
    if (!confirm(`¿Dar de baja el recurso ${res.method} ${res.route}? El registro se conserva como inactivo.`)) return;
    this.service.remove(res.id).subscribe({
      next: () => this.load(),
      error: () => this.error.set('No se pudo dar de baja el recurso.'),
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
