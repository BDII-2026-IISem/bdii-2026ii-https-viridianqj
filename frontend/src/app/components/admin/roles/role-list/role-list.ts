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
import { RoleI, RolePayload } from '../../../../models/security/role';
import { RoleApi } from '../../../../services/security/role-api';
import { stateLabel, stateSeverity } from '../../../../shared/state-severity';

@Component({
  selector: 'app-role-list',
  standalone: true,
  imports: [HasPermission, ReactiveFormsModule, TableModule, Button, Tag, Dialog, InputText, Select],
  templateUrl: './role-list.html',
  styleUrl: './role-list.css',
})
export class RoleList implements OnInit {
  private readonly service = inject(RoleApi);
  private readonly fb = inject(FormBuilder);

  readonly statusOptions = STATUS_OPTIONS;
  readonly stateLabel = stateLabel;
  readonly stateSeverity = stateSeverity;

  readonly items = signal<RoleI[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly search = signal('');
  readonly filtered = computed(() => {
    const q = this.search().trim().toLowerCase();
    return q ? this.items().filter((r) => r.name.toLowerCase().includes(q)) : this.items();
  });

  readonly dialogOpen = signal(false);
  readonly editing = signal<RoleI | null>(null);
  readonly saving = signal(false);
  readonly formError = signal<string | null>(null);

  readonly form = this.fb.nonNullable.group({
    name: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(30), Validators.pattern(/^[A-Za-z][A-Za-z_]*$/)]],
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
        this.error.set('No se pudieron cargar los roles.');
        this.loading.set(false);
      },
    });
  }

  openCreate(): void {
    this.editing.set(null);
    this.formError.set(null);
    this.form.reset({ name: '', status: 'ACTIVE' });
    this.dialogOpen.set(true);
  }

  openEdit(role: RoleI): void {
    this.editing.set(role);
    this.formError.set(null);
    this.form.reset({ name: role.name, status: role.status as RecordStatus });
    this.dialogOpen.set(true);
  }

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const v = this.form.getRawValue();
    const payload: RolePayload = { name: v.name.trim().toUpperCase(), status: v.status };
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

  remove(role: RoleI): void {
    if (!confirm(`¿Dar de baja el rol ${role.name}? El registro se conserva como inactivo.`)) return;
    this.service.remove(role.id).subscribe({
      next: () => this.load(),
      error: () => this.error.set('No se pudo dar de baja el rol.'),
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
